$(function() {
    function reload_table ({page = 1, sort = null}) {
        $('body').css('cursor', 'progress');
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
                $('body').css('cursor', 'default');
            },
            error: function() {
                $('body').css('cursor', 'default');
            }
        });
    }
    
    var debounce = (function() {
        var timer = 0;
        return function(callback, ms){
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    $('#filters > form :input').on('keyup paste change', function() {
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
        $('select').val('').change();
    });

    $('.filter-tabs > a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        $('#' + $(e.target).data('filter')).val($(e.target).data('value')).change();
    })
});
