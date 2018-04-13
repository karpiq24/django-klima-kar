var charts = {};

function load_chart(chart_card) {
    var data = {};
    var date_select = $(chart_card).find("select[id^='chart_date_select']");
    var custom_select = $(chart_card).find("select[id^='chart_custom_select']");
    if (date_select) {
        data['date_select'] = date_select.val();
    }
    if (custom_select) {
        data['custom_select'] = custom_select.val();
    }
    var chart_canvas = $(chart_card).find(".chart_canvas");
    var url = $(chart_card).attr('chart-url');
    var chart_id = $(chart_card).attr('id');
    $.ajax({
        url: url,
        data: data,
        success: function (result) {
            $(chart_card).show();
            if (chart_id in charts) {
                charts[chart_id].type = result.type;
                charts[chart_id].options = result.options;
                charts[chart_id].data = result.data;
                charts[chart_id].update();
            }
            else {
                var chart = new Chart(chart_canvas, {
                    type: result.type,
                    data: result.data,
                    options: result.options 
                })
                charts[chart_id] = chart;
            }
            
        }
    });
};

$(function () {
    $(".chart-card").each(function() {
        load_chart($(this));
    });

    $("select[id^='chart_date_select']").on('change', function() {
       load_chart($(this).closest('.chart-card'));
    });

    $("select[id^='chart_custom_select']").on('change', function() {
        load_chart($(this).closest('.chart-card'));
     });
});