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
    } else if (identifier == '2') {
        var $option = $("<option selected></option>").val(data['pk']).text(data['text']);
        $('#id_vehicle').append($option).trigger('change');
        $('#vehicle-component-edit').prop('disabled', false);
        $('#id_vc_name').val(data['text']);
    } else if (identifier == '3') {
        var $option = $("<option selected></option>").val(data['pk']).text(data['text']);
        $('#id_component').append($option).trigger('change');
        $('#vehicle-component-edit').prop('disabled', false);
        $('#id_vc_name').val(data['text']);
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
    $('#id_value_netto').val(invoice_total_netto);
    $('#id_value_brutto').val(invoice_total_brutto);
    $('#invoice-total-netto').text(invoice_total_netto.toFixed(2).replace(".", ",") + " zł");
    $('#invoice-total-brutto').text(invoice_total_brutto.toFixed(2).replace(".", ",") + " zł");
}

function checkEndDate() {
    if ($('input[type=radio][name=status]:checked').val() === 'DO' || $('input[type=radio][name=status]:checked').val() === 'CA') {
        $('#id_end_date').prop('disabled', false);
        if ($('#id_end_date').val() === '') {
            $('#id_end_date').val(moment().format('DD.MM.YYYY'));
        }
    } else {
        $('#id_end_date').prop('disabled', true);
        $('#id_end_date').val('');
    }
}

$(function () {

    var debounce = (function() {
        var timer = 0;
        return function(callback, ms){
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    $('.sidenav #nav-commissions').children(':first').addClass('active');
    $('.sidenav #nav-commission').collapse('show');

    var CREATE_CONTRACTOR = $('#create_contractor_url').val();
    var UPDATE_CONTRACTOR = $('#update_contractor_url').val();
    var GET_CONTRACTOR_DATA = $('#contractor_detail_url').val();
    var GET_SERVICE_DATA = $('#service_detail_url').val();
    var CREATE_VEHICLE = $('#create_vehicle_url').val();
    var UPDATE_VEHICLE = $('#update_vehicle_url').val();
    var CREATE_COMPONENT = $('#create_component_url').val();
    var UPDATE_COMPONENT = $('#update_component_url').val();
    var DECODE_AZTEC = $('#decode_aztec_url').val();

    $('#optionName').on('change', function () {
        $('#vehicle-component-container').hide();
        $('#name-container').show();
    })

    $('#optionObject').on('change', function () {
        $('#name-container').hide();
        $('#vehicle-component-container').css('display', 'flex');
    })

    $('#id_contractor').on('select2:selecting', function (e) {
        var data = e.params.args.data;

        if (data.create_id !== true) {
            $('#contractor-edit').prop('disabled', false);
            return;
        }
        $('#contractor-edit').prop('disabled', true);

        e.preventDefault();
        if (isInt(data.id)) {
            if (data.id.length === 9) {
                var initial = {'phone_1': data.id};
            } else {
                var initial = {'nip': data.id};
            }
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
                'pk': contractor_pk
            },
            dataType: 'json',
            success: function (result) {
                if (result.contractor.nip) {
                    $('#gus-data').data('nip', result.contractor.nip);
                    $('#gus-data').show();
                } else {
                    $('#gus-data').hide();
                }
                if (result.contractor.phone == null) {
                    $("#id_contractor").addClass('is-invalid');
                    if ($(parent).find('div.invalid-feedback').length == 0) {
                        $(parent).append('<div class="invalid-feedback">Wybrany kontrahent nie ma podanego numeru telefonu.</div>')
                    }    
                }
                else {
                    $("#id_contractor").removeClass('is-invalid');
                    $(parent).find('div.invalid-feedback').remove();
                }
            }
        });
    });

    $("#contractor-edit").click(function() {
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

    if ($('#id_contractor').val() === '') {
        $('#contractor-edit').prop('disabled', true);
    } else {
        $('#contractor-edit').prop('disabled', false);
    }

    if ($('#id_component').length && $('#id_component').val() === '') {
        $('#id_vc_name').prop('readonly', false);
    } else if ($('#id_component').length) {
        $('#id_vc_name').prop('readonly', true);
    } else if ($('#id_vehicle').length && $('#id_vehicle').val() === '') {
        $('#id_vc_name').prop('readonly', false);
    } else if ($('#id_vehicle').length) {
        $('#id_vc_name').prop('readonly', true);
    }

    $('#id_vehicle').on('select2:selecting', function (e) {
        var data = e.params.args.data;

        if (data.create_id !== true) {
            $('#vehicle-component-edit').prop('disabled', false);
            $('#id_vc_name').val(data['text']);
            return;
        }
        $('#vehicle-component-edit').prop('disabled', true);

        e.preventDefault();
        $.ajax({
            url: CREATE_VEHICLE,
            type: 'get',
            data: {'registration_plate': data.id},
            dataType: 'json',
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            }
        });
    });

    $("#id_vehicle").change(function () {
        var vehicle_pk = $('#id_vehicle').val();
        if (!isInt(vehicle_pk)) {
            $('#id_vc_name').val('');
            $('#vehicle-component-edit').prop('disabled', true);
            $('#id_vc_name').prop('readonly', false);
        } else {
            $('#id_vc_name').prop('readonly', true);
        }
    })

    $('#id_component').on('select2:selecting', function (e) {
        var data = e.params.args.data;

        if (data.create_id !== true) {
            $('#vehicle-component-edit').prop('disabled', false);
            $('#id_vc_name').val(data['text']);
            return;
        }
        $('#vehicle-component-edit').prop('disabled', true);

        e.preventDefault();
        $.ajax({
            url: CREATE_COMPONENT,
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

    $("#id_component").change(function () {
        var component_pk = $('#id_component').val();
        if (!isInt(component_pk)) {
            $('#id_vc_name').val('');
            $('#vehicle-component-edit').prop('disabled', true);
            $('#id_vc_name').prop('readonly', false);
        } else {
            $('#id_vc_name').prop('readonly', true);
        }
    })

    $("#vehicle-component-edit").click(function() {
        var pk = null;
        var url = null;
        if ($('#id_commission_type').val() === 'VH'){
            pk = $('#id_vehicle').val();
            url = UPDATE_VEHICLE.replace('0', pk);
        } else {
            pk = $('#id_component').val();
            url = UPDATE_COMPONENT.replace('0', pk);
        }
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

    $('#vehicle-component-edit').prop('disabled', false);
    if ($('#id_commission_type').val() === 'VH' && $('#id_vehicle').val() === '') {
        $('#vehicle-component-edit').prop('disabled', true);
    } else if ($('#id_commission_type').val() === 'CO' && $('#id_component').val() === '') {
        $('#vehicle-component-edit').prop('disabled', true);
    }

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

    $('#item-rows tr:first').removeClass('d-none');
    $('.item-formset-row').each(function() {
        var item_form = $(this);
        if ($(item_form).find(".item-name").val() || $(item_form).find(".item-description").val() ||
            $(item_form).find(".item-ware").val() ||  $(item_form).find(".item-netto").val() != 0 ||
            $(item_form).find(".item-brutto").val() != 0 || $(item_form).find(".item-quantity").val() != 1 ||
            $(item_form).find(".invalid-feedback").length > 0) {

            item_form.removeClass('d-none');
            $(item_form).find(".item-brutto").change();
        }
    })
    calculateInvoiceTotals();

    $('#id_vehicle').on('select2:opening', function (e) {
        $(this).data('select2').$dropdown.find(':input.select2-search__field').addClass('vehicle');
    })

    function decode_aztec(code) {
        $.ajax({
            url: DECODE_AZTEC,
            type: 'post',
            dataType: 'json',
            data: {
                code: code,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                $('#id_vehicle').select2("close");
                if (data.pk === null) {
                    $.ajax({
                        url: CREATE_VEHICLE,
                        type: 'get',
                        dataType: 'json',
                        data: data,
                        beforeSend: function () {
                            $("#modal-generic").modal("show");
                        },
                        success: function (data) {
                            $("#modal-generic .modal-content").html(data.html_form);
                        }
                    });
                } else {
                    var $option = $("<option selected></option>").val(data['pk']).text(data['label']);
                    $('#id_vehicle').append($option).trigger('change');
                    $('#vehicle-component-edit').prop('disabled', false);
                    $('#id_vc_name').val(data['label']);
                }
            }
        });
    }

    $(document).on('input', '.select2-search__field.vehicle', function (e) {
        var code = $(this).val();
        if (code.length > 350) {
            debounce(function () {
                decode_aztec(code);
            }, 300)
        }
    })

    $(document).on('paste', '.select2-search__field.vehicle', function (e) {
        var code = e.originalEvent.clipboardData.getData('Text');
        if (code.length > 350) {
            debounce(function () {
                decode_aztec(code);
            }, 300)
        }
    })

    $('input[type=radio][name=status]').change(function() {
        checkEndDate();
    })
    checkEndDate();

    if ($("#id_contractor").val() !== '') {
        $("#id_contractor").change();
    }
});
