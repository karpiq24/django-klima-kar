let reloadTable = null;

$(function() {
    function reload_table({ page = 1, sort = null, table_id = null, counts_only = false }) {
        $("body").css("cursor", "progress");
        var url = [location.protocol, "//", location.host, location.pathname].join("");
        var data = $("#filters > form").serialize() + "&page=" + page;
        if (sort !== null) {
            data += "&sort=" + sort;
        } else {
            data += "&sort=" + $(".orderable.desc, .orderable.asc").data("sort");
        }
        if (table_id !== null) {
            data += "&table_id=" + table_id;
        }
        $.ajax({
            url: url,
            type: "get",
            dataType: "json",
            data: data,
            success: function(data) {
                if (!counts_only) {
                    if (table_id !== null) {
                        $('.table-container[data-table_id="' + table_id + '"').replaceWith(data.table);
                    } else {
                        $(".table-container").replaceWith(data.table);
                    }
                }
                if (data.tab_counts && data.tab_counts.length !== null) {
                    Object.keys(data.tab_counts).forEach(function(key, index) {
                        $("#nav-" + key + "-tab")
                            .find("span")
                            .text(data.tab_counts[key]);
                    });
                }
                $("body").css("cursor", "default");
            },
            error: function() {
                $("body").css("cursor", "default");
            }
        });
    }

    reloadTable = reload_table;

    var debounce = (function() {
        var timer = 0;
        return function(callback, ms) {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    $("#filters > form :input").on("keyup paste change", function() {
        debounce(function() {
            reload_table({});
        }, 300);
    });

    $("#filters > form select").on("change", function() {
        debounce(function() {
            reload_table({});
        }, 10);
    });

    $("#filters > form :input").on("apply.daterangepicker", function() {
        debounce(function() {
            reload_table({});
        }, 10);
    });

    $(".content").on("click", ".table-container .page-link", function() {
        let table_id = $(this)
            .parents(".table-container")
            .data("table_id");
        if (table_id !== undefined) {
            reload_table({ page: $(this).data("page"), table_id: table_id });
        } else {
            reload_table({ page: $(this).data("page") });
        }
    });

    $(".content").on("change", ".table-container .page-input", function() {
        let table_id = $(this)
            .parents(".table-container")
            .data("table_id");
        if (table_id !== undefined) {
            reload_table({ page: $(this).val(), table_id: table_id });
        } else {
            reload_table({ page: $(this).val() });
        }
    });

    $(".content").on("click", ".table-container .orderable > a", function() {
        let table_id = $(this)
            .parents(".table-container")
            .data("table_id");
        if (table_id !== undefined) {
            reload_table({ sort: $(this).data("query"), table_id: table_id });
        } else {
            reload_table({ sort: $(this).data("query") });
        }
    });

    $(".clear-filters").on("click", function() {
        $(":input", "#filters > form")
            .not(":button, :submit, :reset, :hidden")
            .val("")
            .prop("checked", false)
            .prop("selected", false);
        $("select")
            .val("")
            .change();
    });

    $('.filter-tabs > a[data-toggle="tab"]').on("shown.bs.tab", function(e) {
        $("#" + $(e.target).data("filter"))
            .val($(e.target).data("value"))
            .change();
    });

    if ($(".filter-tabs").length > 0) {
        debounce(function() {
            reload_table({ counts_only: true });
        }, 200);
    }
});
