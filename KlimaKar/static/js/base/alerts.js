function addAlert(title, tag, text = "", html = "") {
    Swal.fire({
        position: "top-end",
        type: tag,
        title: title,
        text: text,
        html: html,
        showConfirmButton: false,
        timer: 10000,
        toast: true,
    });
}

function genericErrorAlert() {
    addAlert("Błąd!", "error", "Coś poszło nie tak. Spróbuj ponownie.");
}

$(function () {
    MESSAGES.forEach(function (message) {
        var title = "";
        switch (message.tag) {
            case "success":
                title = "Sukces!";
                break;
            case "error":
                title = "Błąd!";
                break;
            case "info":
                title = "Informacja!";
                break;
            case "warning":
                title = "Uwaga!";
                break;
            case "debug":
                title = "DEBUG!";
                break;
        }
        addAlert(title, message.tag, "", message.message);
    });
});
