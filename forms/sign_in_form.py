from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired


class SignInForm(FlaskForm):
    email = EmailField("ВВЕДИТЕ ПОЧТУ", validators=[DataRequired()])
    password = PasswordField("ВВЕДИТЕ ПАРОЛЬ", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")
