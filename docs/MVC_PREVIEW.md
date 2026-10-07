# OPPSS Generator v16 — MVC Preview

**Verzija:** v16 (mvc-preview)
**Grana:** `mvc-preview`
**Datum:** 07.10.2026.
**Status:** Spremno za testiranje

---

## Pregled

MVC refaktoring je razdvojio monolitni `gui.py` (2008 linija) na tri sloja:

- **Model** (`model/`) — baza, validacije, XML generator (bez GUI koda)
- **View** (`view/`) — GUI komponente (prozori, dugmad, tabele)
- **Controller** (`controller.py`) — logika koja povezuje Model i View

---

## Struktura fajlova

```
OPPSS-test/
├── opps_generator_gui_v16.py    # Entry point (MVC)
├── controller.py                # Controller - logika (706 linija)
├── gui.py                       # Backward-compat shim (16 linija)
├── view/
│   ├── __init__.py
│   ├── main_window.py           # MainWindow (951 linija)
│   ├── dialogs.py               # ProzorFiltera, ProzorPodnosioca, ProzorPretrage, ProzorStatistike (416 linija)
│   └── widgets.py               # DatumEntry, Kalendar (219 linija)
├── model/
│   ├── __init__.py
│   ├── database.py              # Database (482 linija)
│   ├── validacije.py            # Validacije (193 linija)
│   └── xml_generator.py         # XML/HTML/PDF generator (248 linija)
├── tests/
│   └── test_integration.py      # 41 integration test (774 linije)
├── opps_generator_gui_v15.9.py  # Stari entry point (referenca)
├── opps_generator_cli_v15.py    # CLI verzija (nepromenjena)
├── CHANGELOG.md
├── README.md
└── STATUS.md
```

---

## Instalacija

### Preuzmi repozitorijum

```bash
git clone https://github.com/cuparac/OPPSS-test.git
cd OPPSS-test
git checkout mvc-preview
```

### Instaliraj zavisnosti

```bash
pip install lxml matplotlib reportlab
```

### Pokreni aplikaciju

```bash
python opps_generator_gui_v16.py
```

---

## Testiranje

### Automatski testovi

```bash
xvfb-run -a python tests/test_integration.py
```

**Rezultat:** 41 test | 38 PASS | 3 XFAIL (poznati nasleđeni bugovi) | 0 neočekivanih padova

### Ručno testiranje — proveri sledeće

#### 1. CRUD operacije
- [ ] Dodaj novi unos (Ctrl+N)
- [ ] Izmeni postojeći unos (dvoklik na red)
- [ ] Obriši unos (Ctrl+D)
- [ ] Obriši sve unose

#### 2. Pretraga i filteri
- [ ] Pretraga po opštini
- [ ] Pretraga po imenu
- [ ] Pretraga po identifikatoru
- [ ] Filter po vrsti prometa
- [ ] Filter po opštini
- [ ] Filter po datumu

#### 3. Export
- [ ] Export CSV
- [ ] Export HTML
- [ ] Export PDF
- [ ] Export XML

#### 4. Undo/Redo
- [ ] Ctrl+Z (undo)
- [ ] Ctrl+Y (redo)

#### 5. Podnosioc
- [ ] Izbor podnosioca
- [ ] Brisanje podnosioca

#### 6. Dark theme
- [ ] Uključi dark theme
- [ ] Isključi dark theme

#### 7. Tabovi i grafikoni
- [ ] Svi unosi tab
- [ ] Po opštini tab
- [ ] Po vrsti prometa tab
- [ ] Po datumu tab
- [ ] Grafikoni tab

#### 8. Paginacija
- [ ] Prva strana
- [ ] Prethodna strana
- [ ] Sledeća strana
- [ ] Poslednja strana

---

## Poznati bugovi (nasleđeni iz v15.9, ne regresije)

Ovi bugovi postoje i u v15.9, nisu uvedeni MVC refaktoringom:

| # | Bug | Trigger | Greška |
|---|-----|---------|--------|
| 1 | Statistika prozor | Otvaranje Statistika | `TypeError: string indices must be integers` |
| 2 | Pretraga prozor | Bilo koja pretraga | `sqlite3.ProgrammingError: Incorrect number of bindings` |
| 3 | Search criteria `iznos_od/iznos_do/datum_od/datum_do` | Odabir kriterijuma | `no such column: iznos_od` |
| 4 | Malformiran datum | Sačvanje sa lošim datumom | `ValueError` (neuhvaćen) |
| 5 | Kolone posle filtera | Filtriranje tabele | 7 vrednosti u 9 kolona (pomeranje) |

---

## Arhitektura

### Tok podataka

```
Korisnik → View (klik, unos) → Controller (logika) → Model (baza) → Controller → View (ažuriranje)
```

### Zavisnosti

- **Model** — nema GUI zavisnosti
- **View** — ne zavisi od Controller-a (koristi `set_controller()` injekciju)
- **Controller** — zavisi od Model i View (prima kao argumente)

### Ključne klase

| Klasa | Fajl | Odgovornost |
|-------|------|-------------|
| `Database` | `model/database.py` | CRUD, pretraga, statistika, CSV |
| `validan_jmbg`, `validan_ebs`, `konvertuj_datum` | `model/validacije.py` | Validacija podataka |
| `generisi_xml`, `generisi_html_izvestaj`, `generisi_pdf_izvestaj` | `model/xml_generator.py` | Generisanje fajlova |
| `MainWindow` | `view/main_window.py` | Glavni prozor, tabovi, tabela |
| `DatumEntry`, `Kalendar` | `view/widgets.py` | Widget-i za unos datuma |
| `ProzorFiltera`, `ProzorPodnosioca`, `ProzorPretrage`, `ProzorStatistike` | `view/dialogs.py` | Dijalozi |
| `Controller` | `controller.py` | Sva business logika |
| `UndoStack` | `controller.py` | Undo/Redo operacije |

---

## Final review

**Verdict:** Ready to merge — Yes with minor fixes

**Architecture:** Clean MVC separation. Model (zero GUI deps), View (thin delegation), Controller (mediates). gui.py reduced to 16-line backward-compat shim.

**Completeness:** All major components extracted. forma_osobe() remains in View (acceptable for minimal MVC).

**Testing:** 41 integration tests: 38 pass, 3 inherited v15.9 bugs documented as XFAIL (not regressions).

**Minor gaps (non-blocking):**
- forma_osobe() not extracted to ProzorUnosa dialog
- No CI configuration
- Controller imports tkinter (pragmatic)
- View directly accesses DB in some methods
- Version strings inconsistent (inherited)

---

## Merge u main

Ako ti se sviđa preview, možemo merge-ovati u `main`:

```bash
git checkout main
git merge mvc-preview
```

Ili ako ne, vraćamo se na staro:

```bash
git checkout main
```

---

## Kontakt

- **GitHub:** https://github.com/cuparac/OPPSS-test
- **Autor:** cuparac
- **Verzija:** 16 (mvc-preview)
