$('#dialog-header').css('height', $('#div-new-dialog').css('height'));

$('.dialog-content').hide();

$('#message-text').on('keypress', function(e) {
    if (e.key == 'Enter')
        sendMessage();
})

var recipient = null;
var recipientRole = null;
var recipientId = null;

function openDialog(element) {
    var dialogMessages = $('#dialog-messages');
    dialogMessages.empty();
    recipient = $(element).attr('recipient');
    recipientRole = $(element).attr('recipient-role');
    recipientId = $(element).attr('recipient-id');

    $('#dialog-recipient').text($(element).attr('recipient-name'));

    $('.dialog-content').show();
}

function addMessage(message) {
    var messageBody = $('<div/>', {
        'class': 'message card align-items-end',
        text: message.text,
        message_id: message.id
    });

    // Переносим сообщение влево, если оно от собеседника
    if (message.id == recipientId)
        messageBody.addClass('align-self-start');

    // Метка времени
    var messageDate = new Date(message.date);
    var now = new Date();
    var dateString = messageDate.getHours().toString().padStart(2, '0') + ':' + messageDate.getMinutes().toString().padStart(2, '0');
    var todayMessage = now.getDate() == messageDate.getDate()
                           && now.getMonth() == messageDate.getMonth();
    var todayYear = now.getFullYear() == messageDate.getFullYear();
    if (!todayMessage) {
        if (todayYear) {
            dateString = messageDate.getDate().toString() + ' ' + messageDate.toLocaleString('ru-ru', {month: 'long'}) + ' ' + dateString;
        } else {
            dateString = messageDate.getDate().toString() + ' ' + messageDate.toLocaleString('ru-ru', {month: 'long'}) + ' '
                            + messageDate.getFullYear() + ' ' + dateString;
        }
    }
    $('<span/>', {
        'class': 'ml-3 mr-1',
        style: 'font-size: 70%; color: #a2a2a2; position: relative; bottom: 1px;',
        text: dateString
    }).appendTo(messageBody);

    // Метка прочтения
    $('<span/>', {
        style: 'position: relative; top: 0.25rem; font-size: 100%; color: #6db4ff; letter-spacing: -0.5em;',
        text: '✓✓'
    }).appendTo(messageBody);

    $('#dialog-messages').append(messageBody);
}

function updateMessages() {
    if (recipient === null)
        return;

    //$('#dialog-messages').empty();

    var messages = $.ajax('messages/' + recipient).done(function(messages) {
        for (var i in messages) {
            if (!$('#dialog-messages').children().toArray().some(
                    (element, _, __) => $(element).attr('message_id') == messages[i].id)
            ) addMessage(messages[i]);
        }
    });
}

function sendMessage() {
    var text = $('#message-text').val();
    if (text === '')
        return;

    $.ajax('send_message', {
        type: 'POST',
        data: JSON.stringify({
            recipient_id: recipientId,
            recipient_role: recipientRole,
            text: text
        }),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
    })

    $('#message-text').val('');

    updateMessages();
}

setInterval(updateMessages, 1000);

/*
<div class="message card align-items-end">
На краю дороги стоял дуб. Вероятно
<span class="ml-3 mr-1"
      style="font-size: 70%; color: #a2a2a2; position: relative; bottom: 1px;">23:59</span>
<span class="mr-1"
      style="position: relative; top: 0.25rem; font-size: 100%; color: #6db4ff; letter-spacing: -0.5em;">✓✓</span>
</div>


<div class="message card align-items-end align-self-start">
    ауе
    <span class="ml-3 mr-1" style="font-size: 70%; color: #a2a2a2;">23:59</span>
</div>
*/