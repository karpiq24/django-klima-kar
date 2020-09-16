$(function () {
    $('#deko-tab').on('show.bs.tab', function (e) {
        $("#deko-payments-list tbody").empty();
        $("#deko-payments-list tbody")
            .html(`<tr>
                       <td colspan="3" class="text-center">
                           <i class="fas fa-spinner fa-spin fa-8x text-primary m-4"></i>
                       </td>
                   </tr>`);
        $.ajax({
            url: $("#deko-payments-list").data("url"),
            success: function (result) {
                $("#deko-payments-list tbody").empty();
                if (result.invoices.length === 0) {
                    $("#deko-payments-list tbody").html("Brak zaległych płatności.");
                    return;
                }
                result.invoices.forEach(function (invoice) {
                    let numberCell = "";
                    if (invoice.url) numberCell = `<td><a href="${invoice.url}">${invoice.number}</a></td>`
                    else numberCell = `<td>${invoice.number}</td>`
                    const result_row =
                        `<tr>
                        ${numberCell}
                        <td>${invoice.date}</td>
                        <td>${invoice.to_pay.replace(".", ",")} zł</td>
                        </tr>`;
                    $("#deko-payments-list").find("tbody").append(result_row);
                });
                $("#deko-sum").text(`${result.to_pay.replace(".", ",")} zł`);
            },
        });
    })
})
