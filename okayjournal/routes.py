from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash

from okayjournal.app import app
from okayjournal.forms import LoginForm, RegisterRequestForm
from okayjournal.db import Request, db, SchoolAdmin, School
from okayjournal.login import login, generate_unique_login


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="OkayJournal",
                           after_reg=request.referrer == "http://127.0.0.1:8080/register")


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    form = LoginForm()
    if form.validate_on_submit():
        login_successful = login(form.login.data, form.password.data)
        if not login_successful:
            return render_template('login.html', got=repr(request.form), form=form,
                                   title="Авторизация",
                                   login_error="Неверный логин или пароль")
        if session.get("user_status") == "SystemAdmin":
            return redirect("/admin")
        return redirect("/journal")
    return render_template("login.html", got=repr(request.form), form=form, title="Авторизация")


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
                                   password_hash=generate_password_hash(password_first)))
            db.session.commit()
            return redirect("/")
        return render_template("register_request.html", got=repr(request.form), form=form,
                               title="Запрос на регистрацию", error="Пароли не совпадают")
    return render_template("register_request.html", got=repr(request.form), form=form,
                           title="Запрос на регистрацию")


@app.route("/logout")
def logout():
    session.pop("username", 0)
    session.pop("user_id", 0)
    session.pop("user_status", 0)
    return redirect("/")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("user_status") != "SystemAdmin":
        return redirect("/index")
    if request.method == "POST":
        request_id, answer = list(request.form.items())[0]
        register_request = Request.query.filter_by(id=int(request_id)).first()
        if answer == "ok":
            school = School(region=register_request.region, city=register_request.city,
                            school=register_request.school)
            db.session.add(school)
            admins = SchoolAdmin.query.all()
            last_id = 0 if not admins else admins[-1].id
            # noinspection PyArgumentList
            school_admin = SchoolAdmin(name=register_request.name,
                                       surname=register_request.surname,
                                       patronymic=register_request.patronymic,
                                       email=register_request.email,
                                       login=generate_unique_login(last_id + 1, "SchoolAdmin"),
                                       school_id=school.id,
                                       password_hash=register_request.password_hash
                                       )
            db.session.add(school_admin)
            db.session.commit()
        db.session.delete(register_request)
        db.session.commit()

    requests = Request.query.all()
    return render_template("admin.html", session=session, requests=requests)


# journal routes

@app.route('/journal')
@app.route('/journal/diary')
def journal():
    if session.get("user_id") is None:
        return redirect("/")
    user = globals()[session.get("user_status")].query.filter_by(
        id=int(session.get("user_id"))).first()
    if user is None:
        return redirect("/")
    return render_template('journal/diary.html', user=user, user_status=session.get("user_status"))
