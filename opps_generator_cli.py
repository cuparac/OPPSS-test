"""OPPSS GENERATOR v13.9 CLI - command-line verzija bez GUI-a.
Radi na serverima, terminalima, SSH sesijama.
Zahteva: pip install lxml"""

import json, os, sys, datetime, calendar as _cal, platform

XSD = "opps.xsd"
try:
    from lxml import etree
except ImportError:
    import subprocess
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "lxml"], check=True)
        from lxml import etree
    except (subprocess.CalledProcessError, ImportError) as e:
        print(f"GREŠKA: Ne mogu da instaliram lxml: {e}")
        print("Molimo, instalirajte rucno: pip install lxml")
        sys.exit(1)

if platform.system() != "Windows":
    import fcntl


def validan_jmbg(jmbg):
    if not jmbg.isdigit() or len(jmbg) != 13:
        return False
    a = [int(c) for c in jmbg]
    dan = int(jmbg[0:2])
    mesec = int(jmbg[2:4])
    godina_3 = int(jmbg[4:7])
    datum_ok = False
    for godina in [1000 + godina_3, 2000 + godina_3]:
        try:
            datetime.date(godina, mesec, dan)
            datum_ok = True
            break
        except ValueError:
            continue
    if not datum_ok:
        return False
    tezine = [7, 6, 5, 4, 3, 2] * 2
    k = 11 - (sum(c * t for c, t in zip(a[:12], tezine)) % 11)
    return (0 if k > 9 else k) == a[12]


def validan_ebs(ebs):
    return ebs.isdigit() and len(ebs) == 9


def ucitaj_bazu(godina):
    f = "baza_" + godina + ".json"
    if os.path.exists(f):
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                raise ValueError("Ocekivan objekat, dobijen: " + type(data).__name__)
            if "ljudi" not in data or not isinstance(data["ljudi"], list):
                data["ljudi"] = []
            if "podnosioc" not in data or not isinstance(data["podnosioc"], dict):
                data["podnosioc"] = {}
            return data
        except (json.JSONDecodeError, IOError, ValueError) as e:
            print(f"  [GREŠKA] {f}: {e}")
            print("  Kreirana je prazna baza.")
            return {"podnosioc": {}, "ljudi": []}
    return {"podnosioc": {}, "ljudi": []}


def sacuvaj_bazu(baza, godina):
    f = "baza_" + godina + ".json"
    if platform.system() != "Windows":
        with open(f, "w", encoding="utf-8") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(baza, fh, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    else:
        f_tmp = f + ".tmp"
        with open(f_tmp, "w", encoding="utf-8") as fh:
            json.dump(baza, fh, ensure_ascii=False, indent=2)
        os.replace(f_tmp, f)


def konvertuj_datum(t):
    try:
        return datetime.datetime.strptime(t.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


def generisi_xml(baza, godina):
    p = baza.get("podnosioc")
    if not p or not p.get("pib_jmbg"):
        print("  [GREŠKA] Prvo unesite podatke o PODNOSIOCU za izabranu godinu!")
        return None
    if not baza["ljudi"]:
        print("  [GREŠKA] Dodajte bar jednu osobu!")
        return None

    NS = "http://pid.purs.gov.rs"
    XS = "{" + NS + "}"
    root = etree.Element(XS + "PoreskaDeklaracija", nsmap={None: NS})
    podaci = etree.SubElement(etree.SubElement(root, XS + "OPPPSSPrijava"), XS + "PodaciOPrijavi")
    obrazac = etree.SubElement(podaci, XS + "PodaciOObrascu")
    etree.SubElement(obrazac, XS + "PoreskiPeriod").text = str(godina)
    pn = etree.SubElement(podaci, XS + "PodaciOPodnosiocu")
    etree.SubElement(pn, XS + "PIBJMBG").text = p["pib_jmbg"]
    etree.SubElement(pn, XS + "EPostaPodnosioca").text = p["email"]
    etree.SubElement(pn, XS + "TelefonPodnosioca").text = p["telefon"]
    etree.SubElement(pn, XS + "JMBGPodnosioca").text = p["jmbg"]
    for i, o in enumerate(baza["ljudi"], 1):
        r = etree.SubElement(podaci, XS + "PodaciOPrometu")
        etree.SubElement(r, XS + "RedniBroj").text = str(i)
        etree.SubElement(r, XS + "VrstaPrometa").text = o["vrsta_prometa"]
        etree.SubElement(r, XS + "VrstaIdentifikatora").text = o["vrsta_identifikatora"]
        etree.SubElement(r, XS + "IdentifikatorIzvrsiocaPrometa").text = o["identifikator"]
        etree.SubElement(r, XS + "ImePrezimeNaziv").text = o["ime_naziv"]
        etree.SubElement(r, XS + "OpstinaPrebivalista").text = o["opstina"]
        etree.SubElement(r, XS + "Adresa").text = o["adresa"]
        if o.get("email_osobe"):
            etree.SubElement(r, XS + "ElektronskaAdresa").text = o["email_osobe"]
        etree.SubElement(r, XS + "Telefon").text = o["telefon"]
        if o.get("broj_gazdinstva"):
            etree.SubElement(r, XS + "BrojPoljoprivrednogGazdinstva").text = o["broj_gazdinstva"]
        if o.get("naziv_gazdinstva"):
            etree.SubElement(r, XS + "NazivPoljoprivrednogGazdinstva").text = o["naziv_gazdinstva"]
        etree.SubElement(r, XS + "IznosPrometa").text = str(o["iznos_prometa"])
        etree.SubElement(r, XS + "DatumOd").text = o["datum"]
        etree.SubElement(r, XS + "DatumDo").text = o.get("datum_do", o["datum"])

    etree.indent(root, space="  ")
    izlaz = "OPPS_prijava_" + godina + ".xml"
    etree.ElementTree(root).write(izlaz, encoding="utf-8", xml_declaration=True)

    ukupno = sum(o['iznos_prometa'] for o in baza['ljudi'])
    sazetak = ("Godina: %s\nBroj unosa: %d\nUkupan iznos: %s RSD" %
               (godina, len(baza['ljudi']), format(ukupno, ",").replace(",", ".")))

    if not os.path.exists(XSD):
        print(f"  [UPOZORENJE] XSD fajl '{XSD}' ne postoji!")
        print(f"  XML je kreiran ALI NIJE validiran.")
        print(f"  {sazetak}")
        return izlaz
    try:
        schema = etree.XMLSchema(etree.parse(XSD))
    except Exception as e:
        print(f"  [GREŠKA] Problem sa XSD semom: {e}")
        print(f"  XML je kreiran ALI NIJE validiran.")
        return izlaz
    if schema.validate(root):
        print(f"  ✅ {izlaz} je VALIDAN!")
        print(f"  Spreman za upload na ePorezi portal.")
        print(f"  {sazetak}")
    else:
        greske = "\n".join(e.message for e in schema.error_log)
        print(f"  ❌ XML NIJE VALIDAN:\n{greske}")
    return izlaz


def prikazi_meni(naslov, opcije):
    """Prikazuje tekstualni meni i vraca izbor."""
    print()
    print("=" * 60)
    print(f"  {naslov}")
    print("=" * 60)
    for i, opcija in enumerate(opcije, 1):
        print(f"  {i}. {opcija}")
    print("-" * 60)
    while True:
        try:
            izbor = int(input("  Izaberite opciju: "))
            if 1 <= izbor <= len(opcije):
                return izbor
            print("  Pogresan izbor, pokusajte ponovo.")
        except ValueError:
            print("  Unesite broj.")
        except EOFError:
            return 0


def unesi_podatak(poruka, obavezno=True, default=""):
    """Unos podatka sa opcionim default-om."""
    while True:
        if default:
            poruka_fmt = f"  {poruka} [{default}]: "
        else:
            poruka_fmt = f"  {poruka}: "
        vrednost = input(poruka_fmt).strip()
        if not vrednost and default:
            return default
        if not vrednost and obavezno:
            print("  Ovo polje je obavezno.")
            continue
        return vrednost


def unesi_datum(poruka, obavezno=True):
    """Unos datuma u formatu DD/MM/YYYY."""
    while True:
        datum = unesi_podatak(poruka + " (DD/MM/YYYY)", obavezno)
        if not datum and not obavezno:
            return ""
        konvertovan = konvertuj_datum(datum)
        if konvertovan:
            return datum
        print("  Neispravan datum. Format: DD/MM/YYYY (npr. 01012026)")


def prikazi_tabelu(baza):
    """Prikazuje tabelu unosa."""
    if not baza["ljudi"]:
        print("  (Nema unosa)")
        return
    tipovi = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}
    id_tipovi = {"0": "PIB", "1": "JMBG", "5": "EBS"}
    print()
    print(f"  {'RB':<4} {'Tip':<8} {'Identifikator':<15} {'Ime/Naziv':<25} {'Datum (od-do)':<25} {'Iznos':>10}")
    print("  " + "-" * 90)
    for i, o in enumerate(baza["ljudi"], 1):
        tip_id = id_tipovi.get(o.get("vrsta_identifikatora", "?"), "?")
        datum_od = o.get("datum", "")
        datum_do = o.get("datum_do", datum_od)
        if datum_od:
            try:
                datum_od = datetime.datetime.strptime(datum_od, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                pass
        if datum_do:
            try:
                datum_do = datetime.datetime.strptime(datum_do, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                pass
        datum_str = f"{datum_od} - {datum_do}"
        print(f"  {i:<4} {tip_id:<8} {o.get('identifikator', ''):<15} {o.get('ime_naziv', ''):<25} {datum_str:<25} {o.get('iznos_prometa', 0):>10}")
    ukupno = sum(o["iznos_prometa"] for o in baza["ljudi"])
    print("  " + "-" * 90)
    print(f"  {'':>70} Ukupno: {ukupno:>10} RSD")


def unesi_osobu(baza, podrazumevano=None, indeks_izmene=None):
    """Unos nove osobe ili izmena postojece."""
    vrste_pr = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}
    vrste_id = {"0": "PIB", "1": "JMBG", "5": "EBS"}
    
    if podrazumevano:
        print()
        print("  IZMENA UNOSA:")
        print("  (Pritisnite Enter da zadrzite postojecu vrednost)")
    else:
        print()
        print("  NOVI UNOS:")
    
    # Vrsta prometa
    print(f"  Vrsta prometa: 1={vrste_pr['1']}, 2={vrste_pr['2']}")
    while True:
        vrsta = unesi_podatak("Vrsta prometa", True, podrazumevano.get("vrsta_prometa", "1") if podrazumevano else "1")
        if vrsta in vrste_pr:
            break
        print("  Izaberite 1 ili 2.")
    
    # Vrsta identifikatora
    print(f"  Identifikator: 0=PIB (9 cifara), 1=JMBG (13 cifara), 5=EBS (9 cifara)")
    while True:
        id_tip = unesi_podatak("Vrsta identifikatora", True, podrazumevano.get("vrsta_identifikatora", "1") if podrazumevano else "1")
        if id_tip in vrste_id:
            break
        print("  Izaberite 0, 1 ili 5.")
    
    # Identifikator
    ocekivano = 13 if id_tip == "1" else 9
    while True:
        identifikator = unesi_podatak(f"Identifikator ({ocekivano} cifara)", True, podrazumevano.get("identifikator", "") if podrazumevano else "")
        if not identifikator.isdigit() or len(identifikator) != ocekivano:
            print(f"  Mora imati TACNO {ocekivano} cifara.")
            continue
        if id_tip == "1" and not validan_jmbg(identifikator):
            print("  ⚠ JMBG NE prolazi proveru kontrolne cifre!")
            nastaviti = input("  Nastaviti ipak? (d/n): ").strip().lower()
            if nastaviti != "d":
                continue
        break
    
    # Ostala polja
    ime_naziv = unesi_podatak("Ime i prezime / Naziv", True, podrazumevano.get("ime_naziv", "") if podrazumevano else "")
    opstina = unesi_podatak("Opstina", True, podrazumevano.get("opstina", "") if podrazumevano else "")
    adresa = unesi_podatak("Adresa", True, podrazumevano.get("adresa", "") if podrazumevano else "")
    email_osobe = unesi_podatak("E-posta osobe", False, podrazumevano.get("email_osobe", "") if podrazumevano else "")
    telefon = unesi_podatak("Broj telefona", True, podrazumevano.get("telefon", "") if podrazumevano else "")
    broj_gazdinstva = unesi_podatak("Broj poljoprivrednog gazdinstva", False, podrazumevano.get("broj_gazdinstva", "") if podrazumevano else "")
    naziv_gazdinstva = unesi_podatak("Naziv poljoprivrednog gazdinstva", False, podrazumevano.get("naziv_gazdinstva", "") if podrazumevano else "")
    
    # Datumi
    datum_od = unesi_datum("Datum OD", True)
    datum_do = unesi_datum("Datum DO", True)
    
    # Provera datuma
    datum_iso = konvertuj_datum(datum_od)
    datum_do_iso = konvertuj_datum(datum_do)
    if datum_do_iso < datum_iso:
        print("  ⚠ Datum DO je pre datuma OD! Koristiće se datum OD i za DO.")
        datum_do = datum_od
        datum_do_iso = datum_iso
    
    # Iznos
    while True:
        iznos_str = unesi_podatak("Iznos prometa (RSD, ceo broj)", True, str(podrazumevano.get("iznos_prometa", "")) if podrazumevano else "")
        try:
            iznos = int(iznos_str)
            if iznos <= 0:
                print("  Iznos mora biti pozitivan.")
                continue
            break
        except ValueError:
            print("  Unesite ceo broj.")
    
    r = {
        "vrsta_prometa": vrsta,
        "vrsta_identifikatora": id_tip,
        "identifikator": identifikator,
        "ime_naziv": ime_naziv,
        "opstina": opstina,
        "adresa": adresa,
        "email_osobe": email_osobe,
        "telefon": telefon,
        "broj_gazdinstva": broj_gazdinstva,
        "naziv_gazdinstva": naziv_gazdinstva,
        "datum": datum_iso,
        "datum_do": datum_do_iso,
        "iznos_prometa": iznos,
    }
    
    if indeks_izmene is not None:
        baza["ljudi"][indeks_izmene] = r
        print("  ✅ Unos je izmenjen.")
    else:
        baza["ljudi"].append(r)
        print("  ✅ Unos je sacuvan.")


def unesi_podnosioca(baza, godina):
    """Unos podataka o podnosiocu."""
    p = baza.get("podnosioc", {})
    print()
    print("  PODACI O PODNOSIOCU:")
    print("  (Pritisnite Enter da zadrzite postojecu vrednost)")
    
    while True:
        pib_jmbg = unesi_podatak("PIB (9 cifara) ili JMBG (13 cifara)", True, p.get("pib_jmbg", ""))
        if len(pib_jmbg) in (9, 13) and pib_jmbg.isdigit():
            break
        print("  Mora imati TACNO 9 cifara (PIB) ili 13 cifara (JMBG).")
    
    email = unesi_podatak("E-posta", True, p.get("email", ""))
    telefon = unesi_podatak("Telefon", True, p.get("telefon", ""))
    
    while True:
        jmbg = unesi_podatak("JMBG podnosioca (13 cifara)", True, p.get("jmbg", ""))
        if len(jmbg) == 13 and jmbg.isdigit():
            if validan_jmbg(jmbg):
                break
            print("  ⚠ JMBG NE prolazi proveru kontrolne cifre!")
            nastaviti = input("  Nastaviti ipak? (d/n): ").strip().lower()
            if nastaviti == "d":
                break
        else:
            print("  Mora imati TACNO 13 cifara.")
    
    baza["podnosioc"] = {
        "pib_jmbg": pib_jmbg,
        "email": email,
        "telefon": telefon,
        "jmbg": jmbg,
        "godina": godina
    }
    sacuvaj_bazu(baza, godina)
    print("  ✅ Podaci o podnosiocu su sacuvani.")


def prikazi_glavni_meni():
    """Prikazuje glavni meni i vraca izbor."""
    print()
    print("=" * 60)
    print("  OPPSS GENERATOR v13.9 CLI")
    print("  Aplikacija za generisanje OOPSS prijava")
    print("=" * 60)
    print("  1. Prikazi tabelu unosa")
    print("  2. Dodaj novi unos")
    print("  3. Izmeni unos")
    print("  4. Obrisi unos")
    print("  5. Podaci o podnosiocu")
    print("  6. Generisi XML")
    print("  7. Promeni godinu")
    print("  0. Izlaz")
    print("-" * 60)
    while True:
        try:
            izbor = input("  Izaberite opciju: ").strip()
            if izbor in ["0", "1", "2", "3", "4", "5", "6", "7"]:
                return int(izbor)
            print("  Pogresan izbor, pokusajte ponovo.")
        except EOFError:
            return 0


def main():
    """Glavna funkcija CLI aplikacije."""
    godina = str(datetime.date.today().year)
    baza = ucitaj_bazu(godina)
    
    print()
    print("  Dobrodosli u OPPSS Generator v13.9 CLI!")
    print(f"  Trenutna godina: {godina}")
    
    while True:
        # Prikazi status
        br_unosa = len(baza["ljudi"])
        ukupno = sum(o["iznos_prometa"] for o in baza["ljudi"])
        podnosioc = baza.get("podnosioc", {}).get("pib_jmbg", "NIJE UNESEN")
        print()
        print(f"  [{godina}] Podnosioc: {podnosioc} | Unosa: {br_unosa} | Ukupno: {ukupno} RSD")
        
        izbor = prikazi_glavni_meni()
        
        if izbor == 0:
            print()
            print("  Hvala na koriscenju! Dovidjenja.")
            break
        
        elif izbor == 1:
            prikazi_tabelu(baza)
        
        elif izbor == 2:
            unesi_osobu(baza)
            sacuvaj_bazu(baza, godina)
        
        elif izbor == 3:
            if not baza["ljudi"]:
                print("  (Nema unosa za izmenu)")
                continue
            prikazi_tabelu(baza)
            try:
                rb = int(input("  Unesite RB za izmenu: ")) - 1
                if 0 <= rb < len(baza["ljudi"]):
                    unesi_osobu(baza, baza["ljudi"][rb], rb)
                    sacuvaj_bazu(baza, godina)
                else:
                    print("  Pogresan RB.")
            except (ValueError, EOFError):
                print("  Pogresan unos.")
        
        elif izbor == 4:
            if not baza["ljudi"]:
                print("  (Nema unosa za brisanje)")
                continue
            prikazi_tabelu(baza)
            try:
                rb = int(input("  Unesite RB za brisanje: ")) - 1
                if 0 <= rb < len(baza["ljudi"]):
                    ime = baza["ljudi"][rb]["ime_naziv"]
                    potvrda = input("  Obrisati '{}'? (d/n): ".format(ime)).strip().lower()
                    if potvrda == "d":
                        del baza["ljudi"][rb]
                        sacuvaj_bazu(baza, godina)
                        print("  ✅ Unos je obrisan.")
                else:
                    print("  Pogresan RB.")
            except (ValueError, EOFError):
                print("  Pogresan unos.")
        
        elif izbor == 5:
            unesi_podnosioca(baza, godina)
        
        elif izbor == 6:
            generisi_xml(baza, godina)
        
        elif izbor == 7:
            nova_godina = input("  Unesite godinu (2023-2035): ").strip()
            if nova_godina.isdigit() and 2023 <= int(nova_godina) <= 2035:
                godina = nova_godina
                baza = ucitaj_bazu(godina)
                print(f"  Godina promenjena na {godina}.")
            else:
                print("  Pogresna godina.")


if __name__ == "__main__":
    main()
