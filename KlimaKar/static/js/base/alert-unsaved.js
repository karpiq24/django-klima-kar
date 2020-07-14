$(function () {
    let madeChanges = false;
    $("input, select, textarea").on("change", function () {
        $("#not-saved-alert").removeClass("d-none");
        madeChanges = true;
    });

    $(".date-input").on("apply.daterangepicker", function () {
        $("#not-saved-alert").removeClass("d-none");
        madeChanges = true;
    });

    if ($("#not-saved-alert").length > 0)
        $(window).bind("beforeunload", function () {
            if (madeChanges) {
                return "Zmiany nie zostały zapisane. Czy na pewno chcesz opuścić tą stronę?";
            }
        });
});
