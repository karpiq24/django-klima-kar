$(function () {
    $("#ptu-date-range").on("apply.daterangepicker", function (ev, picker) {
        $.ajax({
            url: $(this).data("url"),
            data: {
                date_from: picker.startDate.format("YYYY-MM-DD"),
                date_to: picker.endDate.format("YYYY-MM-DD"),
            },
            success: function (result) {
                $("#ptu-list").html("");
                result.ptu.forEach(function (ptu) {
                    const row_class = ptu.warning ? "table-warning" : "";
                    const result_row =
                        `<tr class="ptu-date-row ${row_class}" data-date="${ptu.date_value}">
                        <td>${ptu.date}</td>
                        <td>${ptu.value}</td>
                        </tr>`;
                    $("#ptu-list").append(result_row);
                });
                $("#ptu-sum").text(result.sum);
            },
        });
    });

    $("#id_ptu_date").on("apply.daterangepicker", function (ev, picker) {
        $.ajax({
            url: $(this).data("url"),
            data: {
                date: picker.startDate.format("YYYY-MM-DD"),
            },
            success: function (result) {
                $("#id_ptu_value").val(result.value);
                $("#id_ptu_value").focus();
                $("#id_ptu_value").select();
            },
        });
    });

    $("#id_ptu_value").on("keyup", function (e) {
        if (e.keyCode === 13) {
            $("#ptu-save").click();
        }
    });

    $("#ptu-save").on("click", function () {
        $.ajax({
            url: $(this).data("url"),
            type: "POST",
            data: {
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
                date: $("#id_ptu_date").val(),
                value: $("#id_ptu_value").val(),
            },
            success: function (data) {
                if (data.status === "success") {
                    addAlert("Sukces!", data.status, data.message);
                } else {
                    addAlert("Uwaga!", data.status, data.message);
                }
                $("#ptu-date-range").data("daterangepicker").clickApply();
            },
            error: function (data) {
                addAlert("Błąd!", "error", data.responseJSON.message);
            },
        });
    });

    $(document).on("click", ".ptu-date-row", function () {
        $("#id_ptu_date").data("daterangepicker").setStartDate($(this).data("date"));
        $("#id_ptu_date").data("daterangepicker").setEndDate($(this).data("date"));
        $("#id_ptu_date").data("daterangepicker").clickApply();
        $("#id_ptu_date").data("daterangepicker").updateView();
    });

    $('#ptu-tab').on('show.bs.tab', function (e) {
        $("#ptu-date-range").data("daterangepicker").clickApply();
        $("#id_ptu_date").data("daterangepicker").clickApply();
    });

    if ($("#ptu-date-range").length > 0) {
        $("#ptu-date-range").data("daterangepicker").setStartDate(moment().startOf("isoWeek"));
        $("#ptu-date-range").data("daterangepicker").setEndDate(moment().endOf("isoWeek"));
    }
})