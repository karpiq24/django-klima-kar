function toCurrency(value) {
    return parseFloat(parseFloat(value).toFixed(2));
}

function calculateInvoiceTotals() {
    var invoice_total = 0.00;
    $('.item-formset-row').each(function() {
        if (!$(this).hasClass('d-none')){
            var price = toCurrency($(this).find(".item-price").val());
            var quantity = parseFloat($(this).find(".item-quantity").val());
            var total = toCurrency(quantity * price);
            invoice_total = toCurrency(invoice_total + total);
        }
    });
    if (isNaN(invoice_total)) {
        invoice_total = 0;
    }
    $('#id_total_value').val(invoice_total);
    $('#invoice-total').text(invoice_total.toFixed(2).replace(".", ",") + " zł");
}

function customSuccessCreate(data, identifier) {
    if (identifier == '1') {
        var $option = $("<option selected></option>").val(data['pk']).text(data['text']);
        var $sel2 = $("#item-rows tr:not('.d-none'):last").find("select.item-ware");
        if (!$sel2.val() == "") {
            var item_form = $('#item-rows').children('.d-none').first();
            $(item_form).find(".item-DELETE").children('input').prop('checked', false);
            $(item_form).removeClass('d-none');
            $(item_form).insertAfter($("#item-rows tr:not('.d-none'):last"));
            $sel2 = $("#item-rows tr:not('.d-none'):last").find("select.item-ware");
        }
        $sel2.append($option).trigger('change');

        $.ajax({
            url: GET_WARE_DATA,
            data: {
                'pk': data['pk']
            },
            dataType: 'json',
            success: function (result) {
                $option.text(result['ware']['index']);
                $option.removeData();
                $sel2.trigger('change');
            }
        });
    }
};

$(function () {
    $('.sidenav #nav-invoices').children(':first').addClass('active');
    $('.sidenav #nav-warehouse').collapse('show');

    $('#item-rows tr:first').removeClass('d-none');
    $('#item-rows tr:first').find(".item-DELETE").children('input').prop('checked', false);
    $('.item-formset-row').each(function() {
        var ware_pk = $(this).find(".item-ware option:selected").val();
        var item_form = $(this);
        var price = $(item_form).find(".item-price").val();
        var quantity = $(item_form).find(".item-quantity").val();

        if (price != 0 || quantity != '1') {
            $(item_form).removeClass('d-none')
        }
        var total = toCurrency(price * quantity);
        $(item_form).find(".item-total-value").text(total.toFixed(2).replace(".", ",") + ' zł');

        if (ware_pk == '') {
            return;
        }
        $(item_form).removeClass('d-none')
        $.ajax({
            url: GET_WARE_DATA,
            data: {
                'pk': ware_pk
            },
            dataType: 'json',
            success: function (result) {
                $(item_form).find(".item-name").text(result['ware']['name']);
            }
        });
    });
    calculateInvoiceTotals();

    $('.item-ware').on('select2:selecting', function (e) {
        var data = e.params.args.data;

        if (data.create_id !== true)
            return;

        e.preventDefault();
        var initial = {'index': data.id};
        $.ajax({
            url: CREATE_WARE,
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

    $(".item-ware").change(function () {
        var index = $("option:selected", this).text();
        var item_form = $(this).parents(".item-formset-row");
        if (index == '---------') {
            $(item_form).find(".item-name").text('');
            return;
        }
        $.ajax({
            url: GET_WARE_DATA,
            data: {
                'index': index
            },
            dataType: 'json',
            success: function (result) {
                $(item_form).find(".item-name").text(result['ware']['name']);
                $(item_form).find(".item-price").val(result['ware']['last_price']);

                var quantity = parseFloat($(item_form).find(".item-quantity").val());
                var total = toCurrency(result['ware']['last_price'] * quantity);
                $(item_form).find(".item-total-value").text(total.toFixed(2).replace(".", ",") + ' zł');
                calculateInvoiceTotals();
            }
        });
    });

    $("#add_item_formset").click(function(){
        var item_form = $('#item-rows').children('.d-none').first();
        $(item_form).find(".item-DELETE").children('input').prop('checked', false);
        $(item_form).removeClass('d-none');
        $(item_form).insertAfter($("#item-rows tr:not('.d-none'):last"));
        $(item_form).find(".item-ware").select2('open');
    });

    $(".remove_item_formset").click(function(){
        var item_form = $(this).parents(".item-formset-row");
        $(item_form).addClass('d-none');
        $(item_form).find(".item-ware").val('').change();
        $(item_form).find(".item-price").val('');
        $(item_form).find(".item-name").text('');
        $(item_form).find(".item-quantity").val(1);
        $(item_form).find(".item-total-value").text('0,00 zł');
        $(item_form).find(".item-DELETE").children('input').prop('checked', true);
        calculateInvoiceTotals();
    });

    $(".item-quantity").change(function () {
        var item_form = $(this).parents('.item-formset-row');
        var price = toCurrency($(item_form).find(".item-price").val());
        var quantity = parseFloat($(item_form).find(".item-quantity").val());
        var total = toCurrency(price * quantity);
        $(item_form).find(".item-total-value").text(total.toFixed(2).replace(".", ",") + ' zł');
        calculateInvoiceTotals();
    });

    $(".item-price").change(function () {
        var item_form = $(this).parents('.item-formset-row');
        var price = toCurrency($(item_form).find(".item-price").val());
        var quantity = parseFloat($(item_form).find(".item-quantity").val());
        var total = toCurrency(price * quantity);
        $(item_form).find(".item-total-value").text(total.toFixed(2).replace(".", ",") + ' zł');
        calculateInvoiceTotals();
    });
});