$(function () {
    $("#garbage-tab").on("show.bs.tab", function (e) {
        $("#garbageCollectionDates tbody").empty();
        $("#garbageCollectionDates tbody").html(`<tr>
                       <td colspan="3" class="text-center">
                           <i class="fas fa-spinner fa-spin fa-8x text-primary m-4"></i>
                       </td>
                   </tr>`);
        $.ajax({
            url: $("#garbageCollectionDates").data("url"),
            success: function (result) {
                $("#garbageCollectionDates tbody").empty();
                $.each(result.headers, function (index, header) {
                    $("#garbageCollectionDates thead tr").append(`<th scope="col" class="border-top-0">${header}</th>`);
                });
                $.each(result.rows, function (index, row) {
                    let cells = "";
                    $.each(row, function (index, value) {
                        cells += `<td>${value}</td>`;
                    });
                    $("#garbageCollectionDates tbody").append(`<tr>${cells}</tr>`);
                });
            },
            error: function () {
                genericErrorAlert();
            },
        });
    });
});
