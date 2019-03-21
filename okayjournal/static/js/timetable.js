var grade_letter_select = $("#grade_letter_select");
var grade_number_select = $("#grade_number_select");
var pathname = document.location.pathname.split('/');
var grade = $.ajax("/get_class/" + pathname[pathname.length - 1]).done(function (grade) {
    for (var i = 1; i <= 11; i++) {
        var option = $("<option/>", {
            value: i,
            text: i
        });
        if (i === grade["number"])
            option.attr("selected", true);
        option.appendTo(grade_number_select);
    }
    grade_letter_select.empty();
    var classes = $.ajax("/get_classes").done(function (classes) {
        fillLetterSelect(1);

        function fillLetterSelect(grade_number) {
            grade_letter_select.empty();
            for (var g in classes[grade_number]) {
                var option = $("<option/>", {
                    value: classes[grade_number][g],
                    text: classes[grade_number][g]
                });
                if (classes[grade_number][g] === grade["letter"])
                    option.attr("selected", true);
                option.appendTo(grade_letter_select);
            }
        }

        grade_number_select.change(function () {
            fillLetterSelect(grade_number_select.val());
        });
    });
});


if (pathname.length === 3) {
    var teachers_subjects = $.ajax("/get_teachers_subjects").done(function (subjects) {
        for (var i = 1; i <= 6; i++) {
            for (var j = 1; j <= 6; j++) {
                subject_select = $("#subject" + i.toString() + j.toString());
                subject_select.change(function (e) {
                    var current_teacher_select = $("#teacher" + e.target.attributes.day.value.toString() +
                        e.target.attributes.subject.value.toString());
                    current_teacher_select.empty();
                    if (e.target.value !== "none") {
                        for (var t in subjects[e.target.value]["teachers"]) {
                            var teacher_option = $("<option/>", {
                                value: t,
                                text: subjects[e.target.value]["teachers"][t]["name"]
                            });
                            teacher_option.appendTo(current_teacher_select);
                        }
                    } else {
                        $("<option/>", {
                            value: "none",
                            text: "-"
                        }).appendTo(current_teacher_select);
                    }

                })
            }
        }
    });
}


