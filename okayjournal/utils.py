from flask import session, redirect, make_response
from .db import USER_CLASSES


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
