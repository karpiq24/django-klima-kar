function isInt(value) {
    return !isNaN(value) && 
            parseInt(Number(value), 10) == value && 
            !isNaN(parseInt(value, 10));
}

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
        printJS({printable: url, type:'pdf', showModal:true, modalMessage:'Przygotowywanie faktury...'});
    }
    else {
        var w = window.open(url);
        w.print();
    }
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

$(function () {
    $('.sidenav #nav-saleinvoices').children(':first').addClass('active');
    $('.sidenav #nav-invoicing').collapse('show');

    var url = window.location.href;
    if(url.indexOf('?pdf') != -1)
        print_pdf();
    else if(url.indexOf('&pdf') != -1)
        print_pdf();
    
    $("#print-btn").click(function() {
        print_pdf();
    });

    $('#assign_commission').on('click', function() {
        $('#commission-select').show();
        $('#id_commission').select2('open')
    })

    $("#id_commission").change(function() {
        const commission_pk = $(this).val();
        if (isInt(commission_pk)) {
            $.ajax({
                url: $('#commission-select').data('assign-url'),
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                    'invoice': $('#commission-select').data('invoice'),
                    'commission': commission_pk
                },
                success: function(data) {
                    if (data.status === 'success') {
                        addAlert('Sukces!', data.status, data.message);
                        $('#commission-list').find('.li-none').remove();
                        $('#commission-list').append('<li><a href="' + data.commission.url + '">' + data.commission.name + '</a> <i class="fa fa-times unassign-invoice" data-name="' + data.commission.name + '" data-pk="' + commission_pk + '" title="Odłącz zlecenie"></i></li>');
                    } else {
                        addAlert('Uwaga!', data.status, data.message);
                    }
                },
                error: function(data) {
                    addAlert('Błąd!', 'error', data.responseJSON.message);
                }
            });
            $("#id_commission").val('').change();
        }
        $('#commission-select').hide();
    })

    $('#id_commission').on('select2:close', function (e) {
        $('#commission-select').hide();
    })

    $(document).on('click', '.unassign-invoice', function() {
        let container = $(this).parent();
        Swal.fire({
            title: "Czy na pewno chcesz odłączyć zlecenie od faktury?",
            text: $(this).data('name'),
            type: "question",
            showCancelButton: true,
            focusCancel: true,
            focusConfirm: false,
            confirmButtonText: 'Tak',
            cancelButtonText: 'Nie'
        }).then((change) => {
            if (change.value) {
                $.ajax({
                    url: $('#commission-select').data('unassign-url'),
                    type: 'POST',
                    data: {
                        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                        'invoice': $('#commission-select').data('invoice'),
                        'commission': $(this).data('pk')
                    },
                    success: function(data) {
                        if (data.status === 'success') {
                            addAlert('Sukces!', data.status, data.message);
                            container.remove();
                            if ($('#commission-list').children().length === 0) {
                                $('#commission-list').append('<li class="li-none">—</li>');
                            }
                        } else {
                            addAlert('Uwaga!', data.status, data.message);
                        }
                    },
                    error: function(data) {
                        addAlert('Błąd!', 'error', data.responseJSON.message);
                    }
                });
            }
        })
    })
});
