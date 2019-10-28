function submitInvoiceForm(url, commission_pk) {
    var data = $('#invoice_form').serialize() + '&pk=' + commission_pk;
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: function(data) {
            window.location.href = data.url;
        },
        error: function(data) {
            addAlert('Błąd!', 'error', 'Skontaktuj się z administratorem.');
        }
    });
};

function submitEmailForm(url) {
    var data = $('#email_form').serialize();
    var spinner = document.createElement("i");
    spinner.className = 'fas fa-spinner fa-spin fa-8x'
    spinner.style = 'margin-bottom: 26px;color: #00a0df;'
    $("#email_modal").modal("hide");
    Swal.fire({
        title: 'Wysyłanie wiadomości email',
        html: '<i class="fas fa-spinner fa-spin fa-8x" style="margin: 26px;color: #00a0df;"></i>',
        showConfirmButton: false
    })
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: function(data) {
            $("#email_modal").modal("hide");
            addAlert('Sukces!', 'success', data.message + '.');
        },
        error: function(data) {
            addAlert('Błąd!', 'error', data.responseJSON.message + '.');
            $("#email_modal").modal("show");
        }
    });
};

function printJSSupported() {
    if (typeof InstallTrigger !== 'undefined') {
        return false;
    }
    if (navigator.userAgent.indexOf('MSIE') !== -1 || !!document.documentMode) {
        return false;
    }
    if (!!window.StyleMedia) {
        return false;
    }
    return true;
};

function print_pdf() {
    var url = $('#print-btn').attr('data-url');
    if (printJSSupported()) {
        printJS({printable: url, type:'pdf', showModal:true, modalMessage:'Przygotowywanie zlecenia...'});
    }
    else {
        var w = window.open(url);
        w.print();
    }
};

$(function () {
    $('.sidenav #nav-commissions').children(':first').addClass('active');
    $('.sidenav #nav-commission').collapse('show');

    var url = window.location.href;
    if(url.indexOf('?pdf') != -1)
        print_pdf();
    else if(url.indexOf('&pdf') != -1)
        print_pdf();
    
    $("#print-btn").click(function() {
        print_pdf();
    });

    if ($('#file-data').data('upload') == 'True') {
        let check = setInterval(function () {
            $.ajax({
                url: $('#file-data').data('check-url'),
                type: 'get',
                data: {
                    pk: $('#file-data').data('commission')
                },
                dataType: 'json',
                success: function (data) {
                    if (data.status == 'success') {
                        $('#file-data').empty();
                        let fileList = $('#file-data').append($('<ul class="simple-list"></ul>')).find('ul');
                        $.each(data.files, function (i, file) {
                            var li = $('<li><a href="' + file.url + '" target="_blank">' + file.name + ' - ' + file.size + '</a></li>').appendTo(fileList);
                        })
                        clearInterval(check);
                    }
                }
            });
        }, 2000)
    }

    var last_status = $('#status-select input:checked');

    $('#status-select input').on('change', function () {
        const that = this;
        Swal.fire({
            title: "Czy na pewno chcesz zmienić status?",
            type: "question",
            showCancelButton: true,
            focusCancel: false,
            focusConfirm: true,
            confirmButtonText: 'Tak',
            cancelButtonText: 'Nie'
        }).then((change) => {
            if (change.value) {
                const status = $(this).data('value');
                last_status = that;
                $.ajax({
                    url: $('#status-select').data('url'),
                    type: 'post',
                    dataType: 'json',
                    data: {
                        status: status,
                        pk: $(this).data('pk'),
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                    },
                    success: function (data) {
                        $('#end_date').text(data.end_date);
                        if (status === $('#status-select').data('done')) {
                            $('#commission_done').hide();
                            Swal.fire({
                                title: "Czy chcesz wystawić fakturę?",
                                type: "question",
                                showCancelButton: true,
                                focusCancel: false,
                                focusConfirm: true,
                                confirmButtonText: 'Tak',
                                cancelButtonText: 'Nie'
                            }).then((make_invoice) => {
                                if (make_invoice.value) {
                                    $('#add_invoice').click();
                                }
                            });
                        } else if (status === $('#status-select').data('ready')) {
                            $('#commission_done').show();
                            const phone1 = $('#status-select').data('phone1');
                            const phone2 = $('#status-select').data('phone2');
                            options = {};
                            if (phone2 !== undefined && phone2 !== 'None') {
                                options[phone2] = phone2
                            }
                            if (phone1 !== undefined && phone1 !== 'None') {
                                options[phone1] = phone1
                            }
                            if (!$.isEmptyObject(options)) {
                                Swal.fire({
                                    title: "Czy chcesz wysłać powiadomienie SMS do klienta?",
                                    text: $('#sms').val(),
                                    type: "question",
                                    input: 'radio',
                                    inputOptions: options,
                                    inputValue: ((phone1 !== undefined && phone1 !== 'None') ? phone1 : phone2),
                                    inputValidator: (value) => {
                                        if (!value) {
                                            return 'Wybierz numer telefonu.'
                                        }
                                    },
                                    showCancelButton: true,
                                    focusCancel: false,
                                    focusConfirm: true,
                                    confirmButtonText: 'Tak',
                                    cancelButtonText: 'Nie'
                                }).then((send_sms) => {
                                    if (send_sms.value) {
                                        $.ajax({
                                            url: $('#status-select').data('sms-url'),
                                            type: 'post',
                                            dataType: 'json',
                                            data: {
                                                phone: send_sms.value,
                                                message: $('#sms').val(),
                                                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                                            },
                                            success: function (data) {
                                                addAlert('Sukces!', 'success', data.message);
                                            },
                                            error: function () {
                                                addAlert('Błąd!', 'error', 'Coś poszło nie tak. Spróbuj ponownie.');
                                            }
                                        });
                                    }
                                });
                            }
                        } else {
                            $('#commission_done').show();
                        }
                    }
                });
            } else {
                $(that).parent().removeClass('active');
                $(last_status).parent().addClass('active');
            }
        });
    })
})
