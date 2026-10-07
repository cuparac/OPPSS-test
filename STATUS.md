# STATUS — OPPS Generator v15.9

**Poslednji put ažurirano:** 07.10.2026.
**Trenutna verzija:** v15.9
**Lokacija koda:** `/home/ai/OPPSS-test/gui.py`
**GitHub:** https://github.com/cuparac/OPPSS-test
**Git commit:** `c0f466d`

---

## ✅ ŠTA JEURAĐENO

### v13.5 — Originalna verzija
- GUI aplikacija sa tkinter interfejsom
- JMBG validacija (osnovna)
- JSON baza podataka
- XML generisanje sa XSD validacijom
- Kalendar widget za izbor datuma

### v13.6 — Ispravke validacije
- **JMBG validacija** - ekstrahuje godinu iz JMBG-a, probava oba raspona (1000-1999 i 2000-2999)
- **tree.index()** - ispravno indeksiranje nakon brisanja reda
- **Datum OD/DO** - dva posebna polja sa kalendar dugmadima
- **File lock** - fcntl.flock() za atomicno čuvanje

### v13.7 — Cross-platform kompatibilnost
- **fcntl na Windows** - atomic write umesto fcntl
- **assert → if** - ispravna validacija iznosa
- **Provera datuma** - sprečava unos krajnjeg datuma pre početnog
- **Tabela** - prikaz oba datuma u formatu "DD/MM/YYYY - DD/MM/YYYY"
- **XSD iz memorije** - validacija bez čitanja fajla sa diska
- **strip()** - uklanja sve whitespace umesto samo space
- **Error handling** - za korumpirani JSON

### v13.8 — Nova polja i XSD usklađenost
- **EBS identifikator** - podrška za Jedinstveni broj subjekta (9 cifara)
- **Poljoprivredno gazdinstvo** - opciona polja za broj i naziv
- **Email osobe** - opciono polje za kontakt osobe
- **Validacija JSON strukture** - provera ključeva u bazi

### v13.9 — CLI verzija i prečice
- **CLI verzija** - command-line interfejs za terminal/server
- **Prečice tastature** - Ctrl+N, Ctrl+D, Ctrl+G, Ctrl+P, F1
- **About dijalog** - informacije o aplikaciji
- **Error handling za lxml** - bolje rukovanje greškama

### v14.0 — Standalone verzije
- **CLI standalone** - XSD šema ugrađena u kod
- **GUI standalone** - XSD šema ugrađena u kod
- **.exe kompatibilnost** - spreman za PyInstaller

### v15.0 — SQLite baza i napredne funkcionalnosti
- **SQLite baza** - zamena za JSON (brža, sigurnija, SQL upiti)
- **CSV export** - izvoz u Excel format (sa `;` delimiterom)
- **Pretraga** - po opštini, imenu, identifikatoru, iznosu, datumu
- **Statistika** - ukupno po godini, vrsti prometa, opštini
- **Migracija** - automatska konverzija JSON → SQLite
- **Meni** - Datoteka, Unos, Alat, Pomoć
- **Property ispravke** - ispravan redosled inicijalizacije

### v15.1 — Ispravke bugova iz v15.0
- **Bug 1: DatumEntry kursor** - Kursor se sada može pozicionirati bilo gde u polju za datum
- **Bug 2: Provera duplikata** - Upozorenje prilikom unosa postojećeg identifikatora (ne blokira)
- **Bug 3: Dvoklik za izmenu** - Dvoklik na red u tabeli otvara formu za izmenu. Dugme menja tekst

### v15.2 — Nove funkcionalnosti (ZAVRŠENO 15.09.2026)
- **Brisanje svih unosa** - sa dva nivoa potvrde
- **Backup baze** - ručno kopiranje SQLite fajla sa timestamp-om
- **Import iz CSV** - podržava različite formate datuma i nazive kolona
- **Izveštaj za štampu** - HTML izveštaj (štampa se kroz pregledač)
- **Sortiranje tabele** - klikom na zaglavlje kolone
- **Kontekstni meni** - desni klik na red ili prazan prostor
- **Test suite** - 14 testova koji prolaze uspešno

### v15.3 — Kvalitet koda (ZAVRŠENO 19.09.2026)
- **Modularna arhitektura** - Podela na 5 modula (gui.py, database.py, validacije.py, xml_generator.py, entry point)
- **Type hintovi** - Anotacije na svim javnim funkcijama
- **Docstringovi** - Google stil za sve klase i javne metode
- **Logging** - Zamena print() sa logging modulom
- **Pytest testovi** - 25 testova (database, validacije, XML generator)
- **HTML injection fix** - html.escape() na sve dinamičke vrednosti u HTML izveštaju
- **Placeholder podnosioc fix** - ValueError umesto podrazumevanih vrednosti

### v15.4 — Funkcionalnosti (ZAVRŠENO 19.09.2026)
- **Auto-backup baze** - Automatski backup pri svakom pokretanju (`backup_baza_{godina}_{timestamp}.db`)
- **Pametni duplikati** - Provera identifikator + datum, dijalog Zameni/Dodaj kao novi/Preskoči
- **PDF export** - PDF izveštaj preko pregledača (Ctrl+P, bez dodatnih biblioteka)
- **Undo/Redo** - Ctrl+Z/Ctrl+Y za poništavanje i ponavljanje operacija
- **Drag & drop XML upload** - Povuci XML fajl na prozor za učitavanje (Windows)
- **Napredni filteri** - Filter po vrsti prometa, opštini i range iznosa (min/max)

### v15.5 — Više podnosioca (ZAVRŠENO 05.10.2026)
- **Migracija baze** - Tabela `podnosioc` sa `godina` PK na `id` PK, dodata `naziv` i `aktivan` polja
- **Više podnosioca** - Podržano više podnosioca u istoj bazi (različiti PIB/JMBG, opštine, vrste prometa)
- **Selektor podnosioca** - Combobox u ProzorPodnosioca za izbor između podnosioca
- **Upravljanje podnosiocima** - Dugmad + Novi / - Obriši / Aktivan
- **XML import** - Podnosioc iz XML-a se dodaje kao novi i postavlja kao aktivan
- **XML export** - Koristi se aktivni podnosilac za generisanje prijave
- **Migracija postojeće baze** - Automatska konverzija stare tabele (godina PK → id PK)

### v15.6 — Napredni filteri i sortiranje (ZAVRŠENO 05.10.2026)
- **Napredni filteri** - Filter po datumu: "Samo ove godine", "Samo ovog meseca"
- **Sortiranje tabele** - Status label istabele prikazuje trenutno sortiranje (kolona + smer)

### v15.7 — Tabovi, grafikoni i dark theme (ZAVRŠENO 05.10.2026)
- **Tabovi (kartice)** - Notebook sa 5 tabova: Svi unosi, Po opštini, Po vrsti prometa, Po datumu, Grafikoni
- **Grafikoni** - Matplotlib bar/pie chart-ovi po opštini i vrsti prometa
- **Dark theme** - Tamna tema preko Alat menija (🌙 Dark theme)

### v15.8 — Performanse (ZAVRŠENO 05.10.2026)
- **Indeksi u bazi** - UNIQUE constraint na (identifikator, datum, godina) + 5 indeksa (godina, identifikator, datum, opstina, vrsta_prometa)
- **Lazy loading** - Paginacija tabele (100 unosa po stranici) sa dugmadima << Prva / < Prethodna / Sledeća > / Poslednja >>
- **Keširanje XSD seme** - XSD šema se učitava samo jednom i kešira u memoriji

### v15.9 — PDF export i ispravke (ZAVRŠENO 05.10.2026)
- **Pravi PDF export** - ReportLab umesto HTML izveštaja
- **Auto-backup fix** - briše stari backup pre kreiranja novog

---

## ❌ ŠTA NIJE URAĐENO — Preporuke za unapređenja

### Kvalitet koda (preporučujem prvo)
1. **Refaktoring na OOP** - Razdvojiti logiku od GUI-a (MVC pattern). Trenutno je sve u jednoj klasi što otežava održavanje

### Funkcionalnosti (preporučujem)
2. **Export u PDF** - Umjesto HTML izveštaja, praviti pravi PDF (ReportLab ili WeasyPrint)
3. **Napredni filteri** - Range slider za iznos, opcija "samo ove godine", "samo ovog meseca"

### GUI poboljšanja
4. **Sortiranje tabele — tooltip** - Prikaži tooltip kada je sortirano
5. **Pregled unosa — kartice** - Tabovi za različite pregledi (po opštini, vrsti prometa, datumu)
6. **Grafikoni** - Matplotlib grafikon po opštini, vrsti prometa
7. **Dark theme** - Tamna tema

### Sigurnost (odložiti za kasnije)
8. **Lozinka za pristup bazi** - Šifrovanje baze lozinkom
9. **Enkripcija baze** - SQLCipher ili slično
10. **Audit log** - Evidencija ko je šta menjao i kada

### Performanse (odložiti za kasnije)
11. **Indeksi u bazi** - UNIQUE constraint na (identifikator, datum, godina)
12. **Lazy loading** - Učitavanje po stranicama za velike tabele (500+ unosa)
13. **Keširanje XSD seme** - Jedno učitavanje pri startu aplikacije

### Refaktoring (odložiti za kasnije)
14. **MVC pattern** - Razdvojiti Model (baza), View (GUI), Controller (logiku) — **urađeno u v16 (grana `mvc-preview`)**

---

## 📁 STRUKTURA PROJEKTA

```
OPPSS-test/
├── gui.py                               # GUI v15.5 (aktuelna verzija)
├── database.py                          # Database modul (SQLite)
├── validacije.py                        # Validacije (JMBG, EBS, datum)
├── xml_generator.py                     # XML i HTML generator
├── opps.xsd                             # XSD šema za validaciju XML-a
├── KorisnikouputstvoOPPSS.pdf           # Korisničko uputstvo
├── instalacija_ubuntu_server.txt        # Uputstvo za Ubuntu Server
├── kreiranje_exe_uputstvo.txt           # Uputstvo za kreiranje .exe
├── CHANGELOG.md                         # Istorija izmena
├── README.md                            # Dokumentacija
└── STATUS.md                            # Ovaj fajl (status i preporuke)
```

---

## 🧪 TESTIRANJE

### Pokretanje testova:
```bash
python3 -m pytest tests/ -q
```

### Pokretanje aplikacije (Linux sa Xvfb):
```bash
xvfb-run python3 gui.py
```

### Pokretanje na Windows/Mac:
```bash
python gui.py
```

---

## 📌 NAPOMENE

- **Token za GitHub:** Sačuvan u `~/.config/git/credentials_opps` (važi do 15. oktobra 2026)
- **Push na GitHub:** `git config credential.helper 'store --file ~/.config/git/credentials_opps' && git push origin main`
- **Backup baze:** Automatski pri pokretanju (`backup_baza_{godina}_{timestamp}.db`)
- **PDF export:** Trenutno se radi preko HTML i štampe iz pregledača (Ctrl+P)
- **JMBG validacija:** Proverava datum (oba raspona 1000-1999 i 2000-2999) i kontrolnu cifru
- **XSD šema:** Ugrađena u kod, ne zahteva poseban .xsd fajl
- **Podržane platforme:** Windows, Mac, Linux (Python 3.6+, lxml)

---

## 🎯 PREOSTALI ZADACI (za v16)

### Sigurnost (odložiti za kasnije)
1. **Lozinka za pristup bazi** - Šifrovanje baze lozinkom
2. **Enkripcija baze** - SQLCipher ili slično
3. **Audit log** - Evidencija ko je šta menjao i kada

### Refaktoring (odložiti za kasnije)
4. **MVC pattern** - Razdvojiti Model (baza), View (GUI), Controller (logiku)

---

**Kontakt:** Milan Jankovic (Telegram: @cuparac)
**GitHub token ističe:** 15. oktobar 2026.
