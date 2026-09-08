# OPPS Generator

**Aplikacija za generisanje OPPS prijava (Обавештење о промету пољопривредних производа и секундарних сировина)**

![Version](https://img.shields.io/badge/verzija-15.0-blue)
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

**Verzija 15.0** koristi **SQLite bazu** umesto JSON, sa mogućnošću CSV exporta, pretrage i izveštaja.

---

## Funkcionalnosti

### Validacija podataka
- **JMBG** (13 cifara) - provera datuma i kontrolne cifre
- **PIB** (9 cifara) - provera dužine
- **EBS** (9 cifara) - provera dužine
- **Datumi** - provera ispravnosti i redosleda (OD ≤ DO)
- **Iznos** - provera pozitivnog celog broja

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

### Dodatne funkcionalnosti (v15)
- **SQLite baza** - brža i sigurnija od JSON
- **CSV export** - izvoz u Excel format
- **Pretraga** - po opštini, imenu, identifikatoru, iznosu
- **Statistika** - ukupno po godini, vrsti prometa, opštini
- **Migracija** - automatska konverzija JSON → SQLite

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
python opps_generator_gui_v15.py
```

**Glavni meni:**
1. Prikaži tabelu unosa
2. Dodaj novi unos
3. Izmeni unos
4. Obriši unos
5. Podaci o podnosiocu
6. Generiši XML
7. Promeni godinu

**Prečice tastature:**
| Prečica | Akcija |
|---------|--------|
| Ctrl+N | Novi unos |
| Ctrl+D | Obriši unos |
| Ctrl+G | Generiši XML |
| Ctrl+P | Podaci o podnosioca |
| Ctrl+F | Pretraga |
| F1 | O aplikaciji |

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

---

## Struktura projekta

```
OPPSS-test/
├── opps_generator_gui_v15.py          # GUI v15 (SQLite, CSV, pretraga)
├── opps_generator_cli_v15.py          # CLI v15 (SQLite, CSV, pretraga)
├── opps.xsd                           # XSD šema za validaciju XML-a
├── KorisnikouputstvoOPPSS.pdf         # Korisničko uputstvo
├── instalacija_ubuntu_server.txt      # Uputstvo za Ubuntu Server
├── kreiranje_exe_uputstvo.txt         # Uputstvo za kreiranje .exe
└── README.md                          # Ovaj fajl
```

---

## Generisani fajlovi

| Fajl | Opis |
|------|------|
| `baza_2026.db` | SQLite baza podataka |
| `OPPS_prijava_2026.xml` | Generisani XML fajl (za upload na ePorezi) |
| `OPPS_2026.csv` | CSV izveštaj (za Excel) |

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
python opps_generator_gui_v15.py  # bez sudo
```

---

## Licenca

MIT License - slobodno korišćenje i modifikacija.

---

## Kontakt

- **GitHub:** https://github.com/cuparac/OPPSS-test
- **Autor:** cuparac
- **Verzija:** 15.0

---

## Napomena

Ova aplikacija nije zvanični alat Poreske uprave Republike Srbije. Korisnik je odgovoran za ispravnost unetih podataka.
