from flask import session, redirect


def logged_in():
    """Возвращает True, если произведен вход."""
    return 'user' in session


def login_required(func):
    """Перенаправляет на /login, если не залогинен."""

    def decorated(*args, **kwargs):
        if not logged_in():
            return redirect('/login')
        return func(*args, **kwargs)

    return decorated
