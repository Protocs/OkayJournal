from flask import render_template, request

from .app import app
from okayjournal.forms import LoginForm, RegisterRequestForm


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="OkayJournal")


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
        return "Регистрация"
    return render_template("register_request.html", got=repr(request.form), form=form,
                           title="Запрос на регистрацию")
