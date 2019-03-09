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


def user_to_dict(user):
    """
    Просто так засунуть обьект из БД в session невозможно.
    Эта функция конвертирует User в словарь."""
    # Список колонн модели User
    columns = [attrname for attrname, val in vars(User).items()
               if isinstance(val, db.Column)]
    as_dict = {attrname: getattr(user, attrname) for attrname in columns}
    return as_dict


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
