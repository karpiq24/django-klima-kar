$(function () {
    $(".sidenav #nav-invoices").children(":first").addClass("active");
    $(".sidenav #nav-warehouse").collapse("show");

    $("#scanInput").on("change", function () {
        let data = new FormData();
        Array.from($(this).prop("files")).forEach((file) => {
            data.append(file.name, file);
        });
        data.append("csrfmiddlewaretoken", $("input[name=csrfmiddlewaretoken]").val());

        $.ajax({
            url: $("#scanForm").data("url"),
            type: "POST",
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            xhr: function () {
                let xhr = $.ajaxSettings.xhr();
                xhr.upload.onprogress = function (e) {
                    if (e.lengthComputable) {
                        $(".custom-file .progress").css("display", "flex");
                        $(".custom-file .progress-bar").css("width", Math.floor((100 * e.loaded) / e.total) + "%");
                    }
                };
                return xhr;
            },
            success: function (data) {
                window.location = data.url;
            },
            error: function (response) {
                addAlert("Błąd!", "error", response.responseJSON.message);
                $("#scanInput").val("");
                $(".custom-file-label").text($(".custom-file-label").data("label"));
                setTimeout(function () {
                    $(".custom-file .progress").css("display", "none");
                    $(".custom-file .progress-bar").css("width", "0%");
                    $("#scanModal").modal("hide");
                }, 800);
            },
        });
    });
});
