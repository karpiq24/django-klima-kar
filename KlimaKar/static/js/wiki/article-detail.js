$(function () {
    $(".sidenav #nav-wiki").children(":first").addClass("active");

    const converter = new showdown.Converter();
    const html = converter.makeHtml($("#markdown").data("text"));
    $("#markdown").html(html);

    let index = 0;
    let h1 = 0;
    let h2 = 0;
    let h3 = 0;

    $("#markdown h1, #markdown h2, #markdown h3").each(function () {
        let anchor = "<a name='" + index + "'></a>";
        $(this).before(anchor);
        if ($(this).is("h1")) {
            h1 += 1;
            h2 = 0;
            h3 = 0;
            let li = $("<div><a href='#" + index + "'>" + h1 + ". " + $(this).text() + "</a></div>");
            li.appendTo("#toc");
        } else if ($(this).is("h2")) {
            h2 += 1;
            h3 = 0;
            let li = $(
                "<div class='ml-2'><a href='#" + index + "'>" + h1 + "." + h2 + ". " + $(this).text() + "</a></div>"
            );
            li.appendTo("#toc");
        } else {
            h3 += 1;
            let li = $(
                "<div class='ml-4'><a href='#" +
                    index +
                    "'>" +
                    h1 +
                    "." +
                    h2 +
                    "." +
                    h3 +
                    ". " +
                    $(this).text() +
                    "</a></div>"
            );
            li.appendTo("#toc");
        }
        index++;
    });

    if ($("#markdown h1, #markdown h2, #markdown h3").length !== 0){
        $("#toc").parent().removeClass("d-none");
    }

    if ($("#file-data").data("upload") == "True") {
        let check = setInterval(function () {
            $.ajax({
                url: $("#file-data").data("check-url"),
                type: "get",
                data: {
                    pk: $("#file-data").data("article"),
                },
                dataType: "json",
                success: function (data) {
                    if (data.status == "success") {
                        $("#file-data").empty();
                        let fileList = $("#file-data").append($('<ul class="simple-list"></ul>')).find("ul");
                        $.each(data.files, function (i, file) {
                            $(
                                '<li><a href="' +
                                    file.url +
                                    '" target="_blank">' +
                                    file.name +
                                    " - " +
                                    file.size +
                                    "</a></li>"
                            ).appendTo(fileList);
                        });
                        clearInterval(check);
                    }
                },
            });
        }, 2000);
    }
});
