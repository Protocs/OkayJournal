function fillSelector(selector_id, subjects, used_subjects) {
    var selected = $(selector_id).val();
    $(selector_id).empty();
    if (selector_id !== "#subjectSelect1") {
        $(selector_id).append($("<option value='none'>-</option>"));
    }
    for (var s in subjects) {
        if (used_subjects.indexOf(subjects[s].id.toString()) === -1) {
            $(selector_id).append($("<option/>", {
                value: subjects[s].id,
                text: subjects[s].name
            }));
        }
    }
    var elem = $(selector_id + ` [value="${selected}"]`);
    if (elem.val() !== "none") {
        elem.attr("selected", true);
    }
}

const SELECTORS = ["#subjectSelect1", "#subjectSelect2", "#subjectSelect3",
    "#subjectSelect4", "#subjectSelect5"];

$.ajax("/get_subjects").done(function (subjects) {
    SELECTORS.forEach(function (item, i, arr) {
        fillSelector(item, subjects, [$("#subjectSelect1").val()]);
    });

    SELECTORS.forEach(function (item1, i, arr) {
        $(item1).change(function () {
            SELECTORS.forEach(function (item2, j, arr) {
                var used_subjects = [];
                SELECTORS.forEach(function (item, i, arr) {
                    if (item !== item2) {
                        used_subjects.push($(item).val());
                    }
                });
                if (item1 !== item2) {
                    fillSelector(item2, subjects, used_subjects);
                }
            })
        })
    });
});

