const LETTERS = ["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И", "Й", "К",
    "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч",
    "Ш", "Щ", "Э", "Ю", "Я"];

var classes = $.ajax("get_classes").done(function (classes) {
    for (var i = 1; i <= 11; i++) {
        var card = $("#card" + i.toString());
        classes[i].forEach(function (grade, j, arr) {
            var grade_button = $("<button/>", {
                type: "button",
                class: "btn btn-primary",
                text: grade,
                "data-toggle": "modal",
                "data-target": "#gradeInfo",
                grade_number: i,
                grade_letter: grade
            });
            grade_button.appendTo(card);
        });

        var add_grade_button = $("<button/>", {
            type: "button",
            class: "btn btn-light",
            "data-toggle": "modal",
            "data-target": "#addClass",
            id: i.toString(),
            text: "+"
        });
        add_grade_button.appendTo(card);
    }


    $("#addClass").on("show.bs.modal", function (e) {
        $("#grade :first-child").detach();
        var grade_number = e.relatedTarget.id;
        var last_letter = classes[grade_number][classes[grade_number].length - 1];
        var next_letter = LETTERS[classes[grade_number].indexOf(last_letter) + 1];
        var grade = $("<input/>", {
            type: "text",
            class: "form-control",
            name: "grade",
            value: e.relatedTarget.id + " «" + next_letter + "»",
            readonly: true,
            id: "grade_input_readonly"
        });
        grade.appendTo($("#grade"));
    });

    $("#gradeInfo").on("show.bs.modal", function (e) {
        $("#students_info").empty();
        $("#homeroom_teacher_info").empty();
        var grade_number = e.relatedTarget.getAttribute("grade_number");
        var grade_letter = e.relatedTarget.getAttribute("grade_letter");
        $("#gradeInfoLabel").text(grade_number.toString() + grade_letter);
        $.ajax("get_class/" + grade_number.toString() + "/" + grade_letter).done(function (grade) {
            var homeroom_teacher = $("<p/>", {
                text: grade["homeroom_teacher"]["name"]
            });
            for (var s in grade["students"]) {
                var student = $("<p/>", {
                    text: grade["students"][s]
                });
                student.appendTo($("#students_info"));
            }
            homeroom_teacher.appendTo($("#homeroom_teacher_info"));
        });
    })
});

