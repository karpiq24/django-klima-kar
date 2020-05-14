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

    if ($("#file-data").data("upload") == "True") {
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
                                                    sendCommissionNotification(pk: "${$(that).data("pk")}", phone: "${
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
                                                    "error",
                                                    data.sendCommissionNotification.message
                                                );
                                            },
                                            error: function () {
                                                genericErrorAlert();
                                            },
                                        });
                                    }
                                });
                            }
                        } else {
                            $("#commission_done").show();
                        }
                    },
                });
            } else {
                $(that).parent().removeClass("active");
                $(last_status).parent().addClass("active");
            }
        });
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

    $("#addNote").on("click", function () {
        const pk = $(this).data("pk");
        Swal.fire({
            title: "Podaj treść notatki.",
            type: "info",
            input: "textarea",
            showCancelButton: true,
            focusConfirm: true,
            confirmButtonText: "Zapisz",
            cancelButtonText: "Anuluj",
            allowOutsideClick: true,
        }).then(({ value }) => {
            if (value === undefined) return;
            $.ajax({
                url: "/graphql/",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    query: `mutation {
                        addCommissionNote(commission: "${pk}", contents: ${JSON.stringify(value)}) {
                            id
                            contents
                            created
                        }
                    }`,
                }),
                success: function ({ data }) {
                    const created = moment(data.addCommissionNote.created).locale("pl").format("D MMMM YYYY HH:mm");
                    const contents = data.addCommissionNote.contents.replace(/\n/g, "<br/>");
                    $(".notes ul").prepend(`
                        <li class="list-group-item d-flex justify-content-between align-items-start" data-contents="${data.addCommissionNote.contents}" data-active="True">
                            <div>
                                <small class="font-weight-bold">${created}</small>
                                <div>${contents}</div>
                            </div>
                            <button type="button" class="btn p-0 border-0 shadow-none close edit-note" data-pk="${data.addCommissionNote.id}">
                                <i class="fas fa-pencil-alt"></i>
                            </button>
                        </li>`);
                },
                error: function (data) {
                    genericErrorAlert();
                },
            });
        });
    });

    $(document).on("click", ".edit-note", function () {
        const pk = $(this).data("pk");
        const element = $(this).parent("li");
        Swal.fire({
            title: "Edytuj notatkę.",
            type: "info",
            html: `
                <textarea id="swal-contents" class="swal2-textarea" style="display: flex;" placeholder="">${$(
                    element
                ).data("contents")}</textarea>
                <label class="toggle-switch">
                    <input id="swal-active" type="checkbox" ${$(element).data("active") === "True" ? "checked" : null}>
                    <span class="slider"></span>
                    <span>Notatka aktywna</span>
                </label>
            `,
            preConfirm: () => {
                return [document.getElementById("swal-contents").value, document.getElementById("swal-active").checked];
            },
            showCancelButton: true,
            focusConfirm: true,
            confirmButtonText: "Zapisz",
            cancelButtonText: "Anuluj",
            allowOutsideClick: true,
        }).then(({ value }) => {
            if (value === undefined) return;
            $.ajax({
                url: "/graphql/",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    query: `mutation {
                        updateCommissionNote(pk: "${pk}", contents: ${JSON.stringify(value[0])}, isActive: ${
                        value[1]
                    }) {
                            id
                            contents
                            created
                            last_edited
                            is_active
                        }
                    }`,
                }),
                success: function ({ data }) {
                    const created = moment(data.updateCommissionNote.created).locale("pl").format("D MMMM YYYY HH:mm");
                    const last_edited = moment(data.updateCommissionNote.last_edited)
                        .locale("pl")
                        .format("D MMMM YYYY HH:mm");
                    const contents = data.updateCommissionNote.contents.replace(/\n/g, "<br/>");
                    $(element).data("contents", data.updateCommissionNote.contents);
                    $(element).data("active", data.updateCommissionNote.is_active ? "True" : "False");
                    $(element).find("div div").html(contents);
                    $(element).find("small").text(`${created} (edytowano ${last_edited})`);
                    !data.updateCommissionNote.is_active
                        ? $(element).addClass("not-active")
                        : $(element).removeClass("not-active");
                },
                error: function (data) {
                    genericErrorAlert();
                },
            });
        });
    });
});
