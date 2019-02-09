$(function() {
    function reload_table ({page = 1, sort = null}) {
        var url = [location.protocol, '//', location.host, location.pathname].join('');
        var data = $('#filters > form').serialize() + '&page=' + page;
        if (sort !== null) {
            data += '&sort=' + sort;
        } else {
            data += '&sort=' + $('.orderable.desc, .orderable.asc').data('sort');
        }
        $.ajax({
            url: url,
            type: 'get',
            dataType: 'json',
            data: data,
            success: function (data) {
                $('.table-container').replaceWith(data.table)
            }
        });
    }
    
    var debounce = (function() {
        var timer = 0;
        return function(callback, ms){
            clearTimeout (timer);
            timer = setTimeout(callback, ms);
        };
    })();

    $('#filters > form :input').on('keyup paste', function() {
        debounce(function () {
            reload_table({});
        }, 300)
    });

    $('#filters > form select').on('change', function() {
        debounce(function () {
            reload_table({});
        }, 10)
    });

    $('#filters > form :input').on('apply.daterangepicker', function() {
        debounce(function () {
            reload_table({});
        }, 10)
    });

    $('.content').on('click', '.page-link', function() {
        reload_table({page:$(this).data('page')});
    });

    $('.content').on('click', '.orderable > a', function() {
        reload_table({sort:$(this).data('query')});
    });

    $('.clear-filters').on('click', function() {
        $(':input','#filters > form')
            .not(':button, :submit, :reset, :hidden')
            .val('')
            .prop('checked', false)
            .prop('selected', false);
        $("select").val('').change();
    });
});
