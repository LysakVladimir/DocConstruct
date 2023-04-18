from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddClientForm(FlaskForm):
    surname = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    patronymic = StringField("Отчество", validators=[DataRequired()])

    address = StringField("Адрес", validators=[DataRequired()])
    birth_date = StringField("Дата рождения", validators=[DataRequired()])
    submit = SubmitField("Добавить")
