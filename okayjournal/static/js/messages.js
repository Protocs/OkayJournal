$('#dialog-header').css('height', $('#div-new-dialog').css('height'));

$('.dialog-content').hide();

$('#message-text').on('keypress', function (e) {
    if (e.key == 'Enter')
        sendMessage();
});

var recipient = null;
var recipientRole = null;
var recipientId = null;

const ROLES = {
    "SchoolAdmin": "школьный администратор",
    "Teacher": "учитель",
    "Student": "ученик",
    "Parent": "родитель"
};

function openDialog(element) {
    let dialogMessages = $('#dialog-messages');
    dialogMessages.empty();
    recipient = $(element).attr('recipient');
    recipientRole = $(element).attr('recipient_role');
    recipientId = $(element).attr('recipient_id');

    let recipientRoleText = ROLES[recipientRole];
    $('#dialog-recipient').html($(element).attr('recipient_name')
        + ' <span style="color: #bfbfbf">' + recipientRoleText + '</span>');

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
    $('.dialog-content').show();
}

function addMessage(message) {
    let messageBody = $('<div/>', {
        'class': 'message card align-items-end',
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


    $('#dialog-messages').append(messageBody);
}

function updateMessages() {
    updateDialogs();
    if (recipient === null)
        return;

    //$('#dialog-messages').empty();

    $.ajax('messages/' + recipient).done(function (messages) {
        for (let i in messages) {
            if (!$('#dialog-messages').children().toArray().some(
                (element, _, __) => $(element).attr('message_id') == messages[i].id)
            ) addMessage(messages[i]);
        }
    });
}

function sendMessage() {
    let text = $('#message-text');
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

function updateDialogs() {
    $.ajax("dialogs").done(function (dialogs) {
        $("#dialogs>a.hidden-link").detach();
        for (let d in dialogs) {
            let link = $("<a/>", {
                href: "#",
                class: "hidden-link",
                recipient: dialogs[d]["partner"]["login"],
                recipient_role: dialogs[d]["partner"]["role"],
                recipient_id: dialogs[d]["partner"]["id"],
                recipient_name: dialogs[d]["partner"]["name"],
                onclick: "openDialog(this)"
            });
            let dialog = $("<div/>", {
                class: "dialog-btn container py-2 px-3 border-bottom dialog-option"
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
            dialog.appendTo(link);
            link.insertAfter($("#addRecipientLink"));
        }
    });
}

setInterval(updateMessages, 1000);
