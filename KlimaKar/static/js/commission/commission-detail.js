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

    $('#status-select input').on('change', function () {
        const status = $(this).data('value');
        $.ajax({
            url: $('#status-select').data('url'),
            type: 'post',
            dataType: 'json',
            data: {
                status: status,
                pk: $(this).data('pk'),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: async function () {
                if (status === $('#status-select').data('done')) {
                    $('#commission_done').hide();
                    Swal.fire({
                        title: "Czy chcesz wystawić fakturę?",
                        type: "question",
                        showCancelButton: true,
                        focusCancel: false,
                        confirmButtonText: 'Tak',
                        cancelButtonText: 'Nie'
                    }).then((make_invoice) => {
                        if (make_invoice.value) {
                            $('#add_invoice').click();
                        }
                    });
                } else {
                    $('#commission_done').show();
                }
            }
        });
    })
})
