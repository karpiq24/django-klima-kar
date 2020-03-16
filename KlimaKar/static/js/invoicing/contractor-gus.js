$(document).on("click", "#gus-button", function() {
    var nip = $("#id_nip").val();
    var parent = $("#id_nip")
        .parent()
        .parent();
    var url = $(this).attr("data-url");

    if (nip.length < 10 || !$.isNumeric(nip)) {
        $("#id_nip").addClass("is-invalid");
        if ($(parent).find("div.invalid-feedback").length == 0) {
            $(parent).append('<div class="invalid-feedback">Wpisz poprawną wartość.</div>');
        }
    } else {
        $("#id_nip").removeClass("is-invalid");
        $(parent)
            .find("div.invalid-feedback")
            .remove();
        $.ajax({
            url: url,
            type: "get",
            dataType: "json",
            data: {
                nip: nip
            },
            success: function(data) {
                $("#id_name").val(data.name);
                $("#id_city").val(data.city);
                $("#id_address_1").val(data.street_address);
                $("#id_postal_code").val(data.postal_code);
            },
            error: function(data) {
                $("#id_nip").addClass("is-invalid");
                $(parent).append('<div class="invalid-feedback">Nie znaleziono w bazie GUS.</div>');
            }
        });
    }
});
