function append_alert(tag, message) {
    var message_prefix = ''
    switch(tag) {
      case 'danger':
        message_prefix = 'Błąd! ';
        break;
      case 'success':
        message_prefix = 'Sukces! ';
        break;
    }
    var rnd_class = 'alert-' + Math.random().toString(36).substring(7);
    $('#alert-box').append('<div class="' + rnd_class + ' alert alert-' + tag + ' alert-dismissible fade show" role="alert" data-dismiss="alert"><strong>' + message_prefix + '</strong>' + message + '</div>');
    setTimeout(function() {
        $('.' + rnd_class).alert('close');
    }, 5000);
}

$(function () {
    setTimeout(function() {
        $(".alert-django").alert('close');
    }, 5000);
});