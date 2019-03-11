from itertools import cycle

from flask import render_template, request, redirect, session
from werkzeug.security import check_password_hash

from okayjournal.app import app
from okayjournal.forms import LoginForm, RegisterRequestForm, SchoolEditForm, \
    ChangePasswordForm
from okayjournal.db import *
from okayjournal.login import login, generate_unique_login
from okayjournal.utils import logged_in, login_required, school_admin_only


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

        # Запоминание пользователя
        session.permanent = form.remember.data

        return redirect("/journal")
    return render_template("login.html", form=form, title="Авторизация")


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

@app.route('/journal')
@app.route('/journal/diary')
@login_required
def journal():
    if session['role'] == 'SystemAdmin':
        return redirect('/admin')

    week_days = cycle(['Понедельник',
                       'Вторник',
                       'Среда',
                       'Четверг',
                       'Пятница',
                       'Суббота'])

    return render_template('journal/diary.html', session=session,
                           week_days=week_days, next=next)


@app.route("/messages", methods=["POST", "GET"])
@login_required
def messages():
    if request.method == "POST":
        db.session.add(Message(
            sender_id=session["user"]["id"],
            sender_role=session["role"],
            recipient_id=int(request.form["user-select"]),
            recipient_role=request.form["role-select"],
            text=request.form["message"]
        ))
        db.session.commit()
    users = {}
    for user_class in USER_CLASSES:
        users[user_class.__name__] = []
        query = user_class.query.filter_by(
            school_id=session["user"]["school_id"])
        for user in query.order_by(user_class.surname, user_class.name,
                                   user_class.patronymic):
            users[user_class.__name__].append(user)
    dialogs = {}
    # Вытащим все сообщения, которые были отправлены текущим пользователем
    # И сгруппируем их по получателю
    messages_from_cur_user = Message.query.filter_by(
        sender_id=session["user"]["id"],
        sender_role=session["role"]
    ).group_by(Message.recipient_id, Message.recipient_role)
    # Вытащим все сообщения, которые были отправлены текущему пользователю
    # И сгруппируем их по отправителю
    messages_for_cur_user = Message.query.filter_by(
        recipient_id=session["user"]["id"],
        recipient_role=session["role"]
    ).group_by(Message.sender_id, Message.sender_role)
    # Объединим полученные сообщения в один объект BaseQuery
    all_messages = messages_for_cur_user.union(messages_from_cur_user)
    # Пройдемся по каждому сообщению, чтобы составить список диалогов
    for message in all_messages.order_by(Message.date):
        # Вытащим получателя и отправителя сообщения
        recipient = find_user_by_role(message.recipient_id,
                                      message.recipient_role)
        sender = find_user_by_role(message.sender_id,
                                   message.sender_role)
        # Если получатель совпадает с текущим пользователем,
        # то текущий диалог с отправителем
        if (recipient.id, recipient.__class__.__name__) \
                == (session["user"]["id"], session["role"]):
            partner = sender
        # Если же нет, то текущий диалог с получателем
        else:
            partner = recipient
        # Если диалог с этим человеком уже есть в словаре, то пойдем дальше
        if partner in dialogs:
            continue
        # Получим сообщения, отправленные собеседнику и собеседником
        for_partner_messages = Message.query.filter_by(
            sender_id=session["user"]["id"],
            sender_role=session["role"],
            recipient_id=partner.id,
            recipient_role=partner.__class__.__name__)
        from_partner_messages = Message.query.filter_by(
            sender_id=partner.id,
            sender_role=partner.__class__.__name__,
            recipient_id=session["user"]["id"],
            recipient_role=session["role"])
        # Вытащим последнее отправленное сообщение
        last_message = for_partner_messages.union(
            from_partner_messages).order_by(Message.date).all()
        dialogs.update({partner: last_message[-1]})
    return render_template("journal/messages.html", session=session,
                           users=users, dialogs=dialogs)


@app.route("/messages/<login>", methods=["GET", "POST"])
@login_required
def dialog(login):
    recipient = find_user_by_login(login)
    messages_from_sender = Message.query.filter_by(
        sender_id=session["user"]["id"],
        sender_role=session["role"],
        recipient_id=recipient.id,
        recipient_role=recipient.__class__.__name__
    )
    messages_from_recipient = Message.query.filter_by(
        sender_id=recipient.id,
        sender_role=recipient.__class__.__name__,
        recipient_id=session["user"]["id"],
        recipient_role=session["role"]
    )
    all_messages = messages_from_sender.union(messages_from_recipient)
    print(all_messages.all())
    return "<p>...</p>"


@app.route('/school_managing')
@school_admin_only
def school_managing():
    return render_template('journal/school_managing.html', session=session)


@app.route('/users')
@school_admin_only
def users():
    return render_template('journal/users.html', session=session)


@app.route('/school_settings')
@school_admin_only
def school_settings():
    form = SchoolEditForm()
    # TODO
    return render_template('journal/school_settings.html', session=session,
                           form=form)


@app.route('/classes')
@school_admin_only
def classes():
    return render_template('journal/classes.html', session=session)


@app.route('/subjects')
@school_admin_only
def subjects():
    return render_template('journal/subjects.html', session=session)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_password_right = check_password_hash(
            session['user']['password_hash'],
            form.old_password.data)
        if not old_password_right:
            return render_template('journal/settings.html', session=session,
                                   form=form, password_change_error=True)

        user = find_user_by_role(session['user']['id'], session['role'])
        user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        session['user']['password_hash'] = user.password_hash
        return render_template('journal/settings.html', session=session,
                               form=form, password_change_success=True)

    return render_template('journal/settings.html', session=session, form=form)
