$(function() {
    function realodSearch({ page = 1 }) {
        $("body").css("cursor", "progress");
        const url = [location.protocol, "//", location.host, location.pathname].join("");
        const data = $("#search-form").serialize() + "&page=" + page;
        $.ajax({
            url: url,
            type: "get",
            dataType: "json",
            data: data,
            success: function(data) {
                $(".search-result-container").replaceWith(data.html);
                $("body").css("cursor", "default");
            },
            error: function() {
                $("body").css("cursor", "default");
            }
        });
    }

    $(".content").on("click", ".search-result-container .page-link", function() {
        realodSearch({ page: $(this).data("page") });
    });

    $(".content").on("change", ".search-result-container .page-input", function() {
        realodSearch({ page: $(this).val() });
    });

    $("#search-form").on("submit", function(e) {
        e.preventDefault();
        realodSearch({});
    });

    const ALL_CHOICE = "__ALL__";
    const params = new URLSearchParams(window.location.search);
    const models = params.getAll("models");
    if (models.length > 0) {
        $(".model-choice[data-choice='" + ALL_CHOICE + "']").removeClass("active");
        models.forEach(function(model) {
            $(".model-choice[data-choice='" + model + "']").addClass("active");
        });
    } else {
        $(".model-choice[data-choice='" + ALL_CHOICE + "']").addClass("active");
    }

    $(".model-choice").on("click", function() {
        const choice = $(this).data("choice");
        const is_active = $(this).hasClass("active");
        if (is_active) {
            if (choice === ALL_CHOICE) {
                return;
            }
            $(this).removeClass("active");
            $("#id_models input[value='" + choice + "']").prop("checked", false);
            if ($(".model-choice.active").length === 0) {
                $(".model-choice[data-choice='" + ALL_CHOICE + "']").addClass("active");
                $("#id_models input").prop("checked", false);
            }
        } else {
            if (choice === ALL_CHOICE) {
                $(".model-choice").removeClass("active");
                $("#id_models input").prop("checked", false);
            } else {
                $(".model-choice[data-choice='" + ALL_CHOICE + "']").removeClass("active");
                $("#id_models input[value='" + choice + "']").prop("checked", true);
            }
            $(this).addClass("active");
        }
        realodSearch({});
    });
});
