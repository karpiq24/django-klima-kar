$(function () {
    $(".sidenav #nav-employees").children(":first").addClass("active");
    $(".sidenav #nav-management").collapse("show");

    $("#addAbsence").on("click", function () {
        const that = this;
        $.ajax({
            url: $(that).data("url"),
            type: "get",
            dataType: "json",
            data: { employee: $(that).data("employee") },
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            },
        });
    });

    $(".update-abscence").on("click", function () {
        const that = this;
        $.ajax({
            url: $(that).data("url"),
            type: "get",
            dataType: "json",
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            },
        });
    });

    $(".remove-absence").on("click", function () {
        const that = this;
        Swal.fire({
            title: "Czy na pewno chcesz usunąć tą nieobecność?",
            type: "question",
            showCancelButton: true,
            focusCancel: false,
            focusConfirm: true,
            confirmButtonText: "Tak",
            cancelButtonText: "Nie",
        }).then((deleteSession) => {
            if (deleteSession.value) {
                $.ajax({
                    url: $(that).data("url"),
                    type: "post",
                    dataType: "json",
                    data: {
                        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
                    },
                    success: function (data) {
                        addAlert("Sukces!", "success", data.message);
                        reloadTable({});
                    },
                    error: function () {
                        genericErrorAlert();
                    },
                });
            }
        });
    });
});

function customSuccessCreate(data, identifier) {
    reloadTable({});
}
