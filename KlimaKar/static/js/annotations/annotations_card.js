$(function () {
    $("#addAnnotation").on("click", function () {
        addAnnotation($(this).data("pk"), $(this).data("app-name"), $(this).data("model-name"))
    });

    $(document).on("click", ".edit-annotation", function () {
        editAnnotation($(this).data("pk"), $(this).parent("li"))
    });
})
