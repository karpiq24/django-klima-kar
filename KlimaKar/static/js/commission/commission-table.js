function toCurrency(value) {
    return parseFloat(parseFloat(value).toFixed(2));
}

function submitFastCommission(url) {
    var data = $('#fast_commission_form').serialize();
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: function(data) {
            addAlert('Sukces!', 'success', data.message + '.');
            window.location.href = data.url;
        },
        error: function(data) {
            addAlert('Błąd!', 'error', data.responseJSON.message + '.');
            $("#fast_commission_form").modal("show");
        }
    });
};

$(function () {
    $('.sidenav #nav-commissions').children(':first').addClass('active');
    $('.sidenav #nav-commission').collapse('show');
    
    $("#id_value_netto").change(function () {
        $("#id_value_brutto").removeClass('is-invalid');
        var tax_multiplier = parseFloat($("#id_tax_percent").val()) / 100;
        var price_netto = toCurrency($("#id_value_netto").val());
        var price_brutto = toCurrency(price_netto + (price_netto * tax_multiplier));
        $("#id_value_brutto").val(price_brutto);
    });

    $("#id_value_brutto").change(function () {
        var tax_multiplier = parseFloat($("#id_tax_percent").val()) / 100;
        var price_brutto = toCurrency($("#id_value_brutto").val());
        var price_netto = toCurrency(price_brutto / (1 + tax_multiplier));
        $("#id_value_netto").val(price_netto);

        var price_brutto_check = toCurrency(price_netto + (price_netto * tax_multiplier));
        if (price_brutto != price_brutto_check) {
            $("#id_value_brutto").addClass('is-invalid');
        }
        else {
            $("#id_value_brutto").removeClass('is-invalid');
        }
    });

    $('.filter-tabs > a[data-toggle="tab"]').on('show.bs.tab', function (e) {
        const today = moment().format('DD.MM.YYYY') + ' - ' + moment().format('DD.MM.YYYY');
        if ($(e.target).data('value') === $('.filter-tabs').data('done')) {
            if ($('#id_end_date').val() === '') {
                $('#id_end_date').val(today);
            }
        } else if ($('#id_end_date').val() === today) {
            $('#id_end_date').val('');
        }
    })
});
