# OPPS Generator

**Aplikacija za generisanje OPPS prijava (Обавештење о промету пољопривредних производа и секундарних сировина)**

![Version](https://img.shields.io/badge/verzija-16.0-blue)
![Python](https://img.shields.io/badge/python-3.6+-green)
![License](https://img.shields.io/badge/licence-MIT-orange)

---

## Sadržaj

- [O projektu](#o-projektu)
- [Funkcionalnosti](#funkcionalnosti)
- [Instalacija](#instalacija)
- [Korišćenje](#korišćenje)
- [Struktura projekta](#struktura-projekta)
- [Generisani fajlovi](#generisani-fajlovi)
- [Kreiranje .exe fajla](#kreiranje-exe-fajla-portable)
- [Starije verzije](#starije-verzije)
- [Rešavanje problema](#rešavanje-problema)
- [Licenca](#licenca)

---

## O projektu

OPPS Generator je desktop i CLI aplikacija za generisanje XML fajlova namenjenih upload-u na portal **ePorezi** (Poreska uprava Republike Srbije). Aplikacija omogućava unos podataka o podnosiocu i izvršiocima prometa, validaciju unetih podataka, i generisanje XML fajla u skladu sa XSD semom.

**Verzija 16.0** donosi MVC arhitekturu: monolitni `gui.py` (2008 linija) razdvojen je na tri sloja — `model/` (baza, validacije, generator), `view/` (GUI komponente) i `controller.py` (business logika). Time je omogućeno testiranje logike bez GUI-a i lakše održavanje.

Istorija svih verzija je u [CHANGELOG.md](CHANGELOG.md).

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
| JMBG | Jedinstveni matrični broj građana | 13 cifara |
| PIB | Poreski identifikacioni broj | 9 cifara |
| EBS | Jedinstveni broj subjekta | 9 cifara |

### Vrste prometa
| Šifra | Opis |
|-------|------|
| 1 | Unos prometa poljoprivrednih proizvoda i usluga |
| 2 | Unos prometa sekundarnih sirovina |

### Obavezna polja
Vrsta prometa, identifikator (JMBG/PIB/EBS), ime i prezime / naziv, opština, adresa, telefon, datum OD, datum DO, iznos prometa.

### Opciona polja
E-posta osobe, broj poljoprivrednog gazdinstva, naziv poljoprivrednog gazdinstva.

### Rad sa podacima
- **SQLite baza** - po godinama, sa indeksima i UNIQUE constraint-om
- **Više podnosioca** - selektor, dodavanje, brisanje, aktivni podnosilac
- **CSV export / import** - izvoz i uvoz podataka (Excel)
- **Pretraga** - po opštini, imenu, identifikatoru, iznosu, datumu
- **Statistika** - ukupno po godini, vrsti prometa, opštini
- **Napredni filteri** - po vrsti prometa, opštini, rasponu iznosa i datumu
- **Sortiranje tabele** - klikom na zaglavlje kolone
- **Paginacija** - 100 unosa po stranici
- **Undo/Redo** - Ctrl+Z / Ctrl+Y
- **Auto-backup** - backup baze pri svakom pokretanju
- **Migracija** - automatska konverzija JSON → SQLite
- **Drag & drop XML** - povlačenje XML fajla na prozor (Windows)

### Prikaz i izveštaji
- **Tabovi** - Svi unosi, Po opštini, Po vrsti prometa, Po datumu, Grafikoni
- **Grafikoni** - Matplotlib bar/pie chart-ovi
- **Dark theme** - tamna tema preko Alat menija
- **Izveštaji** - HTML (za štampu), PDF (ReportLab), XML (za ePorezi)

### Interfejs
- **Kontekstni meni** - desni klik na red ili prazan prostor
- **Dvoklik izmena** - brza izmena unosa iz tabele
- **Kalendar** - widget za izbor datuma

---

## Instalacija

### Preduvodi
- Python 3.6 ili noviji
- `lxml`, `matplotlib`, `reportlab` paketi

### Instalacija na Ubuntu/Debian

```bash
git clone https://github.com/cuparac/OPPSS-test.git
cd OPPSS-test
sudo apt install -y python3-lxml python3-matplotlib python3-reportlab
```

### Instalacija na Windows/Mac

```bash
git clone https://github.com/cuparac/OPPSS-test.git
cd OPPSS-test
pip install -r requirements.txt
```

---

## Korišćenje

### GUI verzija (desktop)

```bash
python opps_generator_gui_v16.py
```

**Prvi koraci (važno):**

1. **Unesi podnosioca** — `Datoteka → Podaci o podnosiocu` (ili `Ctrl+P`).
   Na praznoj bazi je dovoljno popuniti polja i kliknuti **Sacuvaj** — podnosilac
   se kreira i automatski postaje aktivan. Bez podnosioca XML prijava ne može da
   se generiše.
2. **Dodaj unose** — `+ Dodaj unos` (ili `Ctrl+N`).
3. **Generiši XML** — `GENERISI XML` (ili `Ctrl+G`), pa fajl uploaduj na ePorezi.

**Prečice tastature:**
| Prečica | Akcija |
|---------|--------|
| Ctrl+N | Novi unos |
| Ctrl+D | Obriši unos |
| Ctrl+G | Generiši XML |
| Ctrl+P | Podaci o podnosiocu |
| Ctrl+F | Pretraga |
| Ctrl+Z / Ctrl+Y | Undo / Redo |
| F1 | O aplikaciji |
| Dvoklik | Izmeni unos |
| Desni klik | Kontekstni meni |

### CLI verzija (terminal/server)

```bash
python opps_generator_cli.py
```

---

## Struktura projekta

```
OPPSS-test/
├── opps_generator_gui_v16.py    # Entry point (GUI)
├── opps_generator_cli.py        # CLI verzija
├── controller.py                # Controller — business logika
├── model/
│   ├── __init__.py
│   ├── database.py              # SQLite operacije (CRUD, pretraga, statistika, CSV)
│   ├── validacije.py            # JMBG, EBS, datum, ugrađena XSD šema
│   └── xml_generator.py         # XML / HTML / PDF generator
├── view/
│   ├── __init__.py
│   ├── main_window.py           # Glavni prozor, tabovi, tabela
│   ├── dialogs.py               # Prozori: filteri, podnosioc, pretraga, statistika
│   └── widgets.py               # DatumEntry, Kalendar
├── requirements.txt
├── CHANGELOG.md
├── README.md
└── STATUS.md
```

### Arhitektura

```
Korisnik → View (klik, unos) → Controller (logika) → Model (baza) → Controller → View (ažuriranje)
```

- **Model** — nema GUI zavisnosti
- **View** — ne zavisi od Controller-a (koristi `set_controller()` injekciju)
- **Controller** — zavisi od Model i View (prima kao argumente)

### Pokretanje testova

Integracioni testovi (`tests/test_integration.py`) su **lokalni** — ne nalaze se u
repozitorijumu. Pokreću se iz korena projekta:

```bash
xvfb-run -a python tests/test_integration.py
```

Rezultat: 55 prolazi (0 padova). Sva četiri nasleđena buga iz v15.9 su popravljena.

---

## Generisani fajlovi

| Fajl | Opis |
|------|------|
| `baza_2026.db` | SQLite baza podataka |
| `OPPS_prijava_2026.xml` | Generisani XML fajl (za upload na ePorezi) |
| `OPPS_2026.csv` | CSV izveštaj (za Excel) |
| `OPPS_izvestaj_2026.html` | HTML izveštaj (za štampu) |
| `OPPS_izvestaj_2026.pdf` | PDF izveštaj |
| `baza_2026_backup_YYYYMMDD_HHMMSS.db` | Backup baze |

---

## Kreiranje .exe fajla (portable)

Portable verzija znači da je **sve ugrađeno u jedan fajl** — nije potrebna instalacija, .NET Framework, Visual C++ Redistributable, lxml paketi ni poseban .xsd fajl.

```bash
pyinstaller --onefile --windowed --name "OPPSS_Generator_v16" opps_generator_gui_v16.py
```

Detaljnije uputstvo: `kreiranje_exe_uputstvo.txt`.

---

## Starije verzije

Starije verzije su sačuvane kao git tagovi:

```bash
git tag                 # lista svih verzija (v13.5 ... v15.9)
git checkout v15.9      # preuzimanje stare verzije
git checkout main       # povratak na trenutnu verziju
```

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
python opps_generator_gui_v16.py  # bez sudo
```

---

## Licenca

MIT License - slobodno korišćenje i modifikacija.

---

## Kontakt

- **GitHub:** https://github.com/cuparac/OPPSS-test
- **Autor:** cuparac
- **Verzija:** 16.0

---

## Napomena

Ova aplikacija nije zvanični alat Poreske uprave Republike Srbije. Korisnik je odgovoran za ispravnost unetih podataka.
