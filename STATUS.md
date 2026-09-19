# STATUS — OPPS Generator v15.3

**Poslednji put ažurirano:** 19.09.2026.
**Trenutna verzija:** v15.3
**Lokacija koda:** `/home/ai/OPPSS-test/gui.py`
**GitHub:** https://github.com/cuparac/OPPSS-test
**Git commit:** `d20c258`

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

---

## ❌ ŠTA NIJE URAĆENO — Preporuke za unapređenja

### Kvalitet koda (preporučujem prvo)
1. **Refaktoring na OOP** - Razdvojiti logiku od GUI-a (MVC pattern). Trenutno je sve u jednoj klasi što otežava održavanje
2. **Type hintovi** - Dodati `typing` module i anotacije za sve funkcije
3. **Docstringovi** - Google/Sphinx stil dokumentacije za sve klase i funkcije
4. **Unit testovi** - pytest framework umijesto trenutnog custom test runner-a
5. **Logging** - Zamjena `print()` i `messagebox.showerror()` sa `logging` modulom

### Funkcionalnosti (preporučujem)
6. **Export u PDF** - Umjesto HTML izveštaja, praviti pravi PDF (ReportLab ili WeasyPrint)
7. **Auto-backup** - Automatski backup baze pri svakom pokretanju
8. **Duplikati — pametna izbora** - Kada se pronađe duplikat, ponudi opciju "zamijeni", "dodaj kao novi", "preskoči"
9. **Više sekcija** - Podržati više podnosioca u istoj bazi (po opštini, vrsti prometa)
10. **Undo/Redo** - Poništi/ponovi operacije (brisanje, izmena)
11. **Drag & drop XML upload** - Povuci XML fajl da učitaš postojeću prijavu
12. **Napredni filteri** - Range slider za iznos, opcija "samo ove godine", "samo ovog meseca"

### GUI poboljšanja
13. **Sortiranje tabele — tooltip** - Prikaži tooltip kada je sortirano
14. **Pregled unosa — kartice** - Tabovi za različite pregledi (po opštini, vrsti prometa, datumu)
15. **Grafikoni** - Matplotlib grafikon po opštini, vrsti prometa
16. **Dark theme** - Tamna tema (zatražio Milan — vjerovatno ne treba?)

### Sigurnost (odložiti za kasnije)
17. **Lozinka za pristup bazi** - Šifrovanje baze lozinkom
18. **Enkripcija baze** - SQLCipher ili slično
19. **Audit log** - Evidencija ko je šta menjao i kada

### Performanse (odložiti za kasnije)
20. **Indeksi u bazi** - UNIQUE constraint na (identifikator, datum, godina)
21. **Lazy loading** - Učitavanje po stranicama za velike tabele (500+ unosa)
22. **Keširanje XSD seme** - Jedno učitavanje pri startu aplikacije

---

## 📁 STRUKTURA PROJEKTA

```
OPPSS-test/
├── opps_generator_gui_v15.2.py          # GUI v15.2 (aktuelna verzija)
├── opps_generator_cli_v15.py            # CLI v15
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

### Pokretanje testova (Linux sa Xvfb):
```bash
# Kreiraj virtualno okruženje
python3.11 -m venv /tmp/test_venv
/tmp/test_venv/bin/pip install lxml

# Kopiraj fajl za import (zbog imena sa tačkom)
cp opps_generator_gui_v15.2.py opps_generator_gui_v15_2.py

# Pokreni testove pod Xvfb
xvfb-run /tmp/test_venv/bin/python3.11 test_opps.py
```

### Pokretanje aplikacije (Linux sa Xvfb):
```bash
xvfb-run python3.11 opps_generator_gui_v15.2.py
```

### Pokretanje na Windows/Mac:
```bash
python opps_generator_gui_v15.2.py
```

---

## 📌 NAPOMENE

- **Token za GitHub:** Sačuvan u `~/.config/git/credentials_opps` (važi do 15. oktobra 2026)
- **Push na GitHub:** `git config credential.helper 'store --file ~/.config/git/credentials_opps' && git push origin main`
- **Backup baze:** Trenutno ručno preko "Backup" dugmeta
- **PDF export:** Trenutno se radi preko HTML i štampe iz pregledača (Ctrl+P)
- **JMBG validacija:** Proverava datum (oba raspona 1000-1999 i 2000-2999) i kontrolnu cifru
- **XSD šema:** Ugrađena u kod, ne zahteva poseban .xsd fajl
- **Podržane platforme:** Windows, Mac, Linux (Python 3.6+, lxml)

---

## 🎯 PRIORITETI ZA NAREDNU VERZIJU (v15.4+)

### Kratki rok (1-2 sjednice)
1. Refaktoring na OOP (odvojiti bazu, GUI, logiku)
2. Type hintovi i docstringovi
3. PDF export (pravi PDF umjesto HTML)

### Srednji rok (3-4 sjednice)
4. Auto-backup pri pokretanju
5. Pametna obrada duplikata
6. Pregled po kartićima (po opštini, vrsti prometa)

### Dugoročno
7. Unit testovi (pytest)
8. Logging umjesto print/messagebox
9. Dark theme (ako bude tražio)
10. Undo/Redo funkcionalnost

---

**Kontakt:** Milan Jankovic (Telegram: @cuparac)
**GitHub token ističe:** 15. oktobar 2026.
