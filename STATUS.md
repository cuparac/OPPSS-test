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
- **Id podnosioca se ponovo koristi** posle brisanja
- **Brisanje aktivnog podnosioca** — preostali preuzima aktivnost
- **Prozor za duplikat** — tri jasne opcije (Zameni / Dodaj kao novi / Ne snimaj)
  i popunjavanje forme podacima postojećeg unosa
- **UNIQUE ograničenje uklonjeno** — omogućeno „Dodaj kao novi"
- **Prepis podataka** — ponovni unos istog JMBG/PIB/EBS prepisuje podatke iz
  prethodnog unosa (datumi i iznos ostaju prazni za novi period)
- **Upozorenje na različite podatke** — ako isti JMBG ima različitu opštinu/adresu/
  ime/telefon u svojim unosima, prikazuje se upozorenje sa svim vrednostima
- **Enter prelazi na sledeće polje** (kao Tab); snimanje je na dugmetu „Sačuvaj"
- **Prozor za duplikat: Enter potvrđuje**, strelice/Tab pomeraju između opcija
- **Broj telefona prima samo cifre** — polje odbija slova odmah pri kucanju
  (dozvoljeni: cifre, razmak, `+`, `-`, `/`), pri snimanju se u bazu upisuju samo
  cifre; unos bez cifara ili van opsega 6–15 cifara se odbija porukom. Isto i za
  formu podnosioca, DB sloj i CLI (CSV uvoz ne prolazi kroz GUI)
- **PDF izveštaj prikazuje ćirilicu** — ugrađeni `Helvetica` nema ćirilične
  glifove (crni kvadratići); sada se koristi sistemski font sa ćirilicom
  (DejaVu / Liberation / Noto, Arial / Tahoma / Verdana / Calibri na Windowsu)
- **CLI radi nad bazom koju koristi GUI** — CLI je imao staru strukturu tabele
  `podnosioc` (kolona `godina`), pa je nad GUI bazom pucao sa
  `no such column: godina`; sada je struktura ista (id PK, naziv, aktivan) uz
  automatsku migraciju starih baza
- **CLI unos ne zadržava prethodne vrednosti** — nema više `[stara vrednost]` u
  zagradama; sve se unosi ispočetka

### Testovi (lokalno)
- **Integracioni testovi** (`tests/test_integration.py`) — 99 testova kroz ceo Model + View + Controller stack
  - 99 prolazi
  - 0 padova, 0 poznatih bugova
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

## Ispravljeni bugovi nasleđeni iz v15.9

Sva četiri su popravljena u v16 (i u v15.9):

| # | Bug | Trigger | Greška (pre) | Rešenje |
|---|-----|---------|--------------|---------|
| 1 | Statistika prozor | Otvaranje Statistika | `TypeError` / `KeyError 'ukupno_unosa'` | `statistika()` vraća liste reči, dijalog ih tako čita |
| 2 | Pretraga prozor | Bilo koja pretraga | `ProgrammingError` / `no such column: ime` | nova `Database.pretrazi_po()` |
| 3 | Malformiran datum | Snimanje sa lošim datumom | neuhvaćen `ValueError` | `konvertuj_datum()` u `try/except` |
| 4 | Kolone posle filtera | Filtriranje tabele | 7 vrednosti u 9 kolona | upisuje svih 9 kolona |

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
│   └── test_integration.py      # Integracioni testovi (63)
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
Nema — sva četiri nasleđena buga iz v15.9 su popravljena (statistika, pretraga, filter kolone, datum),
a telefon sada prima samo cifre (07.10.2026).

---

## 📌 NAPOMENE

- **Backup baze:** Automatski pri pokretanju (`backup_baza_{godina}_{timestamp}.db`)
- **JMBG validacija:** Proverava datum (oba raspona 1000-1999 i 2000-2999) i kontrolnu cifru
- **XSD šema:** Ugrađena u kod (`model/validacije.py`), ne zahteva poseban .xsd fajl
- **Podržane platforme:** Windows, Mac, Linux (Python 3.6+, lxml)

---

**Kontakt:** Milan Jankovic (Telegram: @cuparac)
