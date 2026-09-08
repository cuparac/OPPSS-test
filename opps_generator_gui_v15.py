"""OPPSS GENERATOR v15.0 GUI STANDALONE - SQLite baza, CSV export, pretraga, izveštaji.
Grafička verzija (tkinter) sa ugrađenom XSD semom.
Ne zahteva poseban .xsd fajl. Kompatibilan sa 32/64 bit Windows.
Zahteva: pip install lxml"""

import json, os, sys, datetime, calendar as _cal, platform, sqlite3, csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

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


# ============================================================
# SQLite BAZA
# ============================================================

class Database:
    """SQLite baza podataka za OPPSS Generator."""
    
    def __init__(self, godina):
        self.godina = godina
        self.db_file = f"baza_{godina}.db"
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        self.kreiraj_tabele()
    
    def kreiraj_tabele(self):
        """Kreira tabele ako ne postoje."""
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
        """Učitava podatke o podnosiocu."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM podnosioc WHERE godina = ?", (self.godina,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {}
    
    def sacuvaj_podnosioca(self, podaci):
        """Čuva podatke o podnosiocu."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO podnosioc (godina, pib_jmbg, email, telefon, jmbg)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.godina, podaci['pib_jmbg'], podaci['email'], 
              podaci['telefon'], podaci['jmbg']))
        self.conn.commit()
    
    def ucitaj_ljude(self):
        """Učitava sve osobe."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ljudi WHERE godina = ?", (self.godina,))
        return [dict(row) for row in cursor.fetchall()]
    
    def dodaj_osobu(self, podaci):
        """Dodaje novu osobu."""
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
        return cursor.lastrowid
    
    def izmeni_osobu(self, id, podaci):
        """Menja postojeću osobu."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE ljudi SET 
                vrsta_prometa=?, vrsta_identifikatora=?, identifikator=?,
                ime_naziv=?, opstina=?, adresa=?, email_osobe=?,
                telefon=?, broj_gazdinstva=?, naziv_gazdinstva=?,
                datum=?, datum_do=?, iznos_prometa=?
            WHERE id=?
        ''', (podaci['vrsta_prometa'], podaci['vrsta_identifikatora'],
              podaci['identifikator'], podaci['ime_naziv'], podaci['opstina'],
              podaci['adresa'], podaci['email_osobe'], podaci['telefon'],
              podaci['broj_gazdinstva'], podaci['naziv_gazdinstva'],
              podaci['datum'], podaci['datum_do'], podaci['iznos_prometa'], id))
        self.conn.commit()
    
    def obrisi_osobu(self, id):
        """Briše osobu."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM ljudi WHERE id = ?", (id,))
        self.conn.commit()
    
    def pretraga(self, uslov, parametri=None):
        """Pretraga po različitim kriterijumima."""
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
        elif uslov == "datum_od":
            sql += " AND datum >= ?"
            params.append(parametri)
        elif uslov == "datum_do":
            sql += " AND datum <= ?"
            params.append(parametri)
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def statistika(self):
        """Vraća statistiku za godinu."""
        cursor = self.conn.cursor()
        
        # Ukupan broj unosa i iznos
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(iznos_prometa), 0) FROM ljudi WHERE godina = ?", (self.godina,))
        ukupno = cursor.fetchone()
        
        # Po vrsti prometa
        cursor.execute("SELECT vrsta_prometa, COUNT(*), SUM(iznos_prometa) FROM ljudi WHERE godina = ? GROUP BY vrsta_prometa", (self.godina,))
        po_vrsti = cursor.fetchall()
        
        # Po opštini
        cursor.execute("SELECT opstina, COUNT(*), SUM(iznos_prometa) FROM ljudi WHERE godina = ? GROUP BY opstina ORDER BY SUM(iznos_prometa) DESC", (self.godina,))
        po_opstini = cursor.fetchall()
        
        return {
            'ukupno_unosa': ukupto[0],
            'ukupno_iznos': ukupto[1],
            'po_vrsti': [dict(r) for r in po_vrsti],
            'po_opstini': [dict(r) for r in po_opstini]
        }
    
    def export_csv(self, fajl_putanja):
        """Izvoz u CSV fajl."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ljudi WHERE godina = ?", (self.godina,))
        rows = cursor.fetchall()
        
        with open(fajl_putanja, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            # Zaglavlje
            writer.writerow(['RB', 'Vrsta prometa', 'Vrsta ID', 'Identifikator', 
                           'Ime/Naziv', 'Opština', 'Adresa', 'Email', 'Telefon',
                           'Br. gazdinstva', 'Naziv gazdinstva', 'Datum OD', 
                           'Datum DO', 'Iznos'])
            # Podaci
            for i, row in enumerate(rows, 1):
                writer.writerow([
                    i, row['vrsta_prometa'], row['vrsta_identifikatora'],
                    row['identifikator'], row['ime_naziv'], row['opstina'],
                    row['adresa'], row['email_osobe'], row['telefon'],
                    row['broj_gazdinstva'], row['naziv_gazdinstva'],
                    row['datum'], row['datum_do'], row['iznos_prometa']
                ])
    
    def zatvori(self):
        """Zatvara konekciju sa bazom."""
        self.conn.close()


def migriraj_json_u_sqlite(godina):
    """Migrira postojeći JSON fajl u SQLite bazu."""
    json_file = f"baza_{godina}.json"
    db_file = f"baza_{godina}.db"
    
    if not os.path.exists(json_file):
        return False, "JSON fajl ne postoji"
    
    try:
        with open(json_file, encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return False, f"Greška pri čitanju JSON-a: {e}"
    
    db = Database(godina)
    
    # Migracija podnosioca
    podnosioc = data.get("podnosioc", {})
    if podnosioc and podnosioc.get("pib_jmbg"):
        db.sacuvaj_podnosioca(podnosioc)
    
    # Migracija ljudi
    ljudi = data.get("ljudi", [])
    for osoba in ljudi:
        db.dodaj_osobu(osoba)
    
    db.zatvori()
    
    # Backup JSON fajla
    backup_file = f"baza_{godina}.json.backup"
    os.rename(json_file, backup_file)
    
    return True, f"Migracija uspešna! {len(ljudi)} unosa prebaceno. JSON backup: {backup_file}"


def generisi_xml(db, godina):
    """Generiše XML fajl iz SQLite baze."""
    podnosioc = db.ucitaj_podnosioca()
    ljudi = db.ucitaj_ljude()
    
    if not podnosioc or not podnosioc.get("pib_jmbg"):
        messagebox.showerror("Greska", "Prvo unesite podatke o PODNOSIOCU za izabranu godinu!")
        return None
    if not ljudi:
        messagebox.showerror("Greska", "Dodajte bar jednu osobu!")
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
    sazetak = ("Godina: %s\nBroj unosa: %d\nUkupan iznos: %s RSD" %
               (godina, len(ljudi), format(ukupno, ",").replace(",", ".")))

    schema = get_xsd_schema()
    if schema:
        if schema.validate(root):
            messagebox.showinfo("Uspeh", "[OK] %s je VALIDAN!\n\nSpreman za upload na ePorezi portal.\n\n%s" % (izlaz, sazetak))
        else:
            greske = "\n".join(e.message for e in schema.error_log)
            messagebox.showerror("Validacija NIJE uspela", "XML je kreiran ali ima gresaka:\n\n" + greske)
    else:
        messagebox.showwarning("Nema XSD seme", "XML je kreiran ALI NIJE validiran.")
    return izlaz


# ============================================================
# GUI APLIKACIJA
# ============================================================

class DatumEntry(ttk.Entry):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.bind("<KeyRelease>", self._fmt)
        self.configure(justify="center")

    def _fmt(self, ev):
        if ev.keysym in ("BackSpace", "Delete", "Left", "Right", "Home", "End", "Tab", "Return"):
            return
        c = "".join(x for x in self.get() if x.isdigit())[:8]
        r = c[:2] + "/" + c[2:4] + "/" + c[4:] if len(c) > 4 else (c[:2] + "/" + c[2:] if len(c) > 2 else c)
        self.delete(0, "end"); self.insert(0, r); self.icursor("end")

    def dobar_datum(self):
        return konvertuj_datum(self.get()) is not None and len(
            "".join(c for c in self.get() if c.isdigit())) == 8


class Kalendar(tk.Toplevel):
    MESECI = ["Januar", "Februar", "Mart", "April", "Maj", "Jun", "Jul",
              "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar"]
    DANI = ["Po", "Ut", "Sr", "Ce", "Pe", "Su", "Ne"]

    def __init__(self, entry, x, y):
        super().__init__()
        self.entry = entry
        self.overrideredirect(True)
        self.geometry("+%d+%d" % (x, y))
        self.attributes("-topmost", True)
        try:
            d = datetime.datetime.strptime(entry.get().strip(), "%d/%m/%Y")
        except ValueError:
            d = datetime.date.today()
        self.godina, self.mesec = d.year, d.month
        okvir = tk.Frame(self, bd=1, relief="solid", bg="white")
        okvir.pack()
        self.naslov = tk.Label(okvir, font=("Segoe UI", 10, "bold"), bg="white")
        self.naslov.pack(fill="x", padx=5, pady=(5, 0))
        nav = tk.Frame(okvir, bg="white")
        nav.pack(fill="x", pady=2)
        tk.Button(nav, text="<", width=3, command=lambda: self.mes(-1)).pack(side="left", padx=5)
        tk.Button(nav, text="Danas", width=6, command=self.danas).pack(side="left", expand=True)
        tk.Button(nav, text=">", width=3, command=lambda: self.mes(1)).pack(side="right", padx=5)
        self.gf = tk.Frame(okvir, bg="white")
        self.gf.pack(padx=5, pady=5)
        self.crtaj()
        self.grab_set()
        self.focus_set()
        self.bind("<Escape>", lambda e: self.zatvori())
        self.bind("<FocusOut>", lambda e: self.after(200, self.proveri_zatvori))

    def proveri_zatvori(self):
        try:
            aktivan = self.focus_get()
        except Exception:
            aktivan = None
        if aktivan is None or not str(aktivan).startswith(str(self)):
            self.zatvori()

    def mes(self, s):
        self.mesec += s
        if self.mesec > 12:
            self.mesec, self.godina = 1, self.godina + 1
        elif self.mesec < 1:
            self.mesec, self.godina = 12, self.godina - 1
        self.crtaj()
        self.grab_set()

    def danas(self):
        t = datetime.date.today()
        self.izaberi(t.day, t.month, t.year)

    def crtaj(self):
        for w in self.gf.winfo_children():
            w.destroy()
        self.naslov.config(text=self.MESECI[self.mesec - 1] + " " + str(self.godina))
        for col, ime in enumerate(self.DANI):
            tk.Label(self.gf, text=ime, width=4, anchor="center",
                     font=("Segoe UI", 8, "bold"), bg="white").grid(row=0, column=col)
        start = datetime.date(self.godina, self.mesec, 1).weekday()
        dan, red = 1, 1
        br_dana = _cal.monthrange(self.godina, self.mesec)[1]
        for kol in range(start):
            tk.Label(self.gf, text="", width=4, bg="white").grid(row=red, column=kol)
        for kol in range(start, 7):
            self.dugme(dan, red, kol); dan += 1
        while dan <= br_dana:
            red += 1
            for kol in range(7):
                if dan > br_dana:
                    break
                self.dugme(dan, red, kol); dan += 1

    def dugme(self, dan, red, kol):
        b = tk.Label(self.gf, text=str(dan), width=4, anchor="center",
                     cursor="hand2", bg="white")
        b.grid(row=red, column=kol)
        b.bind("<Button-1>", lambda e, d=dan: self.izaberi(d, self.mesec, self.godina))
        b.bind("<Enter>", lambda e: b.config(background="#cce5ff"))
        b.bind("<Leave>", lambda e: b.config(background="white"))

    def izaberi(self, dan, mesec, godina):
        self.entry.delete(0, "end")
        self.entry.insert(0, "%02d/%02d/%d" % (dan, mesec, godina))
        self.zatvori()
        self.entry.focus_set(); self.entry.icursor("end")

    def zatvori(self):
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass


class ProzorPodnosioca(tk.Toplevel):
    def __init__(self, parent, db, godina):
        super().__init__(parent)
        self.title("Podaci o podnosiocu prijave - " + godina + ". godina")
        self.grab_set(); self.resizable(False, False)
        self.db = db
        self.godina = godina
        p = db.ucitaj_podnosioca()
        okvir = ttk.Frame(self, padding=20)
        okvir.pack(fill="both", expand=True)
        ttk.Label(okvir, text="Godina podnosenja: " + godina,
                  font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.entries = {}
        polja = [("pib_jmbg", "PIB (9 cifara) ili JMBG (13 cifara):"),
                 ("email", "E-posta:"), ("telefon", "Telefon:"),
                 ("jmbg", "JMBG podnosioca (13 cifara):")]
        for row, (key, label) in enumerate(polja, start=1):
            ttk.Label(okvir, text=label).grid(row=row, column=0, sticky="w", pady=4)
            e = ttk.Entry(okvir, width=40)
            e.grid(row=row, column=1, padx=10, pady=4)
            e.insert(0, p.get(key, ""))
            self.entries[key] = e
        self.status_jmbg = ttk.Label(okvir, text="", font=("Segoe UI", 9), foreground="gray")
        self.status_jmbg.grid(row=len(polja), column=2, sticky="w", padx=(5, 0))

        def proveri(event=None):
            v = self.entries["jmbg"].get().strip()
            if not v:
                self.status_jmbg.config(text="")
            elif len(v) == 13 and v.isdigit():
                ok = validan_jmbg(v)
                self.status_jmbg.config(text="[OK] ispravan" if ok else "[X] NEISPRAVAN!",
                                        foreground="green" if ok else "red")
            else:
                self.status_jmbg.config(text="%d/13" % len(v), foreground="gray")

        self.entries["jmbg"].bind("<KeyRelease>", proveri)
        proveri()
        dugmad = ttk.Frame(okvir)
        dugmad.grid(row=len(polja) + 1, column=0, columnspan=3, pady=15)
        ttk.Button(dugmad, text="Sacuvaj", command=self.sacuvaj).pack(side="left", padx=5)
        ttk.Button(dugmad, text="Ocisti sva polja", command=self.ocisti).pack(side="left", padx=5)
        for e in self.entries.values():
            e.bind("<Return>", lambda ev: self.sacuvaj())

    def sacuvaj(self):
        d = {k: e.get().strip() for k, e in self.entries.items()}
        if not all(d.values()):
            messagebox.showwarning("Upozorenje", "Popunite SVA polja!", parent=self)
            return
        if not validan_jmbg(d["jmbg"]):
            if not messagebox.askyesno("Upozorenje",
                                       "JMBG podnosioca (%s) NE prolazi proveru kontrolne cifre!\n\nDa li ipak zelite da sacuvate?" % d["jmbg"],
                                       parent=self):
                return
        broj = d["pib_jmbg"].strip()
        if not (len(broj) in (9, 13) and broj.isdigit()):
            messagebox.showerror("Greska", "Polje 'PIB ili JMBG' mora imati TACNO 9 cifara (PIB) ili TACNO 13 cifara (JMBG)!", parent=self)
            return
        self.db.sacuvaj_podnosioca(d)
        messagebox.showinfo("Sacuvano", "Podaci o podnosiocu (%s) su sacuvani." % self.godina, parent=self)
        self.destroy()

    def ocisti(self):
        if not self.db.ucitaj_podnosioca():
            messagebox.showinfo("Ciscenje", "Sva polja su vec prazna.", parent=self)
            return
        if messagebox.askyesno("Potvrda ciscenja",
                               "Obrisati SVE podatke o podnosiocu za %s. godinu?\n\n(Unosi osoba u tabeli ostaju netaknuti!)" % self.godina,
                               parent=self):
            for e in self.entries.values():
                e.delete(0, "end")
            self.db.sacuvaj_podnosioca({'pib_jmbg': '', 'email': '', 'telefon': '', 'jmbg': ''})
            self.status_jmbg.config(text="")
            messagebox.showinfo("Ocisceno", "Podaci o podnosiocu su obrisani.", parent=self)


class ProzorPretrage(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Pretraga")
        self.db = db
        self.geometry("700x500")
        
        okvir = ttk.Frame(self, padding=10)
        okvir.pack(fill="both", expand=True)
        
        # Kriterijumi pretrage
        ttk.Label(okvir, text="Pretraga po:").grid(row=0, column=0, sticky="w")
        self.kriterijum = ttk.Combobox(okvir, values=["opstina", "ime", "identifikator", "iznos_od", "iznos_do", "datum_od", "datum_do"], width=15)
        self.kriterijum.grid(row=0, column=1, padx=5)
        self.kriterijum.current(0)
        
        self.vrednost = ttk.Entry(okvir, width=30)
        self.vrednost.grid(row=0, column=2, padx=5)
        
        ttk.Button(okvir, text="Pretraži", command=self.pretrazi).grid(row=0, column=3, padx=5)
        ttk.Button(okvir, text="Prikaži sve", command=self.prikazi_sve).grid(row=0, column=4, padx=5)
        
        # Tabela rezultata
        kolone = ("id", "tip", "identifikator", "ime_naziv", "opstina", "datum", "iznos")
        self.tree = ttk.Treeview(okvir, columns=kolone, show="headings", height=15)
        for k in kolone:
            self.tree.heading(k, text=k)
            self.tree.column(k, width=80)
        self.tree.column("ime_naziv", width=150)
        self.tree.grid(row=1, column=0, columnspan=5, pady=10, sticky="nsew")
        
        sb = ttk.Scrollbar(okvir, orient="vertical", command=self.tree.yview)
        sb.grid(row=1, column=5, sticky="ns")
        self.tree.configure(yscrollcommand=sb.set)
        
        self.prikazi_sve()
    
    def pretrazi(self):
        kriterijum = self.kriterijum.get()
        vrednost = self.vrednost.get().strip()
        if not vrednost:
            return
        
        rezultati = self.db.pretraga(kriterijum, vrednost)
        self.tree.delete(*self.tree.get_children())
        for r in rezultati:
            self.tree.insert("", "end", values=(
                r['id'], r['vrsta_identifikatora'], r['identifikator'],
                r['ime_naziv'], r['opstina'], r['datum'], r['iznos_prometa']
            ))
    
    def prikazi_sve(self):
        ljudi = self.db.ucitaj_ljude()
        self.tree.delete(*self.tree.get_children())
        for r in ljudi:
            self.tree.insert("", "end", values=(
                r['id'], r['vrsta_identifikatora'], r['identifikator'],
                r['ime_naziv'], r['opstina'], r['datum'], r['iznos_prometa']
            ))


class ProzorStatistike(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Statistika")
        self.db = db
        self.geometry("500x400")
        
        okvir = ttk.Frame(self, padding=10)
        okvir.pack(fill="both", expand=True)
        
        stat = db.statistika()
        
        ttk.Label(okvir, text="STATISTIKA", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        ttk.Label(okvir, text=f"Ukupno unosa: {stat['ukupno_unosa']}", font=("Segoe UI", 11)).pack(anchor="w")
        ttk.Label(okvir, text=f"Ukupan iznos: {stat['ukupno_iznos']} RSD", font=("Segoe UI", 11)).pack(anchor="w")
        
        ttk.Separator(okvir, orient="horizontal").pack(fill="x", pady=10)
        
        ttk.Label(okvir, text="Po vrsti prometa:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        for v in stat['po_vrsti']:
            vrsta = "Poljoprivreda" if v['vrsta_prometa'] == '1' else "Sirovine"
            ttk.Label(okvir, text=f"  {vrsta}: {v['COUNT(*)']} unosa, {v['SUM(iznos_prometa)']} RSD").pack(anchor="w")
        
        ttk.Separator(okvir, orient="horizontal").pack(fill="x", pady=10)
        
        ttk.Label(okvir, text="Po opštini:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        for v in stat['po_opstini']:
            ttk.Label(okvir, text=f"  {v['opstina']}: {v['COUNT(*)']} unosa, {v['SUM(iznos_prometa)']} RSD").pack(anchor="w")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OPPSS Generator v15.0 GUI STANDALONE - ePorezi prijava")
        self.geometry("1000x700")
        
        # Prvo kreiraj godina_var, pa tek onda koristi property
        self._godina = str(datetime.date.today().year)
        self.godina_var = tk.StringVar(value=self._godina)
        self.db = Database(self._godina)
        
        # Provera za migraciju
        self.proveri_migraciju()
        
        self.bind("<Control-n>", lambda e: self.dodaj_osobu())
        self.bind("<Control-d>", lambda e: self.obrisi_osobu())
        self.bind("<Control-g>", lambda e: self.generisi())
        self.bind("<Control-p>", lambda e: self.otvori_podnosioca())
        self.bind("<Control-f>", lambda e: self.pretraga())
        self.bind("<F1>", lambda e: self.prikazi_about())
        
        # Meni
        meni = tk.Menu(self)
        self.config(menu=meni)
        
        datoteka_meni = tk.Menu(meni, tearoff=0)
        meni.add_cascade(label="Datoteka", menu=datoteka_meni)
        datoteka_meni.add_command(label="Podaci o podnosiocu (Ctrl+P)", command=self.otvori_podnosioca)
        datoteka_meni.add_separator()
        datoteka_meni.add_command(label="Export CSV", command=self.export_csv)
        datoteka_meni.add_separator()
        datoteka_meni.add_command(label="Izađi", command=self.quit)
        
        unos_meni = tk.Menu(meni, tearoff=0)
        meni.add_cascade(label="Unos", menu=unos_meni)
        unos_meni.add_command(label="Dodaj (Ctrl+N)", command=self.dodaj_osobu)
        unos_meni.add_command(label="Izmeni", command=self.izmeni_osobu)
        unos_meni.add_command(label="Obriši (Ctrl+D)", command=self.obrisi_osobu)
        
        alat_meni = tk.Menu(meni, tearoff=0)
        meni.add_cascade(label="Alat", menu=alat_meni)
        alat_meni.add_command(label="Pretraga (Ctrl+F)", command=self.pretraga)
        alat_meni.add_command(label="Statistika", command=self.statistika)
        alat_meni.add_command(label="Migracija JSON → SQLite", command=self.migracija)
        
        pomoc_meni = tk.Menu(meni, tearoff=0)
        meni.add_cascade(label="Pomoć", menu=pomoc_meni)
        pomoc_meni.add_command(label="O aplikaciji (F1)", command=self.prikazi_about)
        
        # Glavni prozor
        traka = ttk.Frame(self, padding=10)
        traka.pack(fill="x")
        ttk.Label(traka, text="Godina podnosenja:", font=("Segoe UI", 11, "bold")).pack(side="left")
        self.godina_var = tk.StringVar(value=self.godina)
        combo = ttk.Combobox(traka, textvariable=self.godina_var, state="readonly", width=8,
                             values=[str(y) for y in range(2023, 2036)])
        combo.pack(side="left", padx=10)
        combo.bind("<<ComboboxSelected>>", lambda e: self.promeni_godinu())
        
        gore = ttk.LabelFrame(self, text=" Prijava ", padding=10)
        gore.pack(fill="x", padx=10, pady=5)
        self.info_podnosioc = ttk.Label(gore, font=("Segoe UI", 10))
        self.info_podnosioc.pack(side="left")
        ttk.Button(gore, text="Podaci podnosioca...", command=self.otvori_podnosioca).pack(side="right", padx=5)
        
        # Tabela
        tf = ttk.Frame(self)
        tf.pack(fill="both", expand=True, padx=10, pady=5)
        kolone = ("rb", "tip", "identifikator", "ime_naziv", "opstina", "adresa", "telefon", "datum", "iznos")
        naslovi = {"rb": "R.br", "tip": "Vrsta prometa", "identifikator": "JMBG/PIB/EBS",
                   "ime_naziv": "Ime / Naziv", "opstina": "Opština", "adresa": "Adresa",
                   "telefon": "Telefon", "datum": "Datum (od/do)", "iznos": "Iznos (RSD)"}
        sirine = {"rb": 45, "tip": 165, "identifikator": 115, "ime_naziv": 170,
                  "opstina": 120, "adresa": 140, "telefon": 105, "datum": 100, "iznos": 95}
        self.tree = ttk.Treeview(tf, columns=kolone, show="headings", height=12)
        for k in kolone:
            self.tree.heading(k, text=naslovi[k])
            self.tree.column(k, width=sirine[k])
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        
        # Dugmad
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=10, pady=5)
        ttk.Button(btns, text="+ Dodaj unos", command=self.dodaj_osobu).pack(side="left", padx=3)
        ttk.Button(btns, text="Izmeni", command=self.izmeni_osobu).pack(side="left", padx=3)
        ttk.Button(btns, text="Obriši", command=self.obrisi_osobu).pack(side="left", padx=3)
        self.ukupno_label = ttk.Label(btns, font=("Segoe UI", 11, "bold"))
        self.ukupno_label.pack(side="left", padx=30)
        ttk.Button(btns, text="Pretraga", command=self.pretraga).pack(side="left", padx=3)
        ttk.Button(btns, text="Statistika", command=self.statistika).pack(side="left", padx=3)
        ttk.Button(btns, text="Export CSV", command=self.export_csv).pack(side="left", padx=3)
        ttk.Button(btns, text="GENERISI XML", command=self.generisi).pack(side="right", padx=3)
        
        # Status bar
        status_bar = ttk.Frame(self)
        status_bar.pack(fill="x", side="bottom")
        ttk.Label(status_bar, text="F1 = Pomoć | Ctrl+N = Novi | Ctrl+D = Obriši | Ctrl+F = Pretraga | Ctrl+G = XML | Ctrl+P = Podnosioc",
                  font=("Segoe UI", 8), foreground="gray").pack(side="left", padx=10)
        
        self.osvezi_sve()
    
    def proveri_migraciju(self):
        """Proverava da li postoji stari JSON fajl za migraciju."""
        json_file = f"baza_{self.godina}.json"
        if os.path.exists(json_file):
            odgovor = messagebox.askyesno("Migracija", 
                "Pronađen je stari JSON fajl. Želite li da ga migrirate u SQLite bazu?")
            if odgovor:
                self.migracija()
    
    def migracija(self):
        """Migrira JSON u SQLite."""
        json_file = f"baza_{self.godina}.json"
        if not os.path.exists(json_file):
            messagebox.showinfo("Migracija", "Nema JSON fajla za migraciju.")
            return
        
        uspeh, poruka = migriraj_json_u_sqlite(self.godina)
        if uspeh:
            messagebox.showinfo("Migracija", poruka)
            self.osvezi_sve()
        else:
            messagebox.showerror("Migracija", poruka)
    
    def export_csv(self):
        """Izvoz u CSV fajl."""
        fajl = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV fajlovi", "*.csv"), ("Svi fajlovi", "*.*")],
            initialfile=f"OPPS_{self.godina}.csv"
        )
        if fajl:
            self.db.export_csv(fajl)
            messagebox.showinfo("Export", f"CSV fajl sačuvan: {fajl}")
    
    def pretraga(self):
        """Otvara prozor za pretragu."""
        ProzorPretrage(self, self.db)
    
    def statistika(self):
        """Otvara prozor sa statistikom."""
        ProzorStatistike(self, self.db)
    
    def prikazi_about(self):
        messagebox.showinfo("O aplikaciji",
                            "OPPSS Generator v15.0 GUI STANDALONE\n\n"
                            "Aplikacija za generisanje OOPSS prijava\n"
                            "za portal ePorezi (Poreska uprava RS)\n\n"
                            "Verzija: 15.0\n"
                            "Baza: SQLite\n"
                            "XSD šema: ugrađena\n\n"
                            "Python: " + sys.version.split()[0] + "\n"
                            "Platforma: " + platform.system())
    
    def promeni_godinu(self):
        """Menja godinu."""
        self.db.zatvori()
        self._godina = self.godina_var.get()
        self.db = Database(self._godina)
        self.osvezi_sve()
    
    @property
    def godina(self):
        return self._godina
    
    @godina.setter
    def godina(self, value):
        self._godina = value
        self.godina_var.set(value)
    
    def otvori_podnosioca(self):
        ProzorPodnosioca(self, self.db, self.godina)
        self.osvezi_info()
    
    def osvezi_info(self):
        p = self.db.ucitaj_podnosioca()
        if p.get("pib_jmbg"):
            self.info_podnosioc.config(text="Podnosioc: %s   |   Godina: %s" % (p['pib_jmbg'], self.godina))
        else:
            self.info_podnosioc.config(text="[!] Podaci o podnosiocu NISU uneseni za %s. godinu!" % self.godina)
    
    def osvezi_tabelu(self):
        self.tree.delete(*self.tree.get_children())
        ljudi = self.db.ucitaj_ljude()
        tipovi = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}
        for i, o in enumerate(ljudi, 1):
            prikaz = ""
            if o.get("datum"):
                try:
                    datum_od = datetime.datetime.strptime(o["datum"], "%Y-%m-%d").strftime("%d/%m/%Y")
                    datum_do = datetime.datetime.strptime(o.get("datum_do", o["datum"]), "%Y-%m-%d").strftime("%d/%m/%Y")
                    prikaz = datum_od + " - " + datum_do
                except ValueError:
                    prikaz = o["datum"]
            self.tree.insert("", "end", iid=str(o['id']), values=(
                i, tipovi.get(o["vrsta_prometa"], "?"), o["identifikator"],
                o["ime_naziv"], o["opstina"], o["adresa"], o["telefon"],
                prikaz, format(o['iznos_prometa'], ",").replace(",", ".")))
        ukupno = sum(o["iznos_prometa"] for o in ljudi)
        self.ukupno_label.config(text="%d unosa | Ukupno: %s RSD" % (len(ljudi), format(ukupno, ",").replace(",", ".")))
    
    def osvezi_sve(self):
        self.osvezi_tabelu()
        self.osvezi_info()
    
    def dodaj_osobu(self):
        self.forma_osobe()
    
    def izmeni_osobu(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Izaberite unos u tabeli!")
            return
        id = int(sel[0])
        ljudi = self.db.ucitaj_ljude()
        osoba = next((o for o in ljudi if o['id'] == id), None)
        if osoba:
            self.forma_osobe(osoba, id)
    
    def obrisi_osobu(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Izaberite unos u tabeli!")
            return
        id = int(sel[0])
        ime = self.tree.item(sel[0])['values'][3]
        if messagebox.askyesno("Brisanje", "Obrisati unos: " + str(ime) + "?"):
            self.db.obrisi_osobu(id)
            self.osvezi_tabelu()
    
    def forma_osobe(self, podrazumevano=None, indeks_izmene=None):
        win = tk.Toplevel(self)
        win.title("Izmena unosa" if podrazumevano else "Novi unos")
        win.grab_set(); win.resizable(False, False)
        okvir = ttk.Frame(win, padding=20)
        okvir.pack(fill="both", expand=True)

        vrste_pr = {"Poljoprivredni proizvodi/usluge": "1", "Sekundarne sirovine": "2"}
        vrste_id = {"JMBG": "1", "PIB": "0", "EBS": "5"}
        entries = {}
        redovi = [
            ("vrsta_tip", "VRSTA PROMETA:", list(vrste_pr.keys())),
            ("id_tip", "Identifikator:", list(vrste_id.keys())),
            ("identifikator", "JMBG / PIB / EBS broj:", None),
            ("ime_naziv", "Ime i prezime / Naziv:", None),
            ("opstina", "Opstina:", None),
            ("adresa", "Adresa:", None),
            ("email_osobe", "E-posta osobe:", None),
            ("telefon", "Broj telefona:", None),
            ("broj_gazdinstva", "Broj poljoprivrednog gazdinstva:", None),
            ("naziv_gazdinstva", "Naziv poljoprivrednog gazdinstva:", None),
            ("datum_unos", "Datum OD:", None),
            ("datum_do", "Datum DO:", None),
            ("iznos_prometa", "Iznos prometa (RSD, ceo broj):", None),
        ]
        for row, (key, label, opcije) in enumerate(redovi):
            ttk.Label(okvir, text=label).grid(row=row, column=0, sticky="w", pady=4)
            if opcije:
                cb = ttk.Combobox(okvir, values=opcije, state="readonly", width=38)
                cb.current(0)
                cb.grid(row=row, column=1, padx=10, pady=4)
                entries[key] = cb
            elif key in ("datum_unos", "datum_do"):
                de = DatumEntry(okvir, width=40)
                de.grid(row=row, column=1, padx=10, pady=4)
                entries[key] = de
            else:
                e = ttk.Entry(okvir, width=40)
                e.grid(row=row, column=1, padx=10, pady=4)
                entries[key] = e

        entries["datum_unos"].insert(0, datetime.date.today().strftime("%d/%m/%Y"))
        entries["datum_do"].insert(0, datetime.date.today().strftime("%d/%m/%Y"))

        napomena_id = ttk.Label(okvir, text="", foreground="gray", font=("Segoe UI", 9))
        napomena_id.grid(row=2, column=2, sticky="w", padx=(5, 0))

        def limit_za_tip():
            tip = entries["id_tip"].get()
            if tip == "JMBG":
                return 13
            elif tip == "EBS":
                return 9
            else:
                return 9

        def proveri_identifikator():
            try:
                v = entries["identifikator"].get().strip()
                lim = limit_za_tip()
                if not v:
                    napomena_id.config(text="(%d cifara)" % lim, foreground="gray")
                elif len(v) < lim:
                    napomena_id.config(text="(uneseno %d/%d)" % (len(v), lim), foreground="gray")
                elif entries["id_tip"].get() == "JMBG":
                    if validan_jmbg(v):
                        napomena_id.config(text="[OK] ispravan JMBG", foreground="green")
                    else:
                        napomena_id.config(text="[X] NEISPRAVAN JMBG!", foreground="red")
                elif entries["id_tip"].get() == "EBS":
                    if validan_ebs(v):
                        napomena_id.config(text="[OK] ispravan EBS", foreground="green")
                    else:
                        napomena_id.config(text="[X] NEISPRAVAN EBS!", foreground="red")
                else:
                    napomena_id.config(text="[OK] 9 cifara (PIB)", foreground="green")
            except Exception as e:
                napomena_id.config(text="GRESKA: " + str(e), foreground="red")

        def azuriraj_limit():
            lim = limit_za_tip()
            if len(entries["identifikator"].get()) > lim:
                entries["identifikator"].delete(lim, "end")
            proveri_identifikator()

        info_dupli = ttk.Label(okvir, text="", foreground="blue", font=("Segoe UI", 9))
        info_dupli.grid(row=3, column=2, sticky="w", padx=(5, 0))

        def na_kucanje(ev=None):
            try:
                if ev is not None and ev.keysym in ("BackSpace", "Delete", "Left",
                                                    "Right", "Home", "End", "Tab", "Return"):
                    proveri_identifikator()
                    return
                lim = limit_za_tip()
                c = "".join(x for x in entries["identifikator"].get() if x.isdigit())[:lim]
                entries["identifikator"].delete(0, "end")
                entries["identifikator"].insert(0, c)
                entries["identifikator"].icursor("end")
                proveri_identifikator()
                broj = entries["identifikator"].get().strip()
                if len(broj) != lim:
                    info_dupli.config(text="")
                    return
                ljudi = self.db.ucitaj_ljude()
                nadjen = next((o for o in ljudi if o["identifikator"] == broj), None)
                if nadjen:
                    for k in ("ime_naziv", "opstina", "adresa", "email_osobe", "telefon", "broj_gazdinstva", "naziv_gazdinstva"):
                        if k in entries:
                            entries[k].delete(0, "end")
                            entries[k].insert(0, nadjen.get(k, ""))
                    info_dupli.config(text="[i] Podaci popunjeni iz tabele - unesite datum i iznos",
                                      foreground="blue")
                    win.after(10, lambda: (entries["datum_unos"].focus_set(),
                                           entries["datum_unos"].icursor("end")))
                else:
                    info_dupli.config(text="")
            except Exception as e:
                info_dupli.config(text="GRESKA: " + str(e), foreground="red")

        entries["identifikator"].bind("<KeyRelease>", na_kucanje)
        entries["id_tip"].bind("<<ComboboxSelected>>", lambda e: azuriraj_limit())
        proveri_identifikator()

        btn_kal_od = ttk.Button(okvir, text="\U0001F4C5", width=3)
        btn_kal_od.grid(row=10, column=2, sticky="w", padx=(5, 0))
        def otvori_kalendar_od():
            Kalendar(entries["datum_unos"], win.winfo_rootx() + 350, win.winfo_rooty() + 250)
        btn_kal_od.configure(command=otvori_kalendar_od)

        btn_kal_do = ttk.Button(okvir, text="\U0001F4C5", width=3)
        btn_kal_do.grid(row=11, column=2, sticky="w", padx=(5, 0))
        def otvori_kalendar_do():
            Kalendar(entries["datum_do"], win.winfo_rootx() + 350, win.winfo_rooty() + 300)
        btn_kal_do.configure(command=otvori_kalendar_do)

        ttk.Label(okvir, text="(kucajte samo cifre - kose crte se dodaju same: 01012026)",
                  foreground="gray").grid(row=len(redovi), column=1, sticky="w", padx=10)

        if podrazumevano:
            mapa = {"vrsta_tip": next((k for k, v in vrste_pr.items()
                                       if v == podrazumevano.get("vrsta_prometa")), list(vrste_pr)[0]),
                    "id_tip": next((k for k, v in vrste_id.items()
                                    if v == podrazumevano.get("vrsta_identifikatora")), list(vrste_id)[0])}
            for key, w in entries.items():
                if key in ("datum_unos", "datum_do"):
                    w.delete(0, "end")
                    if podrazumevano.get(key):
                        try:
                            w.insert(0, datetime.datetime.strptime(
                                podrazumevano[key], "%Y-%m-%d").strftime("%d/%m/%Y"))
                        except ValueError:
                            pass
                    continue
                vrednost = podrazumevano.get(mapa.get(key, key), "")
                if hasattr(w, "set"):
                    w.set(vrednost)
                else:
                    w.insert(0, str(vrednost))
            azuriraj_limit()

        def sacuvaj():
            datum_iso = konvertuj_datum(entries["datum_unos"].get())
            if not datum_iso or not entries["datum_unos"].dobar_datum():
                messagebox.showerror("Greska", "Neispravan datum OD!\nKucajte 8 cifara: DDMMYYYY\nPrimer: 01012026", parent=win)
                return
            datum_do_iso = konvertuj_datum(entries["datum_do"].get())
            if not datum_do_iso or not entries["datum_do"].dobar_datum():
                messagebox.showerror("Greska", "Neispravan datum DO!\nKucajte 8 cifara: DDMMYYYY\nPrimer: 01012026", parent=win)
                return
            if datum_do_iso < datum_iso:
                messagebox.showerror("Greska", "Datum DO ne moze biti pre datuma OD!", parent=win)
                return
            broj_id = entries["identifikator"].get().strip()
            tip = entries["id_tip"].get()
            ocekivano = 13 if tip == "JMBG" else 9
            if not broj_id.isdigit() or len(broj_id) != ocekivano:
                messagebox.showerror("Greska", "Identifikator mora imati TACNO %d cifara!\n(Uneseno: %d)" % (ocekivano, len(broj_id)), parent=win)
                return
            if tip == "JMBG" and not validan_jmbg(broj_id):
                if not messagebox.askyesno("Upozorenje",
                                           "JMBG (%s) NE prolazi proveru kontrolne cifre!\n\nDa li IPAK zelite da sacuvate ovaj unos?" % broj_id,
                                           parent=win):
                    return
            if tip == "EBS" and not validan_ebs(broj_id):
                if not messagebox.askyesno("Upozorenje",
                                           "EBS (%s) NIJE ispravan (mora imati 9 cifara)!\n\nDa li IPAK zelite da sacuvate ovaj unos?" % broj_id,
                                           parent=win):
                    return
            try:
                iznos = int(entries["iznos_prometa"].get().strip())
                if iznos <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Greska", "Iznos mora biti pozitivan ceo broj!", parent=win)
                return
            r = {
                "vrsta_prometa": vrste_pr[entries["vrsta_tip"].get()],
                "vrsta_identifikatora": vrste_id[tip],
                "identifikator": broj_id,
                "ime_naziv": entries["ime_naziv"].get().strip(),
                "opstina": entries["opstina"].get().strip(),
                "adresa": entries["adresa"].get().strip(),
                "email_osobe": entries["email_osobe"].get().strip(),
                "telefon": entries["telefon"].get().strip(),
                "broj_gazdinstva": entries["broj_gazdinstva"].get().strip(),
                "naziv_gazdinstva": entries["naziv_gazdinstva"].get().strip(),
                "datum": datum_iso,
                "datum_do": datum_do_iso,
                "iznos_prometa": iznos,
            }
            obavezna = ["vrsta_prometa", "vrsta_identifikatora", "identifikator",
                        "ime_naziv", "opstina", "adresa", "telefon",
                        "datum", "datum_do", "iznos_prometa"]
            for k in obavezna:
                if not r[k]:
                    messagebox.showwarning("Upozorenje", "Popunite sva obavezna polja!", parent=win)
                    return
            if indeks_izmene is not None:
                self.db.izmeni_osobu(indeks_izmene, r)
            else:
                self.db.dodaj_osobu(r)
            self.osvezi_tabelu()
            for key, w in entries.items():
                if key in ("datum_unos", "datum_do"):
                    w.delete(0, "end")
                    w.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
                elif not hasattr(w, "set"):
                    w.delete(0, "end")
            info_dupli.config(text="")
            proveri_identifikator()
            entries["identifikator"].focus_set()

        dugmad = ttk.Frame(okvir)
        dugmad.grid(row=len(redovi) + 1, column=0, columnspan=3, pady=15)
        btn_sacuvaj = ttk.Button(dugmad, text="Sacuvaj", command=sacuvaj)
        btn_sacuvaj.pack(side="left", padx=5)
        ttk.Button(dugmad, text="Zatvori", command=win.destroy).pack(side="left", padx=5)

        redosled_tab = [entries[k] for k, _, _ in redovi] + [btn_sacuvaj]

        def tab_napred(ev):
            try:
                idx = redosled_tab.index(win.focus_get())
            except ValueError:
                idx = -1
            sledeci = redosled_tab[(idx + 1) % len(redosled_tab)]
            sledeci.focus_set()
            if isinstance(sledeci, ttk.Entry):
                sledeci.select_range(0, "end")
            return "break"

        def tab_nazad(ev):
            try:
                idx = redosled_tab.index(win.focus_get())
            except ValueError:
                idx = 0
            prethodni = redosled_tab[(idx - 1) % len(redosled_tab)]
            prethodni.focus_set()
            if isinstance(prethodni, ttk.Entry):
                prethodni.select_range(0, "end")
            return "break"

        def enter_sacuvaj(ev):
            sacuvaj()
            return "break"

        for w in redosled_tab[:-1]:
            w.bind("<Tab>", tab_napred)
            w.bind("<Shift-Tab>", tab_nazad)
            w.bind("<Return>", enter_sacuvaj)
        btn_sacuvaj.bind("<Return>", enter_sacuvaj)
        btn_sacuvaj.bind("<space>", enter_sacuvaj)
        entries["vrsta_tip"].focus_set()

    def generisi(self):
        generisi_xml(self.db, self.godina)


if __name__ == "__main__":
    app = App()
    app.mainloop()
