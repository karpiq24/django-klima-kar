function isInt(value) {
    return !isNaN(value) && parseInt(Number(value), 10) == value && !isNaN(parseInt(value, 10));
}

function submitInvoiceForm(url, commission_pk) {
    var data = $("#invoice_form").serialize() + "&pk=" + commission_pk;
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function (data) {
            window.location.href = data.url;
        },
        error: function (data) {
            addAlert("Błąd!", "error", "Skontaktuj się z administratorem.");
        },
    });
}

function submitEmailForm(url) {
    var data = $("#email_form").serialize();
    var spinner = document.createElement("i");
    spinner.className = "fas fa-spinner fa-spin fa-8x";
    spinner.style = "margin-bottom: 26px;color: #00a0df;";
    $("#email_modal").modal("hide");
    Swal.fire({
        title: "Wysyłanie wiadomości email",
        html: '<i class="fas fa-spinner fa-spin fa-8x" style="margin: 26px;color: #00a0df;"></i>',
        showConfirmButton: false,
    });
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function (data) {
            $("#email_modal").modal("hide");
            addAlert("Sukces!", "success", data.message + ".");
        },
        error: function (data) {
            addAlert("Błąd!", "error", data.responseJSON.message + ".");
            $("#email_modal").modal("show");
        },
    });
}

function printJSSupported() {
    if (typeof InstallTrigger !== "undefined") {
        return false;
    }
    if (navigator.userAgent.indexOf("MSIE") !== -1 || !!document.documentMode) {
        return false;
    }
    if (!!window.StyleMedia) {
        return false;
    }
    return true;
}

function print_pdf() {
    Swal.fire({
        title: "Umieścić opis zlecenia na wydruku?",
        type: "question",
        showCancelButton: true,
        focusCancel: false,
        focusConfirm: true,
        confirmButtonText: "Tak",
        cancelButtonText: "Nie",
    }).then(({ value }) => {
        let url = $("#print-btn").data("url");
        if (value) {
            url = `${url}?include_description=True`;
        } else {
            url = `${url}?include_description=False`;
        }
        if (printJSSupported()) {
            printJS({ printable: url, type: "pdf", showModal: true, modalMessage: "Przygotowywanie zlecenia..." });
        } else {
            const w = window.open(url);
            w.print();
        }
    });
}

function sendSmsNotification() {
    if ($("#status-select").data("sent") === "True") return;
    const phone1 = $("#status-select").data("phone1");
    const phone2 = $("#status-select").data("phone2");
    let options = {};
    if (phone2 !== undefined && phone2 !== "None") {
        options[phone2] = phone2;
    }
    if (phone1 !== undefined && phone1 !== "None") {
        options[phone1] = phone1;
    }
    if (!$.isEmptyObject(options)) {
        Swal.fire({
            title: "Czy chcesz wysłać powiadomienie SMS do klienta?",
            text: $("#sms").val(),
            type: "question",
            input: "radio",
            inputOptions: options,
            inputValue: phone1 !== undefined && phone1 !== "None" ? phone1 : phone2,
            inputValidator: (value) => {
                if (!value) {
                    return "Wybierz numer telefonu.";
                }
            },
            showCancelButton: true,
            focusCancel: false,
            focusConfirm: true,
            confirmButtonText: "Tak",
            cancelButtonText: "Nie",
        }).then((send_sms) => {
            if (send_sms.value) {
                $.ajax({
                    url: "/graphql/",
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify({
                        query: `mutation {
                            sendCommissionNotification(pk: "${$("#status-select input").data("pk")}", phone: "${
                            send_sms.value
                        }") {
                                status
                                message
                            }
                        }`,
                    }),
                    success: function ({ data }) {
                        addAlert(
                            data.sendCommissionNotification.status ? "Sukces!" : "Błąd!",
                            data.sendCommissionNotification.status ? "success" : "error",
                            data.sendCommissionNotification.message
                        );
                        $("#sendSmsBtn").addClass("d-none");
                        $("#status-select").data("sent", "True");
                        $("#smsSentAlert").removeClass("d-none").addClass("d-flex");
                    },
                    error: function () {
                        genericErrorAlert();
                    },
                });
            }
        });
    }
}

function checkFileUpload() {
    let check = setInterval(function () {
        $.ajax({
            url: $("#file-data").data("check-url"),
            type: "get",
            data: {
                pk: $("#file-data").data("commission"),
            },
            dataType: "json",
            success: function (data) {
                if (data.status == "success") {
                    $("#file-data").empty();
                    $("#uploadAlert").addClass("hidden");
                    let fileList = $("#file-data").append($('<ul class="simple-list"></ul>')).find("ul");
                    $.each(data.files, function (i, file) {
                        var li = $(
                            '<li><a href="' +
                                file.url +
                                '" target="_blank">' +
                                file.name +
                                " - " +
                                file.size +
                                "</a></li>"
                        ).appendTo(fileList);
                    });
                    clearInterval(check);
                }
            },
        });
    }, 2000);
}

$(function () {
    $(".sidenav #nav-commissions").children(":first").addClass("active");
    $(".sidenav #nav-commission").collapse("show");

    var url = window.location.href;
    if (url.indexOf("?pdf") != -1) print_pdf();
    else if (url.indexOf("&pdf") != -1) print_pdf();

    $("#print-btn").click(function () {
        print_pdf();
    });

    $("#pdf-btn").click(function () {
        Swal.fire({
            title: "Umieścić opis zlecenia w pliku PDF?",
            type: "question",
            showCancelButton: true,
            focusCancel: false,
            focusConfirm: true,
            confirmButtonText: "Tak",
            cancelButtonText: "Nie",
        }).then(({ value }) => {
            let url = $("#pdf-btn").data("url");
            if (value) {
                url = `${url}?include_description=True`;
            } else {
                url = `${url}?include_description=False`;
            }
            window.location.href = url;
        });
    });

    var last_status = $("#status-select input:checked");

    $("#status-select input").on("change", function () {
        const that = this;
        Swal.fire({
            title: "Czy na pewno chcesz zmienić status?",
            type: "question",
            showCancelButton: true,
            focusCancel: false,
            focusConfirm: true,
            confirmButtonText: "Tak",
            cancelButtonText: "Nie",
        }).then((change) => {
            if (change.value) {
                const status = $(this).data("value");
                last_status = that;
                $.ajax({
                    url: $("#status-select").data("url"),
                    type: "post",
                    dataType: "json",
                    data: {
                        status: status,
                        pk: $(this).data("pk"),
                        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
                    },
                    success: function (data) {
                        $("#end_date").text(data.end_date);
                        if (status === $("#status-select").data("done")) {
                            $("#commission_done").hide();
                            $("#sendSmsBtn").addClass("d-none");
                            Swal.fire({
                                title: "Czy chcesz wystawić fakturę?",
                                type: "question",
                                showCancelButton: true,
                                focusCancel: false,
                                focusConfirm: true,
                                confirmButtonText: "Tak",
                                cancelButtonText: "Nie",
                            }).then((make_invoice) => {
                                if (make_invoice.value) {
                                    $("#add_invoice").click();
                                }
                            });
                        } else if (status === $("#status-select").data("ready")) {
                            $("#commission_done").show();
                            if ($("#status-select").data("sent") === "False") $("#sendSmsBtn").removeClass("d-none");
                            sendSmsNotification();
                        } else {
                            $("#commission_done").show();
                            $("#sendSmsBtn").addClass("d-none");
                        }
                    },
                });
            } else {
                $(that).parent().removeClass("active");
                $(last_status).parent().addClass("active");
            }
        });
    });

    $("#sendSmsBtn").on("click", function () {
        sendSmsNotification();
    });

    $("#assign_invoice").on("click", function () {
        $("#invoice-select").show();
        $("#id_sale_invoice").select2("open");
    });

    $("#id_sale_invoice").change(function () {
        const invoice_pk = $(this).val();
        if (isInt(invoice_pk)) {
            $.ajax({
                url: $("#invoice-select").data("assign-url"),
                type: "POST",
                data: {
                    csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
                    invoice: invoice_pk,
                    commission: $("#invoice-select").data("commission"),
                },
                success: function (data) {
                    if (data.status === "success") {
                        addAlert("Sukces!", data.status, data.message);
                        $("#invoice-list").find(".li-none").remove();
                        $("#invoice-list").append(
                            '<li><a href="' +
                                data.sale_invoice.url +
                                '">' +
                                data.sale_invoice.name +
                                '</a> <i class="fa fa-times unassign-invoice" data-name="' +
                                data.sale_invoice.name +
                                '" data-pk="' +
                                invoice_pk +
                                '" title="Odłącz fakturę"></i></li>'
                        );
                    } else {
                        addAlert("Uwaga!", data.status, data.message);
                    }
                },
                error: function (data) {
                    addAlert("Błąd!", "error", data.responseJSON.message);
                },
            });
            $("#id_sale_invoice").val("").change();
        }
        $("#invoice-select").hide();
    });

    $("#id_sale_invoice").on("select2:close", function (e) {
        $("#invoice-select").hide();
    });

    $(document).on("click", ".unassign-invoice", function () {
        let container = $(this).parent();
        Swal.fire({
            title: "Czy na pewno chcesz odłączyć fakturę od zlecenia?",
            text: $(this).data("name"),
            type: "question",
            showCancelButton: true,
            focusCancel: true,
            focusConfirm: false,
            confirmButtonText: "Tak",
            cancelButtonText: "Nie",
        }).then((change) => {
            if (change.value) {
                $.ajax({
                    url: $("#invoice-select").data("unassign-url"),
                    type: "POST",
                    data: {
                        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
                        invoice: $(this).data("pk"),
                        commission: $("#invoice-select").data("commission"),
                    },
                    success: function (data) {
                        if (data.status === "success") {
                            addAlert("Sukces!", data.status, data.message);
                            container.remove();
                            if ($("#invoice-list").children().length === 0) {
                                $("#invoice-list").append('<li class="li-none">—</li>');
                            }
                        } else {
                            addAlert("Uwaga!", data.status, data.message);
                        }
                    },
                    error: function (data) {
                        addAlert("Błąd!", "error", data.responseJSON.message);
                    },
                });
            }
        });
    });

    $("#change-type").on("click", function () {
        Swal.fire({
            title: "Czy na pewno chcesz zmienić typ zlecenia?",
            type: "question",
            showCancelButton: true,
            focusCancel: true,
            focusConfirm: false,
            confirmButtonText: "Tak",
            cancelButtonText: "Nie",
        }).then((change) => {
            if (change.value) {
                $.ajax({
                    url: $("#change-type").data("url"),
                    type: "POST",
                    data: {
                        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
                        pk: $("#change-type").data("pk"),
                    },
                    success: function (data) {
                        window.location.reload();
                    },
                    error: function (data) {
                        genericErrorAlert();
                    },
                });
            }
        });
    });

    if ($("#file-data").data("upload") == "True") {
        checkFileUpload();
    }
    bsCustomFileInput.init();
    $(".custom-file").bind("custom-upload-success", function (e) {
       $("#upload_modal").modal("hide");
       const data = {
            key: $("#id_upload_key").val(),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            commission: $("#file-data").data("commission"),
        };
       $.ajax({
            url: $(".custom-file").data("enqueue"),
            type: "POST",
            data: data,
            error: function () {
                genericErrorAlert();
            },
        });
       $("#uploadAlert").removeClass("hidden");
       checkFileUpload();
    });
});
