from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from validate_email import validate_email


class LoginForm(FlaskForm):
    login = StringField(id="input_login", validators=[DataRequired()])
    password = PasswordField(id="input_password", validators=[DataRequired()])
    remember = BooleanField()
    submit = SubmitField("Войти")


class RegisterRequestForm(FlaskForm):
    region = StringField(id="input_region", validators=[DataRequired()])
    city = StringField(id="input_city", validators=[DataRequired()])
    school = StringField(id="input_school", validators=[DataRequired()])
    name = StringField(id="input_name", validators=[DataRequired()])
    surname = StringField(id="input_surname", validators=[DataRequired()])
    patronymic = StringField(id="input_patronymic", validators=[DataRequired()])
    email = StringField(id="input_email", validators=[DataRequired()])
    password_first = PasswordField(
        id="input_password_first",
        validators=[
            DataRequired(),
            Length(8, message="В пароле должно быть не менее 8 символов"),
        ],
    )
    password_second = PasswordField(
        id="input_password_second",
        validators=[DataRequired(), EqualTo("password_first", "Пароли не совпадают")],
    )
    submit = SubmitField("Отправить")


class SchoolEditForm(FlaskForm):
    region = StringField("Регион", id="input_region", validators=[DataRequired()])
    city = StringField("Город", id="input_city", validators=[DataRequired()])
    school = StringField(
        "Название школы", id="input_school", validators=[DataRequired()]
    )
    submit = SubmitField("Изменить")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Старый пароль", validators=[DataRequired()])
    new_password = PasswordField("Новый пароль", validators=[DataRequired()])
    new_password_again = PasswordField(
        "Новый пароль (ещё раз)",
        validators=[DataRequired(), EqualTo("new_password", "Пароли не совпадают")],
    )
    submit = SubmitField("Сменить")


def email_validator(_, field):
    if not validate_email(field.data):
        raise ValidationError("Недействительный адрес электронной почты")


class ChangeEmailForm(FlaskForm):
    email = EmailField("Сменить почту", validators=[email_validator])
    submit = SubmitField("Сменить")


class AddTeacherForm(FlaskForm):
    surname = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    patronymic = StringField("Отчество", validators=[DataRequired()])
    email = StringField("Электронная почта", validators=[DataRequired()])
    submit = SubmitField("Добавить")


class AddStudentForm(FlaskForm):
    surname = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    patronymic = StringField("Отчество", validators=[DataRequired()])
    email = StringField("Электронная почта", validators=[DataRequired()])
    submit = SubmitField("Добавить")


class AddParentForm(FlaskForm):
    surname = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    patronymic = StringField("Отчество", validators=[DataRequired()])
    email = StringField("Электронная почта", validators=[DataRequired()])
    submit = SubmitField("Добавить")


class AddSubjectForm(FlaskForm):
    name = StringField("Название предмета", validators=[DataRequired()])
    submit = SubmitField("Добавить")
