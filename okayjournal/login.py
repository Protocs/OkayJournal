from werkzeug.security import check_password_hash
from flask import session

from okayjournal.db import Student, Parent, SchoolAdmin, Teacher, SystemAdmin

LOGIN = {Student.__name__: "stud", Parent.__name__: "par", SchoolAdmin.__name__: "admin",
         Teacher: "teach"}


def generate_unique_login(user_id, user_status):
    return LOGIN[user_status] + str(user_id).zfill(6)


def login(username, password):
    for user_class in [Student, Parent, SchoolAdmin, Teacher, SystemAdmin]:
        user = user_class.query.filter_by(login=username).first()
        if user:
            if not check_password_hash(user.password_hash, password):
                return False
            session['username'] = user.login
            session['user_id'] = user.id
            session["user_status"] = user_class.__name__
            return True
    return False
