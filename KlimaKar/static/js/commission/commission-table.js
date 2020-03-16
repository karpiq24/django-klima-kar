function submitFastCommission(url) {
    var data = $("#fast_commission_form").serialize();
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function(data) {
            addAlert("Sukces!", "success", data.message + ".");
            window.location.href = data.url;
        },
        error: function(data) {
            addAlert("Błąd!", "error", data.responseJSON.message + ".");
            $("#fast_commission_form").modal("show");
        }
    });
}

$(function() {
    $(".sidenav #nav-commissions")
        .children(":first")
        .addClass("active");
    $(".sidenav #nav-commission").collapse("show");

    $('.filter-tabs > a[data-toggle="tab"]').on("show.bs.tab", function(e) {
        if ($(e.target).data("value") === $(".filter-tabs").data("done")) {
            $("#id_end_date").attr("disabled", true);
            $("#id_end_date").val("");
        } else {
            $("#id_end_date").attr("disabled", false);
        }
    });
});
