function humanFileSize(bytes, si) {
    var thresh = si ? 1000 : 1024;
    if(Math.abs(bytes) < thresh) {
        return bytes + ' B';
    }
    var units = si
        ? ['kB','MB','GB','TB','PB','EB','ZB','YB']
        : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return bytes.toFixed(1)+' '+units[u];
}

function uploadFiles(files) {
    let data = new FormData();
    Array.from(files).forEach(file => {
        data.append(file.name, file);
    });
    data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
    data.append('key', $('#id_upload_key').val());

    $.ajax({
        url:  $('.custom-file').data('url'),
        type: 'POST',
        data: data,
        cache: false,
        contentType: false,
        processData: false,
        xhr: function () {
            var xhr = $.ajaxSettings.xhr();
            xhr.upload.onprogress = function (e) {
                if (e.lengthComputable) {
                    $('.custom-file .progress').css('display', 'flex');
                    $('.custom-file .progress-bar').css('width', Math.floor(100 * e.loaded / e.total) + '%');
                }
            };
            return xhr;
        },
        success: function(data) {
            if (!data.status) {
                addAlert('Błąd!', 'error', data.message);
            } else {
                addAlert('Sukces!', 'success', data.message);
            }
            $('.custom-file-input').val('');
            $('.custom-file-label').text($('.custom-file-label').data('label'));
            setTimeout(function() {
                $('.custom-file .progress').css('display', 'none');
                $('.custom-file .progress-bar').css('width', '0%');
                $('#file-list').empty();
                data.files.forEach(file => {
                    $('#file-list').append('<li>' +
                                            '<span class="file-name">' + file.name + '</span> - <span class="file-size">' + humanFileSize(file.size, false) + '</span> <i class="fa fa-times delete-file" data-file="' + file.name + '" title="Usuń plik"></i>' +
                                        '</li>');
                });
            }, 800);
        },
        error: function() {
            addAlert('Błąd!', 'error', data.responseJSON.message);
            $('.custom-file-input').val('');
            $('.custom-file-label').text($('.custom-file-label').data('label'));
            setTimeout(function() {
                $('.custom-file .progress').css('display', 'none');
                $('.custom-file .progress-bar').css('width', '0%');
            }, 800);
        }
    });
}

$(function () {
    const $form = $('.custom-file');
    if ($form) {
        $('.custom-file-input').on('change', function() {
            uploadFiles($(this).prop('files'));
        })
        $('.custom-file-input').on('dragover dragenter', function() {
            $(this).parent().addClass('is-dragover');
        })
        $('.custom-file-input').on('dragleave dragend drop', function() {
            $(this).parent().removeClass('is-dragover');
        })
    }

    $(document).on('click', '.delete-file', function() {
        const that = this;
        const data = {
            key: $('#id_upload_key').val(),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            file: $(this).data('file')
        }
        $.ajax({
            url:  $('.custom-file').data('delete-temp-url'),
            type: 'POST',
            data: data,
            success: function(data) {
                if (!data.status) {
                    addAlert('Błąd!', 'error', data.message);
                } else {
                    addAlert('Sukces!', 'success', data.message);
                    $(that).parents('li').remove();
                }
            },
            error: function() {
                addAlert('Błąd!', 'error', data.responseJSON.message);
            }
        });
    })

    $(document).on('click', '.delete-previous-file', function() {
        const that = this;
        const data = {
            object: $(this).data('object'),
            file: $(this).data('file'),
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        }
        $.ajax({
            url:  $('.custom-file').data('delete-previous-url'),
            type: 'POST',
            data: data,
            success: function(data) {
                if (!data.status) {
                    addAlert('Błąd!', 'error', data.message);
                } else {
                    addAlert('Sukces!', 'success', data.message);
                    $(that).parents('li').remove();
                }
            },
            error: function() {
                addAlert('Błąd!', 'error', data.responseJSON.message);
            }
        });
    })
})
