![](logo.png)


# Bossapy

[EN](README_EN.md) version

Implementacja interfejsu do algo-tradingu obsługującego Bossa API w Pythonie. Jest to projekt open-source, niezwiązany z DM BOŚ.

Projekt powstał, by ułatwić korzystanie z możliwości API udostępnionego przez DM BOSSA w Pythonie.

Bibliotekę udostępniamy na licencji Apache v2.0 - wraz z pełnym, otwartym
kodem źródłowym. W ten sposób każdy może ją wykorzystać w swoich projektach -
nieważne, czy to projekt komercyjny, czy darmowy, otwarty czy też nie... 
Obowiązuje jedynie zasada, by nie zabrakło tam nigdy wzmianki o pierwotnych
autorzach (Feyy i Jarek) i wszystkich kolejnych (jeśli tacy się pojawią
i będą udostepniać swoje modyfikacje, do czego oczywiście zachęcam).

Feyy


# Instalacja
W celu skorzystania z Bossa API konieczne jest posiadanie konta maklerskiego w DM BOŚ.

### Platforma transakcyjna NOL
Do zainstalowanie `bossapy` potrzebna jest instalacja programu 
[NOL](https://bossa.pl/oferta/narzedzia/bossanol3). Jest to program będący platformą trasakcyjną, przez którą przesyłane są dane do Bossa API.
Podręcznik użytkownika dla platformy NOL jest dostępny w [pdf](https://bossa.pl/sites/b30/files/2021-04/document/Podrecznik_bossaNOL3.pdf)

### Biblioteka bossapy
Przenieś pliki z repozytorium `bossapy` do dowolnego lokalnego katalogu. 

# Uruchamianie

1. Zaloguj się do internetowego systemu transakcyjnego bossa przez przeglądarkę [bossa.pl](https://online.bossa.pl/bossaapp/login)
2. Przejdź do zakładki Notowania i kliknij urochom NOL, co uruchomi program NOL na komputerze lokalnym. W ten sposób program NOL łączy się z kontem maklerskim DM BOS.
3. Uruchom plik main.py


## Współpraca 🙋‍♂️?

Współpraca przy projekcie jest mile widziana. Zobacz [Zasady kontrybucji](CONTRIBUTING.md). Możesz też rzucić okiem na [bieżące kwestie](https://github.com/FeyyM/bossapy/issues) for getting more information about current or upcoming tasks.

## Dyskusja 💬

W razie pytań, bądź wątpliwosci możesz rozpocząć dyskusję. 
[Dyskusja](https://github.com/FeyyM/bossapy/discussions).

## Licencja

```
Prawa autorskie 2022 Jarosław Kuś, FeyyM

Licencjonowane na licencji Apache, wersja 2.0 („Licencja”);
nie możesz używać tego pliku, chyba że jest to zgodne z Licencją.
Kopię Licencji można uzyskać pod adresem

     http://www.apache.org/licenses/LICENSE-2.0

O ile nie wymaga tego obowiązujące prawo lub nie uzgodniono tego na piśmie, oprogramowanie
rozpowszechniane na podstawie Licencji są rozpowszechniane na ZASADZIE „TAK JAK JEST”,
BEZ GWARANCJI ANI WARUNKÓW JAKIEGOKOLWIEK RODZAJU, wyraźnych lub dorozumianych.
Zobacz Licencję, aby zapoznać się z uprawnieniami dotyczącymi konkretnego języka i
ograniczenia wynikające z Licencji.
