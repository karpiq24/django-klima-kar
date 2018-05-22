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
});
