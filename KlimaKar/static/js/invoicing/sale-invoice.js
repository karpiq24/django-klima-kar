function isInt(value) {
    return !isNaN(value) && 
            parseInt(Number(value), 10) == value && 
            !isNaN(parseInt(value, 10));
}

function toCurrency(value) {
    return parseFloat(parseFloat(value).toFixed(2));
}

function customSuccessCreate(data, identifier) {
    if (identifier == '1') {
        var $option = $("<option selected></option>").val(data['pk']).text(data['text']);
        $('#id_contractor').append($option).trigger('change');
    }
}

function setItemFormCount() {
    var row_count = $('#item-rows').children('.item-formset-row').length - $('#item-rows').children('.d-none').length;
    $('#id_item-TOTAL_FORMS').val(row_count);
}

function calculateInvoiceTotals() {
    var invoice_total_netto = 0.00;
    var tax_multiplier = $("#id_tax_percent").val() / 100;
    $('.item-formset-row').each(function() {
        if (!$(this).hasClass('d-none')) {
            var price_netto = toCurrency($(this).find(".item-netto").val());
            var quantity = parseInt($(this).find(".item-quantity").val());
            var total_netto = toCurrency(quantity * price_netto);
            invoice_total_netto = invoice_total_netto + total_netto;
        }
    });
    var invoice_total_brutto = toCurrency(invoice_total_netto + invoice_total_netto * tax_multiplier);
    $('#id_total_value_netto').val(invoice_total_netto);
    $('#id_total_value_brutto').val(invoice_total_brutto);
    $('#invoice-total-netto').text(invoice_total_netto.toFixed(2).replace(".", ",") + " zł");
    $('#invoice-total-brutto').text(invoice_total_brutto.toFixed(2).replace(".", ",") + " zł");
}

$(function () {
    $('.sidenav #nav-saleinvoices').children(':first').addClass('active');
    $('.sidenav #nav-invoicing').collapse('show');

    $('#item-rows tr:first').removeClass('d-none');
    calculateInvoiceTotals();
    setItemFormCount();

    $('#id_contractor').on('select2:selecting', function (e) {
        var data = e.params.args.data;

        if (data.create_id !== true)
            return;

        e.preventDefault();
        if (isInt(data.id)) {
            var initial = {'nip': data.id};
        }
        else {
            var initial = {'name': data.id};
        }
        $.ajax({
            url: CREATE_CONTRACTOR,
            type: 'get',
            dataType: 'json',
            data: initial,
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            }
        });
    });

    $("#add_item_formset").click(function(){
        var item_form = $('#item-rows').children('.d-none').first();
        $(item_form).find(".item-DELETE").children('input').prop('checked', false);
        $(item_form).removeClass('d-none');
        $(item_form).insertAfter($("#item-rows tr:not('.d-none'):last"));
        $(item_form).find(".form-control").first().focus();
        setItemFormCount();
    });

    $(".remove_item_formset").click(function(){
        var item_form = $(this).parents(".item-formset-row");
        $(item_form).addClass('d-none');
        $(item_form).find(".item-name").val('');
        $(item_form).find(".item-description").val('');
        $(item_form).find(".item-ware").val('').change();
        $(item_form).find(".item-quantity").val(1);
        $(item_form).find(".item-netto").val('0.00');
        $(item_form).find(".item-brutto").val('0.00');
        $(item_form).find(".item-DELETE").children('input').prop('checked', true);
        calculateInvoiceTotals();
        setItemFormCount();
    });

    $(".item-netto").change(function () {
        var item_form = $(this).parents('.item-formset-row');
        $(item_form).find(".item-brutto").removeClass('is-invalid');
        var tax_multiplier = parseFloat($("#id_tax_percent").val()) / 100;
        var price_netto = toCurrency($(item_form).find(".item-netto").val());
        var price_brutto = toCurrency(price_netto + (price_netto * tax_multiplier));
        var quantity = parseInt($(item_form).find(".item-quantity").val());
        var total_netto = toCurrency(price_netto * quantity);
        $(item_form).find(".item-brutto").val(price_brutto);
        $(item_form).find(".item-total-netto").text(total_netto.toFixed(2).replace(".", ",") + ' zł');
        calculateInvoiceTotals();
    });

    $(".item-brutto").change(function () {
        var item_form = $(this).parents('.item-formset-row');
        var tax_multiplier = parseFloat($("#id_tax_percent").val()) / 100;
        var price_brutto = toCurrency($(item_form).find(".item-brutto").val());
        var price_netto = toCurrency(price_brutto / (1 + tax_multiplier));
        var quantity = parseInt($(item_form).find(".item-quantity").val());
        var total_netto = toCurrency(price_netto * quantity);
        $(item_form).find(".item-netto").val(price_netto);
        $(item_form).find(".item-total-netto").text(total_netto.toFixed(2).replace(".", ",") + ' zł');

        var price_brutto_check = toCurrency(price_netto + (price_netto * tax_multiplier));
        if (price_brutto != price_brutto_check) {
            $(item_form).find(".item-brutto").addClass('is-invalid');
        }
        else {
            $(item_form).find(".item-brutto").removeClass('is-invalid');
        }

        calculateInvoiceTotals();
    });

    $(".item-quantity").change(function () {
        var item_form = $(this).parents('.item-formset-row');
        var price_netto = toCurrency($(item_form).find(".item-netto").val());
        var quantity = parseInt($(item_form).find(".item-quantity").val());
        var total_netto = toCurrency(price_netto * quantity);
        $(item_form).find(".item-total-netto").text(total_netto.toFixed(2).replace(".", ",") + ' zł');
        calculateInvoiceTotals();
    });

    $("#id_tax_percent").change(function () {
        var tax_multiplier = parseFloat($(this).val()) / 100;
        $('.item-formset-row').each(function() {
            $(this).find(".item-brutto").removeClass('is-invalid');
            if (!$(this).hasClass('d-none')) {
                var price_netto = toCurrency($(this).find(".item-netto").val());
                var price_brutto = toCurrency(price_netto + (price_netto * tax_multiplier));
                $(this).find(".item-brutto").val(price_brutto.toFixed(2));
            }
        });
        calculateInvoiceTotals();
    });

    $("#id_payed").change(function(){
        if ($("#id_payed").is(':checked')) {
            $("#id_payment_date").prop('hidden', true);
            $("#id_payment_date").val(null);
        }
        else {
            $("#id_payment_date").prop('hidden', false);
            $("#id_payment_date").focus();
        }
    });
});
