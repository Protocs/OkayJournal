from okayjournal.app import db
from os.path import isfile
from datetime import datetime
from werkzeug.security import generate_password_hash


class User:
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    surname = db.Column(db.String(30), unique=False, nullable=False)
    patronymic = db.Column(db.String(30), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    login = db.Column(db.String(31), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=True, nullable=False)


class SystemAdmin(User, db.Model):
    pass


class Parent(User, db.Model):
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"),
                          nullable=False)
    school = db.relationship("School", backref=db.backref("parents"),
                             lazy=True)


class Teacher(User, db.Model):
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"),
                          nullable=False)
    school = db.relationship("School", backref=db.backref("teachers"),
                             lazy=True)
    homeroom_grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"),
                                  nullable=True)
    homeroom_grade = db.relationship("Grade",
                                     backref=db.backref("homeroom_teacher"),
                                     lazy=True)


class SchoolAdmin(User, db.Model):
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"),
                          nullable=False)
    school = db.relationship("School", backref=db.backref("admins"), lazy=True)


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=False, nullable=False)
    letter = db.Column(db.String(1), unique=False, nullable=False)


class Student(User, db.Model):
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=False)
    grade = db.relationship("Grade", backref=db.backref("students", lazy=True))
    parent_id = db.Column(db.Integer, db.ForeignKey("parent.id"),
                          nullable=False)
    parent = db.relationship("Parent", backref=db.backref("children"),
                             lazy=True)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"),
                          nullable=False)
    school = db.relationship("School", backref=db.backref("students"),
                             lazy=True)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(15), unique=False, nullable=False)
    subject_number = db.Column(db.Integer, unique=False, nullable=False)
    subject = db.Column(db.String(25), nullable=False, unique=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"),
                           nullable=False)
    teacher = db.relationship("Teacher", backref="subjects", lazy=True)
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=False)
    grade = db.relationship("Grade", backref="subjects", lazy=True)
    start = db.Column(db.String(5), nullable=False, unique=False)
    end = db.Column(db.String(5), nullable=False, unique=False)
    recess = db.Column(db.Integer, unique=False, nullable=True)


class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"),
                           nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=False)
    grade = db.relationship("Grade", backref="homework", lazy=True)
    subject = db.relationship("Subject", backref="homework", lazy=True)
    homework = db.Column(db.Text, nullable=False, unique=False)


class Marks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    mark = db.Column(db.Integer, nullable=False, unique=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"),
                           nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"),
                           nullable=False)
    subject = db.relationship("Subject", backref="marks", lazy=True)
    student = db.relationship("Student", backref="marks", lazy=True)


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    school = db.Column(db.String(80), unique=True, nullable=False)


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    school = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(30), unique=False, nullable=False)
    surname = db.Column(db.String(30), unique=False, nullable=False)
    patronymic = db.Column(db.String(30), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=True, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False, unique=False)
    sender_role = db.Column(db.String(11), nullable=False, unique=False)
    recipient_role = db.Column(db.String(11), nullable=False, unique=False)
    recipient_id = db.Column(db.Integer, nullable=False, unique=False)
    text = db.Column(db.Text, unique=False, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    read = db.Column(db.Boolean, nullable=False, default=False)


USER_CLASSES = [Student, Parent, SchoolAdmin, Teacher]
POSSIBLE_ATTRIBUTES = ["id", "name", "surname", "patronymic",
                       "password_hash", "login", "email", "school_id",
                       "homeroom_grade_id", "grade_id", "parent_id"]


def user_to_dict(user):
    """
    Просто так засунуть обьект из БД в session невозможно.
    Эта функция конвертирует User в словарь."""
    result = {}
    for k, v in vars(user).items():
        if k in POSSIBLE_ATTRIBUTES:
            result.update({k: v})
    return result


def find_user_by_role(id, role):
    """Возвращает объект пользователя по его id и role.
    Если пользователь не найден, вернет None."""
    return globals()[role].query.filter_by(id=id).first()


def find_user_by_login(login):
    """Возвращает объект пользователя по его логину.
    Если пользователь не найден, вернет None"""
    for user_class in USER_CLASSES:
        user = user_class.query.filter_by(login=login).first()
        if user:
            return user


def get_count_unread_messages(user_id, user_role):
    messages = Message.query.filter_by(recipient_id=user_id,
                                       recipient_role=user_role,
                                       read=False)
    return len(messages.order_by(Message.sender_id,
                                 Message.sender_role).all())


if not isfile("okayjournal/okayjournal.db"):
    db.create_all()
    # Добавим администратора
    # noinspection PyArgumentList
    db.session.add(SystemAdmin(name="admin",
                               surname="admin",
                               patronymic="admin",
                               email="None",
                               login="admin",
                               password_hash=generate_password_hash("admin")))
    db.session.commit()
