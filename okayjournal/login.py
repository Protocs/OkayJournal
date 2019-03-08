from werkzeug.security import check_password_hash
from flask import session

from okayjournal.db import Student, Parent, SchoolAdmin, Teacher, SystemAdmin


def login(username, password):
    for user_class in [Student, Parent, SchoolAdmin, Teacher, SystemAdmin]:
        user = user_class.query.filter_by(login=username).first()
        if user:
            break
    if user is None:
        return False

    right_password = check_password_hash(user.password_hash, password)
    if not right_password:
        return False

    session['username'] = user.login
    session['user_id'] = user.id

    return True
