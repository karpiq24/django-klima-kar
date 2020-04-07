$(function () {
    $(".sidenav #nav-vehicles").children(":first").addClass("active");
    $(".sidenav #nav-commission").collapse("show");

    const DECODE_AZTEC = $("#decode_aztec_url").val();
    const DECODE_CSV_VEHICLE = $("#decode_csv_vehicle_url").val();

    function decode_aztec(code) {
        $.ajax({
            url: DECODE_AZTEC,
            type: "post",
            dataType: "json",
            data: {
                code: code,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                processVehicleData(data);
            },
            error: function (data) {
                addAlert("Błąd!", "error", "Coś poszło nie tak. Spróbuj ponownie.");
            },
        });
    }

    function decode_csv(code) {
        $.ajax({
            url: DECODE_CSV_VEHICLE,
            type: "post",
            dataType: "json",
            data: {
                code: code,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                processVehicleData(data);
            },
            error: function (data) {
                addAlert("Błąd!", "error", "Coś poszło nie tak. Spróbuj ponownie.");
            },
        });
    }

    function processVehicleData(data) {
        $("#id_brand").val(data.brand);
        $("#id_engine_power").val(data.engine_power);
        $("#id_engine_volume").val(data.engine_volume);
        $("#id_model").val(data.model);
        $("#id_production_year").val(data.production_year);
        $("#id_registration_plate").val(data.registration_plate);
        $("#id_vin").val(data.vin);
        $("#id_fuel_type").val(data.fuel_type);
        $("#id_registration_date").val(data.registration_date);
        $("#id_aztec").val("");
    }

    let debounce = (function () {
        let timer = 0;
        return function (callback, ms) {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    function processCode(code) {
        if (code.length > 50 && code.length <= 350) {
            debounce(function () {
                decode_csv(code);
            }, 300);
        } else if (code.length > 350) {
            debounce(function () {
                decode_aztec(code);
            }, 300);
        }
    }

    $(document).on("input", "#id_aztec", function (e) {
        processCode($(this).val());
    });

    $(document).on("paste", "#id_aztec", function (e) {
        processCode(e.originalEvent.clipboardData.getData("Text"));
    });
});
