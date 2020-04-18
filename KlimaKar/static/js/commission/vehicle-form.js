$(function () {
    $(".sidenav #nav-vehicles").children(":first").addClass("active");
    $(".sidenav #nav-commission").collapse("show");

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

    function processVehicleCode(code) {
        debounce(function () {
            Swal.close();
            $.ajax({
                url: "/graphql/",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    query: `query {
                        decode(code: "${code}") {
                            pk
                            label
                            registration_plate
                            vin
                            brand
                            model
                            engine_volume
                            engine_power
                            production_year
                            registration_date
                            fuel_type
                        }
                    }`,
                }),
                success: function ({ data }) {
                    if (data.decode === null) genericErrorAlert();
                    else processVehicleData(data.decode);
                },
                error: function (data) {
                    genericErrorAlert();
                },
            });
        }, 300);
    }

    $(document).on("input", "#id_aztec", function (e) {
        processVehicleCode($(this).val());
    });

    $(document).on("paste", "#id_aztec", function (e) {
        processVehicleCode(e.originalEvent.clipboardData.getData("Text"));
    });
});
