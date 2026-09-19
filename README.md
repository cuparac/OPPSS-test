# OPPS Generator

**Aplikacija za generisanje OPPS prijava (Обавештење о промету пољопривредних производа и секундарних сировина)**

![Version](https://img.shields.io/badge/verzija-15.4-blue)
![Python](https://img.shields.io/badge/python-3.6+-green)
![License](https://img.shields.io/badge/licence-MIT-orange)

---

## Sadržaj

- [O projektu](#o-projektu)
- [Funkcionalnosti](#funkcionalnosti)
- [Instalacija](#instalacija)
- [Korišćenje](#korišćenje)
- [Istorija unapređenja](#istorija-unapređenja)
- [Struktura projekta](#struktura-projekta)
- [Generisani fajlovi](#generisani-fajlovi)
- [Kreiranje .exe fajla](#kreiranje-exe-fajla-portable)
- [Rešavanje problema](#rešavanje-problema)
- [Licenca](#licenca)

---

## O projektu

OPPS Generator je desktop i CLI aplikacija za generisanje XML fajlova namenjenih upload-u na portal **ePorezi** (Poreska uprava Republike Srbije). Aplikacija omogućava unos podataka o podnosiocu i izvršiocima prometa, validaciju unetih podataka, i generisanje XML fajla u skladu sa XSD semom.

**Verzija 15.4** donosi 6 novih funkcionalnosti: auto-backup baze, pametnu obradu duplikata (zameni/dodaj/preskoči), PDF export preko pregledača, Undo/Redo (Ctrl+Z/Ctrl+Y), drag & drop XML upload i napredne filtere (vrsta prometa, opština, range iznosa). Aplikacija je podeljena na: `gui.py`, `database.py`, `validacije.py`, `xml_generator.py` i `opps_generator_gui_v15.4.py` (entry point).

---

## Funkcionalnosti

### Validacija podataka
- **JMBG** (13 cifara) - provera datuma i kontrolne cifre
- **PIB** (9 cifara) - provera dužine
- **EBS** (9 cifara) - provera dužine
- **Datumi** - provera ispravnosti i redosleda (OD ≤ DO)
- **Iznos** - provera pozitivnog celog broja
- **Provera duplikata** - upozorenje ako postoji isti identifikator (ne blokira unos)

### Vrste identifikatora
| Tip | Opis | Dužina |
|-----|------|--------|
| JMBG | Jedinstveni matični broj građana | 13 cifara |
| PIB | Poreski identifikacioni broj | 9 cifara |
| EBS | Jedinstveni broj subjekta | 9 cifara |

### Vrste prometa
| Šifra | Opis |
|-------|------|
| 1 | Unos prometa poljoprivrednih proizvoda i usluga |
| 2 | Unos prometa sekundarnih sirovina |

### Obavezna polja
- Vrsta prometa
- Identifikator (JMBG/PIB/EBS)
- Ime i prezime / Naziv
- Opština
- Adresa
- Telefon
- Datum OD
- Datum DO
- Iznos prometa

### Opciona polja
- E-posta osobe
- Broj poljoprivrednog gazdinstva
- Naziv poljoprivrednog gazdinstva

### Dodatne funkcionalnosti (v15.2)
- **SQLite baza** - brža i sigurnija od JSON
- **CSV export** - izvoz u Excel format
- **CSV import** - uvoz podataka iz CSV fajla
- **Pretraga** - po opštini, imenu, identifikatoru, iznosu
- **Statistika** - ukupno po godini, vrsti prometa, opštini
- **Migracija** - automatska konverzija JSON → SQLite
- **Brisanje svih unosa** - sa dva nivoa potvrde
- **Backup baze** - ručno kopiranje SQLite fajla sa timestamp-om
- **Izveštaj za štampu** - HTML izveštaj (štampa se kroz pregledač)
- **Sortiranje tabele** - klikom na zaglavlje kolone
- **Kontekstni meni** - desni klik na red ili prazan prostor
- **Dvoklik izmena** - brza izmena unosa iz tabele

---

## Instalacija

### Preduvodi
- Python 3.6 ili noviji
- `lxml` paket

### Instalacija na Ubuntu/Debian

```bash
git clone https://github.com/cuparac/OPPSS-test.git
cd OPPSS-test
sudo apt install -y python3-lxml
```

### Instalacija na Windows/Mac

```bash
git clone https://github.com/cuparac/OPPSS-test.git
cd OPPSS-test
pip install lxml
```

---

## Korišćenje

### GUI verzija (desktop)

```bash
python opps_generator_gui_v15.3.py
```

**Glavni meni:**
1. Prikaži tabelu unosa
2. Dodaj novi unos
3. Izmeni unos (ili dvoklik na red u tabeli)
4. Obriši unos
5. Obriši SVE unose (sa potvrdom)
6. Podaci o podnosiocu
7. Generiši XML
8. Promeni godinu

**Prečice tastature:**
| Prečica | Akcija |
|---------|--------|
| Ctrl+N | Novi unos |
| Ctrl+D | Obriši unos |
| Ctrl+G | Generiši XML |
| Ctrl+P | Podaci o podnosioca |
| Ctrl+F | Pretraga |
| Dvoklik | Izmeni unos |
| Desni klik | Kontekstni meni |

**Kontekstni meni (desni klik na red):**
- ✏️ Izmeni unos
- 🗑️ Obriši unos
- 📋 Kopiraj identifikator
- 🔍 Pretraga po ID-ju

**Kontekstni meni (desni klik na prazan prostor):**
- ➕ Dodaj novi
- 🔄 Osveži
- 📊 Statistika

**Sortiranje tabele:**
Kliknite na zaglavlje bilo koje kolone za sortiranje. Ponovni klik menja redosled (rastajući/opadajući).

### CLI verzija (terminal/server)

```bash
python opps_generator_cli_v15.py
```

---

## Istorija unapređenja

### v13.5 - Originalna verzija
- GUI aplikacija sa tkinter interfejsom
- JMBG validacija (osnovna)
- JSON baza podataka
- XML generisanje sa XSD validacijom
- Kalendar widget za izbor datuma

### v13.6 - Ispravke validacije
- **JMBG validacija** - ekstrahuje godinu iz JMBG-a, probava oba raspona (1000-1999 i 2000-2999)
- **tree.index()** - ispravno indeksiranje nakon brisanja reda
- **Datum OD/DO** - dva posebna polja sa kalendar dugmadima
- **File lock** - fcntl.flock() za atomicno čuvanje

### v13.7 - Cross-platform kompatibilnost
- **fcntl na Windows** - atomic write umesto fcntl
- **assert → if** - ispravna validacija iznosa
- **Provera datuma** - sprečava unos krajjeg datuma pre početnog
- **Tabela** - prikaz oba datuma u formatu "DD/MM/YYYY - DD/MM/YYYY"
- **XSD iz memorije** - validacija bez čitanja fajla sa diska
- **strip()** - uklanja sve whitespace umesto samo space
- **Error handling** - za korumpirani JSON

### v13.8 - Nova polja i XSD usklađenost
- **EBS identifikator** - podrška za Jedinstveni broj subjekta (9 cifara)
- **Poljoprivredno gazdinstvo** - opciona polja za broj i naziv
- **Email osobe** - opciono polje za kontakt osobe
- **Validacija JSON strukture** - provera ključeva u bazi

### v13.9 - CLI verzija i prečice
- **CLI verzija** - command-line interfejs za terminal/server
- **Prečice tastature** - Ctrl+N, Ctrl+D, Ctrl+G, Ctrl+P, F1
- **About dijalog** - informacije o aplikaciji
- **Error handling za lxml** - bolje rukovanje greškama

### v14.0 - Standalone verzije
- **CLI standalone** - XSD šema ugrađena u kod
- **GUI standalone** - XSD šema ugrađena u kod
- **.exe kompatibilnost** - spreman za PyInstaller

### v15.0 - SQLite baza i napredne funkcionalnosti
- **SQLite baza** - zamena za JSON (brža, sigurnija, SQL upiti)
- **CSV export** - izvoz u Excel format (sa `;` delimiterom)
- **Pretraga** - po opštini, imenu, identifikatoru, iznosu, datumu
- **Statistika** - ukupno po godini, vrsti prometa, opštini
- **Migracija** - automatska konverzija JSON → SQLite
- **Meni** - Datoteka, Unos, Alat, Pomoć
- **Property ispravke** - ispravan redosled inicijalizacije

### v15.1 - Ispravke bugova iz v15.0
- **Bug 1: DatumEntry kursor** - Kursor se sada može pozicionirati bilo gde u polju za datum. Navigacioni tasteri (⬅ ➡ Home End BackSpace Delete) ne okidaju formatiranje.
- **Bug 2: Provera duplikata** - Upozorenje prilikom unosa postojećeg identifikatora. Ne blokira unos (razlika može biti u datumu/iznosu) ali prikazuje detalje postojećeg unosa.
- **Bug 3: Dvoklik za izmenu** - Dvoklik na red u tabeli otvara formu za izmenu. Dugme menja tekst: "Sačuvaj" za novi unos, "Sačuvaj izmene" za izmenu. Popravljena greška gde polja za datum nisu bila popunjena prilikom izmene.

### v15.2 - Nove funkcionalnosti
- **Brisanje svih unosa** - Opcija za brisanje svih unosa za izabranu godinu sa dva nivoa potvrde
- **Backup baze** - Ručno kopiranje SQLite baze u odabrani folder sa timestamp-om
- **Import iz CSV** - Uvoz podataka iz CSV fajla (podržava različite formate datuma i nazive kolona)
- **Izveštaj za štampu** - HTML izveštaj sa svim podacima, po opštini, i dugmetom za štampu
- **Sortiranje tabele** - Klikom na zaglavlje kolone sortira se tabela (rastajuće/opadajuće)
- **Kontekstni meni** - Desni klik na red (izmeni, obriši, kopiraj ID, pretraga) ili prazan prostor (dodaj, osveži, statistika)

---

## Struktura projekta

```
OPPSS-test/
├── opps_generator_gui_v15.4.py   # Entry point (pokreće aplikaciju)
├── gui.py                       # GUI komponente (App, DatumEntry, Kalendar, Prozori)
├── database.py                  # Database operacije (CRUD, pretraga, statistika, CSV)
├── validacije.py                # Validacione funkcije (JMBG, EBS, datum, XSD)
├── xml_generator.py             # XML/HTML generator (ePorezi prijave, izveštaji)
├── opps.xsd                     # XSD šema za validaciju XML-a
├── tests/                       # Pytest testovi
│   ├── test_database.py
│   ├── test_validacije.py
│   └── test_xml.py
├── docs/                        # Dokumentacija (specovi, planovi)
├── KorisnikouputstvoOPPSS.pdf   # Korisničko uputstvo
├── instalacija_ubuntu_server.txt
├── kreiranje_exe_uputstvo.txt
├── CHANGELOG.md
├── README.md
└── STATUS.md
```

---

## Generisani fajlovi

| Fajl | Opis |
|------|------|
| `baza_2026.db` | SQLite baza podataka |
| `OPPS_prijava_2026.xml` | Generisani XML fajl (za upload na ePorezi) |
| `OPPS_2026.csv` | CSV izveštaj (za Excel) |
| `OPPS_izvestaj_2026.html` | HTML izveštaj (za štampu) |
| `baza_2026_backup_YYYYMMDD_HHMMSS.db` | Backup baze |

---

## Kreiranje .exe fajla (portable)

### Šta je "portable"?
Portable verzija znači da je **sve ugrađeno u jedan fajl**. Ne treba:
- Instalacija
- .NET Framework
- Visual C++ Redistributable
- lxml paketi
- Poseban .xsd fajl
- Bilo koja druga zavisnost

Samo pokrenute `.exe` fajl i radi odmah.

### Uputstvo za kreiranje
Pogledajte `kreiranje_exe_uputstvo.txt` za detaljna uputstva.

---

## Rešavanje problema

### "externally-managed-environment"
```bash
sudo apt install -y python3-lxml
```

### "ModuleNotFoundError: No module named 'lxml'"
```bash
pip install lxml
```

### "ModuleNotFoundError: No module named 'pip'"
```bash
sudo apt install -y python3-pip
```

### "Permission denied"
```bash
python opps_generator_gui_v15.3.py  # bez sudo
```

---

## Licenca

MIT License - slobodno korišćenje i modifikacija.

---

## Kontakt

- **GitHub:** https://github.com/cuparac/OPPSS-test
- **Autor:** cuparac
- **Verzija:** 15.4

---

## Napomena

Ova aplikacija nije zvanični alat Poreske uprave Republike Srbije. Korisnik je odgovoran za ispravnost unetih podataka.
