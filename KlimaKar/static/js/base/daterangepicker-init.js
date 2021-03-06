var date_input_settings = {
    singleDatePicker: true,
    showDropdowns: true,
    autoUpdateInput: false,
    drops: "down",
    locale: {
        format: "DD.MM.YYYY",
        separator: " - ",
        applyLabel: "Akceptuj",
        cancelLabel: "Anuluj",
        fromLabel: "Od",
        toLabel: "Do",
        customRangeLabel: "Wybierz zakres",
        weekLabel: "T",
        daysOfWeek: ["Niedz", "Pon", "Wt", "Śr", "Czw", "Pt", "Sob"],
        monthNames: [
            "Styczeń",
            "Luty",
            "Marzec",
            "Kwiecień",
            "Maj",
            "Czerwiec",
            "Lipiec",
            "Sierpień",
            "Wrzesień",
            "Październik",
            "Listopad",
            "Grudzień",
        ],
        firstDay: 1,
    },
};

var date_range_input_settings = $.extend({}, date_input_settings, {
    singleDatePicker: false,
    linkedCalendars: false,
    ranges: {
        Dzisiaj: [moment(), moment()],
        Wczoraj: [moment().subtract(1, "days"), moment().subtract(1, "days")],
        "Ten tydzień": [moment().startOf("isoWeek"), moment().endOf("isoWeek")],
        "Poprzedni tydzień": [
            moment().subtract(1, "week").startOf("isoWeek"),
            moment().subtract(1, "week").endOf("isoWeek"),
        ],
        "Dwa tygodnie": [moment().subtract(1, "week").startOf("isoWeek"), moment().endOf("isoWeek")],
        "Ostatnie 30 dni": [moment().subtract(29, "days"), moment()],
        "Ten miesiąc": [moment().startOf("month"), moment().endOf("month")],
        "Ostatni miesiąc": [
            moment().subtract(1, "month").startOf("month"),
            moment().subtract(1, "month").endOf("month"),
        ],
    },
});

$(function () {
    $(".date-input").attr("readonly", true);
    $(".date-input").daterangepicker(date_input_settings);
    $(".date-input").on("apply.daterangepicker", function (ev, picker) {
        $(this).val(picker.startDate.format("DD.MM.YYYY"));
    });

    function date_range_cb(start, end) {
        $(".date-range-input").html(start.format("DD.MM.YYYY") + " - " + end.format("DD.MM.YYYY"));
    }
    $(".date-range-input").attr("readonly", true);
    $(".date-range-input").daterangepicker(date_range_input_settings, date_range_cb);
    $(".date-range-input").on("apply.daterangepicker", function (ev, picker) {
        $(this).val(picker.startDate.format("DD.MM.YYYY") + " - " + picker.endDate.format("DD.MM.YYYY"));
    });

    $(".date-inline").daterangepicker(
        $.extend({}, date_input_settings, {
            parentEl: $(".date-inline-container"),
        })
    );
    $(".date-inline").on("apply.daterangepicker", function (ev, picker) {
        $(this).val(picker.startDate.format("DD.MM.YYYY"));
    });

    if ($(".date-inline").length > 0) {
        $(".date-inline").data("daterangepicker").hide = function () {};
        $(".date-inline").data("daterangepicker").setStartDate(moment());
        $(".date-inline").data("daterangepicker").setEndDate(moment());
        $(".date-inline").data("daterangepicker").clickApply();
        $(".date-inline").data("daterangepicker").show();
    }

    $(".date-input:not(.always-down), .date-range-input:not(.always-down)").on("show.daterangepicker", function (ev, picker) {
        if ($(window).width() < 700 && $(window).height() < 1100) {
            $(".daterangepicker:not(.single)").addClass("scrollable-date");
        }
        if (picker.element.offset().top - $(window).scrollTop() + picker.container.outerHeight() > $(window).height()) {
            picker.drops = "up";
        } else {
            picker.drops = "down";
        }
        picker.move();
    });
});
