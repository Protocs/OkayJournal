from werkzeug.security import check_password_hash
from flask import session

from okayjournal.db import (Student, Parent, SchoolAdmin, Teacher,
                            SystemAdmin, user_to_dict)

LOGIN_PREFIXES = {Student.__name__: "stud", Parent.__name__: "par",
                  SchoolAdmin.__name__: "admin", Teacher.__name__: "teach"}


def generate_unique_login(user_id, user_status):
    return LOGIN_PREFIXES[user_status] + str(user_id).zfill(6)


def login(username, password):
    for user_class in [Student, Parent, SchoolAdmin, Teacher, SystemAdmin]:
        user = user_class.query.filter_by(login=username).first()
        # Если не нашли пользователя по логину, пробуем по почте
        if not user:
            user = user_class.query.filter_by(email=username).first()
        if user:
            if not check_password_hash(user.password_hash, password):
                return False
            session['user'] = user_to_dict(user)
            session['role'] = user_class.__name__
            return True
    return False
