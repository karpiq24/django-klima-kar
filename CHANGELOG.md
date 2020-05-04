# Lista zmian

## 2020-05-04

-   [TILES] Dodano nowy wygląd podsumowania zlecenia
-   [TILES] Dodano informacje o niezapisanym zleceniu

## 2020-04-30

-   [TILES] Poprawiono wyświetlanie nazwy usług z filtrem towaru
-   [TILES] Zmieniono układ strony przy wprowadzaniu pozycji
-   Dodano możliwość zmienienia koloru przycisku usługi

## 2020-04-29

-   Naprawiono pobieranie faktur DEKO
-   Naprawiono usuwanie obiektów z indeksu wyszukiwania
-   Dodano wyświetlanie numerów telefonu kontrahenta bezpośrednio podczas edycji zlecenia
-   Przeniesiono funkcjonalność pobieranie szczegółów kontrahenta do GraphQL

## 2020-04-28

-   [TILES] Poprawiono możliwości wyszukiwania w polach wyboru (wyszukiwanie w więcej niż 1 polu modelu)

## 2020-04-27

-   [TILES] Dodano zapisywanie nowych oraz edycję istniejących zleceń

## 2020-04-26

-   Dodano możliwosć edycji pojazdów, podzespołów i kontrahentów poprzez API GraphQL
-   [TILES] Dodano możliwość dodawania nowych oraz edycji pojazdów, podzespołów i kontrahentów

## 2020-04-24

-   [TILES] Dodano możliwosć odznaczenia wybranego obiektu w niewymaganych polach wyboru
-   [TILES] Poprawiono wygląd pól wyboru

## 2020-04-23

-   zamiast wyświetlać formularz po skanowaniu dowodu rejestracyjnego, pojazd jest zapisywany w tle
-   dodano możliwosć ustawienia nazwy przycisku usług

## 2020-04-21

-   przywrócono towar do pozycji faktur i zleceń
-   dodano wybór towaru w pozycji zlecenia w iterfejsie kafelkowym

## 2020-04-18

-   skanowanie dowodów rejestracyjnych w formularzu pojazdu po wciśnięciu specjalnego przycisku zamiast w polu wyszukiwania

## 2020-04-17

-   dodano endpoint dekodowania kodów z dowodów rejestracyjnych i mPojazd do GraphQL
-   dodano obsługę skanowania kodów w formularzu krokowym zleceń
-   zmieniono wygląd podsumowania formularza zlecenia
-   mniejsze poprawki w formularzu krokowym zleceń

## 2020-04-16

-   dodano link do szczegółów pojazdu/podzespołu oraz ostatniego zlecenia po wyborze pojazdu/podzespołu w formularzu zlecenia

## 2020-04-15

-   dodano alert z potwierdzeniem wylogowania
-   zmieniono format pliku CHANGELOG.md
-   poprawiono etykiety modeli w audycie zmian

## 2020-04-14

-   poprawiono formularz dodawania/edycji zlecenia w wersji dla dużych ekranów dotykowych

## 2020-04-13

-   wyłączono sortowanie wyników wyszukiwania dla znacznego zwiększenia wydajności

## 2020-04-10

-   zwiększono wydajność nowego wyszukiwania (dodano zapisywanie wektora wyszukiwania, oraz indeks w bazie danych)

## 2020-04-09

-   dodano url do szczegółów notatek w audycie zmian
-   wyświetlanie informacji o braku notatek w zleceniu zamiast pustej listy
-   zmieniono backend wyszukiwania: z wykorzystaniem Postgres zamiast Solr i django-haystack

## 2020-04-08

-   dodano możlwiość dodawania i edycji notatek do zleceń
-   kalendarz przy wyborze daty może pokazać się na górze kontrolki jeśli z dołu nie ma miejsca

## 2020-04-07

-   dodano filtrowanie zleceń w zależności czy została przypisana faktura sprzedażowa
-   dodano informacje czy powiadomienie SMS do zlecenia zostało już wysłane
-   naprawiono wczytywanie rodzaju paliwa i daty pierwszej rejestracji w formularzu pojazdu

## 2020-04-04

-   ignorowanie spacji przy wyszukiwaniu kontrahenta podając numer telefonu
-   ignorowanie znaków nie alfanumerycznych przy wyszukiwaniu pojazdu
-   dodano pola data pierwszej rejestracji oraz rodzaj paliwa pojazdu
-   zapisywanie nowych pól podczas skanowania dowodów rejestracyjnych

## 2020-04-03

-   dodano ten plik CHANGELOG
-   dodano wyświetlanie listy zmian bezpośrednio na stronie
-   poprawiono skrypt instalacyjny zmian na serwerze produkcyjnym (npm ci zamiast npm install)

## 2020-04-02

-   dodano wersję WIP formularza zlecenia dla dużych ekranów dotykowych
-   dodano mutacje GraphQL pozwalające na dodanie nowego podzespołu, pojazdu i zlecenia
-   usunięto pole towar z pozycji faktur sprzedażowych i zleceń

## 2020-03-22

-   dodano komendę wczytującą ceny detaliczne towarów z Inter Cars

## 2020-03-19

-   przycisk wyszukiwania nie wyświetla się już dla nie zalogowanych użytkowników

## 2020-03-15

-   dodano interfejs dla dużych ekranów dotykowych z listą zleceń

## 2020-03-07

-   dodano pobieranie faktur ProfiAuto
-   usunięto faktur S-Auto
-   naprawiono eksport sprzedaży czynników chłodniczych

## 2020-03-05

-   naprawiono obliczanie sumy VAT w podsumowaniu

## 2020-03-04

-   dodano ustawienia pobierania faktur
-   dodano logowanie błędów w komendach administracyjnych

## 2020-03-03

-   dodano filtr towarów pozwalający na wykluczenie dostawcy
-   dodano zabezpieczenia usuwania plików z poziomu serwerów developerskich

## 2020-02-27

-   naprawiono błąd powodujący nie wykonywanie się zaplanowanych komend z poziomu cron (zmieniono ścieżki schematów GraphQL z relatywnych na absolutne)

## 2020-02-22

-   dodano kolejne modele to API GraphQL

## 2020-02-21

-   dodano pierwszą wersję API GraphQL
-   dodano domyślne sortowanie modeli

## 2020-02-20

-   dodano wyświetlanie typu faktury w szczegółach kontrahenta
-   wyświetlanie większej ilości pozycji faktur i zleceń
-   generowanie tabeli zmian w audycie z wykorzystaniem szablonu HTML zamiast bezpośrednio w pythonie

## 2020-02-19

-   naprawiono eskport danych tabel

## 2020-02-18

-   dodano logowanie błędów występujących w django-rq
-   dodano pole cena detaliczna towaru
-   pliki po nieudanym wgraniu na WD MyCloud nie są usuwane
-   wyświetlanie wszystkich pól usług w tabeli
-   naprawiono obliczanie ceny towaru przy pobieraniu faktur Gordon

## 2020-02-13

-   poprawiono wygląd wyników wyszukiwania

## 2020-02-12

-   dodano globalne wyszukiwanie
-   poprawiono style głównego paska nawigacyjnego

## 2020-02-07

-   poprawiono proces autoryzacji WD MyCloud Home, przystosowując do obsługi adresu zwrotnego zdalnej usługi

## 2020-02-06

-   dodano wyświetlanie faktur bez przypisanych zleceń w podsumowaniu

## 2020-02-05

-   dodano wykrywanie potencjalnych duplikatów kontrahentów jeśli numer telefonu się powtórzy
-   naprawiono duplikowanie towarów podczas wczytywanie faktur Inter Cars

## 2020-02-04

-   dodano śledzenie zmian w relacji Many to Many w audycie zmian
-   naprawiono filtrowanie kontrahenta po numerze telefonu

## 2020-02-03

-   dodano formatowanie wyświetlanych numerów telefonów
-   spacje w numerach telefonu są teraz usuwane

## 2020-01-24

-   dodano ostrzeżenie o potencjalnie nie poprawnym numerze telefonu kontrahenta
-   dodano ustawianie kontrahenta zlecenia jeśli nie był ustawiony, a faktura została wystawiona
-   zmieniono etykietę pola rodzaj płatności na forma płatności
-   numer VIN i numer rejestracyjny zapisywane są teraz jako pisane wielką literą
-   naprawiono pobieranie plików zawierających w nazwie polskie znaki

## 2020-01-18

-   dodano możliwość wczytywania zeskanowanego kodu QR z aplikacji mPojazd

## 2020-01-13

-   poprawiono sposób obliczania sum w fakturach zakupowych, fakturach sprzedażowych i zleceniach

## 2020-01-02

-   dodano aktualizowanie nazwy zlecenia jeśli nazwa pojazdu lub podzespołu uległa zmianie

## przed 2020-01-01

Nie śledzono zmian w projekcie
