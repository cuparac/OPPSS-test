# CHANGELOG

Sve značajne izmene OPPSS Generatora su dokumentovane u ovom fajlu.

---

## [15.3] — 2026-09-19

### Nove funkcionalnosti
- **Modularna arhitektura** — Podela na 5 modula: `gui.py`, `database.py`, `validacije.py`, `xml_generator.py`, `opps_generator_gui_v15.3.py` (entry point)
- **Type hintovi** — Anotacije na svim javnim funkcijama i klasama
- **Docstringovi** — Google stil dokumentacije za sve klase i javne metode
- **Logging** — Zamena `print()` sa `logging` modulom (log fajl: `opps_generator.log`)
- **Pytest testovi** — 25 testova pokrivajući Database, validacije i XML generator
- **HTML injection fix** — `html.escape()` na sve dinamičke vrednosti u HTML izveštaju
- **Placeholder podnosioc fix** — `ValueError` umesto podrazumevanih vrednosti kada podnosioc ne postoji

---

## [15.2] — 2026-09-15

### Nove funkcionalnosti
- **Brisanje svih unosa** — Opcija za brisanje svih unosa za izabranu godinu sa dva nivoa potvrde i prikazom broja unosa i ukupnog iznosa
- **Backup baze podataka** — Ručno kopiranje SQLite baze u odabrani folder sa timestamp-om u nazivu fajla
- **Import iz CSV** — Uvoz podataka iz CSV fajla. Podržava različite formate datuma (`Y-m-d`, `d/m/Y`, `d.m.Y`) i varijante naziva kolona (ENG/SRB)
- **Izveštaj za štampu** — HTML izveštaj sa svim podacima, statistikom po opštini, i dugmetom za štampu (Ctrl+P iz pregledača)
- **Sortiranje tabele** — Klikom na zaglavlje bilo koje kolone sortira se tabela. Ponovni klik menja redosled (rastajući ↔ opadajući). Indikatori ▼/▲ u zaglavlju
- **Kontekstni meni** — Desni klik na red u tabeli (Izmeni, Obriši, Kopiraj identifikator, Pretraga po ID-ju) ili na prazan prostor (Dodaj novi, Osveži, Statistika)

---

## [15.1] — 2026-09-15

### Ispravljeni bugovi
- **Bug 1: DatumEntry kursor** — Kursor se sada može pozicionirati bilo gde u polju za datum. Navigacioni tasteri (⬅ ➡ Home End BackSpace Delete Tab) ne okidaju formatiranje
- **Bug 2: Provera duplikata identifikatora** — Prilikom unosa postojećeg identifikatora prikazuje se upozorenje sa podacima postojećeg unosa. Ne blokira unos (razlika može biti u datumu/iznosu)
- **Bug 3: Dvoklik za izmenu** — Dvoklik na red u tabeli otvara formu za izmenu. Dugme menja tekst: "Sačuvaj" za novi unos, "Sačuvaj izmene" za izmenu. Popravljena greška gde polja za datum nisu bila popunjena prilikom izmene

---

## [15.0] — 2026-09-08

### Nove funkcionalnosti
- **SQLite baza** — Zamena za JSON bazu (brža, sigurnija, SQL upiti)
- **CSV export** — Izvoz u Excel format (sa `;` delimiterom)
- **Pretraga** — Po opštini, imenu, identifikatoru, iznosu, datumu
- **Statistika** — Ukupno po godini, vrsti prometa, opštini
- **Migracija** — Automatska konverzija JSON → SQLite
- **Meni** — Datoteka, Unos, Alat, Pomoć
- **Property ispravke** — Ispravan redosled inicijalizacije

---

## [14.0] — 2026-09-01

### Nove funkcionalnosti
- **CLI standalone** — XSD šema ugrađena u kod
- **GUI standalone** — XSD šema ugrađena u kod
- **.exe kompatibilnost** — Spreman za PyInstaller

---

## [13.9] — 2026-08-25

### Nove funkcionalnosti
- **CLI verzija** — Command-line interfejs za terminal/server
- **Prečice tastature** — Ctrl+N, Ctrl+D, Ctrl+G, Ctrl+P, F1
- **About dijalog** — Informacije o aplikaciji
- **Error handling za lxml** — Bolje rukovanje greškama

---

## [13.8] — 2026-08-18

### Nove funkcionalnosti
- **EBS identifikator** — Podrška za Jedinstveni broj subjekta (9 cifara)
- **Poljoprivredno gazdinstvo** — Opciona polja za broj i naziv
- **Email osobe** — Opciono polje za kontakt osobe
- **Validacija JSON strukture** — Provera ključeva u bazi

---

## [13.7] — 2026-08-11

### Nove funkcionalnosti
- **fcntl na Windows** — Atomic write umesto fcntl
- **assert → if** — Ispravna validacija iznosa
- **Provera datuma** — Sprečava unos krajnjeg datuma pre početnog
- **Tabela** — Prikaz oba datuma u formatu "DD/MM/YYYY - DD/MM/YYYY"
- **XSD iz memorije** — Validacija bez čitanja fajla sa diska
- **strip()** — Uklanja sve whitespace umesto samo space
- **Error handling** — Za korumpirani JSON

---

## [13.6] — 2026-08-04

### Ispravljeni bugovi
- **JMBG validacija** — Ekstrahuje godinu iz JMBG-a, probava oba raspona (1000-1999 i 2000-2999)
- **tree.index()** — Ispravno indeksiranje nakon brisanja reda
- **Datum OD/DO** — Dva posebna polja sa kalendar dugmadima
- **File lock** — fcntl.flock() za atomicno čuvanje

---

## [13.5] — 2026-07-28

### Originalna verzija
- GUI aplikacija sa tkinter interfejsom
- JMBG validacija (osnovna)
- JSON baza podataka
- XML generisanje sa XSD validacijom
- Kalendar widget za izbor datuma
