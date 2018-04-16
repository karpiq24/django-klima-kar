var charts = {};

function number_format(number) {
    number = number.toString();
    var decimal_split = number.split('.');
    number = decimal_split[0].split(/(?=(?:...)*$)/);
    number = number.join(' ');
    if (decimal_split.length == 2)
        number = number + ',' + decimal_split[1];
    return number;
}

function set_chart_options(chart, type, custom) {
    if (type !== 'doughnut') {
        chart.options.scales.yAxes[0].ticks.callback = function(value, index, values) {
            return custom.values_prefix + number_format(value) + custom.values_appendix;
        }
    }
    chart.options.tooltips.callbacks.label = function(tooltipItem, chart) {
        var label = '';
        var value = chart['datasets'][0]['data'][tooltipItem['index']];
        if (type !== 'doughnut') {
            label = chart.datasets[tooltipItem.datasetIndex].label  || '';
        }
        else {
            label = chart['labels'][tooltipItem['index']] || '';
        }
        if (label !== '')
            label = label + ': ';
        return label + custom.values_prefix + number_format(value) + custom.values_appendix;
    }
    chart.update();
};

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
                set_chart_options(charts[chart_id], result.type, result.custom);
            }
            else {
                var chart = new Chart(chart_canvas, {
                    type: result.type,
                    data: result.data,
                    options: result.options 
                })
                set_chart_options(chart, result.type, result.custom);
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