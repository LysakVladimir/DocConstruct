from datetime import datetime
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


@app.route("/clients")
def clients():
    new_session = db_session.create_session()
    user_clients = new_session.query(Client).filter((Client.user == current_user))

    return render_template("clients.html", clients=user_clients)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    new_session = db_session.create_session()

    if not form.validate_on_submit():
        return render_template("register.html", form=form)

    if form.password.data != form.password_again.data:
        return render_template("register.html", form=form, message="Пароли не совпадают")

    if new_session.query(User).filter(User.email == form.email.data).first():
        return render_template("register.html", form=form, message="Такой пользователь уже есть")

    user = User(name=form.name.data, email=form.email.data)
    user.set_password(form.password.data)
    new_session.add(user)
    new_session.commit()
    login_user(user)

    return redirect("/clients")


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    form = SignInForm()
    new_session = db_session.create_session()

    if not form.validate_on_submit():
        return render_template("sign_in.html", form=form)

    user = new_session.query(User).filter(User.email == form.email.data).first()
    if user and user.check_password(form.password.data):
        login_user(user, remember=form.remember_me.data)
        return redirect("/clients")

    return render_template("sign_in.html", form=form, message="Неправильный логин или пароль")


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
        """------------------------ НАДО ИСПРАВИТЬ ЭТУ ДИЧЬ ------------------------"""
        client.birth_date = datetime.strptime(form.birth_date.data, "%d/%m/%Y")

        current_user.new_document.append(client)
        new_session.merge(current_user)
        new_session.commit()
        return redirect("/clients")

    return render_template("add_client.html", title="Новый клиент", form=form)


@app.route("/edit_client/<int:id>", methods=["GET", "POST"])
@login_required
def edit_client(id):
    form = AddClientForm()

    if request.method == "GET":
        new_session = db_session.create_session()
        client = new_session.query(Client).filter(Client.id == id).first()

        form.surname.data = client.surname
        form.name.data = client.name
        form.patronymic.data = client.patronymic
        form.address.data = client.address
        """------------------------ НАДО ИСПРАВИТЬ ЭТУ ДИЧЬ ------------------------"""
        form.birth_date.data = "/".join(str(client.birth_date).split()[0].split("-")[::-1])

    if form.validate_on_submit():
        new_session = db_session.create_session()
        client = new_session.query(Client).filter(Client.id == id).first()

        client.surname = form.surname.data
        client.name = form.name.data
        client.patronymic = form.patronymic.data
        client.address = form.address.data
        """------------------------ НАДО ИСПРАВИТЬ ЭТУ ДИЧЬ ------------------------"""
        client.birth_date = datetime.strptime(form.birth_date.data, "%d/%m/%Y")

        new_session.commit()
        return redirect("/clients")

    return render_template("add_client.html", title="Редактирование клиента", form=form)


@app.route("/new_document")
def new_document():
    # new_session = db_session.create_session()
    # user_clients = new_session.query(Client).filter((Client.user == current_user))
    return redirect("/")


@app.route("/remove_client/<int:id>", methods=["GET", "POST"])
@login_required
def remove_client(id):
    new_session = db_session.create_session()
    client = new_session.query(Client).filter(Client.id == id).first()
    new_session.delete(client)
    new_session.commit()
    return redirect("/clients")


@app.route("/log_out")
@login_required
def log_out():
    logout_user()
    return redirect("/register")


if __name__ == "__main__":
    db_session.global_init("db/db_flask.db")
    session = db_session.create_session()

    app.run(debug=True)
