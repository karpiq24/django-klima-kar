$(function () {
    $('.sidenav #nav-vehicles').children(':first').addClass('active');
    $('.sidenav #nav-commission').collapse('show');

    var DECODE_AZTEC = $('#decode_aztec_url').val();

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
                $('#id_brand').val(data.brand);
                $('#id_engine_power').val(data.engine_power);
                $('#id_engine_volume').val(data.engine_volume);
                $('#id_model').val(data.model);
                $('#id_production_year').val(data.production_year);
                $('#id_registration_plate').val(data.registration_plate);
                $('#id_vin').val(data.vin);
                $("#id_aztec").val('');
            },
            error: function (data) {
                addAlert('Błąd!', 'error', 'Coś poszło nie tak. Spróbuj ponownie.');
            }
        });
    }

    var debounce = (function() {
        var timer = 0;
        return function(callback, ms){
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    $(document).on('input', '#id_aztec', function (e) {
        var code = $(this).val();
        if (code.length > 350) {
            debounce(function () {
                decode_aztec(code);
            }, 300)
        }
    })

    $(document).on('paste', '#id_aztec', function (e) {
        var code = e.originalEvent.clipboardData.getData('Text');
        if (code.length > 350) {
            debounce(function () {
                decode_aztec(code);
            }, 300)
        }
    })
});
