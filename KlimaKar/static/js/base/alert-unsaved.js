function blockUnload() {
    if ($(".not-saved-alert").length > 0)
        $(".not-saved-alert").removeClass("d-none");
        $(window).bind("beforeunload", function () {
            return "Zmiany nie zostały zapisane. Czy na pewno chcesz opuścić tą stronę?";
        });
}

$(function () {
    $(document).on("change", "form input, form select, form textarea", function () {
        blockUnload();
    });

    $(document).on("apply.daterangepicker", "form .date-input", function () {
        blockUnload();
    });

    $(document).on("submit", "form", function (event) {
        $(window).off("beforeunload");
    });
});
