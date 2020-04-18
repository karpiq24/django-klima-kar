function isInt(value) {
    return !isNaN(value) && parseInt(Number(value), 10) == value && !isNaN(parseInt(value, 10));
}

function toCurrency(value) {
    return parseFloat(parseFloat(value).toFixed(2));
}

function customSuccessCreate(data, identifier) {
    let $option = $("<option selected></option>").val(data["pk"]).text(data["text"]);
    if (identifier == "1") {
        $("#id_contractor").append($option).trigger("change");
        $("#contractor-edit").prop("disabled", false);
    } else if (identifier == "2") {
        $("#id_vehicle").append($option).trigger("change");
        $("#vehicle-component-edit").prop("disabled", false);
        $("#id_vc_name").val(data["text"]);
    } else if (identifier == "3") {
        $("#id_component").append($option).trigger("change");
        $("#vehicle-component-edit").prop("disabled", false);
        $("#id_vc_name").val(data["text"]);
    }
}

function calculateInvoiceTotals() {
    let invoice_total = 0.0;
    $(".item-formset-row")
        .not(".readonly")
        .each(function () {
            if (!$(this).hasClass("d-none")) {
                let price = toCurrency($(this).find(".item-price").val().replace(",", "."));
                if (isNaN(price)) {
                    price = 0;
                }
                const quantity = parseInt($(this).find(".item-quantity").val());
                const total_row = toCurrency(quantity * price);
                invoice_total = toCurrency(invoice_total + total_row);
            }
        });
    if (isNaN(invoice_total)) {
        invoice_total = 0;
    }
    $("#invoice-total").text(invoice_total.toFixed(2).replace(".", ",") + " zł");
}

function checkEndDate() {
    if (
        $("input[type=radio][name=status]:checked").val() === "DO" ||
        $("input[type=radio][name=status]:checked").val() === "CA"
    ) {
        $("#id_end_date").prop("disabled", false);
        if ($("#id_end_date").val() === "") {
            $("#id_end_date").val(moment().format("DD.MM.YYYY"));
        }
    } else {
        $("#id_end_date").prop("disabled", true);
        $("#id_end_date").val("");
    }
}

$(function () {
    let debounce = (function () {
        let timer = 0;
        return function (callback, ms) {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    $(".sidenav #nav-commissions").children(":first").addClass("active");
    $(".sidenav #nav-commission").collapse("show");

    const CREATE_CONTRACTOR = $("#create_contractor_url").val();
    const UPDATE_CONTRACTOR = $("#update_contractor_url").val();
    const GET_SERVICE_DATA = $("#service_detail_url").val();
    const CREATE_VEHICLE = $("#create_vehicle_url").val();
    const UPDATE_VEHICLE = $("#update_vehicle_url").val();
    const CREATE_COMPONENT = $("#create_component_url").val();
    const UPDATE_COMPONENT = $("#update_component_url").val();
    const GET_CONTRACTOR_DATA = $("#get_contractor_data_url").val();

    $("#id_contractor").on("select2:selecting", function (e) {
        const data = e.params.args.data;

        if (data.create_id !== true) {
            $("#contractor-edit").prop("disabled", false);
            return;
        }
        $("#contractor-edit").prop("disabled", true);

        e.preventDefault();
        let initial = {};
        const input = data.id.replace(/ /g, "");
        if (isInt(input)) {
            if (input.length === 9) {
                initial = { phone_1: input };
            } else {
                initial = { nip: input };
            }
        } else {
            initial = { name: data.id };
        }
        $.ajax({
            url: CREATE_CONTRACTOR,
            type: "get",
            dataType: "json",
            data: initial,
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            },
        });
    });

    $("#id_contractor").change(function () {
        const parent = $("#id_contractor").parent();
        const contractor_pk = $("#id_contractor").val();
        $("#id_contractor").removeClass("is-invalid");
        $("#id_contractor").removeClass("is-warning");
        $(parent).find("div.invalid-feedback").remove();
        $(parent).find("div.warning-feedback").remove();
        $.ajax({
            url: GET_CONTRACTOR_DATA,
            data: {
                pk: contractor_pk,
            },
            dataType: "json",
            success: function (result) {
                if (result.contractor.id === "") {
                    $("#contractor-edit").prop("disabled", true);
                    $("#gus-data").hide();
                    return;
                }

                if (result.contractor.nip) {
                    $("#gus-data").data("nip", result.contractor.nip);
                    $("#gus-data").show();
                } else {
                    $("#gus-data").hide();
                }
                if (result.contractor.phone == null) {
                    $("#id_contractor").addClass("is-invalid");
                    $(parent).append(
                        '<div class="invalid-feedback">Wybrany kontrahent nie ma podanego numeru telefonu.</div>'
                    );
                } else if (result.contractor.phone.length !== 9) {
                    $("#id_contractor").addClass("is-warning");
                    $(parent).append(
                        '<div class="warning-feedback">Sprawdź numer telefonu - podany posiada niestandardową liczbę cyfr.</div>'
                    );
                }
            },
        });
    });

    $("#contractor-edit").click(function () {
        const contractor_pk = $("#id_contractor").val();
        const url = UPDATE_CONTRACTOR.replace("0", contractor_pk);
        $.ajax({
            url: url,
            type: "get",
            dataType: "json",
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            },
        });
    });

    if ($("#id_contractor").val() === "") {
        $("#contractor-edit").prop("disabled", true);
    } else {
        $("#contractor-edit").prop("disabled", false);
    }

    if ($("#id_component").length && $("#id_component").val() === "") {
        $("#id_vc_name").prop("readonly", false);
    } else if ($("#id_component").length) {
        $("#id_vc_name").prop("readonly", true);
    } else if ($("#id_vehicle").length && $("#id_vehicle").val() === "") {
        $("#id_vc_name").prop("readonly", false);
    } else if ($("#id_vehicle").length) {
        $("#id_vc_name").prop("readonly", true);
    }

    $("#id_vehicle").on("select2:selecting", function (e) {
        const data = e.params.args.data;

        if (data.create_id !== true) {
            $("#vehicle-component-edit").prop("disabled", false);
            $("#id_vc_name").val(data["text"]);
            return;
        }
        $("#vehicle-component-edit").prop("disabled", true);

        e.preventDefault();
        $.ajax({
            url: CREATE_VEHICLE,
            type: "get",
            data: { registration_plate: data.id.replace(/ /g, "") },
            dataType: "json",
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            },
        });
    });

    $("#id_vehicle").change(function () {
        const vehicle_pk = $("#id_vehicle").val();
        if (!isInt(vehicle_pk)) {
            $("#id_vc_name").val("");
            $("#vehicle-component-edit").prop("disabled", true);
            $("#id_vc_name").prop("readonly", false);
        } else {
            getVehicleData(vehicle_pk);
            $("#id_vc_name").prop("readonly", true);
        }
    });

    $(document).on("click", ".scan-vehicle", function (e) {
        $("#id_vehicle").select2("close");
        Swal.fire({
            title: "Zeskanuj dowód rejestracyjny.",
            html: `<input id="swal-code" class="swal2-input" style="display: flex;" placeholder="" type="text">`,
            showCancelButton: false,
            showConfirmButton: false,
        });
    });

    $(document).on("keyup paste", "#swal-code", function () {
        processVehicleCode($(this).val());
    });

    function getVehicleData(pk) {
        $.ajax({
            url: "/graphql/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                query: `query {
                    vehicles(filters: {id: "${pk}"}) {
                        objects {
                            get_absolute_url
                            last_commission {
                                get_absolute_url
                                start_date
                                contractor {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }`,
            }),
            success: function ({ data }) {
                const parent = $("#id_vehicle").parent().parent().parent().parent();
                $(parent).find("div.extra-feedback").remove();
                $(parent).append(`<div class="extra-feedback d-flex justify-content-between flex-wrap"></div>`);
                const feedback = $(parent).find("div.extra-feedback");
                const vehicle = data.vehicles.objects[0];
                const contractor = vehicle.last_commission.contractor;
                if (contractor && contractor.id !== $("#id_contractor").val()) {
                    Swal.fire({
                        title: "Ustawić kontrahenta?",
                        text: contractor.name,
                        type: "question",
                        showCancelButton: true,
                        focusCancel: false,
                        focusConfirm: true,
                        confirmButtonText: "Tak",
                        cancelButtonText: "Nie",
                    }).then((change) => {
                        if (change.value) {
                            const $option = $("<option selected></option>").val(contractor.id).text(contractor.name);
                            $("#id_contractor").append($option).trigger("change");
                            $("#contractor-edit").prop("disabled", false);
                        }
                    });
                }
                $(feedback).append(
                    `<small class="vehicle-details"><a href="${vehicle.get_absolute_url}" target="_blank">Szczegóły pojazdu</a></small>`
                );
                if (vehicle.last_commission.start_date) {
                    $(feedback).append(
                        `<small class="last-visit"><a href="${vehicle.last_commission.get_absolute_url}" target="_blank">Ostatnia wizyta: ${vehicle.last_commission.start_date}</a></small>`
                    );
                }
            },
            error: function (data) {
                genericErrorAlert();
            },
        });
    }

    function getComponentData(pk) {
        $.ajax({
            url: "/graphql/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                query: `query {
                    components(filters: {id: "${pk}"}) {
                        objects {
                            get_absolute_url
                            last_commission {
                                get_absolute_url
                                start_date
                                contractor {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }`,
            }),
            success: function ({ data }) {
                const parent = $("#id_component").parent().parent().parent().parent();
                $(parent).find("div.extra-feedback").remove();
                $(parent).append(`<div class="extra-feedback d-flex justify-content-between flex-wrap"></div>`);
                const feedback = $(parent).find("div.extra-feedback");
                const component = data.components.objects[0];
                const contractor = component.last_commission.contractor;
                if (contractor && contractor.id !== $("#id_contractor").val()) {
                    Swal.fire({
                        title: "Ustawić kontrahenta?",
                        text: contractor.name,
                        type: "question",
                        showCancelButton: true,
                        focusCancel: false,
                        focusConfirm: true,
                        confirmButtonText: "Tak",
                        cancelButtonText: "Nie",
                    }).then((change) => {
                        if (change.value) {
                            const $option = $("<option selected></option>").val(contractor.id).text(contractor.name);
                            $("#id_contractor").append($option).trigger("change");
                            $("#contractor-edit").prop("disabled", false);
                        }
                    });
                }
                $(feedback).append(
                    `<small class="component-details"><a href="${component.get_absolute_url}" target="_blank">Szczegóły podzespołu</a></small>`
                );
                if (component.last_commission.start_date) {
                    $(feedback).append(
                        `<small class="last-visit"><a href="${component.last_commission.get_absolute_url}" target="_blank">Ostatnia wizyta: ${component.last_commission.start_date}</a></small>`
                    );
                }
            },
            error: function (data) {
                genericErrorAlert();
            },
        });
    }

    $("#id_component").on("select2:selecting", function (e) {
        const data = e.params.args.data;

        if (data.create_id !== true) {
            $("#vehicle-component-edit").prop("disabled", false);
            $("#id_vc_name").val(data["text"]);
            return;
        }
        $("#vehicle-component-edit").prop("disabled", true);

        e.preventDefault();
        $.ajax({
            url: CREATE_COMPONENT,
            type: "get",
            data: { model: data.id },
            dataType: "json",
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            },
        });
    });

    $("#id_component").change(function () {
        const component_pk = $("#id_component").val();
        if (!isInt(component_pk)) {
            $("#id_vc_name").val("");
            $("#vehicle-component-edit").prop("disabled", true);
            $("#id_vc_name").prop("readonly", false);
        } else {
            getComponentData(component_pk);
            $("#id_vc_name").prop("readonly", true);
        }
    });

    $("#vehicle-component-edit").click(function () {
        let pk = null;
        let url = null;
        if ($("#id_commission_type").val() === "VH") {
            pk = $("#id_vehicle").val();
            url = UPDATE_VEHICLE.replace("0", pk);
        } else {
            pk = $("#id_component").val();
            url = UPDATE_COMPONENT.replace("0", pk);
        }
        $.ajax({
            url: url,
            type: "get",
            dataType: "json",
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            },
        });
    });

    $("#vehicle-component-edit").prop("disabled", false);
    if ($("#id_commission_type").val() === "VH" && $("#id_vehicle").val() === "") {
        $("#vehicle-component-edit").prop("disabled", true);
    } else if ($("#id_commission_type").val() === "CO" && $("#id_component").val() === "") {
        $("#vehicle-component-edit").prop("disabled", true);
    }

    $("#add_item_formset").click(function () {
        let item_form = $("#item-rows").children(".d-none").first();
        $(item_form).find(".item-DELETE").children("input").prop("checked", false);
        $(item_form).removeClass("d-none");
        $(item_form).insertAfter($("#item-rows tr:not('.d-none'):last"));
        $(item_form).find(".form-control").first().focus();
    });

    $(".remove_item_formset").click(function () {
        let item_form = $(this).parents(".item-formset-row");
        $(item_form).addClass("d-none");
        $(item_form).find(".item-name").val("");
        $(item_form).find(".item-description").val("");
        $(item_form).find(".item-quantity").val(1);
        $(item_form).find(".item-price").val("");
        $(item_form).find(".item-DELETE").children("input").prop("checked", true);
        calculateInvoiceTotals();
    });

    $(".item-price").change(function () {
        let item_form = $(this).parents(".item-formset-row");
        const price = toCurrency($(item_form).find(".item-price").val().replace(",", "."));
        const quantity = parseInt($(item_form).find(".item-quantity").val());
        const total = toCurrency(price * quantity);
        $(item_form)
            .find(".item-total")
            .text(total.toFixed(2).replace(".", ",") + " zł");
        calculateInvoiceTotals();
    });

    $(".item-quantity").change(function () {
        let item_form = $(this).parents(".item-formset-row");
        const price = toCurrency($(item_form).find(".item-price").val());
        const quantity = parseInt($(item_form).find(".item-quantity").val());
        const total = toCurrency(price * quantity);
        $(item_form)
            .find(".item-total")
            .text(total.toFixed(2).replace(".", ",") + " zł");
        calculateInvoiceTotals();
    });

    $(".choose_service").click(function () {
        let item_form = $(this).parents(".item-formset-row");
        const service_pk = $(item_form).find(".item-service").val();
        if (service_pk === "") {
            return;
        }
        $.ajax({
            url: GET_SERVICE_DATA,
            data: {
                pk: service_pk,
            },
            dataType: "json",
            success: function (result) {
                $(item_form).find(".item-name").val(result.service.name);
                $(item_form).find(".item-description").val(result.service.description);
                $(item_form).find(".item-price").val(result.service.price_brutto);
                $(item_form).find(".item-quantity").val(result.service.quantity);
                $(item_form).find(".item-price").change();
            },
        });
    });

    $("#item-rows tr:first").removeClass("d-none");
    $(".item-formset-row").each(function () {
        let item_form = $(this);
        if (
            $(item_form).find(".item-name").val() ||
            $(item_form).find(".item-description").val() ||
            $(item_form).find(".item-price").val() != 0 ||
            $(item_form).find(".item-quantity").val() != 1 ||
            $(item_form).find(".invalid-feedback").length > 0
        ) {
            item_form.removeClass("d-none");
            $(item_form).find(".item-price").change();
        }
    });
    calculateInvoiceTotals();

    $("#id_vehicle").on("select2:opening", function (e) {
        $(this).data("select2").$dropdown.find(":input.select2-search__field").addClass("vehicle");
    });

    function processVehicleData(data) {
        $("#id_vehicle").select2("close");
        if (data.pk === null) {
            $.ajax({
                url: CREATE_VEHICLE,
                type: "get",
                dataType: "json",
                data: data,
                beforeSend: function () {
                    $("#modal-generic").modal("show");
                },
                success: function (data) {
                    $("#modal-generic .modal-content").html(data.html_form);
                },
            });
        } else {
            const $option = $("<option selected></option>").val(data["pk"]).text(data["label"]);
            $("#id_vehicle").append($option).trigger("change");
            $("#vehicle-component-edit").prop("disabled", false);
            $("#id_vc_name").val(data["label"]);
        }
    }

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

    $("input[type=radio][name=status]").change(function () {
        checkEndDate();
    });
    checkEndDate();

    if ($("#id_contractor").val() !== "") {
        $("#id_contractor").change();
    }
    if ($("#id_vehicle").val() !== "") {
        $("#id_vehicle").change();
    }
    if ($("#id_component").val() !== "") {
        $("#id_component").change();
    }
    $("#vehicle-select .select2-selection").append($("#scan-icon-template").html());
    bsCustomFileInput.init();
});
