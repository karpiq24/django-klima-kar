$(function () {
    $('.sidenav #nav-dashboard').children(':first').addClass('active');

    $('#ware-change-date-range').on('apply.daterangepicker', function(ev, picker) {
        var url = $(this).attr('data-url');
        $.ajax({
            url: url,
            data: {
                date_from: picker.startDate.format('YYYY-MM-DD'),
                date_to: picker.endDate.format('YYYY-MM-DD')
            },
            success: function (result) {
                if (result.changes.length === 0) {
                    $('#ware-price-changes-list').html('Brak zmian w cenach towarów.');
                    return;
                }
                $('#ware-price-changes-list').html('');
                result.changes.forEach(function (change) {
                    var div_class = ((change.is_discount) ? 'success' : 'danger');
                    var change_text = ((change.is_discount) ? 'Obniżka' : 'Podwyżka');
                    var result_div = '<div class="list-group-item list-group-item-action list-group-item-' + div_class + '">\
                        <div><small>' + change.created_date + '</small></div>\
                        <strong>' + change_text + ' ceny</strong>\
                        <a href="' + change.ware.url + '">' + change.ware.index + '</a>\
                        z ' + change.last_price + ' na ' + change.new_price + ' u dostawcy\
                        <a href="' + change.supplier.url + '">' + change.supplier.name + '</a>\
                        w fakturze <a href="' + change.invoice.url + '">' + change.invoice.number + '</a>.\
                        </div>'
                    $('#ware-price-changes-list').append(result_div);
                });
            }
        });
    });

    $('#ware-change-date-range').data('daterangepicker').setStartDate(moment().subtract(6, 'days'));
    $('#ware-change-date-range').data('daterangepicker').setEndDate(moment());
    $('#ware-change-date-range').data('daterangepicker').clickApply();

    $('.metrics-date-range').each(function () {
        $(this).data('daterangepicker').setStartDate(moment().startOf('week').add(1, 'days'));
        $(this).data('daterangepicker').setEndDate(moment().endOf('week').add(1, 'days'));
        $(this).data('daterangepicker').clickApply();
    })

    $('.metrics-date-range').on('apply.daterangepicker', function(ev, picker) {
        var url = $(this).attr('data-url');
        $.ajax({
            url: url,
            data: {
                date_from: picker.startDate.format('YYYY-MM-DD'),
                date_to: picker.endDate.format('YYYY-MM-DD')
            },
            success: function (result) {
                for (var key in result) {
                    var value = result[key];
                    $('.metrics-number.' + key).text(value);
                }
            }
        });
    });

    var url = $('#due-payments-list').attr('data-url');
    if (url) {
        $.ajax({
            url: url,
            success: function (result) {
                console.log(result)
                if (result.invoices.length === 0) {
                    $('#due-payments-list').html('Brak zaległych płatności.');
                    return;
                }
                result.invoices.forEach(function (invoice) {
                    var row_class = ((invoice.is_exceeded) ? 'table-danger' : '');
                    var result_row = '<tr class="' + row_class +'">\
                        <td><a href="' + invoice.url + '">' + invoice.number +'</a></td>\
                        <td><a href="' + invoice.contractor.url + '">' + invoice.contractor.name +'</a></td>\
                        <td>' + invoice.brutto_price + '</td>\
                        <td>' + invoice.payment_date + '</td>\
                        <td><button class="btn btn-outline-dark btn-table payed" data-invoice="' + invoice.number + '" data-contractor="' + invoice.contractor.name + '" data-url="' + invoice.payed_url + '">Zapłacono</button></td>\
                        </tr>'
                    $('#due-payments-list').find('tbody').append(result_row);
                });
            }
        });
    }
    $('#due-payments-list').on('click', '.payed', function() {
        var that = this;
        swal({
            title: "Jesteś pewny, że faktura została opłacona?",
            text: "Faktura " + $(this).data('invoice') + " dla kontrahenta " + $(this).data('contractor'),
            icon: "warning",
            buttons: ["Nie", "Tak"],
            dangerMode: true,
          })
          .then((payed) => {
            if (payed) {
                $.ajax({
                    url: $(this).data('url'),
                    success: function (result) {
                        swal("Sukces!", "", {
                            icon: "success",
                          });
                        $(that).closest('tr').remove();
                        if ($('#due-payments-list tbody tr').length === 0) {
                            $('#due-payments-list').html('Brak zaległych płatności.');
                        }
                    },
                    error: function (result) {
                        swal("Błąd!", "Coś poszło nie tak, spróbuj ponownie.", {
                            icon: "error",
                          });
                    }
                })
            }
          });
    });
});
