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
fillNumberSelect(grade_number_select);
grade_letter_select.empty();

$.ajax("get_classes").done(function (classes) {
    fillLetterSelect(grade_letter_select, 1, classes);

    grade_number_select.change(function () {
        fillLetterSelect(grade_letter_select, grade_number_select.val(), classes);
    });
});

var parent_select = $("#parent_select");
parent_select.empty();
$.ajax("get_parents").done(function (parents) {
    for (let p in parents) {
        let option = $("<option/>", {
            value: p,
            text: parents[p]
        });
        option.appendTo(parent_select);
    }
});