var subject_select = $("#subject_select");
var grade_number_select = $("#grade_number_select");
var grade_letter_select = $("#grade_letter_select");

var grade_number_selected = grade_number_select.val();
var grade_letter_selected = grade_letter_select.val();

function fillGradeNumberSelect(schedule) {
    grade_number_select.empty();
    let used_classes = [];
    for (let day in schedule) {
        for (let s in schedule[day]) {
            if (schedule[day][s]["subject"]["id"] == subject_select.val()) {
                if (used_classes.indexOf(schedule[day][s]["grade"]["number"]) === -1) {
                    let grade_number_option = $("<option/>", {
                        value: schedule[day][s]["grade"]["number"],
                        text: schedule[day][s]["grade"]["number"]
                    });
                    if (grade_number_option.val() === grade_number_selected)
                        grade_number_option.attr("selected", true);
                    grade_number_option.appendTo(grade_number_select);
                    used_classes.push(schedule[day][s]["grade"]["number"]);
                }
            }
        }
    }
}

function fillGradeLetterSelect(schedule) {
    let used_classes = [];
    grade_letter_select.empty();
    for (let day in schedule) {
        for (let s in schedule[day]) {
            if (schedule[day][s]["grade"]["number"] == grade_number_select.val()) {
                if (used_classes.indexOf(schedule[day][s]["grade"]["letter"]) === -1) {
                    let grade_letter_option = $("<option/>", {
                        value: schedule[day][s]["grade"]["letter"],
                        text: schedule[day][s]["grade"]["letter"]
                    });
                    if (grade_letter_option.val() === grade_letter_selected)
                        grade_letter_option.attr("selected", true);
                    grade_letter_option.appendTo(grade_letter_select);
                    used_classes.push(schedule[day][s]["grade"]["letter"]);
                }
            }
        }
    }
}

$.ajax("/get_teacher_schedule").done(function (schedule) {
    let used_subjects = [];
    for (let day in schedule) {
        for (let s in schedule[day]) {
            if (used_subjects.indexOf(schedule[day][s]["subject"]["id"]) === -1) {
                let subject_option = $("<option/>", {
                    value: schedule[day][s]["subject"]["id"],
                    text: schedule[day][s]["subject"]["name"]
                });
                subject_option.appendTo(subject_select);
                used_subjects.push(schedule[day][s]["subject"]["id"]);
            }
        }
    }

    fillGradeNumberSelect(schedule);
    fillGradeLetterSelect(schedule);

    subject_select.change(function () {
        fillGradeNumberSelect(schedule);
    });
    grade_number_select.change(function () {
        fillGradeLetterSelect(schedule);
    })
});
