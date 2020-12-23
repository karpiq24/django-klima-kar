function openAnnotationModal(appName, modelName, objectID) {
    $("#addAnnotation").data("pk", objectID);
    $("#addAnnotation").data("app-name", appName);
    $("#addAnnotation").data("model-name", modelName);

    $.ajax({
        url: "/graphql/",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            query: `query {
                        annotations(filters: {content_type__app_label: "${appName}", content_type__model: "${modelName}", object_id: "${objectID}"}, pagination: {forceAll: true}) {
                            objects {
                                id
                                contents
                                created
                                last_edited
                                is_active
                                was_edited
                            }
                        }
                    }`,
        }),
        success: function ({data}) {
            $("#annotationsModal .modal-body ul").empty();
            if (data.annotations === null) genericErrorAlert();
            else {
                if (data.annotations.objects.length === 0) {
                    $("#annotationsModal .modal-body ul").append(`
                       <li class="list-group-item d-flex justify-content-between align-items-start empty-annotations">
                           Brak notatek.
                       </li>
                    `)
                }
                $(data.annotations.objects).each(function (i, annotation) {
                    const created = moment(annotation.created).locale("pl").calendar({sameElse: 'D MMMM YYYY HH:mm:ss'});
                    const edited = moment(annotation.last_edited).locale("pl").calendar({sameElse: 'D MMMM YYYY HH:mm:ss'});
                    $("#annotationsModal .modal-body ul").append(`
                        <li class="list-group-item d-flex justify-content-between align-items-start ${!annotation.is_active ? "not-acive" : "" }" data-contents="${annotation.contents}" data-active="${ annotation.is_active }">
                            <div>
                                <small class="font-weight-bold">${created} ${annotation.was_edited ? `(edytowano ${edited})` : "" }</small>
                                <div>${annotation.contents}</div>
                            </div>
                            <button type="button" class="btn p-0 border-0 shadow-none close edit-annotation" data-pk="${ annotation.id}">
                                <i class="fas fa-pencil-alt"></i>
                            </button>
                        </li>
                    `)
                });
                $("#annotationsModal").modal("show");
            }
        },
        error: function (data) {
            genericErrorAlert();
        },
    });
}

$(function () {
    $("#addAnnotation").on("click", function () {
        addAnnotation($(this).data("pk"), $(this).data("app-name"), $(this).data("model-name"))
    });

    $(document).on("click", ".edit-annotation", function () {
        editAnnotation($(this).data("pk"), $(this).parent("li"))
    });

    $(".open-annotation-modal").on("click", function () {
        openAnnotationModal($(this).data("app-name"), $(this).data("model-name"), $(this).data("pk"))
    })
})
