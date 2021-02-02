function checkScanningStatus() {
    let check = setInterval(function () {
        $.ajax({
            url: $("#scanFile").data("check-url"),
            type: "get",
            data: {
                pk: $("#scanFile").data("pk"),
            },
            dataType: "json",
            success: function (data) {
                if (data.status == "success") {
                    clearInterval(check);
                    setTimeout(function () {
                        window.location.reload();
                    }, 1000);
                }
            },
        });
    }, 2000);
}

function customSuccessCreate(data, identifier) {
    Swal.fire({
        title: "Uruchomiono skanowanie dokumentów",
        html: '<i class="fas fa-spinner fa-spin fa-8x" style="margin: 26px;color: #00a0df;"></i>',
        showConfirmButton: false,
    });
    setTimeout(function () {
        checkScanningStatus();
    }, 5000);
}

$(function () {
    $("#scanFile").on("click", function () {
        const data = {
            object_pk: $(this).data("pk"),
            content_type: $(this).data("content-type"),
            file_content_type: $(this).data("content-type-file"),
        };
        $.ajax({
            url: "/scanner_form",
            type: "get",
            dataType: "json",
            data: data,
            beforeSend: function () {
                $("#modal-generic").modal("show");
            },
            success: function (data) {
                $("#modal-generic .modal-content").html(data.html_form);
            },
        });
    });

    $(document).on("change", "input[type=radio][name=scanner_type]", function () {
        if (this.value === "ADF") {
            $("input[type=radio][name=file_type][value=JPG]").prop("checked", false);
            $("input[type=radio][name=file_type][value=PDF]").prop("checked", true);
            $("input[type=radio][name=file_type][value=PDF]").parent().addClass("active");
            $("input[type=radio][name=file_type][value=JPG]").parent().removeClass("active");
            $("input[type=radio][name=file_type][value=JPG]").parent().addClass("disabled");
            $("input[type=radio][name=file_type][value=JPG]").attr("disabled", true);
        } else {
            $("input[type=radio][name=file_type][value=JPG]").attr("disabled", false);
            $("input[type=radio][name=file_type][value=JPG]").parent().removeClass("disabled");
        }
    });
});
