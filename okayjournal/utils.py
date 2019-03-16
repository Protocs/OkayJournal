from flask import session, redirect, make_response
from .db import USER_CLASSES, Student, Parent, SchoolAdmin, Teacher
from .local_settings import EMAIL_PASSWORD

from random import choice
from string import ascii_lowercase as lowercase, ascii_uppercase as uppercase, \
    digits

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LOGIN_PREFIXES = {Student.__name__: "stud", Parent.__name__: "par",
                  SchoolAdmin.__name__: "admin", Teacher.__name__: "teach"}

SYMBOLS = list(filter(lambda char: char not in ['l', 'I', '1', 'o', 'O', '0'],
                      list(uppercase) + list(lowercase) + list(digits)))

REGISTRATION_LETTER_TEXT = "Добро пожаловать в OkayJournal, {}!\nВаши данные" \
                           " для входа в систему:\nЛогин: {}\nПароль: {}\nОбр" \
                           "атите внимание, что данный пароль сгенерирован на" \
                           "ми и его нужно будет изменить при первом входе в " \
                           "систему.\nС уважением,\nАдминистрация OkayJournal"
APPROVAL_LETTER_TEXT = "Здравствуйте, {}.\nВаша заявка была рассмотрена и о" \
                       "добрена. Для Вас был сгенерирован логин:\n{}. \nДл" \
                       "я входа в систему можете использовать его или электр" \
                       "онную почту, а также пароль, который указывали при " \
                       "регистрации.\nС уважением,\nАдминистрация OkayJournal"
REJECTION_LETTER_TEXT = "Здравствуйте, {}.\nВаша заявка была рассмотрена и о" \
                        "тклонена. Проверьте корректность введенных данных и "\
                        "попробуйте ещё раз.\nС уважением,\nАдминистрация Ok" \
                        "ayJournal"


def generate_unique_login(user_status):
    users = globals()[user_status].query.all()
    last_id = users[-1].id if users else 0
    return LOGIN_PREFIXES[user_status] + str(last_id + 1).zfill(6)


def generate_throwaway_password():
    """Возвращает случайно сгенерированный пароль длиною в 8 символов."""
    result = ""
    used_symbols = []
    for k in range(8):
        symbol = choice(SYMBOLS)
        while symbol in used_symbols:
            symbol = choice(SYMBOLS)
        result += symbol
        used_symbols.append(symbol)
    return result


def logged_in():
    """Возвращает True, если произведен вход."""
    return 'user' in session


def login_required(func):
    """Перенаправляет на /login, если не залогинен."""

    def decorated(*args, **kwargs):
        if not logged_in():
            return redirect('/login')
        return func(*args, **kwargs)

    decorated.__name__ = func.__name__
    return decorated


def school_admin_only(func):
    @login_required
    def decorated(*args, **kwargs):
        if session['role'] != 'SchoolAdmin':
            return make_response("Вы не являетесь школьным администратором.")
        return func(*args, **kwargs)

    decorated.__name__ = func.__name__
    return decorated


def need_to_change_password(func):
    def decorated(*args, **kwargs):
        if session["user"]["throwaway_password"]:
            return redirect("/settings")
        return func(*args, **kwargs)

    decorated.__name__ = func.__name__
    return decorated


def user_equal(user1, user2):
    """Возвращает True, если id и role пользователей одинаковы
    При этом, вторым аргументом можно передать session.
    """
    user1_data = (user1.id, user1.__class__.__name__)
    if not any(isinstance(user2, user_class) for user_class in USER_CLASSES):
        user2_data = (user2["user"]["id"], user2["role"])
    else:
        user2_data = (user2.id, user2.__class__.__name__)
    return user1_data == user2_data


def send_registration_letter(email, login, password, name):
    message = MIMEMultipart()
    message['From'] = "admin@okayjournal.ru"
    message['To'] = email
    message['Subject'] = 'Регистрация в OkayJournal'
    text = REGISTRATION_LETTER_TEXT.format(name, login, password)
    message.attach(MIMEText(text, 'plain'))

    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    server.login("admin@okayjournal.ru", EMAIL_PASSWORD)
    server.send_message(message)
    server.quit()
    return True


def send_approval_letter(email, login, name):
    message = MIMEMultipart()
    message['From'] = "admin@okayjournal.ru"
    message['To'] = email
    message['Subject'] = 'Регистрация в OkayJournal'
    text = APPROVAL_LETTER_TEXT.format(name, login)
    message.attach(MIMEText(text, 'plain'))

    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    server.login("admin@okayjournal.ru", EMAIL_PASSWORD)
    server.send_message(message)
    server.quit()
    return True


def send_rejection_letter(email, name):
    message = MIMEMultipart()
    message['From'] = "admin@okayjournal.ru"
    message['To'] = email
    message['Subject'] = 'Регистрация в OkayJournal'
    text = REJECTION_LETTER_TEXT.format(name)
    message.attach(MIMEText(text, 'plain'))

    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    server.login("admin@okayjournal.ru", EMAIL_PASSWORD)
    server.send_message(message)
    server.quit()
    return True
