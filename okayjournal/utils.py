from flask import session, redirect, make_response
from .db import USER_CLASSES, Student, Parent, SchoolAdmin, Teacher

from random import choice
from string import ascii_lowercase as lowercase, ascii_uppercase as uppercase, \
    digits

LOGIN_PREFIXES = {Student.__name__: "stud", Parent.__name__: "par",
                  SchoolAdmin.__name__: "admin", Teacher.__name__: "teach"}

SYMBOLS = list(filter(lambda chr: chr not in ['l', 'I', '1', 'o', 'O', '0'],
                      list(uppercase) + list(lowercase) + list(digits)))


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
