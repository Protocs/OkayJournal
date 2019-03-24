// function fillNumberSelect(selector, selected) {
//     for (let i = 1; i <= 11; i++) {
//         let option = $("<option/>", {
//             value: i,
//             text: i
//         });
//         if (i === selected)
//             option.attr("selected", true);
//         option.appendTo(selector);
//     }
// }
//
// function fillLetterSelect(selector, grade_number, classes, selected) {
//     selector.empty();
//     for (let g in classes[grade_number]) {
//         let option = $("<option/>", {
//             value: classes[grade_number][g],
//             text: classes[grade_number][g]
//         });
//         if (classes[grade_number][g] === selected)
//             option.attr("selected", true);
//         option.appendTo(selector);
//     }
// }
//
//
// var grade_letter_select = $("#grade_letter_select");
// var grade_number_select = $("#grade_number_select");
// var pathname = document.location.pathname.split('/');
// $.ajax("/get_class/" + pathname[pathname.length - 1]).done(function (grade) {
//     fillNumberSelect(grade_number_select, grade["number"]);
//
//     grade_letter_select.empty();
//
//     $.ajax("/get_classes").done(function (classes) {
//         fillLetterSelect(
//             grade_letter_select,
//             grade_number_select.val(),
//             classes,
//             grade["letter"]);
//
//         grade_number_select.change(function () {
//             fillLetterSelect(
//                 grade_letter_select,
//                 grade_number_select.val(),
//                 classes,
//                 grade["letter"]);
//         });
//     });
// });

if (pathname.length === 3) {
    $.ajax("/get_teachers_subjects").done(function (subjects) {
        // Заполним таблицу с расписанием
        for (let i = 1; i <= 6; i++) {
            for (let j = 1; j <= 6; j++) {
                let subject_select = $("#subject" + i.toString() + j.toString());
                // Как только изменяется выбранный элемент одного из селекторов
                // предметов, меняем список учителей
                subject_select.change(function (e) {
                    let current_teacher_select = $("#teacher" +
                        e.target.attributes.day.value.toString() +
                        e.target.attributes.subject.value.toString());
                    current_teacher_select.empty();
                    if (e.target.value !== "none") {
                        for (let t in subjects[e.target.value]["teachers"]) {
                            let teacher_option = $("<option/>", {
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
                });
            }
        }
    });
}


