function isInt(value) {
    return !isNaN(value) && parseInt(Number(value), 10) == value && !isNaN(parseInt(value, 10));
}

function toCurrency(value) {
    return parseFloat(parseFloat(value).toFixed(2));
}

function customSuccessCreate(data, identifier) {
    if (identifier == "1") {
        var $option = $("<option selected></option>").val(data["pk"]).text(data["text"]);
        $("#id_contractor").append($option).trigger("change");
        $("#contractor-edit").prop("disabled", false);
        $("#id_contractor_modified").val(true);
    }
}

function calculateInvoiceTotals() {
    var invoice_total_netto = 0.0;
    var tax_multiplier = $("#id_tax_percent").val() / 100;
    $(".item-formset-row")
        .not(".readonly")
        .each(function () {
            if (!$(this).hasClass("d-none")) {
                var price_netto = toCurrency($(this).find(".item-netto").val().replace(",", "."));
                if (isNaN(price_netto)) {
                    price_netto = 0;
                }
                var quantity = parseFloat($(this).find(".item-quantity").val().replace(",", "."));
                var total_netto = toCurrency(quantity * price_netto);
                invoice_total_netto = toCurrency(invoice_total_netto + total_netto);
            }
        });
    if (isNaN(invoice_total_netto)) {
        invoice_total_netto = 0;
    }
    var invoice_total_brutto = toCurrency(invoice_total_netto + invoice_total_netto * tax_multiplier);
    $("#invoice-total-netto").text(invoice_total_netto.toFixed(2).replace(".", ",") + " zł");
    $("#invoice-total-brutto").text(invoice_total_brutto.toFixed(2).replace(".", ",") + " zł");
}

$(function () {
    $(".sidenav #nav-saleinvoices").children(":first").addClass("active");
    $(".sidenav #nav-invoicing").collapse("show");

    $("#id_contractor").on("select2:selecting", function (e) {
        const data = e.params.args.data;

        if (data.create_id !== true) {
            $("#contractor-edit").prop("disabled", false);
            $("#id_contractor_modified").val(true);
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
        $("#id_contractor").removeClass("is-valid");
        $("#id_contractor").removeClass("is-warning");
        $("#id_contractor").removeClass("is-invalid");
        $(parent).find("div.valid-feedback").remove();
        $(parent).find("div.invalid-feedback").remove();
        $(parent).find("div.warning-feedback").remove();
        $(parent).append(
            '<small id="loding-contractor" class="form-text text-muted"><i class="fas fa-spinner fa-spin"></i> Sprawdzam kontrahenta..</small>'
        );
        console.log(contractor_pk)
        if (contractor_pk) {
            $(".contractor-notes").data("pk", contractor_pk);
            $(".contractor-notes").parent().show();
            $.ajax({
                url: "/graphql/",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    query: `query {
                    contractors(filters: {id: "${contractor_pk}"}) {
                        objects {
                            nip
                            nip_prefix
                            phone_1
                            phone_2
                            vatStatus {
                                status
                                url
                            }
                        }
                    }
                }`,
                }),
                success: function ({ data }) {
                    const contractor = data.contractors.objects[0];
                    $(parent).find("#loding-contractor").remove();
                    if (contractor.nip) {
                        $("#gus-data").data("nip", contractor.nip);
                        $("#gus-data").show();
                    } else {
                        $("#gus-data").hide();
                    }
                    if (contractor.vatStatus === null) {
                        $("#id_contractor").addClass("is-warning");
                        $(parent).append(
                            '<div class="warning-feedback vat-failed">Nie udało się sprawdzić statusu płatnika VAT. Sprawdź ręcznie.</div>'
                        );
                    } else if (contractor.vatStatus.status === false) {
                        $("#id_contractor").addClass("is-warning");
                        $(parent).append(
                            '<div class="warning-feedback vat-invalid">Wybrany kontrahent nie jest płatnikiem VAT. <a href="' +
                                contractor.vatStatus.url +
                                '" target="_blank">(sprawdź tutaj)</a></div>'
                        );
                    } else {
                        $("#id_contractor").addClass("is-valid");
                        $(parent).append('<div class="valid-feedback">Kontrahent jest płatnikiem VAT</div>');
                    }

                    if (INVOICE_TYPE === "4" || INVOICE_TYPE === "5") {
                        if (contractor.nip_prefix == null) {
                            $("#id_contractor").addClass("is-invalid");
                            $("#id_contractor").removeClass("is-valid");
                            $(parent).append(
                                '<div class="invalid-feedback no-prefix">Wybrany kontrahent nie ma podanego prefiksu NIP.</div>'
                            );
                        }
                    }
                },
                error: function (data) {
                    addAlert("Błąd!", "error", "Coś poszło nie tak. Spróbuj ponownie.");
                },
            });
        } else {
            $(".contractor-notes").parent().hide();
        }
    });

    $("#add_item_formset").click(function () {
        var item_form = $("#item-rows").children(".d-none").first();
        $(item_form).find(".item-DELETE").children("input").prop("checked", false);
        $(item_form).removeClass("d-none");
        $(item_form).insertAfter($("#item-rows tr:not('.d-none'):last"));
        $(item_form).find(".form-control").first().focus();
    });

    $(".remove_item_formset").click(function () {
        var item_form = $(this).parents(".item-formset-row");
        $(item_form).addClass("d-none");
        $(item_form).find(".item-name").val("");
        $(item_form).find(".item-description").val("");
        $(item_form).find(".item-ware").val("").change();
        $(item_form).find(".item-quantity").val(1);
        $(item_form).find(".item-netto").val("");
        $(item_form).find(".item-brutto").val("");
        $(item_form).find(".item-DELETE").children("input").prop("checked", true);
        calculateInvoiceTotals();
    });

    $(".item-netto").change(function () {
        var item_form = $(this).parents(".item-formset-row");
        $(item_form).find(".item-brutto").removeClass("is-invalid");
        var tax_multiplier = parseFloat($("#id_tax_percent").val()) / 100;
        var price_netto = toCurrency($(item_form).find(".item-netto").val().replace(",", "."));
        var price_brutto = toCurrency(price_netto + price_netto * tax_multiplier);
        var quantity = parseFloat($(item_form).find(".item-quantity").val().replace(",", "."));
        var total_netto = toCurrency(price_netto * quantity);
        $(item_form).find(".item-brutto").val(String(price_brutto).replace(".", ","));
        $(item_form)
            .find(".item-total-netto")
            .text(total_netto.toFixed(2).replace(".", ",") + " zł");
        calculateInvoiceTotals();
    });

    $(".item-brutto").change(function () {
        var item_form = $(this).parents(".item-formset-row");
        var tax_multiplier = parseFloat($("#id_tax_percent").val()) / 100;
        var price_brutto = toCurrency($(item_form).find(".item-brutto").val().replace(",", "."));
        var price_netto = toCurrency(price_brutto / (1 + tax_multiplier));
        var quantity = parseFloat($(item_form).find(".item-quantity").val().replace(",", "."));
        var total_netto = toCurrency(price_netto * quantity);
        $(item_form).find(".item-netto").val(String(price_netto).replace(".", ","));
        $(item_form)
            .find(".item-total-netto")
            .text(total_netto.toFixed(2).replace(".", ",") + " zł");

        var price_brutto_check = toCurrency(price_netto + price_netto * tax_multiplier);
        if (price_brutto != price_brutto_check) {
            $(item_form).find(".item-brutto").addClass("is-invalid");
        } else {
            $(item_form).find(".item-brutto").removeClass("is-invalid");
        }

        calculateInvoiceTotals();
    });

    $(".item-quantity").change(function () {
        var item_form = $(this).parents(".item-formset-row");
        var price_netto = toCurrency($(item_form).find(".item-netto").val().replace(",", "."));
        var quantity = parseFloat($(item_form).find(".item-quantity").val().replace(",", "."));
        var total_netto = toCurrency(price_netto * quantity);
        $(item_form)
            .find(".item-total-netto")
            .text(total_netto.toFixed(2).replace(".", ",") + " zł");
        calculateInvoiceTotals();
    });

    $("#id_tax_percent").change(function () {
        var tax_multiplier = parseFloat($(this).val()) / 100;
        $(".item-formset-row").each(function () {
            $(this).find(".item-brutto").removeClass("is-invalid");
            if (!$(this).hasClass("d-none")) {
                var price_netto = toCurrency($(this).find(".item-netto").val());
                var price_brutto = toCurrency(price_netto + price_netto * tax_multiplier);
                $(this).find(".item-brutto").val(price_brutto.toFixed(2));
            }
        });
        calculateInvoiceTotals();
    });

    $("#id_payed").change(function () {
        if ($("#id_payed").is(":checked")) {
            $("#id_payment_date").prop("hidden", true);
            $("#id_payment_date").val(null);
        } else {
            $("#id_payment_date").prop("hidden", false);
            $("#id_payment_date").focus();
        }
    });

    $("#id_payment_type").change(function (event, focus = true) {
        if ($("input[type=radio][name=payment_type]:checked").val() === "4") {
            $("#id_payment_type_other").parent().show();
            if (focus) {
                setTimeout(function () {
                    $("#id_payment_type_other").focus();
                }, 10);
            }
        } else {
            $("#id_payment_type_other").parent().hide();
            $("#id_payment_type_other").val("");
        }
    });

    $(".service-button").on("click", function () {
        const pk = $(this).data("pk");
        $.ajax({
            url: "/graphql/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                query: `query {
                    services(filters: {id: "${pk}"}) {
                        objects {
                            name
                            description
                            ware {
                                id
                                index
                            }
                            quantity
                            price_brutto
                            price_netto
                            is_ware_service
                            is_group
                            is_ware_service
                            ware_filter
                        }
                    }
                }`,
            }),
            success: function ({ data }) {
                const service = data.services.objects[0];
                if (service.is_group) {
                    $(".modal").modal("hide");
                    $(`#serviceModal_${pk}`).modal("show");
                } else if (service.is_ware_service) {
                    localStorage.setItem("service", JSON.stringify(service));
                    $("#id_service_ware-name").val(service.ware_filter);
                    $("#wareFilterModal .modal-title").text(service.name);
                    $("#wareFilterModal").modal("show");
                    setTimeout(function () {
                        $("#id_service_ware-ware").select2("open");
                    }, 400);
                }else {
                    const item_form = $(".item-formset-row.d-none").first();
                    $(".modal").modal("hide");
                    $(item_form).find(".item-name").val(service.name);
                    $(item_form).find(".item-description").val(service.description);
                    if (service.ware) {
                        let $option = $("<option selected></option>").val(service.ware.id).text(service.ware.index);
                        let $sel2 = $(item_form).find("select.item-ware");
                        $sel2.append($option).trigger("change");
                    }
                    $(item_form).find(".item-netto").val(service.price_netto);
                    $(item_form).find(".item-brutto").val(service.price_brutto);
                    $(item_form).find(".item-quantity").val(service.quantity);
                    $(item_form).find(".item-DELETE").children("input").prop("checked", false);
                    $(item_form).removeClass("d-none");
                    if (service.price_brutto) {
                        $(item_form).find(".item-brutto").change();
                    } else {
                        $(item_form).find(".item-netto").change();
                    }
                    $(item_form).insertAfter($("#item-rows tr:not('.d-none'):last"));
                }
            },
            error: function (data) {
                addAlert("Błąd!", "error", "Coś poszło nie tak. Spróbuj ponownie.");
            },
        });
    });

    $("#id_service_ware-ware").on("select2:selecting", function (e) {
        if (localStorage.getItem("service") === null) {
            genericErrorAlert();
            return;
        }
        const data = e.params.args.data;
        const service = JSON.parse(localStorage.getItem("service"));

        $("#wareFilterModal").modal("hide");
        setTimeout(function () {
            $("#id_service_ware-ware").empty();
        }, 500);

        const item_form = $(".item-formset-row.d-none").first();
        $(item_form).find(".item-name").val(service.name);
        $(item_form).find(".item-description").val(service.description);

        let $option = $("<option selected></option>").val(data.id).text(data.text);
        let $sel2 = $(item_form).find("select.item-ware");
        $sel2.append($option).trigger("change");

        $(item_form).find(".item-brutto").val(data.retail);
        $(item_form)
            .find(".item-quantity")
            .val(service.quantity || 1);
        $(item_form).find(".item-DELETE").children("input").prop("checked", false);
        $(item_form).removeClass("d-none");
        $(item_form).find(".item-brutto").change();
        $(item_form).insertAfter($("#item-rows tr:not('.d-none'):last"));
    });

    $("#contractor-edit").click(function () {
        var contractor_pk = $("#id_contractor").val();
        var url = UPDATE_CONTRACTOR.replace("0", contractor_pk);
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

    if ($("#id_contractor").val() != "") {
        $("#contractor-edit").prop("disabled", false);
    }

    $("#item-rows tr:first").removeClass("d-none");
    $(".item-formset-row").each(function () {
        var item_form = $(this);
        if (
            $(item_form).find(".item-name").val() ||
            $(item_form).find(".item-description").val() ||
            $(item_form).find(".item-ware").val() ||
            $(item_form).find(".item-netto").val() != 0 ||
            $(item_form).find(".item-brutto").val() != 0 ||
            $(item_form).find(".item-quantity").val() != 1 ||
            $(item_form).find(".invalid-feedback").length > 0
        ) {
            item_form.removeClass("d-none");
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has("value_type") && urlParams.get("value_type") === "netto") {
                $(item_form).find(".item-netto").change();
            } else {
                $(item_form).find(".item-brutto").change();
            }
        }
    });

    $("#generate_pdf").on("click", function () {
        $("#id_generate_pdf").val(true);
    });

    if ($("#id_contractor").val() !== "") {
        $("#id_contractor").change();
    }
    $("#id_payment_type").trigger("change", false);
    calculateInvoiceTotals();
});
