from functools import partial

from flask import render_template, request
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError

from okayjournal.app import app
from okayjournal.forms import *
from okayjournal.db import *
from okayjournal.login import login as do_login
from okayjournal.utils import *


# Как render_template, только сразу добавляет session и unread в параметры вызова.
def journal_render(*args, **kwargs):
    return partial(
        render_template,
        session=session,
        unread=get_count_unread_dialogs(
            user_id=session["user"]["id"], user_role=session["role"]
        ),
        today_week=today_week(),
    )(*args, **kwargs)


@app.route("/index")
def index():
    if logged_in():
        return redirect("/main_page")

    return render_template(
        "index.html",
        title="OkayJournal",
        after_reg=(request.referrer and request.referrer.endswith("/register")),
    )


@app.route("/login", methods=["GET", "POST"])
def login_route():
    form = LoginForm()
    if form.validate_on_submit():
        login_successful = do_login(form.login.data, form.password.data)
        if not login_successful:
            return render_template(
                "login.html",
                form=form,
                title="Авторизация",
                login_error="Неверный логин или пароль",
            )

        # Запоминание пользователя
        # TODO: Починить
        session.permanent = form.remember.data

        return redirect("/main_page")

    return render_template("login.html", form=form, title="Авторизация")


@app.route("/")
@app.route("/main_page")
def main_page():
    if not logged_in():
        return redirect("/index")
    if session["role"] in ("Student", "Parent"):
        return redirect("/diary/" + str(today_week()))
    if session["role"] == "Teacher":
        return redirect("/journal")
    if session["role"] == "SystemAdmin":
        return redirect("/admin")
    if session["role"] == "SchoolAdmin":
        return redirect("/school_managing")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterRequestForm()
    if form.validate_on_submit():
        password_first = request.form["password_first"]
        password_second = request.form["password_second"]
        if not validate_email(request.form["email"]):
            return render_template(
                "register_request.html",
                form=form,
                title="Запрос на регистрацию",
                error="Некорректный адрес электронной почты",
            )
        if email_exists(request.form["email"]):
            return render_template(
                "register_request.html",
                session=session,
                error="Пользователь с такой электронной почтой уже существует",
                form=form,
                title="Запрос на регистрацию",
            )
        if password_first == password_second:
            password_hash = generate_password_hash(password_first)
            db.session.add(
                Request(
                    region=request.form["region"],
                    city=request.form["city"],
                    school=request.form["school"],
                    name=request.form["name"],
                    surname=request.form["surname"],
                    patronymic=request.form["patronymic"],
                    email=request.form["email"],
                    password_hash=password_hash,
                )
            )
            try:
                db.session.commit()
            except IntegrityError:
                error = (
                    "Учётная запись с такой электронной почтой "
                    "или названием школы уже существует"
                )
                return render_template(
                    "register_request.html",
                    form=form,
                    title="Запрос на регистрацию",
                    error=error,
                )
            return redirect("/")
    return render_template(
        "register_request.html", form=form, title="Запрос на регистрацию"
    )


@app.route("/logout")
def logout():
    if logged_in():
        del session["user"]
        del session["role"]

    return redirect("/")


@app.route("/admin", methods=["GET", "POST"])
@restricted_access(["SystemAdmin"])
def admin():
    if request.method == "POST":
        request_id, answer = list(request.form.items())[0]
        register_request = Request.query.filter_by(id=int(request_id)).first()
        if answer == "ok":
            school = School(
                region=register_request.region,
                city=register_request.city,
                school=register_request.school,
            )
            db.session.add(school)
            admin_login = generate_unique_login("SchoolAdmin")
            # noinspection PyArgumentList
            school_admin = SchoolAdmin(
                name=register_request.name,
                surname=register_request.surname,
                patronymic=register_request.patronymic,
                email=register_request.email,
                login=admin_login,
                school_id=school.id,
                password_hash=register_request.password_hash,
                throwaway_password=False,
            )
            db.session.add(school_admin)
            db.session.commit()
            send_approval_letter(
                school_admin.email, school_admin.login, school_admin.name
            )
        else:
            send_rejection_letter(register_request.email, register_request.name)
        db.session.delete(register_request)
        db.session.commit()

    requests = Request.query.all()
    return render_template("admin.html", session=session, requests=requests)


# journal routes


@app.route("/diary/<int:week>")
@restricted_access(["Student", "Parent"])
@need_to_change_password
def diary(week):
    if session["role"] == "Parent":
        parent = find_user_by_role(session["user"]["id"], "Parent")
        if parent.children:
            return redirect("diary/" + str(week) + "/" + str(parent.children[0].id))
        return journal_render("journal/diary.html", parent=parent, current_week=week)

    schedule, subject_descriptions, marks = get_student_week(
        week, session["user"]["id"], session["user"]["school_id"]
    )

    return journal_render(
        "journal/diary.html",
        week_days=week_days,
        next=next,
        schedule=schedule,
        subject_descriptions=subject_descriptions,
        marks=marks,
        weeks=weeks,
        current_week=week,
        timedelta=timedelta,
    )


@app.route("/diary/<int:week>/<int:student_id>")
@restricted_access(["Parent"])
@need_to_change_password
def children_diary(week, student_id):
    student = find_user_by_role(student_id, "Student")
    parent = find_user_by_role(session["user"]["id"], "Parent")
    schedule, subject_descriptions, marks = get_student_week(
        week, student_id, session["user"]["school_id"]
    )
    return journal_render(
        "journal/diary.html",
        week_days=week_days,
        next=next,
        schedule=schedule,
        parent=parent,
        student=student,
        weeks=weeks,
        subject_descriptions=subject_descriptions,
        marks=marks,
        current_week=week,
        timedelta=timedelta,
    )


@app.route("/reports", methods=["GET", "POST"])
@restricted_access(["Parent", "Student"])
@need_to_change_password
def reports():
    if session["role"] == "Parent":
        children = find_user_by_role(session["user"]["id"], "Parent").children
        if request.method == "POST":
            child_id = int(request.form["childSelect"])
            quarter = int(request.form["quarterSelect"])
            report = get_student_marks(child_id, quarter)
            return journal_render(
                "journal/reports.html",
                selected={
                    "child": find_user_by_role(child_id, "Student"),
                    "quarter": quarter,
                },
                report=report,
                children=children,
                len=len,
                sum=sum,
                round=round,
            )
        return journal_render("journal/reports.html", children=children)
    if request.method == "POST":
        quarter = int(request.form["quarterSelect"])
        report = get_student_marks(session["user"]["id"], quarter)
        return journal_render(
            "journal/reports.html",
            selected={"quarter": quarter},
            report=report,
            len=len,
            sum=sum,
            round=round,
        )
    return journal_render("journal/reports.html")


@app.route("/messages", methods=["POST", "GET"])
@login_required
@need_to_change_password
def messages():
    if request.method == "POST":
        db.session.add(
            Message(
                sender_id=session["user"]["id"],
                sender_role=session["role"],
                recipient_id=int(request.form["user-select"]),
                recipient_role=request.form["role-select"],
                text=request.form["message"],
            )
        )
        db.session.commit()

    # Список пользователей, которые будут отображаться в добавлении нового
    # диалога
    users = {}
    for user_class in USER_CLASSES:
        users[user_class.__name__] = []
        query = user_class.query.filter_by(
            school_id=session["user"]["school_id"]
        ).order_by(user_class.surname, user_class.name, user_class.patronymic)
        for u in query:
            if not user_equal(u, session):
                users[user_class.__name__].append(u)
    return journal_render("journal/messages.html", users=users, type=type)


@app.route("/school_managing")
@restricted_access(["SchoolAdmin"])
@need_to_change_password
def school_managing():
    return journal_render("journal/school_managing.html")


@app.route("/users", methods=["GET", "POST"])
@restricted_access(["SchoolAdmin"])
@need_to_change_password
def users_route():
    add_teacher_form = AddTeacherForm(prefix="add-teacher")
    add_student_form = AddStudentForm(prefix="add-student")
    add_parent_form = AddParentForm(prefix="add-parent")

    kwargs = {
        "add_teacher_form": add_teacher_form,
        "add_student_form": add_student_form,
        "add_parent_form": add_parent_form,
        "teachers": Teacher.query.filter_by(
            school_id=session["user"]["school_id"]
        ).all(),
        "parents": Parent.query.filter_by(school_id=session["user"]["school_id"]).all(),
        "students": Student.query.filter_by(
            school_id=session["user"]["school_id"]
        ).all(),
    }

    if add_teacher_form.validate_on_submit():
        if not validate_email(request.form["add-teacher-email"]):
            return journal_render(
                "journal/users.html",
                **kwargs,
                error="Некорректный адрес электронной почты"
            )
        if email_exists(request.form["add-teacher-email"]):
            return journal_render(
                "journal/users.html",
                **kwargs,
                error="Пользователь с такой электронной почтой уже существует"
            )
        password = generate_throwaway_password()
        login = generate_unique_login("Teacher")
        print(login, password)
        # noinspection PyArgumentList
        teacher = Teacher(
            school_id=session["user"]["school_id"],
            name=request.form["add-teacher-name"],
            surname=request.form["add-teacher-surname"],
            patronymic=request.form["add-teacher-patronymic"],
            email=request.form["add-teacher-email"],
            login=login,
            password_hash=generate_password_hash(password),
        )
        for k in request.form:
            if k.startswith("subjectSelect"):
                if request.form[k] != "none":
                    subj = Subject.query.filter_by(id=int(request.form[k]))
                    teacher.subjects.append(subj.first())
        send_registration_letter(teacher.email, teacher.login, password, teacher.name)
        db.session.add(teacher)
        db.session.commit()
        kwargs["teachers"] = Teacher.query.filter_by(
            school_id=session["user"]["school_id"]
        ).all()

    if add_student_form.validate_on_submit():
        if not validate_email(request.form["add-student-email"]):
            return journal_render(
                "journal/users.html",
                **kwargs,
                error="Некорректный адрес электронной почты"
            )
        if email_exists(request.form["add-student-email"]):
            return journal_render(
                "journal/users.html",
                **kwargs,
                error="Пользователь с такой электронной почтой уже существует"
            )
        password = generate_throwaway_password()
        login = generate_unique_login("Student")
        print(login, password)

        grade = Grade.query.filter_by(
            school_id=session["user"]["school_id"],
            number=int(request.form["grade_number"]),
            letter=request.form["grade_letter"],
        )
        # noinspection PyArgumentList
        student = Student(
            school_id=session["user"]["school_id"],
            name=request.form["add-student-name"],
            surname=request.form["add-student-surname"],
            patronymic=request.form["add-student-patronymic"],
            email=request.form["add-student-email"],
            login=login,
            password_hash=generate_password_hash(password),
            grade_id=grade.first().id,
            parent_id=int(request.form["parent"]),
        )
        db.session.add(student)
        db.session.commit()

        send_registration_letter(student.email, student.login, password, student.name)

        kwargs["students"] = Student.query.filter_by(
            school_id=session["user"]["school_id"]
        ).all()

    if add_parent_form.validate_on_submit():
        if not validate_email(request.form["add-parent-email"]):
            return journal_render(
                "journal/users.html",
                **kwargs,
                error="Некорректный адрес электронной почты"
            )
        if email_exists(request.form["add-parent-email"]):
            return journal_render(
                "journal/users.html",
                **kwargs,
                error="Пользователь с такой электронной почтой уже существует"
            )
        password = generate_throwaway_password()
        login = generate_unique_login("Parent")
        print(login, password)

        # noinspection PyArgumentList
        parent = Parent(
            school_id=session["user"]["school_id"],
            name=request.form["add-parent-name"],
            surname=request.form["add-parent-surname"],
            patronymic=request.form["add-parent-patronymic"],
            email=request.form["add-parent-email"],
            login=login,
            password_hash=generate_password_hash(password),
        )
        db.session.add(parent)
        db.session.commit()

        send_registration_letter(parent.email, parent.login, password, parent.name)

        kwargs["parents"] = Parent.query.filter_by(
            school_id=session["user"]["school_id"]
        ).all()

    return journal_render("journal/users.html", **kwargs)


@app.route("/school_settings", methods=["GET", "POST"])
@restricted_access(["SchoolAdmin"])
@need_to_change_password
def school_settings():
    school = School.query.filter_by(id=session["user"]["school_id"]).first()

    form = SchoolEditForm()
    if form.validate_on_submit():
        school.region = form.region.data
        school.city = form.city.data
        school.school = form.school.data
        db.session.commit()

        return journal_render(
            "journal/school_settings.html", form=form, school=school, success=True
        )

    return journal_render("journal/school_settings.html", form=form, school=school)


@app.route("/classes", methods=["GET", "POST"])
@restricted_access(["SchoolAdmin"])
@need_to_change_password
def classes():
    if request.method == "POST":
        grade_number = int(request.form["grade"].split()[0])
        grade_letter = request.form["grade"].split()[1][1]
        teacher = find_user_by_role(int(request.form["homeroom_teacher"]), "Teacher")
        grade = Grade(
            number=grade_number,
            letter=grade_letter,
            school_id=session["user"]["school_id"],
        )
        db.session.add(grade)
        db.session.commit()
        teacher.homeroom_grade_id = grade.id
        db.session.commit()
    free_teachers = Teacher.query.filter_by(
        homeroom_grade_id=None, school_id=session["user"]["id"]
    ).all()
    return journal_render("journal/classes.html", free_teachers=free_teachers)


@app.route("/subjects", methods=["GET", "POST"])
@restricted_access(["SchoolAdmin"])
@need_to_change_password
def subjects_route():
    if request.method == "POST":
        db.session.add(
            Subject(name=request.form["name"], school_id=session["user"]["school_id"])
        )
        db.session.commit()
    subject_list = Subject.query.filter_by(school_id=session["user"]["school_id"]).all()
    form = AddSubjectForm()
    return journal_render("journal/subjects.html", subjects=subject_list, form=form)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    change_password_form = ChangePasswordForm(prefix="pwd")
    change_email_form = ChangeEmailForm(prefix="email")
    u = find_user_by_role(session["user"]["id"], session["role"])

    if change_password_form.submit.data and change_password_form.validate_on_submit():
        print(session["user"]["password_hash"])
        old_password_right = check_password_hash(
            session["user"]["password_hash"], change_password_form.old_password.data
        )
        if not old_password_right:
            return journal_render(
                "journal/settings.html",
                change_password_form=change_password_form,
                change_email_form=change_email_form,
                password_change_error=True,
                current_email=u.email,
            )

        u.password_hash = generate_password_hash(change_password_form.new_password.data)
        u.throwaway_password = False
        db.session.commit()
        user_id, role = session["user"]["id"], session["role"]
        del session["user"]
        session["user"] = user_to_dict(find_user_by_role(user_id, role))
        return journal_render(
            "journal/settings.html",
            change_password_form=change_password_form,
            change_email_form=change_email_form,
            password_change_success=True,
            current_email=u.email,
        )

    if change_email_form.submit.data and change_email_form.validate_on_submit():
        u.email = change_email_form.email.data
        db.session.commit()

    return journal_render(
        "journal/settings.html",
        change_password_form=change_password_form,
        change_email_form=change_email_form,
        current_email=u.email,
    )


# TODO
@app.route("/journal", methods=["GET", "POST"])
@restricted_access(["Teacher"])
@need_to_change_password
def journal():
    if request.method == "GET":
        return journal_render("journal/journal.html")
    if request.method == "POST":
        subject_id = int(request.form["subject"])
        grade_number = request.form["grade-number"]
        grade_letter = request.form["grade-letter"]
        grade = Grade.query.filter_by(
            school_id=session["user"]["school_id"],
            number=int(grade_number),
            letter=grade_letter,
        ).first()
        quarter = int(request.form["quarter"])

        weekdays = [
            subject.day
            for subject in Schedule.query.filter_by(
                subject_id=subject_id,
                grade_id=grade.id,
                teacher_id=session["user"]["id"],
                school_id=session["user"]["school_id"],
            )
        ]
        date_range = list(
            filter(
                lambda d: (d.weekday() + 1) in weekdays,
                list(get_quarter_date_range(quarter)),
            )
        )

        marks = {}
        for date_obj in date_range:
            # TODO: Параметр date - ультра-костыль 80 уровня
            subject_desc = SubjectDescription.query.filter_by(
                date=datetime.strptime(date_obj.strftime("%d-%m-%Y"), "%d-%m-%Y"),
                grade_id=grade.id,
                subject_id=subject_id,
            )

            if subject_desc is not None:
                if subject_desc.first() is not None:
                    marks.update({date_obj: get_subject_marks(subject_desc.first().id)})

        students = []
        for student in grade.students:
            student_marks = get_student_marks(student.id, quarter).get(subject_id)
            if student_marks["marks"]:
                average_mark = round(
                    sum(student_marks["marks"]) / len(student_marks["marks"]), 2
                )
            else:
                average_mark = None
            students.append(
                (student.id, student.surname + " " + student.name, average_mark)
            )

        return journal_render(
            "journal/journal.html",
            date_range=date_range,
            selected={
                "grade_number_select": grade_number,
                "grade_letter_select": grade_letter,
                "quarter": quarter,
                "subject_id": subject_id,
                "grade_id": grade.id,
            },
            students=sorted(students, key=lambda s: s[1]),
            homeroom_teacher=get_fullname(grade.homeroom_teacher[0]),
            marks=marks,
        )


@app.route("/timetable", methods=["GET", "POST"])
@restricted_access(["SchoolAdmin"])
@need_to_change_password
def timetable_index():
    if request.method == "POST":
        grade = Grade.query.filter_by(
            number=int(request.form["number"]),
            letter=request.form["letter"],
            school_id=session["user"]["school_id"],
        )
        return redirect("/timetable/" + str(grade.first().id))

    return journal_render("journal/timetable.html", week_days=week_days, next=next)


@app.route("/timetable/<int:grade_id>", methods=["GET", "POST"])
@restricted_access(["SchoolAdmin"])
@need_to_change_password
def timetable(grade_id):
    errors = []
    if request.method == "POST":
        for i in range(1, 7):
            for j in range(1, 7):
                subject = request.form["subject" + str(i) + str(j)]
                teacher = request.form.get("teacher" + str(i) + str(j), None)
                schedule = Schedule.query.filter_by(
                    school_id=session["user"]["school_id"],
                    day=i,
                    subject_number=j,
                    grade_id=grade_id,
                ).first()
                if subject != "none" and teacher is not None:
                    # Если у учителя уже есть урок под таким номером в этот день,
                    # То выводим ошибку
                    collision = Schedule.query.filter_by(
                        school_id=session["user"]["school_id"],
                        teacher_id=int(teacher),
                        day=i,
                        subject_number=j,
                    ).first()
                    if collision and collision.grade_id != grade_id:
                        error = "У учителя {} уже запланирован {} урок в {}"
                        teacher_name = get_fullname(
                            find_user_by_role(int(teacher), "Teacher")
                        )
                        weekday = [
                            "понедельник",
                            "вторник",
                            "среду",
                            "четверг",
                            "пятницу",
                            "субботу",
                        ][i - 1]
                        errors.append(error.format(teacher_name, str(j), weekday))
                        break
                    if schedule is None:
                        db.session.add(
                            Schedule(
                                day=i,
                                subject_number=j,
                                subject_id=int(subject),
                                school_id=session["user"]["school_id"],
                                teacher_id=int(teacher),
                                grade_id=grade_id,
                            )
                        )
                    else:
                        schedule.subject_id = int(subject)
                        schedule.teacher_id = int(teacher)
                    db.session.commit()
                else:
                    if schedule is not None:
                        db.session.delete(schedule)
                        db.session.commit()
    schedule = get_grade_schedule(grade_id, session["user"]["school_id"])
    teachers_subjects = get_teachers_subjects(session["user"]["school_id"])
    return journal_render(
        "journal/timetable.html",
        week_days=week_days,
        next=next,
        schedule=schedule,
        teachers_subjects=teachers_subjects,
        errors=errors,
    )


@app.route("/announcements", methods=["GET", "POST"])
@login_required
@need_to_change_password
def announcements_route():
    if request.method == "POST":
        for_users = " ".join(
            [elem[0] for elem in request.form.items() if elem[1] == "on"]
            + ["SchoolAdmin"]
        )
        db.session.add(
            Announcement(
                school_id=session["user"]["school_id"],
                author_id=session["user"]["id"],
                author_role=session["role"],
                header=request.form.get("announcementHeader"),
                text=request.form.get("announcement"),
                for_users=for_users,
            )
        )
        db.session.commit()
    announcements = {}
    for announcement in (
        Announcement.query.filter_by(school_id=session["user"]["school_id"])
        .order_by(Announcement.date)
        .all()
    ):
        author = find_user_by_role(announcement.author_id, announcement.author_role)
        announcements.update(
            {
                announcement.id: {
                    "author": {
                        "name": get_fullname(author),
                        "id": author.id,
                        "role": author.__class__.__name__,
                    },
                    "header": announcement.header,
                    "text": announcement.text,
                    "date": announcement.date,
                    "for_users": announcement.for_users,
                }
            }
        )
    return journal_render(
        "journal/announcements.html",
        announcements=announcements,
        reversed=reversed,
        list=list,
    )


@app.route("/lesson_times", methods=["GET", "POST"])
@restricted_access(["SchoolAdmin"])
@need_to_change_password
def lesson_times():
    if request.method == "POST":
        for i in range(1, len(request.form) // 2 + 1):
            start = request.form["start" + str(i)]
            end = request.form["end" + str(i)]
            if start and end:
                schedule = CallSchedule.query.filter_by(
                    school_id=session["user"]["school_id"], subject_number=i
                ).first()
                if schedule:
                    schedule.start = start
                    schedule.end = end
                else:
                    db.session.add(
                        CallSchedule(
                            school_id=session["user"]["school_id"],
                            subject_number=i,
                            start=start,
                            end=end,
                        )
                    )
                db.session.commit()

    schedule = {}
    for subject in CallSchedule.query.filter_by(
        school_id=session["user"]["school_id"]
    ).all():
        schedule[subject.subject_number] = {"start": subject.start, "end": subject.end}

    return journal_render("journal/lesson_times.html", schedule=schedule)


@app.route("/grading/<int:subject_id>/<int:grade_id>/<date>", methods=["GET", "POST"])
@restricted_access(["Teacher"])
@need_to_change_password
def grading(subject_id, grade_id, date):
    date_object = datetime.strptime(date, "%d-%m-%Y")
    if request.method == "POST":
        lesson_topic = request.form["lesson-topic"]
        homework = request.form["homework"]
        # Проверим, существует ли в базе описание предмета для этой даты
        subject_description = SubjectDescription.query.filter_by(
            date=date_object,
            grade_id=grade_id,
            school_id=session["user"]["school_id"],
            subject_id=subject_id,
        ).first()
        # Если да, то просто меняем тему и домашнее задание для этого объекта
        if subject_description:
            subject_description.theme = lesson_topic
            subject_description.homework = homework
        # Если нет, то добавляем новый объект в базу
        else:
            subject_description = SubjectDescription(
                date=date_object,
                school_id=session["user"]["school_id"],
                grade_id=grade_id,
                subject_id=subject_id,
                theme=lesson_topic,
                homework=homework,
            )
            db.session.add(subject_description)
        db.session.commit()
        # Заполним оценки и посещаемость
        for key in request.form:
            if key.startswith("mark"):
                student_id = int(key.split("-")[1])
                atd_key = "attendance-" + str(student_id)
                # Если учитель не выбирает оценку или посещаемость, то передаваться
                # будет пустая строка
                mark = request.form[key]
                attendance = request.form[atd_key]
                # Проверим, существует ли объект оценки для этого ученика
                mark_obj = Marks.query.filter_by(
                    subject_id=subject_description.id, student_id=student_id
                ).first()
                # Если да, то меняем оценку и посещаемость
                if mark_obj:
                    mark_obj.mark = mark
                    mark_obj.attendance = attendance
                # Если нет, добавляем новый объект в базу
                else:
                    mark = Marks(
                        mark=mark,
                        subject_id=subject_description.id,
                        student_id=student_id,
                        school_id=session["user"]["school_id"],
                        attendance=attendance,
                    )
                    db.session.add(mark)
        db.session.commit()

        if "save-and-return" in request.form:
            return redirect("/journal")

    grade = Grade.query.filter_by(id=grade_id).first()
    subject_description = SubjectDescription.query.filter_by(
        date=date_object,
        grade_id=grade_id,
        school_id=session["user"]["school_id"],
        subject_id=subject_id,
    ).first()
    marks = None
    if subject_description:
        marks = get_subject_marks(subject_description.id)
    students = []
    for student in grade.students:
        students.append((student.id, student.surname + " " + student.name))
    return journal_render(
        "journal/grading.html",
        students=sorted(students, key=lambda s: s[1]),
        subject=subject_description,
        marks=marks,
    )


@app.errorhandler(404)
def not_found_error(_):
    if logged_in():
        return journal_render("journal/404.html")

    return redirect("/")
