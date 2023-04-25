from datetime import datetime
from docxtpl import DocxTemplate
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.sign_in_form import SignInForm
from forms.register_form import RegisterForm
from forms.add_client_form import AddClientForm

from data import db_session
from data.user import User
from data.client import Client

app = Flask(__name__)
app.config["SECRET_KEY"] = "DocC_Shield"
login_manager = LoginManager()
login_manager.init_app(app)


DOCUMENTS = (
    "Ходатайство об обеспечении иска",
    "Заявление о выдачи испольнительного листа",
    "Исковое заявление о защите чести",
    "Исковое заявление о разделе наследства",
    "Исковое заявление об обжаловании дисциплинарного взыскания",
    "Ходатайство об истребовании документа"
)


@login_manager.user_loader
def load_user(user_id):
    new_session = db_session.create_session()
    return new_session.query(User).get(user_id)


@app.route("/")
@app.route("/index")
def index():
    if current_user.is_authenticated:
        return redirect("/clients")

    return redirect("/register")


@app.route("/clients", methods=["GET", "POST"])
@login_required
def clients():
    if request.method == "POST":
        return redirect(f"""/new_document/{request.form.get("document_id")}/{request.form.get("client_id")}""")

    new_session = db_session.create_session()
    user_clients = new_session.query(Client).filter((Client.user == current_user))
    return render_template("clients.html", title="Клиенты", clients=user_clients, user=current_user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect("/clients")
    form = RegisterForm()
    new_session = db_session.create_session()

    if not form.validate_on_submit():
        return render_template("register.html", title="Регистрация", form=form, user=current_user)

    if len(form.name.data) > 16:
        return render_template("register.html", title="Регистрация", form=form,
                               message="Слишком длинное имя. Не более 16 символов", user=current_user)

    if form.password.data != form.password_again.data:
        return render_template("register.html", title="Регистрация", form=form,
                               message="Пароли не совпадают", user=current_user)

    if new_session.query(User).filter(User.email == form.email.data).first():
        return render_template("register.html", title="Регистрация", form=form,
                               message="Пользователь с данной почтой уже существует.", user=current_user)

    user = User(name=form.name.data, email=form.email.data.lower())
    user.set_password(form.password.data)
    new_session.add(user)
    new_session.commit()
    login_user(user)

    return redirect("/clients")


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if current_user.is_authenticated:
        return redirect("/clients")
    form = SignInForm()
    new_session = db_session.create_session()

    if not form.validate_on_submit():
        return render_template("sign_in.html", title="Авторизация", form=form, user=current_user)

    user = new_session.query(User).filter(User.email == form.email.data.lower()).first()
    if user and user.check_password(form.password.data):
        login_user(user, remember=form.remember_me.data)
        return redirect("/clients")

    return render_template("sign_in.html", title="Авторизация",
                           form=form, message="Неправильный логин или пароль", user=current_user)


@app.route("/add_client", methods=["GET", "POST"])
@login_required
def add_client():
    form = AddClientForm()

    if form.validate_on_submit():
        new_session = db_session.create_session()
        client = Client()

        client.surname = form.surname.data
        client.name = form.name.data
        client.patronymic = form.patronymic.data

        client.address = form.address.data
        client.birth_date = datetime.strptime(form.birth_date.data, "%Y-%m-%d")

        current_user.clients.append(client)
        new_session.merge(current_user)
        new_session.commit()
        return redirect("/clients")

    return render_template("add_client.html", title="Новый клиент", form=form, user=current_user)


@app.route("/edit_client/<int:client_id>", methods=["GET", "POST"])
@login_required
def edit_client(client_id):
    form = AddClientForm()

    if request.method == "GET":
        new_session = db_session.create_session()
        client = new_session.query(Client).filter(Client.id == client_id).first()

        form.surname.data = client.surname
        form.name.data = client.name
        form.patronymic.data = client.patronymic
        form.address.data = client.address
        """------------------------ НАДО ИСПРАВИТЬ ЭТУ ДИЧЬ ------------------------"""
        form.birth_date.data = "/".join(str(client.birth_date).split()[0].split("-")[::-1])

    if form.validate_on_submit():
        new_session = db_session.create_session()
        client = new_session.query(Client).filter(Client.id == client_id).first()

        client.surname = form.surname.data
        client.name = form.name.data
        client.patronymic = form.patronymic.data
        client.address = form.address.data
        """------------------------ НАДО ИСПРАВИТЬ ЭТУ ДИЧЬ ------------------------"""
        client.birth_date = datetime.strptime(form.birth_date.data, "%Y-%m-%d")

        new_session.commit()
        return redirect("/clients")

    return render_template("add_client.html", title="Редактирование клиента", form=form, user=current_user)


@app.route("/remove_client/<int:client_id>", methods=["GET", "POST"])
@login_required
def remove_client(client_id):
    new_session = db_session.create_session()
    client = new_session.query(Client).filter(Client.id == client_id).first()
    new_session.delete(client)
    new_session.commit()
    return redirect("/clients")


@app.route("/new_document/<int:document_id>/<int:client_id>", methods=["GET", "POST"])
@login_required
def new_document(document_id, client_id):
    if request.method == "POST":
        return redirect("/clients")

    new_session = db_session.create_session()
    client = new_session.query(Client).filter(Client.id == client_id).first()

    document_way = "/static/documents/NewDocument.docx"
    document = DocxTemplate(f"static/documents/{document_id}.docx")

    context = {
        "surname":          client.surname,
        "name":             client.name,
        "patronymic":       client.patronymic,
        "address":          client.address,
        "birth_date_place": client.birth_date
    }
    document.render(context)
    document.save(f"./{document_way}")

    return render_template(
        "new_document.html",
        title="Новый документ",
        document_name=DOCUMENTS[document_id],
        document_way=document_way,
        client=client,
        user=current_user
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', user=current_user), 404


@app.errorhandler(401)
def unauthorized(e):
    return redirect('/sign_in')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/register")


if __name__ == "__main__":
    db_session.global_init("db/db_flask.db")
    session = db_session.create_session()

    app.run(debug=True)
