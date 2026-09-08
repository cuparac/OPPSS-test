"""OPPSS GENERATOR v13.9 STANDALONE - XSD šema je ugrađena u kod.
Ne zahteva poseban .xsd fajl. Kompatibilan sa 32/64 bit Windows.
Zahteva: pip install lxml"""

import json, os, sys, datetime, calendar as _cal, platform

# XSD šema je ugrađena u kod - ne treba poseban fajl
XSD_CONTENT = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema elementFormDefault="qualified" targetNamespace="http://pid.purs.gov.rs" version="1.0.0"
           xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:tns="http://pid.purs.gov.rs">
    <xs:element name="PoreskaDeklaracija" type="tns:PoreskaDeklaracijaType"/>
    <xs:complexType name="PoreskaDeklaracijaType">
        <xs:sequence>
            <xs:element name="OPPPSSPrijava" maxOccurs="1" minOccurs="1" type="tns:OPPPSSPrijavaType"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="OPPPSSPrijavaType">
        <xs:sequence>
            <xs:element name="PodaciOPrijavi" maxOccurs="1" minOccurs="1" type="tns:PodaciOPrijaviType"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="PodaciOPrijaviType">
        <xs:sequence>
            <xs:element name="KlijentskaOznakaDeklaracije" maxOccurs="1" minOccurs="0" type="tns:String255Type"/>
            <xs:element name="PortalOznakaDeklaracije" maxOccurs="1" minOccurs="0" type="tns:String255Type"/>
            <xs:element name="PodaciOObrascu" maxOccurs="1" minOccurs="1" type="tns:PodaciOObrascuType"/>
            <xs:element name="PodaciOPodnosiocu" maxOccurs="1" minOccurs="1" type="tns:PodaciOPodnosiocuType"/>
            <xs:element name="PodaciOPrometu" minOccurs="1" maxOccurs="unbounded" type="tns:PodaciOPrometuType"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="PodaciOObrascuType">
        <xs:sequence>
            <xs:element name="PoreskiPeriod" type="xs:positiveInteger" maxOccurs="1" minOccurs="1"/>
            <xs:element name="IspravkaObavestenja" type="xs:boolean" maxOccurs="1" minOccurs="0"/>
            <xs:element name="JBIPKojaSeMenja" type="xs:long" maxOccurs="1" minOccurs="0"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="PodaciOPodnosiocuType">
        <xs:sequence>
            <xs:element name="PIBJMBG" type="tns:PIBJMBGTip" minOccurs="1" maxOccurs="1"/>
            <xs:element name="EPostaPodnosioca" type="tns:eMailAdresaType" minOccurs="1" maxOccurs="1"/>
            <xs:element name="TelefonPodnosioca" type="tns:String255Type" maxOccurs="1" minOccurs="1"/>
            <xs:element name="JMBGPodnosioca" type="tns:JMBGType" minOccurs="1" maxOccurs="1"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="PodaciOPrometuType">
        <xs:sequence>
            <xs:element name="RedniBroj" type="xs:positiveInteger" maxOccurs="1" minOccurs="1"/>
            <xs:element name="VrstaPrometa" maxOccurs="1" minOccurs="1">
                <xs:simpleType>
                    <xs:restriction base="xs:int">
                        <xs:enumeration value="1"/>
                        <xs:enumeration value="2"/>
                    </xs:restriction>
                </xs:simpleType>
            </xs:element>
            <xs:element name="VrstaIdentifikatora" maxOccurs="1" minOccurs="1">
                <xs:simpleType>
                    <xs:restriction base="xs:int">
                        <xs:enumeration value="0"/>
                        <xs:enumeration value="1"/>
                        <xs:enumeration value="5"/>
                    </xs:restriction>
                </xs:simpleType>
            </xs:element>
            <xs:element name="IdentifikatorIzvrsiocaPrometa" type="tns:String255Type" minOccurs="1" maxOccurs="1"/>
            <xs:element name="ImePrezimeNaziv" type="tns:String255Type" minOccurs="1" maxOccurs="1"/>
            <xs:element name="OpstinaPrebivalista" type="tns:String255Type" minOccurs="1" maxOccurs="1"/>
            <xs:element name="Adresa" type="tns:String255Type" minOccurs="1" maxOccurs="1"/>
            <xs:element name="ElektronskaAdresa" type="tns:eMailAdresaType" minOccurs="0" maxOccurs="1"/>
            <xs:element name="Telefon" maxOccurs="1" minOccurs="1" type="tns:String255Type"/>
            <xs:element name="BrojPoljoprivrednogGazdinstva" maxOccurs="1" minOccurs="0" type="tns:String255Type"/>
            <xs:element name="NazivPoljoprivrednogGazdinstva" maxOccurs="1" minOccurs="0" type="tns:String2000Type"/>
            <xs:element name="IznosPrometa" maxOccurs="1" minOccurs="1" type="xs:positiveInteger"/>
            <xs:element name="DatumOd" maxOccurs="1" minOccurs="1" type="tns:DatumType"/>
            <xs:element name="DatumDo" maxOccurs="1" minOccurs="1" type="tns:DatumType"/>
        </xs:sequence>
    </xs:complexType>
    <xs:simpleType name="DatumType">
        <xs:restriction base="xs:date"/>
    </xs:simpleType>
    <xs:simpleType name="eMailAdresaType">
        <xs:restriction base="xs:string">
            <xs:maxLength value="512"/>
            <xs:minLength value="3"/>
            <xs:pattern value="[A-Za-z0-9_]+([-+.&#39;][A-Za-z0-9_]+)*@[A-Za-z0-9_]+([-.][A-Za-z0-9_]+)*\\.[A-Za-z0-9_]+([-.][A-Za-z0-9_]+)*"/>
        </xs:restriction>
    </xs:simpleType>
    <xs:simpleType name="PIBType">
        <xs:restriction base="xs:string">
            <xs:pattern value="[0-9]{9}"/>
        </xs:restriction>
    </xs:simpleType>
    <xs:simpleType name="PIBJMBGTip">
        <xs:restriction base="xs:string">
            <xs:pattern value="[0-9]{9}"/>
            <xs:pattern value="[0-9]{13}"/>
        </xs:restriction>
    </xs:simpleType>
    <xs:simpleType name="JMBGType">
        <xs:restriction base="xs:string">
            <xs:pattern value="[0-9]{13}"/>
        </xs:restriction>
    </xs:simpleType>
    <xs:simpleType name="String2000Type">
        <xs:restriction base="xs:string">
            <xs:maxLength value="2000"/>
            <xs:minLength value="1"/>
        </xs:restriction>
    </xs:simpleType>
    <xs:simpleType name="String255Type">
        <xs:restriction base="xs:string">
            <xs:maxLength value="255"/>
            <xs:minLength value="1"/>
        </xs:restriction>
    </xs:simpleType>
</xs:schema>'''

XSD = None  # Biće inicijalizovano pri pokretanju

def get_xsd_path():
    """Vraća putanju do XSD fajla - prvo proverava da li postoji lokalno,
    ako ne, kreira privremeni fajl sa ugrađenom šemom."""
    xsd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "opps.xsd")
    if os.path.exists(xsd_path):
        return xsd_path
    # Ako ne postoji, koristi ugrađenu šemu
    return None

def get_xsd_schema():
    """Učitava XSD šemu - prvo pokušava lokalni fajl, onda ugrađenu."""
    global XSD
    if XSD is not None:
        return XSD
    
    xsd_path = get_xsd_path()
    if xsd_path:
        try:
            from lxml import etree
            XSD = etree.XMLSchema(etree.parse(xsd_path))
            return XSD
        except Exception:
            pass
    
    # Koristi ugrađenu šemu
    from lxml import etree
    XSD = etree.XMLSchema(etree.fromstring(XSD_CONTENT.encode('utf-8')))
    return XSD


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

    schema = get_xsd_schema()
    if schema.validate(root):
        print(f"  ✅ {izlaz} je VALIDAN!")
        print(f"  Spreman za upload na ePorezi portal.")
        print(f"  {sazetak}")
    else:
        greske = "\n".join(e.message for e in schema.error_log)
        print(f"  ❌ XML NIJE VALIDAN:\n{greske}")
    return izlaz


def main():
    """Glavna funkcija CLI aplikacije."""
    godina = str(datetime.date.today().year)
    baza = ucitaj_bazu(godina)
    
    print()
    print("  Dobrodosli u OPPSS Generator v13.9 STANDALONE!")
    print(f"  Trenutna godina: {godina}")
    print("  XSD šema je ugrađena u kod - ne treba poseban .xsd fajl.")
    
    while True:
        br_unosa = len(baza["ljudi"])
        ukupno = sum(o["iznos_prometa"] for o in baza["ljudi"])
        podnosioc = baza.get("podnosioc", {}).get("pib_jmbg", "NIJE UNESEN")
        print()
        print(f"  [{godina}] Podnosioc: {podnosioc} | Unosa: {br_unosa} | Ukupno: {ukupno} RSD")
        
        print()
        print("=" * 60)
        print("  OPPSS GENERATOR v13.9 STANDALONE")
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
        
        try:
            izbor = input("  Izaberite opciju: ").strip()
        except EOFError:
            break
        
        if izbor == "0":
            print()
            print("  Hvala na koriscenju! Dovidjenja.")
            break
        
        elif izbor == "1":
            if not baza["ljudi"]:
                print("  (Nema unosa)")
            else:
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
        
        elif izbor == "2":
            # Dodaj novi unos
            vrste_pr = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}
            vrste_id = {"0": "PIB", "1": "JMBG", "5": "EBS"}
            
            print()
            print("  NOVI UNOS:")
            
            # Vrsta prometa
            print(f"  Vrsta prometa: 1={vrste_pr['1']}, 2={vrste_pr['2']}")
            while True:
                vrsta = input("  Vrsta prometa: ").strip()
                if vrsta in vrste_pr:
                    break
                print("  Izaberite 1 ili 2.")
            
            # Vrsta identifikatora
            print(f"  Identifikator: 0=PIB (9 cifara), 1=JMBG (13 cifara), 5=EBS (9 cifara)")
            while True:
                id_tip = input("  Vrsta identifikatora: ").strip()
                if id_tip in vrste_id:
                    break
                print("  Izaberite 0, 1 ili 5.")
            
            # Identifikator
            ocekivano = 13 if id_tip == "1" else 9
            while True:
                identifikator = input(f"  Identifikator ({ocekivano} cifara): ").strip()
                if not identifikator.isdigit() or len(identifikator) != ocekivano:
                    print(f"  Mora imati TACNO {ocekivano} cifara.")
                    continue
                if id_tip == "1" and not validan_jmbg(identifikator):
                    print("  ⚠ JMBG NE prolazi proveru kontrolne cifre!")
                    nastaviti = input("  Nastaviti ipak? (d/n): ").strip().lower()
                    if nastaviti != "d":
                        continue
                break
            
            ime_naziv = input("  Ime i prezime / Naziv: ").strip()
            opstina = input("  Opstina: ").strip()
            adresa = input("  Adresa: ").strip()
            email_osobe = input("  E-posta osobe (opciono): ").strip()
            telefon = input("  Broj telefona: ").strip()
            broj_gazdinstva = input("  Broj poljoprivrednog gazdinstva (opciono): ").strip()
            naziv_gazdinstva = input("  Naziv poljoprivrednog gazdinstva (opciono): ").strip()
            
            # Datumi
            while True:
                datum_od = input("  Datum OD (DD/MM/YYYY): ").strip()
                if konvertuj_datum(datum_od):
                    break
                print("  Neispravan datum.")
            
            while True:
                datum_do = input("  Datum DO (DD/MM/YYYY): ").strip()
                if konvertuj_datum(datum_do):
                    break
                print("  Neispravan datum.")
            
            # Iznos
            while True:
                try:
                    iznos = int(input("  Iznos prometa (RSD): ").strip())
                    if iznos > 0:
                        break
                    print("  Iznos mora biti pozitivan.")
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
                "datum": konvertuj_datum(datum_od),
                "datum_do": konvertuj_datum(datum_do),
                "iznos_prometa": iznos,
            }
            
            baza["ljudi"].append(r)
            sacuvaj_bazu(baza, godina)
            print("  ✅ Unos je sacuvan.")
        
        elif izbor == "3":
            if not baza["ljudi"]:
                print("  (Nema unosa za izmenu)")
                continue
            # Prikazi tabelu
            tipovi = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}
            id_tipovi = {"0": "PIB", "1": "JMBG", "5": "EBS"}
            print()
            for i, o in enumerate(baza["ljudi"], 1):
                tip_id = id_tipovi.get(o.get("vrsta_identifikatora", "?"), "?")
                print(f"  {i}. {tip_id} {o.get('identifikator', '')} - {o.get('ime_naziv', '')}")
            try:
                rb = int(input("  Unesite RB za izmenu: ")) - 1
                if 0 <= rb < len(baza["ljudi"]):
                    # TODO: Implementirati izmenu
                    print("  (Izmena u izradi - koristite brisanje i dodavanje)")
                else:
                    print("  Pogresan RB.")
            except (ValueError, EOFError):
                print("  Pogresan unos.")
        
        elif izbor == "4":
            if not baza["ljudi"]:
                print("  (Nema unosa za brisanje)")
                continue
            tipovi = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}
            id_tipovi = {"0": "PIB", "1": "JMBG", "5": "EBS"}
            print()
            for i, o in enumerate(baza["ljudi"], 1):
                tip_id = id_tipovi.get(o.get("vrsta_identifikatora", "?"), "?")
                print(f"  {i}. {tip_id} {o.get('identifikator', '')} - {o.get('ime_naziv', '')}")
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
        
        elif izbor == "5":
            p = baza.get("podnosioc", {})
            print()
            print("  PODACI O PODNOSIOCU:")
            print("  (Pritisnite Enter da zadrzite postojecu vrednost)")
            
            while True:
                pib_jmbg = input(f"  PIB (9 cifara) ili JMBG (13 cifara) [{p.get('pib_jmbg', '')}]: ").strip()
                if not pib_jmbg and p.get("pib_jmbg"):
                    pib_jmbg = p["pib_jmbg"]
                if len(pib_jmbg) in (9, 13) and pib_jmbg.isdigit():
                    break
                print("  Mora imati TACNO 9 cifara (PIB) ili 13 cifara (JMBG).")
            
            email = input(f"  E-posta [{p.get('email', '')}]: ").strip()
            if not email and p.get("email"):
                email = p["email"]
            
            telefon = input(f"  Telefon [{p.get('telefon', '')}]: ").strip()
            if not telefon and p.get("telefon"):
                telefon = p["telefon"]
            
            while True:
                jmbg = input(f"  JMBG podnosioca (13 cifara) [{p.get('jmbg', '')}]: ").strip()
                if not jmbg and p.get("jmbg"):
                    jmbg = p["jmbg"]
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
        
        elif izbor == "6":
            generisi_xml(baza, godina)
        
        elif izbor == "7":
            nova_godina = input("  Unesite godinu (2023-2035): ").strip()
            if nova_godina.isdigit() and 2023 <= int(nova_godina) <= 2035:
                godina = nova_godina
                baza = ucitaj_bazu(godina)
                print(f"  Godina promenjena na {godina}.")
            else:
                print("  Pogresna godina.")


if __name__ == "__main__":
    main()
