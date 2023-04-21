from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField("ВВЕДИТЕ ПОЧТУ", validators=[DataRequired()])
    password = PasswordField("ВВЕДИТЕ ПАРОЛЬ", validators=[DataRequired()])
    password_again = PasswordField("ПОВТОРИТЕ ПАРОЛЬ", validators=[DataRequired()])
    name = StringField("ВВЕДИТЕ ИМЯ ПОЛЬЗОВАТЕЛЯ", validators=[DataRequired()])
    submit = SubmitField("Зарегистрироваться")
