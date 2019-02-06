$(function() {
    function reload_table (page = 1) {
        $.ajax({
            url: window.location.href,
            type: 'get',
            dataType: 'json',
            data: $('#filters > form').serialize() + '&page=' + page,
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
        debounce(reload_table, 300)
    });

    $('#filters > form select').on('change', function() {
        reload_table();
    });

    $('#filters > form :input').on('apply.daterangepicker', function() {
        reload_table();
    });

    $('.content').on('click', '.page-link', function() {
        reload_table(page=$(this).data('page'));
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
