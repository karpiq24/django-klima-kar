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

    $('#ptu-date-range').on('apply.daterangepicker', function(ev, picker) {
        $.ajax({
            url: $(this).attr('data-url'),
            data: {
                date_from: picker.startDate.format('YYYY-MM-DD'),
                date_to: picker.endDate.format('YYYY-MM-DD')
            },
            success: function (result) {
                $('#ptu-list').html('');
                result.ptu.forEach(function (ptu) {
                    var row_class = ((ptu.warning) ? 'table-warning' : '');
                    var result_row = '<tr class="' + row_class + '">\
                        <td>' + ptu.date + '</td>\
                        <td>' + ptu.value + '</td>\
                        </tr>'
                    $('#ptu-list').append(result_row);
                });
                $('#ptu-sum').text(result.sum)
            }
        });
    });

    if ($('#ptu-date-range').length > 0) {
        $('#ptu-date-range').data('daterangepicker').setStartDate(moment().startOf('isoWeek'));
        $('#ptu-date-range').data('daterangepicker').setEndDate(moment().endOf('isoWeek'));
        $('#ptu-date-range').data('daterangepicker').clickApply();
    }

    $('#id_ptu_date').on('apply.daterangepicker', function(ev, picker) {
        $.ajax({
            url: $(this).attr('data-url'),
            data: {
                date: picker.startDate.format('YYYY-MM-DD'),
            },
            success: function (result) {
                $('#id_ptu_value').val(result.value);
            }
        });
    });
    if ($('#id_ptu_date').length > 0) {
        $('#id_ptu_date').data('daterangepicker').clickApply();
    }

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

    $('.metrics-date-range').each(function () {
        $(this).data('daterangepicker').setStartDate(moment().startOf('isoWeek'));
        $(this).data('daterangepicker').setEndDate(moment().endOf('isoWeek'));
        $(this).data('daterangepicker').clickApply();
    })

    var url = $('#due-payments-list').attr('data-url');
    if (url) {
        $.ajax({
            url: url,
            success: function (result) {
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
        Swal.fire({
            title: "Jesteś pewny, że faktura została opłacona?",
            text: "Faktura " + $(this).data('invoice') + " dla kontrahenta " + $(this).data('contractor'),
            type: "warning",
            showCancelButton: true,
            focusCancel: true,
            confirmButtonText: 'Tak',
            cancelButtonText: 'Nie'
        }).then((payed) => {
            if (payed.value) {
                $.ajax({
                    url: $(that).data('url'),
                    success: function (result) {
                        addAlert('Sukces!', 'success', 'Faktura została opłacona.');
                        $(that).closest('tr').remove();
                        if ($('#due-payments-list tbody tr').length === 0) {
                            $('#due-payments-list').html('Brak zaległych płatności.');
                        }
                    },
                    error: function (result) {
                        addAlert('Błąd!', 'error', 'Coś poszło nie tak, spróbuj ponownie.');
                    }
                })
            }
          });
    });

    $('#ptu-save').on('click', function() {
        $.ajax({
            url: $(this).data('url'),
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'date': $('#id_ptu_date').val(),
                'value': $('#id_ptu_value').val()
            },
            success: function(data) {
                if (data.status === 'success') {
                    addAlert('Sukces!', data.status, data.message);
                } else {
                    addAlert('Uwaga!', data.status, data.message);
                }
                $('#ptu-date-range').data('daterangepicker').clickApply();
            },
            error: function(data) {
                addAlert('Błąd!', 'error', data.responseJSON.message);
            }
        });
    })
});
