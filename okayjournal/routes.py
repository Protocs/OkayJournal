from flask import render_template, request, redirect, session

from okayjournal.app import app
from okayjournal.forms import LoginForm, RegisterRequestForm
from okayjournal.db import *
from okayjournal.login import login, generate_unique_login
from okayjournal.utils import logged_in, login_required


@app.route("/")
@app.route("/index")
def index():
    if logged_in():
        return redirect('/journal')
    else:
        return render_template(
            "index.html", title="OkayJournal",
            after_reg=request.referrer == "http://127.0.0.1:8080/register")


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    form = LoginForm()
    if form.validate_on_submit():
        login_successful = login(form.login.data, form.password.data)
        if not login_successful:
            return render_template('login.html', got=repr(request.form),
                                   form=form,
                                   title="Авторизация",
                                   login_error="Неверный логин или пароль")
        if session['role'] == "SystemAdmin":
            return redirect("/admin")
        return redirect("/journal")
    return render_template("login.html", got=repr(request.form), form=form,
                           title="Авторизация")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterRequestForm()
    if form.validate_on_submit():
        password_first = request.form["password_first"]
        password_second = request.form["password_second"]
        if password_first == password_second:
            db.session.add(Request(region=request.form["region"],
                                   city=request.form["city"],
                                   school=request.form["school"],
                                   name=request.form["name"],
                                   surname=request.form["surname"],
                                   patronymic=request.form["patronymic"],
                                   email=request.form["email"],
                                   password_hash=generate_password_hash(
                                       password_first)))
            db.session.commit()
            return redirect("/")
        return render_template("register_request.html", form=form,
                               title="Запрос на регистрацию",
                               error="Пароли не совпадают")
    return render_template("register_request.html", form=form,
                           title="Запрос на регистрацию")


@app.route("/logout")
def logout():
    del session['user']
    del session['role']

    return redirect("/")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("role") != "SystemAdmin":
        return redirect("/index")

    if request.method == "POST":
        request_id, answer = list(request.form.items())[0]
        register_request = Request.query.filter_by(id=int(request_id)).first()
        if answer == "ok":
            school = School(region=register_request.region,
                            city=register_request.city,
                            school=register_request.school)
            db.session.add(school)
            admins = SchoolAdmin.query.all()
            last_id = 0 if not admins else admins[-1].id
            # noinspection PyArgumentList
            school_admin = SchoolAdmin(name=register_request.name,
                                       surname=register_request.surname,
                                       patronymic=register_request.patronymic,
                                       email=register_request.email,
                                       login=generate_unique_login(
                                           last_id + 1, "SchoolAdmin"),
                                       school_id=school.id,
                                       password_hash=
                                       register_request.password_hash)
            db.session.add(school_admin)
            db.session.commit()
        db.session.delete(register_request)
        db.session.commit()

    requests = Request.query.all()
    return render_template("admin.html", session=session, requests=requests)


# journal routes

@login_required
@app.route('/journal')
@app.route('/journal/diary')
def journal():
    return render_template('journal/diary.html', session=session)
