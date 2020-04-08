# Lista zmian

## 2020-04-08

### Dodano

-   możlwiość dodawania i edycji notatek do zleceń

### Poprawiono

-   kalendarz przy wyborze daty może pokazać się na górze kontrolki jeśli z dołu nie ma miejsca

## 2020-04-07

### Dodano

-   filtrowanie zleceń w zależności czy została przypisana faktura sprzedażowa
-   informacje czy powiadomienie SMS do zlecenia zostało już wysłane

### Naprawiono

-   wczytywanie rodzaju paliwa i daty pierwszej rejestracji w formularzu pojazdu

## 2020-04-04

### Dodano

-   ignorowanie spacji przy wyszukiwaniu kontrahenta podając numer telefonu
-   ignorowanie znaków nie alfanumerycznych przy wyszukiwaniu pojazdu
-   pola data pierwszej rejestracji oraz rodzaj paliwa pojazdu
-   zapisywanie nowych pól podczas skanowania dowodów rejestracyjnych

## 2020-04-03

### Dodano

-   ten plik CHANGELOG
-   wyświetlanie listy zmian bezpośrednio na stronie

### Naprawiono

-   skrypt instalacyjny zmian na serwerze produkcyjnym (npm ci zamiast npm install)

## 2020-04-02

### Dodano

-   wersję WIP formularza zlecenia dla dużych ekranów dotykowych
-   mutacje GraphQL pozwalające na dodanie nowego podzespołu, pojazdu i zlecenia

### Usunięto

-   pole towar z pozycji faktur sprzedażowych i zleceń

## 2020-03-22

### Dodano

-   komendę wczytującą ceny detaliczne towarów z Inter Cars

## 2020-03-19

### Naprawiono

-   przycisk wyszukiwania nie wyświetla się już dla nie zalogowanych użytkowników

## 2020-03-15

### Dodano

-   interfejs dla dużych ekranów dotykowych z listą zleceń

## 2020-03-07

### Dodano

-   pobieranie faktur ProfiAuto

### Usunięto

-   pobieranie faktur S-Auto

### Naprawiono

-   eksport sprzedaży czynników chłodniczych

## 2020-03-05

### Naprawiono

-   obliczanie sumy VAT w podsumowaniu

## 2020-03-04

### Dodano

-   ustawienia pobierania faktur
-   logowanie błędów w komendach administracyjnych

## 2020-03-03

### Dodano

-   filtr towarów pozwalający na wykluczenie dostawcy
-   zabezpieczenia usuwania plików z poziomu serwerów developerskich

## 2020-02-27

### Naprawiono

-   błąd powodujący nie wykonywanie się zaplanowanych komend z poziomu cron (zmieniono ścieżki schematów GraphQL z relatywnych na absolutne)

## 2020-02-22

### Dodano

-   kolejne modele to API GraphQL

## 2020-02-21

### Dodano

-   pierwszą wersję API GraphQL
-   domyślne sortowanie modeli

## 2020-02-20

### Dodano

-   wyświetlanie typu faktury w szczegółach kontrahenta

### Zmieniono

-   wyświetlanie większej ilości pozycji faktur i zleceń
-   generowanie tabeli zmian w audycie z kodu python do szablonu HTML

## 2020-02-19

### Naprawiono

-   eskport danych tabel

## 2020-02-18

### Dodano

-   logowanie błędów występujących w django-rq
-   pole cena detaliczna towaru

### Zmieniono

-   pliki po nieudanym wgraniu na WD MyCloud nie są usuwane
-   wyświetlanie wszystkich pól usług w tabeli

### Naprawiono

-   obliczanie ceny towaru przy pobieraniu faktur Gordon

## 2020-02-13

### Zmieniono

-   wygląd wyników wyszukiwania

## 2020-02-12

### Dodano

-   globalne wyszukiwanie

### Zmieniono

-   style głównego paska nawigacyjnego

## 2020-02-07

### Zmieniono

-   proces autoryzacji WD MyCloud Home, przystosowując do obsługi adresu zwrotnego zdalnej usługi

## 2020-02-06

### Dodano

-   wyświetlanie faktur bez przypisanych zleceń w podsumowaniu

## 2020-02-05

### Dodano

-   wykrywanie potencjalnych duplikatów kontrahentów jeśli numer telefonu się powtórzy

### Naprawiono

-   duplikowanie towarów podczas wczytywanie faktur Inter Cars

## 2020-02-04

### Dodano

-   śledzenie zmian w relacji Many to Many w audycie zmian

### Naprawiono

-   filtrowanie kontrahenta po numerze telefonu

## 2020-02-03

### Dodano

-   formatowanie wyświetlanych numerów telefonów

### Zmieniono

-   spacje w numerach telefonu są teraz usuwane

## 2020-01-24

### Dodano

-   ostrzeżenie o potencjalnie nie poprawnym numerze telefonu kontrahenta
-   ustawianie kontrahenta zlecenia jeśli nie był ustawiony, a faktura została wystawiona

### Zmieniono

-   etykietę pola rodzaj płatności na forma płatności
-   numer VIN i numer rejestracyjny zapisywane jako pisane wielką literą

### Naprawiono

-   pobieranie plików zawierających w nazwie polskie znaki

## 2020-01-18

### Dodano

-   możliwość wczytywania zeskanowanego kodu QR z aplikacji mPojazd

## 2020-01-13

### Zmieniono

-   sposób obliczania sum w fakturach zakupowych, fakturach sprzedażowych i zleceniach

## 2020-01-02

### Dodano

-   aktualizowanie nazwy zlecenia jeśli nazwa pojazdu lub podzespołu uległa zmianie

## przed 2020-01-01

Nie śledzono zmian w projekcie
