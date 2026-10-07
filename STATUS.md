# STATUS — OPPS Generator v16.0

**Poslednji put ažurirano:** 07.10.2026.
**Trenutna verzija:** v16.0
**Lokacija koda:** `/home/ai/OPPSS-test/`
**GitHub:** https://github.com/cuparac/OPPSS-test
**Grana:** `main`

---

## ✅ ŠTA JE URAĐENO — v16.0 (MVC refaktoring)

### Arhitektura
- **Model / View / Controller** — monolitni `gui.py` (2008 linija) razdvojen na tri sloja:
  - `model/database.py` — SQLite operacije (CRUD, pretraga, statistika, CSV)
  - `model/validacije.py` — JMBG, EBS, datum, ugrađena XSD šema
  - `model/xml_generator.py` — XML / HTML / PDF generator
  - `view/main_window.py` — glavni prozor, tabovi, tabela, paginacija
  - `view/dialogs.py` — ProzorFiltera, ProzorPodnosioca, ProzorPretrage, ProzorStatistike
  - `view/widgets.py` — DatumEntry, Kalendar
  - `controller.py` — business logika, povezuje Model i View

### Ispravke
- **Naslov prozora** — prikazivao je v15.3, sada v16
- **Dijalog O aplikaciji** — prikazivao je v15.7, sada v16
- **Prvi podnosilac na praznoj bazi** — bez ovoga generisanje XML prijave nije
  moglo da se završi (vidi CHANGELOG)

### Testovi (lokalno)
- **Integracioni testovi** (`tests/test_integration.py`) — 45 testova kroz ceo Model + View + Controller stack
  - 42 prolazi
  - 3 poznata buga nasleđena iz v15.9, markirana kao XFAIL
  - Testovi su **lokalni** — ne nalaze se u repozitorijumu (u `.gitignore`)
  - Pokretanje: `xvfb-run -a python tests/test_integration.py`

### Struktura repozitorijuma
- Uklonjeno: `gui.py` (shim), `opps_generator_gui_v15.9.py`, `opps.xsd` (šema je u kodu), `docs/superpowers/`, `tests/` (lokalno testiranje)
- Preimenovano: `opps_generator_cli_v15.py` → `opps_generator_cli.py`

### Važno pri korišćenju
- Prvi podnosilac se unosi preko **Datoteka → Podaci o podnosiocu** (ili Ctrl+P).
  Na praznoj bazi je dovoljno popuniti polja i kliknuti **Sacuvaj** — podnosilac
  se kreira i automatski postaje aktivan. Bez podnosioca XML prijava ne može da
  se generiše.

---

## Poznati bugovi (nasleđeni iz v15.9, nisu regresije)

| # | Bug | Trigger | Greška |
|---|-----|---------|--------|
| 1 | Statistika prozor | Otvaranje Statistika | `TypeError: string indices must be integers` |
| 2 | Pretraga prozor | Bilo koja pretraga | `sqlite3.ProgrammingError: Incorrect number of bindings` |
| 3 | Malformiran datum | Snimanje sa lošim datumom | `ValueError` (neuhvaćen) |
| 4 | Kolone posle filtera | Filtriranje tabele | 7 vrednosti u 9 kolona (pomeranje) |

---

## 📁 STRUKTURA PROJEKTA

```
OPPSS-test/
├── opps_generator_gui_v16.py    # Entry point (GUI)
├── opps_generator_cli.py        # CLI verzija
├── controller.py                # Controller — business logika
├── model/
│   ├── __init__.py
│   ├── database.py              # SQLite operacije
│   ├── validacije.py            # JMBG, EBS, datum, ugrađena XSD šema
│   └── xml_generator.py         # XML / HTML / PDF generator
├── view/
│   ├── __init__.py
│   ├── main_window.py           # Glavni prozor, tabovi, tabela
│   ├── dialogs.py               # Prozori: filteri, podnosioc, pretraga, statistika
│   └── widgets.py               # DatumEntry, Kalendar
├── tests/
│   └── test_integration.py      # Integracioni testovi (45)
├── KorisnikouputstvoOPPSS.pdf
├── instalacija_ubuntu_server.txt
├── kreiranje_exe_uputstvo.txt
├── requirements.txt
├── CHANGELOG.md
├── README.md
└── STATUS.md
```

---

## 🧪 TESTIRANJE

Integracioni testovi su lokalni (`tests/` je u `.gitignore`) i pokreću se iz korena projekta.

```bash
# Integracioni testovi (headless)
xvfb-run -a python tests/test_integration.py

# Aplikacija (Linux sa Xvfb)
xvfb-run -a python opps_generator_gui_v16.py

# Aplikacija (Windows/Mac)
python opps_generator_gui_v16.py
```

---

## Starije verzije

Sve starije verzije (v13.5–v15.9) su sačuvane kao git tagovi:

```bash
git tag                 # lista verzija
git checkout v15.9      # preuzimanje stare verzije
git checkout main       # povratak na trenutnu verziju
```

---

## 🎯 PREOSTALI ZADACI

### Sigurnost (odložiti za kasnije)
1. **Lozinka za pristup bazi** - Šifrovanje baze lozinkom
2. **Enkripcija baze** - SQLCipher ili slično
3. **Audit log** - Evidencija ko je šta menjao i kada

### Poznati bugovi
4. **Statistika / Pretraga / filter kolone / datum** - 4 buga nasleđena iz v15.9 (vidi tabelu gore)

---

## 📌 NAPOMENE

- **Backup baze:** Automatski pri pokretanju (`backup_baza_{godina}_{timestamp}.db`)
- **JMBG validacija:** Proverava datum (oba raspona 1000-1999 i 2000-2999) i kontrolnu cifru
- **XSD šema:** Ugrađena u kod (`model/validacije.py`), ne zahteva poseban .xsd fajl
- **Podržane platforme:** Windows, Mac, Linux (Python 3.6+, lxml)

---

**Kontakt:** Milan Jankovic (Telegram: @cuparac)
