# MVC Refaktoring Spec — v16

**Datum:** 2026-10-06
**Verzija:** v16 (mvc-preview)
**Grana:** `mvc-preview`

---

## 1. Cilj

Razdvojiti `gui.py` (2008 linija) na tri sloja:
- **Model** — baza, validacije, XML generator (bez promena u kodu)
- **View** — GUI komponente (prozori, dugmad, tabele)
- **Controller** — logika koja povezuje Model i View

**Princip:** Minimalni MVC — najmanje rizika, najbrža implementacija, lako vraćanje na staro.

---

## 2. Struktura fajlova

```
OPPSS-test/
├── opps_generator_gui_v16.py    # Entry point
├── controller.py                # Controller - logika
├── view/
│   ├── __init__.py
│   ├── main_window.py           # MainWindow (glavni prozor)
│   ├── dialogs.py               # ProzorPodnosioca, ProzorFiltera, ProzorPretrage, ProzorStatistike
│   └── widgets.py               # DatumEntry, Kalendar, kontekstni meniji
├── model/
│   ├── __init__.py
│   ├── database.py              # Database (iz postojećeg)
│   ├── validacije.py            # Validacije (iz postojećeg)
│   └── xml_generator.py         # XML/HTML/PDF generator (iz postojećeg)
├── opps_generator_cli_v15.py    # CLI (nepromenjena)
├── KorisnikouputstvoOPPSS.pdf
├── instalacija_ubuntu_server.txt
├── kreiranje_exe_uputstvo.txt
├── CHANGELOG.md
├── README.md
└── STATUS.md
```

---

## 3. Komponente

### 3.1 Model (`model/`)

**`database.py`** — Sadašnja `Database` klasa, bez promena:
- CRUD operacije (dodaj, izmeni, obriši, pretraga)
- Statistika, CSV import/export
- Auto-backup, migracija

**`validacije.py`** — Sadašnje funkcije, bez promena:
- `validan_jmbg()`, `validan_ebs()`, `konvertuj_datum()`, `get_xsd_schema()`

**`xml_generator.py`** — Sadašnji generatori, bez promena:
- `generisi_xml()`, `generisi_html_izvestaj()`, `generisi_pdf_izvestaj()`

### 3.2 View (`view/`)

**`main_window.py`** — `MainWindow` klasa:
- Glavni prozor, meni, toolbar, status bar
- Notebook sa tabovima
- Tabela sa paginacijom
- Poziva Controller za sve akcije

**`dialogs.py`** — Svi prozori:
- `ProzorPodnosioca` — izbor i upravljanje podnosiocima
- `ProzorFiltera` — napredni filteri
- `ProzorPretrage` — pretraga
- `ProzorStatistike` — statistika
- `ProzorUnosa` — unos/izmena osobe

**`widgets.py`** — Pomoćni widget-i:
- `DatumEntry` — unos datuma sa kalendarom
- `Kalendar` — kalendar widget
- Kontekstni meniji

### 3.3 Controller (`controller.py`)

**`Controller` klasa:**
- Prima događaje iz View-a
- Poziva Model (database, validacije, xml_generator)
- Ažurira View sa rezultatima
- Sadrži `UndoStack` (logika, ne GUI)

**Metode Controller-a:**
- `dodaj_osobu()`, `izmeni_osobu()`, `obrisi_osobu()`, `obrisi_sve()`
- `pretraga()`, `primeni_filter()`, `sort_by()`
- `export_csv()`, `export_html()`, `export_pdf()`, `export_xml()`
- `generisi()`, `undo()`, `redo()`
- `otvori_podnosioca()`, `promeni_godinu()`, `promeni_temu()`

---

## 4. Tok podataka

```
Korisnik → View (klik, unos) → Controller (logika) → Model (baza) → Controller → View (ažuriranje)
```

**Primer — dodavanje osobe:**
1. `MainWindow.on_dodaj_osobu()` → `controller.dodaj_osobu()`
2. `Controller.dodaj_osobu()` → `ProzorUnosa.prikazi()` (View)
3. Korisnik popunjuje formu → `Controller` prima podatke
4. `Controller` → `validacije.validan_jmbg()` (Model)
5. `Controller` → `database.dodaj_osobu()` (Model)
6. `Controller` → `view.osvezi_tabelu()` (View)

---

## 5. Migracija

**Koraci:**
1. Kreirati granu `mvc-preview`
2. Kreirati `model/` folder, prebaciti `database.py`, `validacije.py`, `xml_generator.py`
3. Kreirati `view/` folder, izdvojiti GUI komponente iz `gui.py`
4. Kreirati `controller.py` sa logikom iz `gui.py`
5. Ažurirati `opps_generator_gui_v16.py` entry point
6. Testirati sve funkcionalnosti

**Testiranje:**
- Dodaj, izmeni, obriši unos
- Pretraga, filteri, sortiranje
- Export CSV, HTML, PDF, XML
- Undo/Redo
- Podnosioc (izbor, brisanje)
- Dark theme
- Tabovi, grafikoni, paginacija

---

## 6. Rizici i mitigacija

| Rizik | Mitigacija |
|-------|------------|
| Greška u komunikaciji Controller ↔ View | Testiranje nakon svakog koraka |
| Greška u prebacivanju koda | Postepena migracija, commit po koraku |
| Gubitak funkcionalnosti | Lista za testiranje, poređenje sa starom verzijom |
| Vreme implementacije | ~2-3 sata, može se pauzirati |

---

## 7. Kriteriji uspeha

- [ ] Aplikacija se pokreće bez grešaka
- [ ] Sve funkcionalnosti rade kao pre
- [ ] Kod je podeljen na model/, view/, controller.py
- [ ] Nema dupliranog koda
- [ ] Lak je za čitanje i održavanje
