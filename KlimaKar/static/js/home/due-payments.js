$(function () {
    $('#payments-tab').on('show.bs.tab', function (e) {
        $("#due-payments-list tbody").empty();
        $.ajax({
            url: $("#due-payments-list").data("url"),
            success: function (result) {
                if (result.invoices.length === 0) {
                    $("#due-payments-list").html("Brak zaległych płatności.");
                    return;
                }
                result.invoices.forEach(function (invoice) {
                    const row_class = invoice.is_exceeded ? "table-danger" : "";
                    const result_row =
                        `<tr class="${row_class}">
                        <td><a href="${invoice.url}">${invoice.number}</a></td>
                        <td><a href="${invoice.contractor.url}">${invoice.contractor.name}</a></td>
                        <td>${invoice.brutto_price}</td>
                        <td>${invoice.payment_date}</td>
                        <td><button class="btn btn-outline-dark btn-table payed" data-invoice="${invoice.number}" data-contractor="${invoice.contractor.name}" data-url="${invoice.payed_url}">Zapłacono</button></td>
                        </tr>`;
                    $("#due-payments-list").find("tbody").append(result_row);
                });
            },
        });
    })

    $("#due-payments-list").on("click", ".payed", function () {
        var that = this;
        Swal.fire({
            title: "Jesteś pewny, że faktura została opłacona?",
            text: "Faktura " + $(this).data("invoice") + " dla kontrahenta " + $(this).data("contractor"),
            type: "warning",
            showCancelButton: true,
            focusCancel: true,
            confirmButtonText: "Tak",
            cancelButtonText: "Nie",
        }).then((payed) => {
            if (payed.value) {
                $.ajax({
                    url: $(that).data("url"),
                    success: function (result) {
                        addAlert("Sukces!", "success", "Faktura została opłacona.");
                        $(that).closest("tr").remove();
                        if ($("#due-payments-list tbody tr").length === 0) {
                            $("#due-payments-list").html("Brak zaległych płatności.");
                        }
                    },
                    error: function (result) {
                        genericErrorAlert();
                    },
                });
            }
        });
    });
})
