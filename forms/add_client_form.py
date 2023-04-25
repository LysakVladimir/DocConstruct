from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddClientForm(FlaskForm):
    surname = StringField("ФАМИЛИЯ", validators=[DataRequired()])
    name = StringField("ИМЯ", validators=[DataRequired()])
    patronymic = StringField("ОТЧЕСТВО", validators=[DataRequired()])

    address = StringField("АДРЕС", validators=[DataRequired()])
    birth_date = StringField("ДАТА РОЖДЕНИЯ", validators=[DataRequired()])
    submit = SubmitField("Применить")
