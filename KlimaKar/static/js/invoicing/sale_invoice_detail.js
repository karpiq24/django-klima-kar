function print_pdf() {
    var url = $('#print-btn').attr('data-url');
    var w = window.open(url);
    w.print();
}
function submitEmailForm(url) {
    var data = $('#email_form').serialize();
    data
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: function(data){
            $("#email_modal").modal("hide");
            append_alert('success', data.message);
        },
        error: function(data){
            append_alert('danger', data.responseJSON.message);
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