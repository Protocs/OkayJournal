"use strict";

$('.dialog').hide();

let input = $('input');

input.on('keypress', function (e) {
    if (e.key == 'Enter')
        sendMessage();
});

input.on('focus', function(e) {
    $('.message-input').css('box-shadow', '0px 0px 7px #00000054');
});

input.on('focusout', function(e) {
    $('.message-input').css('box-shadow', '');
});

let recipient = null;
let recipientRole = null;
let recipientId = null;

const ROLES = {
    "SchoolAdmin": "школьный администратор",
    "Teacher": "учитель",
    "Student": "ученик",
    "Parent": "родитель"
};

function openDialog(element) {
    for (let dialog of $('dialogs-drawer').children().toArray()) {
        $(dialog).removeAttr('selected');
    }
    $(element).attr('selected', true);

    let messages = $('messages');
    messages.empty();
    recipient = $(element).attr('recipient');
    recipientRole = $(element).attr('recipient_role');
    recipientId = $(element).attr('recipient_id');

    let recipientRoleText = ROLES[recipientRole];
    $('dialog-header').html('<div>' + $(element).attr('recipient_name')
        + ' <span style="color: #bfbfbf">' + recipientRoleText + '</span></div>');

    // Пометим сообщения как прочитанные
    $.ajax("messages/" + recipient, {
        type: "POST",
        data: JSON.stringify({
            mark_as_read: true
        }),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    });
    let unread_dialogs = $("#unread_dialogs");
    if (unread_dialogs.text() - 1 > 0) {
        unread_dialogs.text(unread_dialogs.text() - 1);
    } else {
        unread_dialogs.remove();
    }

    updateMessages();
    $('.dialog').show();
    $('.message-input input').focus();
}

function addMessage(message) {
    let messageBody = $('<message></message>', {
        text: message.text,
        message_id: message.id
    });

    // Метка времени
    let messageDate = new Date(message.date);
    let now = new Date();
    let dateString = messageDate.getHours().toString().padStart(2, '0')
        + ':' + messageDate.getMinutes().toString().padStart(2, '0');
    let todayMessage = now.getDate() == messageDate.getDate()
        && now.getMonth() == messageDate.getMonth();
    let todayYear = now.getFullYear() == messageDate.getFullYear();
    if (!todayMessage) {
        if (todayYear) {
            dateString = messageDate.getDate().toString() + ' ' + messageDate.toLocaleString('ru-ru', {month: 'long'})
                + ' ' + dateString;
        } else {
            dateString = messageDate.getDate().toString() + ' ' + messageDate.toLocaleString('ru-ru', {month: 'long'})
                + ' ' + messageDate.getFullYear() + ' ' + dateString;
        }
    }
    $('<span/>', {
        'class': 'time-mark',
        text: dateString
    }).appendTo(messageBody);

    // Переносим сообщение влево, если оно от собеседника
    if ($('user').attr('user-id') == message.recipient.id && $('user').attr('user-role') == message.recipient.role) {
        messageBody.addClass('align-self-start');
    }
    // Если сообщение не от собеседника, добавляем метку прочтения
    else {
        $('<span/>', {
            'class': 'read-mark',
            text: message.read ? "✓✓" : "✓"
        }).appendTo(messageBody);
    }


    $('messages').append(messageBody);
}

function updateMessages() {
    updateDialogs();
    if (recipient === null)
        return;

    $.ajax('messages/' + recipient).done(function (messages) {
        let messagesChanged = false;
        for (let i in messages) {
            if (!$('messages').children().toArray().some(
                (element, _, let__) => $(element).attr('message_id') == messages[i].id)
            ) {
                addMessage(messages[i]);
                messagesChanged = true;
            }
        }

        let messagesElement = $('messages');
//         messagesElement.scrollTo(messagesElement.children().last());
        if (messagesChanged)
            messagesElement.animate({
                scrollTop: 50000 * messagesElement.children().length
            }, 500);
    });
}

function sendMessage() {
    let text = $('.message-input input');
    if (text.val() === '')
        return;

    $.ajax('send_message', {
        type: 'POST',
        data: JSON.stringify({
            recipient_id: recipientId,
            recipient_role: recipientRole,
            text: text.val()
        }),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
    });

    text.val('');

    updateMessages();
}

let previousDialogs;

function updateDialogs() {
    $.ajax("dialogs").done(function (dialogs) {
        dialogs = Object.values(dialogs);
        dialogs.reverse();
        if (previousDialogs !== undefined && JSON.stringify(previousDialogs) === JSON.stringify(dialogs))
           return;
        
        $('dialog-option').detach();
        for (let d in dialogs) {
            let dialog = $("<dialog-option></dialog-option>", {
                recipient: dialogs[d]["partner"]["login"],
                recipient_role: dialogs[d]["partner"]["role"],
                recipient_id: dialogs[d]["partner"]["id"],
                recipient_name: dialogs[d]["partner"]["name"],
                onclick: "openDialog(this)"
            });
            let name = $("<h5/>", {
                text: dialogs[d]["partner"]["name"]
            });
            let last_message = $("<small/>", {
                class: "text-muted text-truncate",
                style: 'display: block; max-width: 100%;',
                text: dialogs[d]["text"]
            });
            if (dialogs[d]["unread"] !== 0) {
                let unread = $("<span/>", {
                    class: "badge badge-secondary",
                    text: dialogs[d]["unread"],
                    style: "margin-left: 5px;"
                });
                unread.appendTo(last_message);
            }
            name.appendTo(dialog);
            last_message.appendTo(dialog);
            dialog.appendTo("dialogs-drawer");
        }

        previousDialogs = dialogs;

        $(`dialog-option[recipient_id=${recipientId}][recipient_role=${recipientRole}]`).attr('selected', true);
    });
}

setInterval(updateMessages, 1000);


// Выбор получателя в диалоге нового сообщения

let role_select = $("#role-select");
let user_select = $("#user-select");

$.ajax("/get_users").done(function (users) {
    role_select.change(function () {
        user_select.empty();
        for (var u in users[role_select.val()]) {
            if ($("user").attr("user-role") === role_select.val() && $("user").attr("user-id") === u)
                continue;
            user_select.append($("<option/>", {
                text: users[role_select.val()][u]["name"],
                value: u
            }));
        }
    });
});
