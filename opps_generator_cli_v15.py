"""OPPSS GENERATOR v15.0 CLI STANDALONE - SQLite baza, CSV export, pretraga, izveštaji.
Command-line verzija sa ugrađenom XSD semom.
Ne zahteva poseban .xsd fajl. Kompatibilan sa 32/64 bit Windows.
Zahteva: pip install lxml"""

import json, os, sys, datetime, calendar as _cal, platform, sqlite3, csv

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

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

try:
    from lxml import etree
except ImportError:
    import subprocess
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "lxml"], check=True)
        from lxml import etree
    except (subprocess.CalledProcessError, ImportError) as e:
        print(f"GREŠKA: Ne mogu da instaliram lxml: {e}")
        sys.exit(1)


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


def konvertuj_datum(t):
    try:
        return datetime.datetime.strptime(t.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


def get_xsd_schema():
    try:
        return etree.XMLSchema(etree.fromstring(XSD_CONTENT.encode('utf-8')))
    except Exception:
        return None


class Database:
    """SQLite baza podataka."""
    
    def __init__(self, godina):
        self.godina = godina
        self.db_file = f"baza_{godina}.db"
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        self.kreiraj_tabele()
    
    def kreiraj_tabele(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS podnosioc (
                godina TEXT PRIMARY KEY,
                pib_jmbg TEXT,
                email TEXT,
                telefon TEXT,
                jmbg TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ljudi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                godina TEXT,
                vrsta_prometa TEXT,
                vrsta_identifikatora TEXT,
                identifikator TEXT,
                ime_naziv TEXT,
                opstina TEXT,
                adresa TEXT,
                email_osobe TEXT,
                telefon TEXT,
                broj_gazdinstva TEXT,
                naziv_gazdinstva TEXT,
                datum TEXT,
                datum_do TEXT,
                iznos_prometa INTEGER,
                FOREIGN KEY (godina) REFERENCES podnosioc(godina)
            )
        ''')
        self.conn.commit()
    
    def ucitaj_podnosioca(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM podnosioc WHERE godina = ?", (self.godina,))
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def sacuvaj_podnosioca(self, podaci):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO podnosioc (godina, pib_jmbg, email, telefon, jmbg)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.godina, podaci['pib_jmbg'], podaci['email'], 
              podaci['telefon'], podaci['jmbg']))
        self.conn.commit()
    
    def ucitaj_ljude(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ljudi WHERE godina = ?", (self.godina,))
        return [dict(row) for row in cursor.fetchall()]
    
    def dodaj_osobu(self, podaci):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO ljudi (godina, vrsta_prometa, vrsta_identifikatora, 
                identifikator, ime_naziv, opstina, adresa, email_osobe, 
                telefon, broj_gazdinstva, naziv_gazdinstva, datum, datum_do, iznos_prometa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.godina, podaci['vrsta_prometa'], podaci['vrsta_identifikatora'],
              podaci['identifikator'], podaci['ime_naziv'], podaci['opstina'],
              podaci['adresa'], podaci['email_osobe'], podaci['telefon'],
              podaci['broj_gazdinstva'], podaci['naziv_gazdinstva'],
              podaci['datum'], podaci['datum_do'], podaci['iznos_prometa']))
        self.conn.commit()
    
    def obrisi_osobu(self, id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM ljudi WHERE id = ?", (id,))
        self.conn.commit()
    
    def pretraga(self, uslov, parametri=None):
        cursor = self.conn.cursor()
        sql = "SELECT * FROM ljudi WHERE godina = ?"
        params = [self.godina]
        
        if uslov == "opstina":
            sql += " AND opstina LIKE ?"
            params.append(f"%{parametri}%")
        elif uslov == "ime":
            sql += " AND ime_naziv LIKE ?"
            params.append(f"%{parametri}%")
        elif uslov == "identifikator":
            sql += " AND identifikator = ?"
            params.append(parametri)
        elif uslov == "iznos_od":
            sql += " AND iznos_prometa >= ?"
            params.append(int(parametri))
        elif uslov == "iznos_do":
            sql += " AND iznos_prometa <= ?"
            params.append(int(parametri))
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def statistika(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(iznos_prometa), 0) FROM ljudi WHERE godina = ?", (self.godina,))
        ukupto = cursor.fetchone()
        cursor.execute("SELECT vrsta_prometa, COUNT(*), SUM(iznos_prometa) FROM ljudi WHERE godina = ? GROUP BY vrsta_prometa", (self.godina,))
        po_vrsti = cursor.fetchall()
        cursor.execute("SELECT opstina, COUNT(*), SUM(iznos_prometa) FROM ljudi WHERE godina = ? GROUP BY opstina ORDER BY SUM(iznos_prometa) DESC", (self.godina,))
        po_opstini = cursor.fetchall()
        
        return {
            'ukupno_unosa': ukupto[0],
            'ukupno_iznos': ukupto[1],
            'po_vrsti': [dict(r) for r in po_vrsti],
            'po_opstini': [dict(r) for r in po_opstini]
        }
    
    def export_csv(self, fajl_putanja):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ljudi WHERE godina = ?", (self.godina,))
        rows = cursor.fetchall()
        
        with open(fajl_putanja, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['RB', 'Vrsta prometa', 'Vrsta ID', 'Identifikator', 
                           'Ime/Naziv', 'Opština', 'Adresa', 'Email', 'Telefon',
                           'Br. gazdinstva', 'Naziv gazdinstva', 'Datum OD', 
                           'Datum DO', 'Iznos'])
            for i, row in enumerate(rows, 1):
                writer.writerow([
                    i, row['vrsta_prometa'], row['vrsta_identifikatora'],
                    row['identifikator'], row['ime_naziv'], row['opstina'],
                    row['adresa'], row['email_osobe'], row['telefon'],
                    row['broj_gazdinstva'], row['naziv_gazdinstva'],
                    row['datum'], row['datum_do'], row['iznos_prometa']
                ])
    
    def zatvori(self):
        self.conn.close()


def migriraj_json_u_sqlite(godina):
    json_file = f"baza_{godina}.json"
    if not os.path.exists(json_file):
        return False, "JSON fajl ne postoji"
    
    try:
        with open(json_file, encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return False, f"Greška pri čitanju JSON-a: {e}"
    
    db = Database(godina)
    podnosioc = data.get("podnosioc", {})
    if podnosioc and podnosioc.get("pib_jmbg"):
        db.sacuvaj_podnosioca(podnosioc)
    
    ljudi = data.get("ljudi", [])
    for osoba in ljudi:
        db.dodaj_osobu(osoba)
    
    db.zatvori()
    backup_file = f"baza_{godina}.json.backup"
    os.rename(json_file, backup_file)
    return True, f"Migracija uspešna! {len(ljudi)} unosa prebaceno."


def generisi_xml(db, godina):
    podnosioc = db.ucitaj_podnosioca()
    ljudi = db.ucitaj_ljude()
    
    if not podnosioc or not podnosioc.get("pib_jmbg"):
        print("  [GREŠKA] Prvo unesite podatke o PODNOSIOCU!")
        return None
    if not ljudi:
        print("  [GREŠKA] Dodajte bar jednu osobu!")
        return None

    NS = "http://pid.purs.gov.rs"
    XS = "{" + NS + "}"
    root = etree.Element(XS + "PoreskaDeklaracija", nsmap={None: NS})
    podaci = etree.SubElement(etree.SubElement(root, XS + "OPPPSSPrijava"), XS + "PodaciOPrijavi")
    obrazac = etree.SubElement(podaci, XS + "PodaciOObrascu")
    etree.SubElement(obrazac, XS + "PoreskiPeriod").text = str(godina)
    pn = etree.SubElement(podaci, XS + "PodaciOPodnosiocu")
    etree.SubElement(pn, XS + "PIBJMBG").text = podnosioc["pib_jmbg"]
    etree.SubElement(pn, XS + "EPostaPodnosioca").text = podnosioc["email"]
    etree.SubElement(pn, XS + "TelefonPodnosioca").text = podnosioc["telefon"]
    etree.SubElement(pn, XS + "JMBGPodnosioca").text = podnosioc["jmbg"]
    
    for i, o in enumerate(ljudi, 1):
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

    ukupno = sum(o['iznos_prometa'] for o in ljudi)
    sazetak = (f"Godina: {godina}\nBroj unosa: {len(ljudi)}\nUkupan iznos: {format(ukupno, ',').replace(',', '.')} RSD")

    schema = get_xsd_schema()
    if schema:
        if schema.validate(root):
            print(f"  ✅ {izlaz} je VALIDAN!")
            print(f"  {sazetak}")
        else:
            greske = "\n".join(e.message for e in schema.error_log)
            print(f"  ❌ XML NIJE VALIDAN:\n{greske}")
    else:
        print("  [UPOZORENJE] XML je kreiran ALI NIJE validiran.")
    return izlaz


def unesi_podatak(poruka, obavezno=True, default=""):
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
    while True:
        datum = unesi_podatak(poruka + " (DD/MM/YYYY)", obavezno)
        if not datum and not obavezno:
            return ""
        if konvertuj_datum(datum):
            return datum
        print("  Neispravan datum.")


def main():
    godina = str(datetime.date.today().year)
    db = Database(godina)
    
    # Provera za migraciju
    json_file = f"baza_{godina}.json"
    if os.path.exists(json_file):
        print()
        odgovor = input("  Pronađen je stari JSON fajl. Migrirati u SQLite? (d/n): ").strip().lower()
        if odgovor == "d":
            uspeh, poruka = migriraj_json_u_sqlite(godina)
            print(f"  {poruka}")
    
    print()
    print("  Dobrodosli u OPPSS Generator v15.0 CLI STANDALONE!")
    print(f"  Trenutna godina: {godina}")
    print("  XSD šema je ugrađena u kod - ne treba poseban .xsd fajl.")
    
    while True:
        br_unosa = len(db.ucitaj_ljude())
        ukupno = sum(o["iznos_prometa"] for o in db.ucitaj_ljude())
        podnosioc = db.ucitaj_podnosioca().get("pib_jmbg", "NIJE UNESEN")
        print()
        print(f"  [{godina}] Podnosioc: {podnosioc} | Unosa: {br_unosa} | Ukupno: {ukupno} RSD")
        
        print()
        print("=" * 60)
        print("  OPPSS GENERATOR v15.0 CLI STANDALONE")
        print("=" * 60)
        print("  1. Prikazi tabelu unosa")
        print("  2. Dodaj novi unos")
        print("  3. Obrisi unos")
        print("  4. Podaci o podnosiocu")
        print("  5. Generisi XML")
        print("  6. Pretraga")
        print("  7. Statistika")
        print("  8. Export CSV")
        print("  9. Promeni godinu")
        print("  0. Izlaz")
        print("-" * 60)
        
        try:
            izbor = input("  Izaberite opciju: ").strip()
        except EOFError:
            break
        
        if izbor == "0":
            print("  Hvala na koriscenju! Dovidjenja.")
            break
        
        elif izbor == "1":
            ljudi = db.ucitaj_ljude()
            if not ljudi:
                print("  (Nema unosa)")
            else:
                id_tipovi = {"0": "PIB", "1": "JMBG", "5": "EBS"}
                print()
                print(f"  {'RB':<4} {'Tip':<8} {'Identifikator':<15} {'Ime/Naziv':<25} {'Datum (od-do)':<25} {'Iznos':>10}")
                print("  " + "-" * 90)
                for i, o in enumerate(ljudi, 1):
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
                ukupno = sum(o["iznos_prometa"] for o in ljudi)
                print("  " + "-" * 90)
                print(f"  {'':>70} Ukupno: {ukupno:>10} RSD")
        
        elif izbor == "2":
            vrste_pr = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}
            vrste_id = {"0": "PIB", "1": "JMBG", "5": "EBS"}
            
            print()
            print("  NOVI UNOS:")
            
            print(f"  Vrsta prometa: 1={vrste_pr['1']}, 2={vrste_pr['2']}")
            while True:
                vrsta = input("  Vrsta prometa: ").strip()
                if vrsta in vrste_pr:
                    break
                print("  Izaberite 1 ili 2.")
            
            print(f"  Identifikator: 0=PIB (9 cifara), 1=JMBG (13 cifara), 5=EBS (9 cifara)")
            while True:
                id_tip = input("  Vrsta identifikatora: ").strip()
                if id_tip in vrste_id:
                    break
                print("  Izaberite 0, 1 ili 5.")
            
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
            
            datum_od = unesi_datum("Datum OD")
            datum_do = unesi_datum("Datum DO")
            
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
            
            db.dodaj_osobu(r)
            print("  ✅ Unos je sacuvan.")
        
        elif izbor == "3":
            ljudi = db.ucitaj_ljude()
            if not ljudi:
                print("  (Nema unosa za brisanje)")
                continue
            for i, o in enumerate(ljudi, 1):
                print(f"  {i}. {o.get('identifikator', '')} - {o.get('ime_naziv', '')}")
            try:
                rb = int(input("  Unesite RB za brisanje: ")) - 1
                if 0 <= rb < len(ljudi):
                    ime = ljudi[rb]["ime_naziv"]
                    potvrda = input("  Obrisati '{}'? (d/n): ".format(ime)).strip().lower()
                    if potvrda == "d":
                        db.obrisi_osobu(ljudi[rb]['id'])
                        print("  ✅ Unos je obrisan.")
                else:
                    print("  Pogresan RB.")
            except (ValueError, EOFError):
                print("  Pogresan unos.")
        
        elif izbor == "4":
            p = db.ucitaj_podnosioca()
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
            
            db.sacuvaj_podnosioca({
                "pib_jmbg": pib_jmbg,
                "email": email,
                "telefon": telefon,
                "jmbg": jmbg
            })
            print("  ✅ Podaci o podnosiocu su sacuvani.")
        
        elif izbor == "5":
            generisi_xml(db, godina)
        
        elif izbor == "6":
            print()
            print("  PRETRAGA:")
            print("  1. Po opštini")
            print("  2. Po imenu")
            print("  3. Po identifikatoru")
            print("  4. Po iznosu (od)")
            print("  5. Po iznosu (do)")
            try:
                tip = int(input("  Izaberite: "))
                uslovi = {1: "opstina", 2: "ime", 3: "identifikator", 4: "iznos_od", 5: "iznos_do"}
                if tip in uslovi:
                    vrednost = input("  Unesite vrednost: ").strip()
                    rezultati = db.pretraga(uslovi[tip], vrednost)
                    if rezultati:
                        for r in rezultati:
                            print(f"  {r['identifikator']} - {r['ime_naziv']} - {r['opstina']} - {r['iznos_prometa']} RSD")
                    else:
                        print("  (Nema rezultata)")
            except (ValueError, EOFError):
                print("  Pogresan unos.")
        
        elif izbor == "7":
            stat = db.statistika()
            print()
            print("  STATISTIKA:")
            print(f"  Ukupno unosa: {stat['ukupno_unosa']}")
            print(f"  Ukupan iznos: {stat['ukupno_iznos']} RSD")
            print()
            print("  Po vrsti prometa:")
            for v in stat['po_vrsti']:
                vrsta = "Poljoprivreda" if v['vrsta_prometa'] == '1' else "Sirovine"
                print(f"    {vrsta}: {v['COUNT(*)']} unosa, {v['SUM(iznos_prometa)']} RSD")
            print()
            print("  Po opštini:")
            for v in stat['po_opstini']:
                print(f"    {v['opstina']}: {v['COUNT(*)']} unosa, {v['SUM(iznos_prometa)']} RSD")
        
        elif izbor == "8":
            fajl = input("  Unesite ime CSV fajla (npr. OPPS_2026.csv): ").strip()
            if fajl:
                db.export_csv(fajl)
                print(f"  ✅ CSV fajl sačuvan: {fajl}")
        
        elif izbor == "9":
            nova_godina = input("  Unesite godinu (2023-2035): ").strip()
            if nova_godina.isdigit() and 2023 <= int(nova_godina) <= 2035:
                db.zatvori()
                godina = nova_godina
                db = Database(godina)
                print(f"  Godina promenjena na {godina}.")
            else:
                print("  Pogresna godina.")
    
    db.zatvori()


if __name__ == "__main__":
    main()
