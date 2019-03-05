from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login = StringField(id='input_login', validators=[DataRequired()])
    password = PasswordField(id='input_password', validators=[DataRequired()])
    remember = BooleanField()
    submit = SubmitField('Войти')


class RegisterRequestForm(FlaskForm):
    region = StringField(id="input_region", validators=[DataRequired()])
    city = StringField(id="input_city", validators=[DataRequired()])
    school = StringField(id="input_school", validators=[DataRequired()])
    name = StringField(id="input_name", validators=[DataRequired()])
    surname = StringField(id="input_surname", validators=[DataRequired()])
    patronymic = StringField(id="input_patronymic", validators=[DataRequired()])
    email = StringField(id="input_email", validators=[DataRequired()])
    password_first = PasswordField(id="input_password_first", validators=[DataRequired()])
    password_second = PasswordField(id="input_password_second", validators=[DataRequired()])
    submit = SubmitField("Отправить")