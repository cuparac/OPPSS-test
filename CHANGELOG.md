# CHANGELOG

Sve značajne izmene OPPSS Generatora su dokumentovane u ovom fajlu.

---

## [16.0] — 2026-10-07

### Arhitektura
- **MVC refaktoring** — monolitni `gui.py` (2008 linija) razdvojen na tri sloja:
  - `model/` — baza, validacije, XML/HTML/PDF generator (bez GUI zavisnosti)
  - `view/` — GUI komponente (prozori, dijalozi, widget-i)
  - `controller.py` — business logika koja povezuje Model i View
- **Entry point** — `opps_generator_gui_v16.py`

### Ispravke
- **Naslov prozora** — prikazivao je v15.3, sada v16
- **Dijalog O aplikaciji** — prikazivao je v15.7, sada v16
- **Prvi podnosilac na praznoj bazi** — na praznoj bazi nije bilo načina da se
  napravi prvi podnosilac (dugme „+ Novi" je bilo uklonjeno, a „Sacuvaj" je
  odbijao sa „Nije izabran podnosioc"), pa generisanje XML prijave nije moglo da
  se završi. Vraćena dugmad „+ Novi" i „Aktivan"; „Sacuvaj" na praznoj bazi
  kreira prvog podnosioca i postavlja ga kao aktivnog
- **Id podnosioca se ponovo koristi** posle brisanja (AUTOINCREMENT je čuvao
  najveći ikad upotrebljeni broj)
- **Brisanje aktivnog podnosioca** — prvi preostali preuzima aktivnost
- **Prozor za duplikat sa tri jasne opcije** — umesto sistemskog dijaloga sa
  dugmadima Yes/No/Cancel (koja ne govore šta znače): „Zameni", „Dodaj kao novi",
  „Ne snimaj". Kod duplikata se forma popunjava podacima postojećeg unosa
- **Uklonjeno UNIQUE ograničenje** na (identifikator, datum, godina) da bi
  „Dodaj kao novi" mogao da radi; postojeća baza se automatski migrira
- **Upozorenje na različite podatke istog identifikatora** — ista osoba treba da
  ima iste podatke u svim unosima tokom godine. Ako se opština, adresa, ime,
  telefon ili gazdinstvo razlikuju među unosima sa istim JMBG/PIB/EBS, pri
  kucanju tog identifikatora prikazuje se upozorenje sa svim pronađenim
  vrednostima i brojem pojavljivanja. Datumi i iznos se ne proveravaju
- **Enter potvrđuje u prozoru za duplikat** — u prozoru sa opcijama radilo je samo
  Space (podrazumevano ponašanje Tk dugmeta). Sada Enter potvrđuje izabrano dugme,
  strelice gore/dole (i Tab / Shift+Tab) prelaze između opcija u krug, Escape
  odustaje; izabrano dugme je podebljano
- **Enter prelazi na sledeće polje** — ranije je Enter odmah snimao unos, pa je
  pritisnut na pola forme prikazivao „Popunite sva obavezna polja!". Sada Enter
  ide na sledeće polje (kao Tab), a snimanje je na dugmetu „Sačuvaj"
- **Prepis podataka kod ponovnog unosa istog JMBG/PIB/EBS** — čim se ukuca ceo
  identifikator, ostali podaci (ime/naziv, opština, adresa, e-pošta, telefon,
  gazdinstvo, vrste) prepisuju se iz poslednjeg unosa sa tim identifikatorom;
  **datumi i iznos se ne prepisuju** (unose se za novi period). Poruka:
  „↻ Podaci prepisani iz prethodnog unosa"
- **Broj telefona prima samo cifre** — u polje telefona nije moglo da se ukuca
  slovo, ali se sadržaj polja čuvao samo `strip`-ovan, pa je „060abc111" mogao da
  uđe u bazu. Sada polje odbija slova odmah pri kucanju (dozvoljeni su cifre,
  razmak, `+`, `-` i `/`), a pri snimanju se zadržavaju samo cifre. Unos bez
  cifara ili van opsega 6–15 cifara se odbija sa porukom. Isto važi i za formu
  podnosioca. Kursor ostaje na mestu gde je kucano, ne skače na kraj polja

### Testovi
- **Integracioni testovi** — 81 test kroz ceo Model + View + Controller stack:
  svi prolaze (0 padova); četiri nasleđena buga iz v15.9 popravljena.
  Testovi su lokalni — `tests/` je u `.gitignore`, ne ide u repozitorijum.

### Uklonjeno iz v16
- `gui.py` — backward-compat shim više nije potreban
- `opps_generator_gui_v15.9.py` — stari entry point
- `opps.xsd` — XSD šema je ugrađena u kod (`model/validacije.py`)
- `docs/superpowers/` — interni planning fajlovi

### Preimenovano
- `opps_generator_cli_v15.py` → `opps_generator_cli.py`

### Ispravljeni bugovi nasleđeni iz v15.9
Sva četiri su popravljena (i u v16 i u v15.9):

| # | Bug | Greška (pre) | Rešenje |
|---|-----|--------------|---------|
| 1 | Statistika prozor | `TypeError: string indices must be integers` / `KeyError 'ukupno_unosa'` | `Database.statistika()` vraća liste reči (`opstina`/`vrsta_prometa`, `broj`, `iznos`), dijalog ih tako čita |
| 2 | Pretraga prozor | `sqlite3.ProgrammingError` / `no such column: ime` | nova `Database.pretrazi_po()` prevodi kriterijume u SQL uslov i parametre |
| 3 | Malformiran datum | neuhvaćen `ValueError` | `konvertuj_datum()` u `try/except`, prikazuje se poruka |
| 4 | Kolone posle filtera | 7 vrednosti u 9 kolona (pomeranje) | `filtriraj_tabelu` upisuje svih 9 kolona |

### Starije verzije
Starije verzije (v13.5–v15.9) su dostupne kao git tagovi:
`git checkout v15.9`

---

## [15.9] — 2026-10-06

### Nove funkcionalnosti
- **Pravi PDF export** — ReportLab umesto HTML izveštaja (v15.9)
- **Dark theme fix** — Tekst dugme u meniju se sada menja (Dark/Light)
- **requirements.txt** — Dodat reportlab u zavisnosti

---

## [15.8] — 2026-10-05

### Nove funkcionalnosti
- **Indeksi u bazi** — UNIQUE constraint na (identifikator, datum, godina) + 5 indeksa (godina, identifikator, datum, opstina, vrsta_prometa)
- **Lazy loading** — Paginacija tabele (100 unosa po stranici) sa dugmadima << Prva / < Prethodna / Sledeća > / Poslednja >>
- **Keširanje XSD seme** — XSD šema se učitava samo jednom i kešira u memoriji

---

## [15.7] — 2026-10-05

### Nove funkcionalnosti
- **Tabovi (kartice)** — Notebook sa 5 tabova: Svi unosi, Po opštini, Po vrsti prometa, Po datumu, Grafikoni
- **Grafikoni** — Matplotlib bar/pie chart-ovi po opštini i vrsti prometa
- **Dark theme** — Tamna tema preko Alat menija (🌙 Dark theme)

---

## [15.6] — 2026-10-05

### Nove funkcionalnosti
- **Napredni filteri** — Filter po datumu: "Samo ove godine", "Samo ovog meseca"
- **Sortiranje tabele** — Status label ispod tabele prikazuje trenutno sortiranje (kolona + smer)

---

## [15.5] — 2026-10-05

### Nove funkcionalnosti
- **Više podnosioca u bazi** — Podržano više podnosioca (različiti PIB/JMBG, opštine, vrste prometa). Migracija tabele `podnosioc` sa `godina` PK na `id` PK, dodata `naziv` i `aktivan` polja
- **Selektor podnosioca** — Combobox u ProzorPodnosioca za izbor između podnosioca
- **Upravljanje podnosiocima** — Dugmad + Novi / - Obriši / Aktivan
- **XML import** — Podnosioc iz XML-a se dodaje kao novi i postavlja kao aktivan
- **XML export** — Koristi se aktivni podnosilac za generisanje prijave
- **Migracija postojeće baze** — Automatska konverzija stare tabele (godina PK → id PK)

---

## [15.4] — 2026-09-19

### Nove funkcionalnosti
- **Auto-backup baze** — Automatski backup pri svakom pokretanju (`backup_baza_{godina}_{timestamp}.db`)
- **Pametni duplikati** — Provera identifikator + datum pri unosu, dijalog sa opcijama Zameni / Dodaj kao novi / Preskoči
- **PDF export** — PDF izveštaj preko pregledača (bez dodatnih biblioteka)
- **Undo/Redo** — Ctrl+Z / Ctrl+Y za poništavanje i ponavljanje operacija (dodaj, izmeni, obriši)
- **Drag & drop XML upload** — Povuci XML fajl na prozor za učitavanje (Windows, `windnd` opciono)
- **Napredni filteri** — Filter po vrsti prometa, opštini i range iznosa (min/max)

---

## [15.3] — 2026-09-19

### Nove funkcionalnosti
- **Modularna arhitektura** — Podela na 5 modula: `gui.py`, `database.py`, `validacije.py`, `xml_generator.py`, `opps_generator_gui_v15.8.py` (entry point)
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
