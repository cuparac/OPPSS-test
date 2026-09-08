# OPPSS Generator

**Aplikacija za generisanje OOPSS prijava (Обавештење о промету пољопривредних производа и секундарних сировина)**

![Version](https://img.shields.io/badge/verzija-13.9-blue)
![Python](https://img.shields.io/badge/python-3.6+-green)
![License](https://img.shields.io/badge/licence-MIT-orange)

---

## 📋 Sadržaj

- [O projektu](#o-projektu)
- [Funkcionalnosti](#funkcionalnosti)
- [Instalacija](#instalacija)
- [Korišćenje](#korišćenje)
- [Verzije](#verzije)
- [Rešavanje problema](#rešavanje-problema)
- [Licenca](#licenca)

---

## 📖 O projektu

OPPSS Generator je desktop i CLI aplikacija za generisanje XML fajlova namenjenih upload-u na portal **ePorezi** (Poreska uprava Republike Srbije). Aplikacija omogućava unos podataka o podnosiocu i izvršiocima prometa, validaciju unetih podataka, i generisanje XML fajla u skladu sa XSD semom.

---

## ✅ Funkcionalnosti

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

---

## 🚀 Instalacija

### Preduvodi
- Python 3.6 ili noviji
- `lxml` paket

### Instalacija na Ubuntu/Debian

```bash
# Klonirajte repozitorijum
git clone https://github.com/cuparac/OPPSS-test.git
cd OPPSS-test

# Instalirajte lxml
sudo apt install -y python3-lxml
```

### Instalacija na Windows/Mac

```bash
# Klonirajte repozitorijum
git clone https://github.com/cuparac/OPPSS-test.git
cd OPPSS-test

# Instalirajte lxml
pip install lxml
```

---

## 💻 Korišćenje

### GUI verzija (desktop)

```bash
python opps_generator.py
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
| F1 | O aplikaciji |

### CLI verzija (terminal/server)

```bash
python opps_generator_cli.py
```

---

## 📁 Struktura projekta

```
OPPSS-test/
├── opps_generator.py              # GUI verzija (desktop)
├── opps_generator_cli.py          # CLI verzija (terminal/server)
├── opps.xsd                       # XSD šema za validaciju XML-a
├── KorisnikouputstvoOPPSS.pdf     # Korisničko uputstvo
├── instalacija_ubuntu_server.txt  # Uputstvo za Ubuntu Server
├── sve_ispravke.txt               # Kompletan pregled svih ispravki
├── ispravke_v13.7.txt             # Ispravke v13.7
├── ispravke_v13.8.txt             # Ispravke v13.8
├── ispravke_v13.9.txt             # Ispravke v13.9
└── README.md                      # Ovaj fajl
```

---

## 📦 Generisani fajlovi

| Fajl | Opis |
|------|------|
| `baza_2026.json` | JSON baza podataka |
| `OPPS_prijava_2026.xml` | Generisani XML fajl (za upload na ePorezi) |

---

## 🔄 Istorija verzija

| Verzija | Datum | Opis |
|---------|-------|------|
| v13.9 | 08.09.2026 | CLI verzija, prečice tastature, about dijalog |
| v13.8 | 08.09.2026 | EBS identifikator, poljoprivredno gazdinstva, email osobe |
| v13.7 | 08.09.2026 | Cross-platform file lock, assert→if, datum provere |
| v13.6 | 08.09.2026 | JMBG validacija, tree.index, datum OD/DO, file lock |
| v13.5 | 08.09.2026 | Originalna verzija |

---

## ❓ Rešavanje problema

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
python opps_generator.py  # bez sudo
```

---

## 📝 Licence

MIT License - slobodno korišćenje i modifikacija.

---

## 📞 Kontakt

- **GitHub:** https://github.com/cuparac/OPPSS-test
- **Autor:** cuparac
- **Verzija:** 13.9

---

## ⚠️ Napomena

Ova aplikacija nije zvanični alat Poreske uprave Republike Srbije. Korisnik je odgovoran za ispravnost unetih podataka.
