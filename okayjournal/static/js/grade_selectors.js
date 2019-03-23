function fillNumberSelect(selector, selected) {
    for (let i = 1; i <= 11; i++) {
        let option = $("<option/>", {
            value: i,
            text: i
        });
        if (i === selected)
            option.attr("selected", true);
        option.appendTo(selector);
    }
}

function fillLetterSelect(selector, grade_number, classes, selected) {
    selector.empty();
    for (let g in classes[grade_number]) {
        let option = $("<option/>", {
            value: classes[grade_number][g],
            text: classes[grade_number][g]
        });
        if (classes[grade_number][g] === selected)
            option.attr("selected", true);
        option.appendTo(selector);
    }
}


var grade_letter_select = $("#grade_letter_select");
var grade_number_select = $("#grade_number_select");

var pathname = document.location.pathname.split('/');
// Для страниц журнала и составления расписания - в пути присутствует ID класса
$.ajax("/get_class/" + pathname[pathname.length - 1]).done(function (grade) {
    fillNumberSelect(grade_number_select, grade["number"]);

    grade_letter_select.empty();

    $.ajax("/get_classes").done(function (classes) {
        console.log(classes);
        fillLetterSelect(
            grade_letter_select,
            grade_number_select.val(),
            classes,
            grade["letter"]);

        grade_number_select.change(function () {
            fillLetterSelect(
                grade_letter_select,
                grade_number_select.val(),
                classes,
                grade["letter"]);
        });
    });
});