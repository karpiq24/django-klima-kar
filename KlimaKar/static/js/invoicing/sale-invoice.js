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
        $('#contractor-edit').prop('disabled', false);
    }
}

function calculateInvoiceTotals() {
    var invoice_total_netto = 0.00;
    var tax_multiplier = $("#id_tax_percent").val() / 100;
    $('.item-formset-row').not('.readonly').each(function() {
        if (!$(this).hasClass('d-none')) {
            var price_netto = toCurrency($(this).find(".item-netto").val());
            if (isNaN(price_netto)) {
                price_netto = 0;
            }
            var quantity = parseInt($(this).find(".item-quantity").val());
            var total_netto = toCurrency(quantity * price_netto);
            invoice_total_netto = toCurrency(invoice_total_netto + total_netto);
        }
    });
    if (isNaN(invoice_total_netto)) {
        invoice_total_netto = 0;
    }
    var invoice_total_brutto = toCurrency(invoice_total_netto + invoice_total_netto * tax_multiplier);
    $('#id_total_value_netto').val(invoice_total_netto);
    $('#id_total_value_brutto').val(invoice_total_brutto);
    $('#invoice-total-netto').text(invoice_total_netto.toFixed(2).replace(".", ",") + " zł");
    $('#invoice-total-brutto').text(invoice_total_brutto.toFixed(2).replace(".", ",") + " zł");
}

$(function () {
    $('.sidenav #nav-saleinvoices').children(':first').addClass('active');
    $('.sidenav #nav-invoicing').collapse('show');

    $('#id_contractor').on('select2:selecting', function (e) {
        var data = e.params.args.data;

        if (data.create_id !== true) {
            $('#contractor-edit').prop('disabled', false);
            return;
        }
        $('#contractor-edit').prop('disabled', true);

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

    $("#id_contractor").change(function () {
        var parent = $("#id_contractor").parent();
        var contractor_pk = $('#id_contractor').val();
        $.ajax({
            url: GET_CONTRACTOR_DATA,
            data: {
                'pk': contractor_pk,
                'validate_vat': true
            },
            dataType: 'json',
            success: function (result) {
                if (result.contractor.nip) {
                    $('#gus-data').data('nip', result.contractor.nip);
                    $('#gus-data').show();
                } else {
                    $('#gus-data').hide();
                }
                if (result.contractor.vat_valid === false) {
                    $(parent).find('div.vat-failed').remove();
                    $("#id_contractor").addClass('is-invalid');
                        if ($(parent).find('div.vat-invalid').length == 0) {
                            $(parent).append('<div class="invalid-feedback vat-invalid">Wybrany kontrahent nie jest płatnikiem VAT. <a href="' + result.contractor.vat_url + '" target="_blank">(sprawdź tutaj)</a></div>')
                        }
                } else if (result.contractor.vat_valid === 'failed') {
                    $(parent).find('div.vat-invalid').remove();
                    $("#id_contractor").addClass('is-invalid');
                    if ($(parent).find('div.vat-failed').length == 0) {
                        $(parent).append('<div class="invalid-feedback vat-failed">Nie udało się sprawdzić statusu płatnika VAT. Sprawdź ręcznie.</div>')
                    }
                } else {
                    $(parent).find('div.vat-failed').remove();
                    $(parent).find('div.vat-invalid').remove();
                    if ($(parent).find('div.invalid-feedback').length == 0) {
                        $("#id_contractor").removeClass('is-invalid');
                    }
                }
                if (INVOICE_TYPE === '4' || INVOICE_TYPE === '5') {
                    if (result.contractor.nip_prefix == null) {
                        $("#id_contractor").addClass('is-invalid');
                        if ($(parent).find('div.no-prefix').length == 0) {
                            $(parent).append('<div class="invalid-feedback no-prefix">Wybrany kontrahent nie ma podanego prefixu NIP.</div>')
                        }
                    }
                    else {
                        $(parent).find('div.no-prefix').remove();
                        if ($(parent).find('div.invalid-feedback').length == 0) {
                            $("#id_contractor").removeClass('is-invalid');
                        }
                    }
                }
            }
        });
    });

    $("#add_item_formset").click(function(){
        var item_form = $('#item-rows').children('.d-none').first();
        $(item_form).find(".item-DELETE").children('input').prop('checked', false);
        $(item_form).removeClass('d-none');
        $(item_form).insertAfter($("#item-rows tr:not('.d-none'):last"));
        $(item_form).find(".form-control").first().focus();
    });

    $(".remove_item_formset").click(function(){
        var item_form = $(this).parents(".item-formset-row");
        $(item_form).addClass('d-none');
        $(item_form).find(".item-name").val('');
        $(item_form).find(".item-description").val('');
        $(item_form).find(".item-ware").val('').change();
        $(item_form).find(".item-quantity").val(1);
        $(item_form).find(".item-netto").val('');
        $(item_form).find(".item-brutto").val('');
        $(item_form).find(".item-DELETE").children('input').prop('checked', true);
        calculateInvoiceTotals();
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

    $(".choose_service").click(function() {
        var item_form = $(this).parents(".item-formset-row");
        var service_pk = $(item_form).find(".item-service").val();
        if (service_pk === '') {
            return;
        }
        $.ajax({
            url: GET_SERVICE_DATA,
            data: {
                'pk': service_pk
            },
            dataType: 'json',
            success: function (result) {
                $(item_form).find(".item-name").val(result.service.name);
                $(item_form).find(".item-description").val(result.service.description);
                $(item_form).find(".item-netto").val(result.service.price_netto);
                $(item_form).find(".item-brutto").val(result.service.price_brutto);
                $(item_form).find(".item-quantity").val(result.service.quantity);

                if (result.service.ware) {
                    var $option = $("<option selected></option>").val(result.service.ware.pk).text(result.service.ware.index);
                    var $sel2 = $(item_form).find(".item-ware");
                    $sel2.append($option).trigger('change');
                }
                if (result.service.price_brutto) {
                    $(item_form).find(".item-brutto").change();
                }
                else {
                    $(item_form).find(".item-netto").change();
                }
            }
        });
    });

    $("#contractor-edit").click(function(){
        var contractor_pk = $('#id_contractor').val();
        var url = UPDATE_CONTRACTOR.replace('0', contractor_pk);
        $.ajax({
            url: url,
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            }
        });
    });

    if ($('#id_contractor').val() != '') {
        $('#contractor-edit').prop('disabled', false);
    }

    $('#item-rows tr:first').removeClass('d-none');
    $('.item-formset-row').each(function() {
        var item_form = $(this);
        if ($(item_form).find(".item-name").val() || $(item_form).find(".item-description").val() ||
            $(item_form).find(".item-ware").val() ||  $(item_form).find(".item-netto").val() != 0 ||
            $(item_form).find(".item-brutto").val() != 0 || $(item_form).find(".item-quantity").val() != 1 ||
            $(item_form).find(".invalid-feedback").length > 0) {

            item_form.removeClass('d-none');
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('value_type') && urlParams.get('value_type') === 'netto') {
                $(item_form).find(".item-netto").change();
            } else {
                $(item_form).find(".item-brutto").change();
            }
        }
    })

    if ($("#id_contractor").val() !== '') {
        $("#id_contractor").change();
    }
    calculateInvoiceTotals();
});
