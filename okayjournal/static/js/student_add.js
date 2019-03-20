var grade_letter_select = $("#grade_letter_select");
var grade_number_select = $("#grade_number_select");
for (var i = 1; i <= 11; i++) {
    var option = $("<option/>", {
        value: i,
        text: i
    });
    option.appendTo(grade_number_select);
}
grade_letter_select.empty();
var classes = $.ajax("get_classes").done(function (classes) {
    fillLetterSelect(1);

    function fillLetterSelect(grade_number) {
        grade_letter_select.empty();
        for (var g in classes[grade_number]) {
            var option = $("<option/>", {
                value: classes[grade_number][g],
                text: classes[grade_number][g]
            });
            option.appendTo(grade_letter_select);
        }
    }

    grade_number_select.change(function () {
        fillLetterSelect(grade_number_select.val());
    });
});

var parent_select = $("#parent_select");
parent_select.empty();
var parents = $.ajax("get_parents").done(function (parents) {
    for (var p in parents) {
        var option = $("<option/>", {
            value: p,
            text: parents[p]
        });
        option.appendTo(parent_select);
    }
});