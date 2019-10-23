function submitIssue(url) {
    var data = $('#issue_form').serialize();
    var spinner = document.createElement("i");
    spinner.className = 'fas fa-spinner fa-spin fa-8x'
    spinner.style = 'margin-bottom: 26px;color: #00a0df;'
    $("#issue_modal").modal("hide");
    Swal.fire({
        title: 'Wysyłanie zgłoszenia',
        html: '<i class="fas fa-spinner fa-spin fa-8x" style="margin: 26px;color: #00a0df;"></i>',
        showConfirmButton: false
    })
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: function(data) {
            addAlert('Sukces!', 'success', data.message + '.');
        },
        error: function(data) {
            addAlert('Błąd!', 'error', data.responseJSON.message + '.');
            $("#issue_modal").modal("show");
        }
    });
};
