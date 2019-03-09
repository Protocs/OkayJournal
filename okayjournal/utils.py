from flask import session


def logged_in():
    """Возвращает True, если произведен вход."""
    return 'username' in session
