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
    swal({
        title: "Wysyłanie wiadomości email",
        content: spinner,
        buttons: false,
    })
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: function(data) {
            $("#email_modal").modal("hide");
            swal({
                title: data.message,
                icon: 'success'
            })
        },
        error: function(data) {
            swal({
                title: data.responseJSON.message,
                icon: 'error'
            }).then(function() {
                $("#email_modal").modal("show");
            })
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
});
