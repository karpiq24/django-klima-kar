function addAnnotation(objectId, appName, modelName) {
    Swal.fire({
        title: "Podaj treść notatki.",
        type: "info",
        input: "textarea",
        showCancelButton: true,
        focusConfirm: true,
        confirmButtonText: "Zapisz",
        cancelButtonText: "Anuluj",
        allowOutsideClick: true,
    }).then(({ value }) => {
        if (value === undefined) return;
        $.ajax({
            url: "/graphql/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                query: `mutation {
                    addAnnotation(app_name: "${appName}", model_name: "${modelName}", object_id: "${objectId}", contents: ${JSON.stringify(value)}) {
                        id
                        contents
                        created
                    }
                }`,
            }),
            success: function ({ data }) {
                const created = moment(data.addAnnotation.created).locale("pl").format("D MMMM YYYY HH:mm");
                const contents = data.addAnnotation.contents.replace(/\n/g, "<br/>");
                if ($(".empty-annotations")) {
                    $(".empty-annotations").removeClass("d-flex");
                    $(".empty-annotations").hide();
                }
                $(".annotations ul").prepend(`
                    <li class="list-group-item d-flex justify-content-between align-items-start" data-contents="${data.addAnnotation.contents}" data-active="True">
                        <div>
                            <small class="font-weight-bold">${created}</small>
                            <div>${contents}</div>
                        </div>
                        <button type="button" class="btn p-0 border-0 shadow-none close edit-note" data-pk="${data.addAnnotation.id}">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                    </li>`);
            },
            error: function (data) {
                genericErrorAlert();
            },
        });
    });
}

function editAnnotation(objectId, element) {
    Swal.fire({
        title: "Edytuj notatkę.",
        type: "info",
        html: `
            <textarea id="swal-contents" class="swal2-textarea" style="display: flex;" placeholder="">${$(
                element
            ).data("contents")}</textarea>
            <label class="toggle-switch">
                <input id="swal-active" type="checkbox" ${$(element).data("active") === "True" ? "checked" : null}>
                <span class="slider"></span>
                <span>Notatka aktywna</span>
            </label>
        `,
        preConfirm: () => {
            return [document.getElementById("swal-contents").value, document.getElementById("swal-active").checked];
        },
        showCancelButton: true,
        focusConfirm: true,
        confirmButtonText: "Zapisz",
        cancelButtonText: "Anuluj",
        allowOutsideClick: true,
    }).then(({ value }) => {
        if (value === undefined) return;
        $.ajax({
            url: "/graphql/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                query: `mutation {
                    updateAnnotation(pk: "${objectId}", contents: ${JSON.stringify(value[0])}, is_active: ${
                    value[1]
                }) {
                        id
                        contents
                        created
                        last_edited
                        is_active
                    }
                }`,
            }),
            success: function ({ data }) {
                const created = moment(data.updateAnnotation.created).locale("pl").format("D MMMM YYYY HH:mm");
                const last_edited = moment(data.updateAnnotation.last_edited)
                    .locale("pl")
                    .format("D MMMM YYYY HH:mm");
                const contents = data.updateAnnotation.contents.replace(/\n/g, "<br/>");
                $(element).data("contents", data.updateAnnotation.contents);
                $(element).data("active", data.updateAnnotation.is_active ? "True" : "False");
                $(element).find("div div").html(contents);
                $(element).find("small").text(`${created} (edytowano ${last_edited})`);
                !data.updateAnnotation.is_active
                    ? $(element).addClass("not-active")
                    : $(element).removeClass("not-active");
            },
            error: function (data) {
                genericErrorAlert();
            },
        });
    });
}
