from flask import render_template, request

from app import app
from okayjournal.forms import LoginForm


@app.route("/")
@app.route("/index")
def index():
    return render_template("base.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return "Вошел"
    return render_template("login.html", got=repr(request.form), form=form)
