from flask import render_template, request, redirect
from werkzeug.security import generate_password_hash

from okayjournal.app import app
from okayjournal.forms import LoginForm, RegisterRequestForm
from okayjournal.db import Request, db


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="OkayJournal",
                           after_reg=request.referrer == "http://127.0.0.1:8080/register")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return "Вошел"
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
                                   password_hash=generate_password_hash(password_first)))
            db.session.commit()
            return redirect("/")
        return render_template("register_request.html", got=repr(request.form), form=form,
                               title="Запрос на регистрацию", error="Пароли не совпадают")
    return render_template("register_request.html", got=repr(request.form), form=form,
                           title="Запрос на регистрацию")
