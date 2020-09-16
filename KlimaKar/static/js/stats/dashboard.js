$(function () {
    $(".sidenav #nav-dashboard").children(":first").addClass("active");
    $("#summary-date-range").on("apply.daterangepicker", function (ev, picker) {
        $.ajax({
            url: $(this).data("url"),
            data: {
                date_from: picker.startDate.format("YYYY-MM-DD"),
                date_to: picker.endDate.format("YYYY-MM-DD"),
            },
            success: function (result) {
                const urls = result.urls;
                const invoices_without_commission = result.invoices_without_commission;
                delete result.invoices_without_commission;
                delete result.urls;
                for (const key in result) {
                    $("#summary-" + key).text(result[key]);
                }
                for (const key in urls) {
                    $("#summary-link-" + key).attr("href", urls[key]);
                }

                $("#invoices-without-commission").empty();
                if (invoices_without_commission.length === 0) {
                    $("#invoices-without-commission").html('<tr><td colspan="4">Brak faktur bez zleceń.</td></tr>');
                } else {
                    invoices_without_commission.forEach(function (invoice) {
                        const result_row =
                            `<tr class="">
                            <td>${invoice.number}</td>
                            <td><a href="${invoice.contractor.url}">${invoice.contractor.name}</a></td>
                            <td>${invoice.brutto_price}</td>
                            <td><a class="btn btn-outline-primary btn-sm btn-table" href="${invoice.url}" title="Szczegóły">Szczegóły</a></td>
                            </tr>`;
                        $("#invoices-without-commission").append(result_row);
                    });
                }
            },
        });
    });

    if ($("#summary-date-range").length > 0) {
        $("#summary-date-range").data("daterangepicker").setStartDate(moment().startOf("isoWeek"));
        $("#summary-date-range").data("daterangepicker").setEndDate(moment().endOf("isoWeek"));
        $("#summary-date-range").data("daterangepicker").clickApply();
    }

    $(".metrics-date-range").on("apply.daterangepicker", function (ev, picker) {
        $.ajax({
            url: $(this).data("url"),
            data: {
                date_from: picker.startDate.format("YYYY-MM-DD"),
                date_to: picker.endDate.format("YYYY-MM-DD"),
            },
            success: function (result) {
                for (const key in result) {
                    const value = result[key];
                    $(".metrics-number." + key).text(value);
                }
            },
        });
    });

    $(".metrics-date-range").each(function () {
        $(this).data("daterangepicker").setStartDate(moment().startOf("isoWeek"));
        $(this).data("daterangepicker").setEndDate(moment().endOf("isoWeek"));
        $(this).data("daterangepicker").clickApply();
    });
});
