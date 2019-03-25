from okayjournal.app import db
from datetime import datetime
from werkzeug.security import generate_password_hash

# Many-to-Many relationships

teacher_subjects = db.Table(
    "teacher_subjects",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teacher.id")),
    db.Column("subject_id", db.Integer, db.ForeignKey("subject.id")),
)


class User:
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    surname = db.Column(db.String(30), unique=False, nullable=False)
    patronymic = db.Column(db.String(30), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    login = db.Column(db.String(31), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=False, nullable=False)
    throwaway_password = db.Column(db.Boolean, default=True)


class SystemAdmin(User, db.Model):
    pass


class Parent(User, db.Model):
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    school = db.relationship("School", backref=db.backref("parents"), lazy=True)


class Teacher(User, db.Model):
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    school = db.relationship("School", backref=db.backref("teachers"), lazy=True)
    homeroom_grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=True)
    homeroom_grade = db.relationship(
        "Grade", backref=db.backref("homeroom_teacher"), lazy=True
    )
    subjects = db.relationship(
        "Subject", secondary=teacher_subjects, backref=db.backref("teachers", lazy=True)
    )


class SchoolAdmin(User, db.Model):
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    school = db.relationship("School", backref=db.backref("admins"), lazy=True)


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=False, nullable=False)
    letter = db.Column(db.String(1), unique=False, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)


class Student(User, db.Model):
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=False)
    grade = db.relationship("Grade", backref=db.backref("students", lazy=True))
    parent_id = db.Column(db.Integer, db.ForeignKey("parent.id"), nullable=False)
    parent = db.relationship("Parent", backref=db.backref("children"), lazy=True)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    school = db.relationship("School", backref=db.backref("students"), lazy=True)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=False, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, unique=False, nullable=False)
    subject_number = db.Column(db.Integer, unique=False, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    subject = db.relationship("Subject", backref="schedule", lazy=True)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=False)
    teacher = db.relationship("Teacher", backref=db.backref("schedule"), lazy=True)
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=False)
    grade = db.relationship("Grade", backref="subjects", lazy=True)


class SubjectDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=False)
    grade = db.relationship("Grade", backref="subject_descriptions", lazy=True)
    subject = db.relationship("Subject", backref="subject_descriptions", lazy=True)
    theme = db.Column(db.Text, nullable=False, unique=False)
    homework = db.Column(db.Text, nullable=False, unique=False)


class Marks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.Integer, nullable=True, unique=False)
    attendance = db.Column(db.Text, nullable=True, unique=False)
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subject_description.id"), nullable=False
    )
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    subject = db.relationship("SubjectDescription", backref="marks", lazy=True)
    student = db.relationship("Student", backref="marks", lazy=True)


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    school = db.Column(db.String(80), unique=False, nullable=False)


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    school = db.Column(db.String(80), unique=False, nullable=False)
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
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now())
    read = db.Column(db.Boolean, nullable=False, default=False)


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    author_id = db.Column(db.Integer, nullable=False, unique=False)
    author_role = db.Column(db.String(11), nullable=False, unique=False)
    header = db.Column(db.String(80), nullable=False, unique=False)
    text = db.Column(db.Text, unique=False, nullable=False)
    for_users = db.Column(db.String(34), unique=False, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now())


class CallSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("school.id"), nullable=False)
    subject_number = db.Column(db.Integer, nullable=False, unique=False)
    start = db.Column(db.String(5), nullable=False, unique=False)
    end = db.Column(db.String(5), nullable=False, unique=False)


USER_CLASSES = [Student, Parent, SchoolAdmin, Teacher]
POSSIBLE_ATTRIBUTES = [
    "id",
    "name",
    "surname",
    "patronymic",
    "password_hash",
    "login",
    "email",
    "school_id",
    "homeroom_grade_id",
    "grade_id",
    "parent_id",
    "throwaway_password",
]


def user_to_dict(user):
    """
    Просто так засунуть обьект из БД в session невозможно.
    Эта функция конвертирует User в словарь.
    """
    result = {}
    for k, v in vars(user).items():
        if k in POSSIBLE_ATTRIBUTES:
            result.update({k: v})
    return result


def find_user_by_role(user_id, role):
    """
    Возвращает объект пользователя по его id и role.
    Если пользователь не найден, вернет None.
    """
    return globals()[role].query.filter_by(id=user_id).first()


def find_user_by_login(login):
    """
    Возвращает объект пользователя по его логину.
    Если пользователь не найден, вернет None.
    """
    for user_class in USER_CLASSES:
        user = user_class.query.filter_by(login=login).first()
        if user:
            return user


def get_count_unread_dialogs(user_id, user_role):
    messages = Message.query.filter_by(
        recipient_id=user_id, recipient_role=user_role, read=False
    )
    return len(messages.group_by(Message.sender_id, Message.sender_role).all())


def get_count_unread_messages(recipient, sender):
    messages = Message.query.filter_by(
        recipient_id=recipient[0],
        recipient_role=recipient[1],
        sender_id=sender[0],
        sender_role=sender[1],
        read=False,
    )
    return len(messages.all())


def get_grade_schedule(grade_id, school_id):
    from okayjournal.utils import get_fullname

    schedule = Schedule.query.filter_by(grade_id=grade_id, school_id=school_id).all()
    response = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
    for subject in schedule:
        response[subject.day].update(
            {
                subject.subject_number: {
                    "subject": {"id": subject.subject.id, "name": subject.subject.name},
                    "teacher": {
                        "id": subject.teacher.id,
                        "name": get_fullname(subject.teacher),
                    },
                }
            }
        )
    return response


def get_teachers_subjects(school_id):
    from okayjournal.utils import get_fullname

    subjects = Subject.query.filter_by(school_id=school_id).all()
    response = {}
    for subject in subjects:
        response.update(
            {
                subject.id: {
                    "name": subject.name,
                    "teachers": {
                        teacher.id: {"name": get_fullname(teacher)}
                        for teacher in subject.teachers
                    },
                }
            }
        )
    return response


def get_subject_marks(subject_id):
    marks = {}
    marks_query = Marks.query.filter_by(subject_id=subject_id).all()
    for mark in marks_query:
        marks.update(
            {mark.student_id: {"mark": mark.mark, "attendance": mark.attendance}}
        )
    return marks


def get_student_week(week, student_id, school_id):
    """Возвращает всю информацию о учебной неделе ученика: оценки, предметы..."""
    from okayjournal.utils import get_week, DateRange

    student = find_user_by_role(student_id, "Student")
    schedule = get_grade_schedule(student.grade_id, school_id)
    subject_descriptions = {}
    marks = {}
    week_range = get_week(week)
    day_number = 1
    for day in DateRange(week_range[1], week_range[2]):
        # TODO
        # По непонятным причинам база не видит объекты с датой ``day``, хотя
        # год, месяц и день этого объекта равны преобразованной дате datetime.strptime()
        subject_descriptions.update({day_number: {}})
        marks.update({day_number: {}})
        for subject in SubjectDescription.query.filter_by(
            date=datetime.strptime(datetime.strftime(day, "%d-%m-%Y"), "%d-%m-%Y"),
            grade_id=student.grade_id,
        ).all():
            subject_descriptions[day_number].update({subject.subject_id: subject})
            mark = Marks.query.filter_by(
                subject_id=subject.id, student_id=student_id
            ).first()
            if mark:
                marks[day_number].update({subject.subject_id: mark.mark})
        day_number += 1
    return schedule, subject_descriptions, marks


def email_exists(email):
    """Проверяет, существует ли пользователь с такой электронной почтой"""
    for user_class in USER_CLASSES:
        if user_class.query.filter_by(email=email).first():
            return True
    return False


def get_student_marks(student_id, quarter):
    """Возвращает оценки ученика за четверть ``quarter``"""
    from okayjournal.utils import get_quarter_date_range, date

    student = find_user_by_role(student_id, "Student")
    marks = filter(
        lambda m: date(m.subject.date.year, m.subject.date.month, m.subject.date.day)
        in get_quarter_date_range(quarter),
        student.marks,
    )
    schedule = get_grade_schedule(student.grade_id, student.school_id)
    response = {}
    for day in schedule:
        for subject in schedule[day]:
            if schedule[day][subject]["subject"]["id"] not in response:
                response.update(
                    {
                        schedule[day][subject]["subject"]["id"]: {
                            "name": schedule[day][subject]["subject"]["name"],
                            "marks": [],
                        }
                    }
                )
    for mark in marks:
        if mark.mark:
            if mark.subject.subject.id not in response:
                response.update(
                    {
                        mark.subject.subject.id: {
                            "name": mark.subject.subject.name,
                            "marks": [],
                        }
                    }
                )
            response[mark.subject.subject.id]["marks"].append(mark.mark)
    return response


db.create_all()

# Добавим администратора
if not SystemAdmin.query.all():
    # noinspection PyArgumentList
    db.session.add(
        SystemAdmin(
            name="admin",
            surname="admin",
            patronymic="admin",
            email="None",
            login="admin",
            password_hash=generate_password_hash("admin"),
        )
    )
    db.session.commit()
