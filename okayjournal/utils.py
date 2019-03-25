from itertools import cycle
from datetime import date, timedelta, datetime

from flask import session, redirect, abort, jsonify
from .db import USER_CLASSES, Student, Parent, SchoolAdmin, Teacher
from .local_settings import EMAIL_PASSWORD

from random import choice
from string import ascii_lowercase as lowercase, ascii_uppercase as uppercase, digits

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LOGIN_PREFIXES = {
    Student.__name__: "stud",
    Parent.__name__: "par",
    SchoolAdmin.__name__: "admin",
    Teacher.__name__: "teach",
}

SYMBOLS = list(
    filter(
        lambda char: char not in ["l", "I", "1", "o", "O", "0"],
        list(uppercase) + list(lowercase) + list(digits),
    )
)

REGISTRATION_LETTER_TEXT = """Добро пожаловать в OkayJournal, {}!

Ваши данные для входа в систему:

Логин: {}
Пароль: {}

Обратите внимание, что данный пароль сгенерирован нами 
и его нужно будет изменить при первом входе в систему.

С уважением,
Администрация OkayJournal"""

APPROVAL_LETTER_TEXT = """Здравствуйте, {}.

Ваша заявка была рассмотрена и одобрена.

Для Вас был сгенерирован логин:
{}

Для входа в систему можете использовать его или электронную почту, 
а также пароль, который указывали при регистрации.

С уважением,
Администрация OkayJournal"""

REJECTION_LETTER_TEXT = """Здравствуйте, {}.

Ваша заявка была рассмотрена и отклонена. 
Проверьте корректность введенных данных и попробуйте ещё раз.

С уважением,
Администрация OkayJournal"""

week_days = cycle(["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"])

quarter_ranges = [
    ((3, 9, 2018), (26, 10, 2018)),
    ((6, 11, 2018), (28, 12, 2018)),
    ((10, 1, 2019), (22, 3, 2019)),
    ((1, 4, 2019), (26, 5, 2019)),
]


weeks = []
start = date(*reversed(quarter_ranges[0][0]))
end = date(*reversed(quarter_ranges[-1][-1]))
count = 0
while start < end:
    count += 1
    weeks.append((count, start, start + timedelta(6)))
    start += timedelta(7)


def today_week():
    now = datetime.now()
    today = date(now.year, now.month, now.day)
    for week in weeks:
        if today in DateRange(week[1], week[2]):
            return week[0]


def get_week(week_number):
    for week in weeks:
        if week[0] == week_number:
            return week


class DateRange:
    def __init__(self, from_: date, to: date):
        self.from_ = from_
        self.current = self.from_ - timedelta(1)
        self.to = to

    def __iter__(self):
        return self

    def __next__(self):
        self.current += timedelta(1)
        if self.current > self.to:
            raise StopIteration
        return self.current

    def __contains__(self, item):
        return self.from_ <= item <= self.to


def get_quarter_date_range(quarter):
    return DateRange(
        date(*reversed(quarter_ranges[quarter - 1][0])),
        date(*reversed(quarter_ranges[quarter - 1][1])),
    )


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
    return "user" in session


def login_required(func):
    """Перенаправляет на /login, если не залогинен."""

    def decorated(*args, **kwargs):
        if not logged_in():
            return redirect("/login")
        return func(*args, **kwargs)

    decorated.__name__ = func.__name__
    return decorated


def login_required_rest(func):
    """Возвращает JSON, сообщающий об ошибке, если не залогинен."""

    def decorated(*args, **kwargs):
        if not logged_in():
            return jsonify({"error": "Not logged in"})
        return func(*args, **kwargs)

    decorated.__name__ = func.__name__
    return decorated


def restricted_access(allowed_users):
    def decorated(func):
        @login_required
        def wrapped(*args, **kwargs):
            if session["role"] not in allowed_users:
                return abort(404)
            return func(*args, **kwargs)

        wrapped.__name__ = func.__name__
        return wrapped

    return decorated


def need_to_change_password(func):
    def decorated(*args, **kwargs):
        if session["user"]["throwaway_password"]:
            return redirect("/settings")
        return func(*args, **kwargs)

    decorated.__name__ = func.__name__
    return decorated


def user(user_db_obj):
    """
    Возвращает кортеж с id и role пользователя.
    Функция создана для сокращения кода.
    """
    return user_db_obj.id, user_db_obj.__class__.__name__


def user_equal(user1, user2):
    """
    Возвращает True, если id и role пользователей одинаковы
    При этом, вторым аргументом можно передать session.
    """
    user1_data = user(user1)
    if not any(isinstance(user2, user_class) for user_class in USER_CLASSES):
        user2_data = (user2["user"]["id"], user2["role"])
    else:
        user2_data = user(user2)
    return user1_data == user2_data


def send_registration_letter(email, login, password, name):
    message = MIMEMultipart()
    message["From"] = "admin@okayjournal.ru"
    message["To"] = email
    message["Subject"] = "Регистрация в OkayJournal"
    text = REGISTRATION_LETTER_TEXT.format(name, login, password)
    message.attach(MIMEText(text, "plain"))

    with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as server:
        server.login("admin@okayjournal.ru", EMAIL_PASSWORD)
        server.send_message(message)
    return True


def send_approval_letter(email, login, name):
    message = MIMEMultipart()
    message["From"] = "admin@okayjournal.ru"
    message["To"] = email
    message["Subject"] = "Регистрация в OkayJournal"
    text = APPROVAL_LETTER_TEXT.format(name, login)
    message.attach(MIMEText(text, "plain"))

    with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as server:
        server.login("admin@okayjournal.ru", EMAIL_PASSWORD)
        server.send_message(message)
    return True


def send_rejection_letter(email, name):
    message = MIMEMultipart()
    message["From"] = "admin@okayjournal.ru"
    message["To"] = email
    message["Subject"] = "Регистрация в OkayJournal"
    text = REJECTION_LETTER_TEXT.format(name)
    message.attach(MIMEText(text, "plain"))

    with smtplib.SMTP_SSL("smtp.yandex.ru", 465) as server:
        server.login("admin@okayjournal.ru", EMAIL_PASSWORD)
        server.send_message(message)
    return True


def get_fullname(user_db_obj):
    """Возвращает ФИО пользователя."""
    return " ".join([user_db_obj.surname, user_db_obj.name, user_db_obj.patronymic])
