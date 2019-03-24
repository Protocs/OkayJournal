import email.utils

from flask import request

from okayjournal.app import app
from okayjournal.utils import *
from okayjournal.db import *


@app.route("/get_subjects")
@restricted_access(["SchoolAdmin"])
def get_subjects():
    subject_list = Subject.query.filter_by(school_id=session["user"]["school_id"]).all()
    response = {}
    for subject in subject_list:
        response.update({subject.id: {"id": subject.id, "name": subject.name}})
    return jsonify(response)


@app.route("/messages/<login>", methods=["GET", "POST"])
@login_required_rest
def get_dialog(login):
    """Возвращает JSON-объект сообщений."""

    recipient = find_user_by_login(login)
    if not recipient:
        return jsonify({"error": "Recipient not found"})

    messages_from_recipient = Message.query.filter_by(
        sender_id=recipient.id,
        sender_role=recipient.__class__.__name__,
        recipient_id=session["user"]["id"],
        recipient_role=session["role"],
    )

    if request.method == "POST":
        if request.json.get("mark_as_read"):
            for message in messages_from_recipient.all():
                message.read = True
            db.session.commit()
            return jsonify({"success": "ok"})

    messages_from_sender = Message.query.filter_by(
        sender_id=session["user"]["id"],
        sender_role=session["role"],
        recipient_id=recipient.id,
        recipient_role=recipient.__class__.__name__,
    )

    all_messages = messages_from_sender.union(messages_from_recipient)
    response = {}
    for message in all_messages.order_by(Message.date).all():
        response.update(
            {
                message.id: {
                    "id": message.id,
                    "sender": {"id": message.sender_id, "role": message.sender_role},
                    "recipient": {
                        "id": message.recipient_id,
                        "role": message.recipient_role,
                    },
                    "text": message.text,
                    "date": email.utils.formatdate(message.date.timestamp()),
                    "read": message.read,
                }
            }
        )

    return jsonify(response)


@app.route("/dialogs")
@login_required_rest
def get_dialogs():
    dialogs = {}
    # Вытащим все сообщения, которые были отправлены текущим пользователем
    # и сгруппируем их по получателю
    messages_from_cur_user = Message.query.filter_by(
        sender_id=session["user"]["id"], sender_role=session["role"]
    ).group_by(Message.recipient_id, Message.recipient_role)
    # Вытащим все сообщения, которые были отправлены текущему пользователю
    # и сгруппируем их по отправителю
    messages_for_cur_user = Message.query.filter_by(
        recipient_id=session["user"]["id"], recipient_role=session["role"]
    ).group_by(Message.sender_id, Message.sender_role)
    # Объединим полученные сообщения в один объект BaseQuery
    all_messages = messages_for_cur_user.union(messages_from_cur_user)

    # Пройдемся по каждому сообщению, чтобы составить список диалогов
    for message in reversed(all_messages.order_by(Message.date).all()):
        # Вытащим получателя и отправителя сообщения
        recipient = find_user_by_role(message.recipient_id, message.recipient_role)
        sender = find_user_by_role(message.sender_id, message.sender_role)
        # Если получатель совпадает с текущим пользователем,
        # то текущий диалог с отправителем
        if user_equal(recipient, session):
            partner = sender
        else:  # Если же нет, то текущий диалог с получателем
            partner = recipient
        # Если диалог с этим человеком уже есть в словаре, то пойдем дальше
        if any(partner.login == dialogs[k]["partner"]["login"] for k in dialogs):
            continue
        if (message.sender_id, message.sender_role) == (
            session["user"]["id"],
            session["role"],
        ):
            last_message_text = "Вы: " + message.text
        else:
            last_message_text = message.text
        dialogs.update(
            {
                str(message.date.timestamp()): {
                    "text": last_message_text,
                    "sender": {"id": message.sender_id, "role": message.sender_role},
                    "partner": {
                        "id": partner.id,
                        "role": partner.__class__.__name__,
                        "name": get_fullname(partner),
                        "login": partner.login,
                    },
                    "unread": get_count_unread_messages(
                        (session["user"]["id"], session["role"]), user(partner)
                    ),
                }
            }
        )
    return jsonify(dialogs)


@app.route("/send_message", methods=["POST"])
@login_required_rest
def send_message():
    db.session.add(
        Message(
            sender_id=session["user"]["id"],
            sender_role=session["role"],
            recipient_id=request.json["recipient_id"],
            recipient_role=request.json["recipient_role"],
            text=request.json["text"],
        )
    )
    db.session.commit()
    return jsonify({"success": "OK"})


@app.route("/get_classes")
@restricted_access(["SchoolAdmin"])
def get_classes():
    grades = Grade.query.filter_by(school_id=session["user"]["school_id"]).all()
    grades_structured = {}
    for n in range(1, 12):
        grades_structured[n] = {
            g.id: g.letter
            for g in sorted(
                filter(lambda g: g.number == n, grades), key=lambda g: g.letter
            )
        }
    return jsonify(grades_structured)


@app.route("/get_parents")
@restricted_access(["SchoolAdmin"])
def get_parents():
    parents = Parent.query.filter_by(school_id=session["user"]["school_id"]).all()
    response = {}
    for parent in parents:
        response.update({parent.id: get_fullname(parent)})
    return jsonify(response)


@app.route("/get_class/<int:grade_id>")
@restricted_access(["SchoolAdmin"])
def get_class(grade_id):
    grade = Grade.query.filter_by(id=grade_id).first()
    homeroom_teacher = Teacher.query.filter_by(
        school_id=session["user"]["school_id"], homeroom_grade_id=grade.id
    ).first()
    response = {
        "id": grade.id,
        "homeroom_teacher": {
            "id": homeroom_teacher.id,
            "name": get_fullname(homeroom_teacher),
        },
        "students": [],
        "number": grade.number,
        "letter": grade.letter,
    }
    for student in sorted(
        grade.students, key=lambda s: (s.surname, s.name, s.patronymic)
    ):
        response["students"].append(get_fullname(student))
    return jsonify(response)


@app.route("/get_teachers_subjects")
@restricted_access(["SchoolAdmin"])
def get_teachers_subjects_route():
    return jsonify(get_teachers_subjects(session["user"]["school_id"]))


@app.route("/get_teacher_schedule")
@restricted_access(["SchoolAdmin", "Teacher"])
def get_teacher_schedule():
    teacher = find_user_by_role(session["user"]["id"], session["role"])
    response = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
    for subject in teacher.schedule:
        response[subject.day].update(
            {
                subject.subject_number: {
                    "subject": {"id": subject.subject.id, "name": subject.subject.name},
                    "grade": {
                        "id": subject.grade_id,
                        "letter": subject.grade.letter,
                        "number": subject.grade.number,
                    },
                }
            }
        )
    return jsonify(response)


@app.route("/get_users")
@login_required_rest
def get_users():
    response = {}
    for user_class in USER_CLASSES:
        response.update({user_class.__name__: {}})
        for user in user_class.query.filter_by(
            school_id=session["user"]["school_id"]
        ).all():
            response[user_class.__name__].update(
                {user.id: {"name": get_fullname(user)}}
            )
    return jsonify(response)
