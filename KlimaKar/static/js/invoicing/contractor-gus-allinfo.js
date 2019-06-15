$(function () {
    $('#gus-data').on('click', function (){
        var that = $(this);
        var nip = null;
        if ($('#id_nip').length > 0)
            nip = $('#id_nip').val();
        else
            nip = $(that).data('nip');

        $('#gus-pkd tbody').empty();
        $('#gus-info tbody').empty();
        $.ajax({
            url: $(that).data('url'),
            type: 'get',
            dataType: 'json',
            data: {
                'nip': nip,
                'type': 'all'
            },
            success: function (data) {
                if (data.pkd.length > 0) {
                    data.pkd.forEach(function (elem, index) {
                        var number = index + 1;
                        $('#gus-pkd tbody').append('<tr><th scope="row">' + number + '</th><td>' + elem.name + '</td><td>' + elem.code +'</td></tr>')
                    })
                    $('#gus-pkd').show();
                }
                if (data.info) {
                    if (data.info.adresemail)
                        $('#gus-info tbody').append('<tr><td>Adres e-mail</td><td>' + data.info.adresemail +'</td></tr>')
                    if (data.info.adresemail2)
                        $('#gus-info tbody').append('<tr><td>Adres e-mail 2</td><td>' + data.info.adresemail2 +'</td></tr>')
                    if (data.info.adresstronyinternetowej)
                        $('#gus-info tbody').append('<tr><td>Adres strony internetowej</td><td>' + data.info.adresstronyinternetowej +'</td></tr>')
                    if (data.info.adsiedzgmina_nazwa)
                        $('#gus-info tbody').append('<tr><td>Gmina</td><td>' + data.info.adsiedzgmina_nazwa  +'</td></tr>')
                    if (data.info.adsiedzgmina_symbol)
                        $('#gus-info tbody').append('<tr><td>Symbol gminy</td><td>' + data.info.adsiedzgmina_symbol +'</td></tr>')
                    if (data.info.adsiedzkodpocztowy)
                        $('#gus-info tbody').append('<tr><td>Kod pocztowy</td><td>' + data.info.adsiedzkodpocztowy +'</td></tr>')
                    if (data.info.adsiedzkraj_nazwa)
                        $('#gus-info tbody').append('<tr><td>Kraj</td><td>' + data.info.adsiedzkraj_nazwa +'</td></tr>')
                    if (data.info.adsiedzmiejscowosc_nazwa)
                        $('#gus-info tbody').append('<tr><td>Miejscowość</td><td>' + data.info.adsiedzmiejscowosc_nazwa +'</td></tr>')
                    if (data.info.adsiedzmiejscowosc_symbol)
                        $('#gus-info tbody').append('<tr><td>Kod miejscowości</td><td>' + data.info.adsiedzmiejscowosc_symbol +'</td></tr>')
                    if (data.info.adsiedzmiejscowoscpoczty_nazwa)
                        $('#gus-info tbody').append('<tr><td>Poczta</td><td>' + data.info.adsiedzmiejscowoscpoczty_nazwa +'</td></tr>')
                    if (data.info.adsiedzmiejscowoscpoczty_symbol)
                        $('#gus-info tbody').append('<tr><td>Symbol poczty</td><td>' + data.info.adsiedzmiejscowoscpoczty_symbol +'</td></tr>')
                    if (data.info.adsiedznietypowemiejscelokalizacji)
                        $('#gus-info tbody').append('<tr><td>Nietypowa lokalizacja</td><td>' + data.info.adsiedznietypowemiejscelokalizacji +'</td></tr>')
                    if (data.info.adsiedznumerlokalu)
                        $('#gus-info tbody').append('<tr><td>Numer lokalu</td><td>' + data.info.adsiedznumerlokalu +'</td></tr>')
                    if (data.info.adsiedznumernieruchomosci)
                        $('#gus-info tbody').append('<tr><td>Numer nieruchomości</td><td>' + data.info.adsiedznumernieruchomosci +'</td></tr>')
                    if (data.info.adsiedzpowiat_nazwa)
                        $('#gus-info tbody').append('<tr><td>Powiat</td><td>' + data.info.adsiedzpowiat_nazwa +'</td></tr>')
                    if (data.info.adsiedzpowiat_symbol)
                        $('#gus-info tbody').append('<tr><td>Symbol powiatu</td><td>' + data.info.adsiedzpowiat_symbol +'</td></tr>')
                    if (data.info.adsiedzulica_nazwa)
                        $('#gus-info tbody').append('<tr><td>Ulica</td><td>' + data.info.adsiedzulica_nazwa +'</td></tr>')
                    if (data.info.adsiedzulica_symbol)
                        $('#gus-info tbody').append('<tr><td>Symbol ulicy</td><td>' + data.info.adsiedzulica_symbol +'</td></tr>')
                    if (data.info.adsiedzwojewodztwo_nazwa)
                        $('#gus-info tbody').append('<tr><td>Województwo</td><td>' + data.info.adsiedzwojewodztwo_nazwa +'</td></tr>')
                    if (data.info.adsiedzwojewodztwo_symbol)
                        $('#gus-info tbody').append('<tr><td>Symbol województwa</td><td>' + data.info.adsiedzwojewodztwo_symbol +'</td></tr>')
                    if (data.info.datapowstania)
                        $('#gus-info tbody').append('<tr><td>Data powstania</td><td>' + data.info.datapowstania +'</td></tr>')
                    if (data.info.datarozpoczeciadzialalnosci)
                        $('#gus-info tbody').append('<tr><td>Data rozpoczęcia działaności</td><td>' + data.info.datarozpoczeciadzialalnosci +'</td></tr>')
                    if (data.info.dataskresleniazregondzialalnosci)
                        $('#gus-info tbody').append('<tr><td>Data skreślenia z REGON działalności</td><td>' + data.info.dataskresleniazregondzialalnosci +'</td></tr>')
                    if (data.info.dataskresleniazrejestruewidencji)
                        $('#gus-info tbody').append('<tr><td>Data skreślenia z rejestru ewidencji</td><td>' + data.info.dataskresleniazrejestruewidencji +'</td></tr>')
                    if (data.info.datawpisudoregondzialalnosci)
                        $('#gus-info tbody').append('<tr><td>Data wpisu do REGON</td><td>' + data.info.datawpisudoregondzialalnosci +'</td></tr>')
                    if (data.info.datawpisudorejestruewidencji)
                        $('#gus-info tbody').append('<tr><td>Data wpisu do rejestru ewidencji</td><td>' + data.info.datawpisudorejestruewidencji +'</td></tr>')
                    if (data.info.datawznowieniadzialalnosci)
                        $('#gus-info tbody').append('<tr><td>Data wznowienia działalności</td><td>' + data.info.datawznowieniadzialalnosci +'</td></tr>')
                    if (data.info.datazaistnieniazmianydzialalnosci)
                        $('#gus-info tbody').append('<tr><td>Data zmiany w działaności</td><td>' + data.info.datazaistnieniazmianydzialalnosci +'</td></tr>')
                    if (data.info.datazakonczeniadzialalnosci)
                        $('#gus-info tbody').append('<tr><td>Data zakończenia działalności</td><td>' + data.info.datazakonczeniadzialalnosci +'</td></tr>')
                    if (data.info.datazawieszeniadzialalnosci)
                        $('#gus-info tbody').append('<tr><td>Data zawieszenia działalności</td><td>' + data.info.datazawieszeniadzialalnosci +'</td></tr>')
                    if (data.info.nazwa)
                        $('#gus-info tbody').append('<tr><td>Nazwa</td><td>' + data.info.nazwa +'</td></tr>')
                    if (data.info.nazwaskrocona)
                        $('#gus-info tbody').append('<tr><td>Nazwa skrócona</td><td>' + data.info.nazwaskrocona +'</td></tr>')
                    if (data.info.numerfaksu)
                        $('#gus-info tbody').append('<tr><td>Numer faksu</td><td>' + data.info.numerfaksu +'</td></tr>')
                    if (data.info.numertelefonu)
                        $('#gus-info tbody').append('<tr><td>Numer telefonu</td><td>' + data.info.numertelefonu +'</td></tr>')
                    if (data.info.numerwewnetrznytelefonu)
                        $('#gus-info tbody').append('<tr><td>Numer wewnętrzny telefonu</td><td>' + data.info.numerwewnetrznytelefonu +'</td></tr>')
                    if (data.info.numerwrejestrzeewidencji)
                        $('#gus-info tbody').append('<tr><td>Numer w rejestrze ewidencji</td><td>' + data.info.numerwrejestrzeewidencji +'</td></tr>')
                    if (data.info.organrejestrowy_nazwa)
                        $('#gus-info tbody').append('<tr><td>Organ rejestrowy</td><td>' + data.info.organrejestrowy_nazwa +'</td></tr>')
                    if (data.info.organrejestrowy_symbol)
                        $('#gus-info tbody').append('<tr><td>Symbol organu rejestrowego</td><td>' + data.info.organrejestrowy_symbol +'</td></tr>')
                    if (data.info.regon9)
                        $('#gus-info tbody').append('<tr><td>REGON 9</td><td>' + data.info.regon9 +'</td></tr>')
                    if (data.info.rodzajrejestru_nazwa)
                        $('#gus-info tbody').append('<tr><td>Rodzaj rejestru</td><td>' + data.info.rodzajrejestru_nazwa +'</td></tr>')
                    if (data.info.rodzajrejestru_symbol)
                        $('#gus-info tbody').append('<tr><td>Symbol rejestru</td><td>' + data.info.rodzajrejestru_symbol +'</td></tr>')

                    $('#gus-info').show();
                }
                $("#gus_modal").modal("show");
            },
            error: function(data) {
                swal("Błąd!", "Upewnij się, że NIP jest poprawny.", "error");
            }
        });
    });
});
