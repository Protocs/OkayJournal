from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login = StringField(id='input_login', validators=[DataRequired()])
    password = PasswordField(id='input_password', validators=[DataRequired()])
    remember = BooleanField()
    submit = SubmitField('Войти')
