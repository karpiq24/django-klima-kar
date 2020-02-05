$(function () {
    if ($('#duplicated_phone').length > 0) {
        const contractor_data = JSON.parse($('#duplicated_phone').val().slice(2, -2));
        let contractor_display =  $('<p>');
        for (const key in contractor_data) {
            if (contractor_data.hasOwnProperty(key)) {
                contractor_display.append(contractor_data[key].label + ': ' + contractor_data[key].value);
                contractor_display.append($('<br>'));
            }
        }
        let html_content = $('<div>')
            .append(contractor_display)
            .append($('<button style="margin: 0px 4px;" id="swal-close" class="btn btn-outline-dark">Anuluj</button>'))
            .append($('<button style="margin: 0px 4px;" id="swal-force-save" class="btn btn-outline-primary">Zapisz mimo to</button>'));
        if ($('#id_ignore_duplicated_phone').parents('form').attr('id') === 'modal_form') {
            html_content.append($('<button style="margin: 0px 4px;" id="swal-set-contractor" class="btn btn-outline-success">Ustaw tego kontrahenta</button>'));
        }

        $(document).on('click', '#swal-close', function () {
            Swal.close();
        });
        $(document).on('click', '#swal-force-save', function () {
            Swal.close();
            $('#id_ignore_duplicated_phone').val('True');
            $('#id_ignore_duplicated_phone').parents('form').submit();
        });
        $(document).on('click', '#swal-set-contractor', function () {
            Swal.close();
            $("#modal-generic").modal("hide");
            let $option = $("<option selected></option>").val(contractor_data['id'].value).text(contractor_data['name'].value);
            $('#id_contractor').append($option).trigger('change');
            $('#contractor-edit').prop('disabled', false);
        });

        Swal.fire({
            title: "Kontrahent z takim numerem telefonu już istnieje.",
            html: html_content,
            type: "question",
            showCancelButton: false,
            showConfirmButton: false,
        })
    }
});
