import os
from datetime import datetime

import requests
from docxtpl import DocxTemplate
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.orm.exc import DetachedInstanceError

from data import db_session
from data.client import Client
from data.user import User
from forms.add_client_form import AddClientForm
from forms.register_form import RegisterForm
from forms.sign_in_form import SignInForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "DocC_Shield"
login_manager = LoginManager()
login_manager.init_app(app)

DOCUMENTS = (
    "ХОДАТАЙСТВО ОБ ОБЕСПЕЧЕНИИ ИСКА",
    "ЗАЯВЛЕНИЕ О ВЫДАЧЕ ИСПОЛНИТЕЛЬНОГО ЛИСТА",
    "ИСКОВОЕ ЗАЯВЛЕНИЕ О ЗАЩИТЕ ЧЕСТИ",
    "ИСКОВОЕ ЗАЯВЛЕНИЕ О РАЗДЕЛЕ НАСЛЕДСТВА",
    "ИСКОВОЕ ЗАЯВЛЕНИЕ ОБ ОБЖАЛОВАНИИ ДИСЦИПЛИНАРНОГО ВЗЫСКАНИЯ",
    "ХОДАТАЙСТВО ОБ ИСТРЕБОВАНИИ ДОКУМЕНТА"
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


@app.route("/clients")
@login_required
def clients():
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
        try:
            current_user.clients.append(client)
        except DetachedInstanceError:
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
        form.birth_date.data = ".".join(str(client.birth_date).split()[0].split(".")[::-1])

    if form.validate_on_submit():
        new_session = db_session.create_session()
        client = new_session.query(Client).filter(Client.id == client_id).first()

        client.surname = form.surname.data
        client.name = form.name.data
        client.patronymic = form.patronymic.data
        client.address = form.address.data
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


@app.route("/show_address/<int:client_id>", methods=["GET", "POST"])
@login_required
def show_address(client_id):
    new_session = db_session.create_session()
    client = new_session.query(Client).filter(Client.id == client_id).first()
    lon, lat = map(float, requests.get(f'https://geocode-maps.yandex.ru/1.x/',
                                       params={
                                           'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                                           'geocode': f'{client.address}',
                                           'format': 'json'
                                       }).json()[
        "response"][
        "GeoObjectCollection"][
        "featureMember"][0][
        "GeoObject"][
        "Point"][
        'pos'].split())
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={lon},{lat}&" \
                  f"spn=0.005,0.005&l=map&pt={lon},{lat},pm2rdm"
    response = requests.get(map_request)
    with open('static/img/map.png', "wb") as file:
        file.write(response.content)
    return render_template('show_address.html', user=current_user)


@app.route("/create_document", methods=["GET", "POST"])
def new_document():
    new_session = db_session.create_session()
    user_clients = new_session.query(Client).filter((Client.user == current_user))
    if request.method == "GET" or not (document_id := request.form.get("document_id")):
        return render_template(
            "create_document.html",
            title="Новый документ",
            clients=user_clients,
            documents=enumerate(DOCUMENTS),
            user=current_user
        )
    if request.form.get("client_id") != 'Nothing':
        client = new_session.query(Client).filter(Client.id == request.form.get("client_id")).first()
        context = {
            "surname": client.surname,
            "name": client.name,
            "patronymic": client.patronymic,
            "address": client.address,
            "birth_date_place": client.birth_date
        }
        document_way = """/static/documents/NewDocument.docx"""
        document = DocxTemplate(f"""static/documents/{document_id}.docx""")
        document.render(context)
        document.save(f"./{document_way}")
        return redirect("/static/documents/NewDocument.docx")
    return render_template(
        "create_document.html",
        title="Новый документ",
        clients=user_clients,
        documents=enumerate(DOCUMENTS),
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
