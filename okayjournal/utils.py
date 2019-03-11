from flask import session, redirect, make_response


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
