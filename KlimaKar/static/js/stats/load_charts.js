$(function () {
    $("canvas[id^='chart']").each(function() {
        var parent_div = $(this).parent().parent().parent();
        var url = $(this).attr('chart-url');
        var ctx = $(this)
        $.ajax({
            url: url,
            success: function (result) {
                $(parent_div).show();
                var chart = new Chart(ctx, {
                    type: result.type,
                    data: result.data,
                    options: result.options 
                })
            }
        });
    });
});