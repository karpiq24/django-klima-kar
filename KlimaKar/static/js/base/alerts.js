function addAlert(title, tag, text='', html='') {
    Swal.fire({
        position: 'top-end',
        type: tag,
        title: title,
        text: text,
        html: html,
        showConfirmButton: false,
        timer: 3000,
        toast: true
    });
}

$(function () {
    MESSAGES.forEach(function (message) {
        addAlert(message.message, message.tag)
    });
});
