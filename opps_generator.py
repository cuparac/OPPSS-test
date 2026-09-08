"""OPPSS GENERATOR v13.9 - baze po godinama, JMBG kontrola, kalendar,
auto-popunjavanje iz tabele + fokus na datum, XML + XSD validacija,
datum od/do kao posebna polja, file lock za JSON bazu,
cross-platform kompatibilnost, poboljsana validacija,
EBS identifikator, broj/naziv poljoprivrednog gazdinstva, email osobe,
error handling za lxml instalaciju, preccice tastature.
Zahteva: pip install lxml"""

import json, os, sys, datetime, calendar as _cal, platform
import tkinter as tk
from tkinter import ttk, messagebox

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

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

# Import fcntl samo na Unix/Mac (ne radi na Windows)
if platform.system() != "Windows":
    import fcntl


def validan_jmbg(jmbg):
    """Validacija JMBG-a: provera datuma i kontrolne cifre."""
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
    """Validacija EBS (Jedinstveni broj subjekta): 9 cifara."""
    return ebs.isdigit() and len(ebs) == 9


def ucitaj_bazu(godina):
    """Ucitavanje JSON baze sa error handling-om za korumpirane fajlove."""
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
            messagebox.showwarning("Upozorenje",
                                   "Fajl '%s' je ostecen: %s\n\nKreirana je prazna baza." % (f, str(e)))
            return {"podnosioc": {}, "ljudi": []}
    return {"podnosioc": {}, "ljudi": []}


def sacuvaj_bazu(baza, godina):
    """Cuvanje JSON baze sa file lock-om protiv korupcije (cross-platform)."""
    f = "baza_" + godina + ".json"
    if platform.system() != "Windows":
        with open(f, "w", encoding="utf-8") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(baza, fh, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    else:
        # Windows: koristi atomic write (write to temp, then rename)
        f_tmp = f + ".tmp"
        with open(f_tmp, "w", encoding="utf-8") as fh:
            json.dump(baza, fh, ensure_ascii=False, indent=2)
        os.replace(f_tmp, f)


def konvertuj_datum(t):
    try:
        return datetime.datetime.strptime(t.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


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


def generisi_xml(baza, godina):
    p = baza.get("podnosioc")
    if not p or not p.get("pib_jmbg"):
        messagebox.showerror("Greska", "Prvo unesite podatke o PODNOSIOCU za izabranu godinu!")
        return None
    if not baza["ljudi"]:
        messagebox.showerror("Greska", "Dodajte bar jednu osobu!")
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
        # Opciona polja
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
        messagebox.showwarning("Nema XSD seme",
                               "Fajl '%s' nije pronadjen!\n\nXML je kreiran ALI NIJE validiran.\n\n%s" % (XSD, sazetak))
        return izlaz
    try:
        schema = etree.XMLSchema(etree.parse(XSD))
    except Exception as e:
        messagebox.showwarning("Problem sa XSD semom",
                               "Nije moguce ucitati '%s':\n%s\n\nXML je kreiran ALI NIJE validiran.\n\n%s" % (XSD, e, sazetak))
        return izlaz
    # Validacija iz memorije (ne cita fajl dvaput sa diska)
    if schema.validate(root):
        messagebox.showinfo("Uspeh", "[OK] %s je VALIDAN!\n\nSpreman za upload na ePorezi portal.\n\n%s" % (izlaz, sazetak))
    else:
        greske = "\n".join(e.message for e in schema.error_log)
        messagebox.showerror("Validacija NIJE uspela", "XML je kreiran ali ima gresaka:\n\n" + greske)
    return izlaz


class ProzorPodnosioca(tk.Toplevel):
    def __init__(self, parent, baza, godina):
        super().__init__(parent)
        self.title("Podaci o podnosiocu prijave - " + godina + ". godina")
        self.grab_set(); self.resizable(False, False)
        self.baza, self.godina = baza, godina
        p = baza.get("podnosioc", {})
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
        d["godina"] = self.godina
        self.baza["podnosioc"] = d
        sacuvaj_bazu(self.baza, self.godina)
        messagebox.showinfo("Sacuvano", "Podaci o podnosiocu (%s) su sacuvani." % self.godina, parent=self)
        self.destroy()

    def ocisti(self):
        if not any(e.get().strip() for e in self.entries.values()) and not self.baza.get("podnosioc"):
            messagebox.showinfo("Ciscenje", "Sva polja su vec prazna.", parent=self)
            return
        if messagebox.askyesno("Potvrda ciscenja",
                               "Obrisati SVE podatke o podnosiocu za %s. godinu?\n\n(Unosi osoba u tabeli ostaju netaknuti!)" % self.godina,
                               parent=self):
            for e in self.entries.values():
                e.delete(0, "end")
            self.baza["podnosioc"] = {}
            sacuvaj_bazu(self.baza, self.godina)
            self.status_jmbg.config(text="")
            messagebox.showinfo("Ocisceno", "Podaci o podnosiocu su obrisani.", parent=self)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OPPSS Generator v13.9 - ePorezi prijava")
        self.geometry("950x650")

        # Preccice tastature
        self.bind("<Control-n>", lambda e: self.dodaj_osobu())
        self.bind("<Control-N>", lambda e: self.dodaj_osobu())
        self.bind("<Control-d>", lambda e: self.obrisi_osobu())
        self.bind("<Control-D>", lambda e: self.obrisi_osobu())
        self.bind("<Control-g>", lambda e: self.generisi())
        self.bind("<Control-G>", lambda e: self.generisi())
        self.bind("<Control-p>", lambda e: self.otvori_podnosioca())
        self.bind("<Control-P>", lambda e: self.otvori_podnosioca())
        self.bind("<F1>", lambda e: self.prikazi_about())

        traka = ttk.Frame(self, padding=10)
        traka.pack(fill="x")
        ttk.Label(traka, text="Godina podnosenja:", font=("Segoe UI", 11, "bold")).pack(side="left")
        self.godina_var = tk.StringVar(value=str(datetime.date.today().year))
        combo = ttk.Combobox(traka, textvariable=self.godina_var, state="readonly", width=8,
                             values=[str(y) for y in range(2023, 2036)])
        combo.pack(side="left", padx=10)
        combo.bind("<<ComboboxSelected>>", lambda e: self.ucitaj_godinu())

        gore = ttk.LabelFrame(self, text=" Prijava ", padding=10)
        gore.pack(fill="x", padx=10, pady=5)
        self.info_podnosioc = ttk.Label(gore, font=("Segoe UI", 10))
        self.info_podnosioc.pack(side="left")
        ttk.Button(gore, text="Podaci podnosioca... (Ctrl+P)", command=self.otvori_podnosioca).pack(side="right", padx=5)

        tf = ttk.Frame(self)
        tf.pack(fill="both", expand=True, padx=10, pady=5)
        kolone = ("rb", "tip", "identifikator", "ime_naziv", "opstina", "adresa", "telefon", "datum", "iznos")
        naslovi = {"rb": "R.br", "tip": "Vrsta prometa", "identifikator": "JMBG/PIB/EBS",
                   "ime_naziv": "Ime / Naziv", "opstina": "Opstina", "adresa": "Adresa",
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

        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=10, pady=5)
        ttk.Button(btns, text="+ Dodaj unos (Ctrl+N)", command=self.dodaj_osobu).pack(side="left", padx=3)
        ttk.Button(btns, text="Izmeni", command=self.izmeni_osobu).pack(side="left", padx=3)
        ttk.Button(btns, text="Obrisi (Ctrl+D)", command=self.obrisi_osobu).pack(side="left", padx=3)
        self.ukupno_label = ttk.Label(btns, font=("Segoe UI", 11, "bold"))
        self.ukupno_label.pack(side="left", padx=30)
        ttk.Button(btns, text="GENERISI XML (Ctrl+G)", command=self.generisi).pack(side="right", padx=3)

        # Status bar
        status_bar = ttk.Frame(self)
        status_bar.pack(fill="x", side="bottom")
        ttk.Label(status_bar, text="F1 = O aplikaciji | Ctrl+N = Novi | Ctrl+D = Obrisi | Ctrl+G = XML | Ctrl+P = Podnosioc",
                  font=("Segoe UI", 8), foreground="gray").pack(side="left", padx=10)

        self.ucitaj_godinu()

    def prikazi_about(self):
        """Prijava informacija o aplikaciji."""
        messagebox.showinfo("O aplikaciji",
                            "OPPSS Generator v13.9\n\n"
                            "Aplikacija za generisanje OOPSS prijava\n"
                            "za portal ePorezi (Poreska uprava RS)\n\n"
                            "Verzija: 13.9\n"
                            "Python: " + sys.version.split()[0] + "\n"
                            "Platforma: " + platform.system() + "\n\n"
                            "Podrzani identifikatori:\n"
                            "- JMBG (13 cifara)\n"
                            "- PIB (9 cifara)\n"
                            "- EBS (9 cifara)\n\n"
                            "XSD validacija: opps.xsd\n"
                            "Izlazni format: XML (ePorezi)")

    @property
    def godina(self):
        return self.godina_var.get()

    def ucitaj_godinu(self):
        self.baza = ucitaj_bazu(self.godina)
        self.osvezi_sve()

    def otvori_podnosioca(self):
        ProzorPodnosioca(self, self.baza, self.godina)
        self.osvezi_info()

    def osvezi_info(self):
        p = self.baza.get("podnosioc", {})
        if p.get("pib_jmbg"):
            self.info_podnosioc.config(text="Podnosioc: %s   |   Godina: %s" % (p['pib_jmbg'], self.godina))
        else:
            self.info_podnosioc.config(text="[!] Podaci o podnosiocu NISU uneseni za %s. godinu!" % self.godina)

    def osvezi_tabelu(self):
        self.tree.delete(*self.tree.get_children())
        tipovi = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}
        for i, o in enumerate(self.baza["ljudi"], 1):
            prikaz = ""
            if o.get("datum"):
                try:
                    datum_od = datetime.datetime.strptime(o["datum"], "%Y-%m-%d").strftime("%d/%m/%Y")
                    datum_do = datetime.datetime.strptime(o.get("datum_do", o["datum"]), "%Y-%m-%d").strftime("%d/%m/%Y")
                    prikaz = datum_od + " - " + datum_do
                except ValueError:
                    prikaz = o["datum"]
            self.tree.insert("", "end", iid=str(i), values=(
                i, tipovi.get(o["vrsta_prometa"], "?"), o["identifikator"],
                o["ime_naziv"], o["opstina"], o["adresa"], o["telefon"],
                prikaz, format(o['iznos_prometa'], ",").replace(",", ".")))
        ukupno = sum(o["iznos_prometa"] for o in self.baza["ljudi"])
        self.ukupno_label.config(text="%d unosa | Ukupno: %s RSD" %
                                 (len(self.baza['ljudi']), format(ukupno, ",").replace(",", ".")))

    def osvezi_sve(self):
        self.osvezi_tabelu()
        self.osvezi_info()

    # ---------- Forma osobe ----------
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
            else:  # PIB
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

        # JEDAN handler: filtrira cifre + azurira labelu + auto-popunjava
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
                # auto-popunjavanje kad je broj kompletan
                broj = entries["identifikator"].get().strip()
                if len(broj) != lim:
                    info_dupli.config(text="")
                    return
                nadjen = None
                for o in self.baza["ljudi"]:
                    if o["identifikator"] == broj:
                        nadjen = o
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

        # Kalendar dugme za DATUM OD
        btn_kal_od = ttk.Button(okvir, text="\U0001F4C5", width=3)
        btn_kal_od.grid(row=11, column=2, sticky="w", padx=(5, 0))
        def otvori_kalendar_od():
            Kalendar(entries["datum_unos"], win.winfo_rootx() + 350, win.winfo_rooty() + 250)
        btn_kal_od.configure(command=otvori_kalendar_od)

        # Kalendar dugme za DATUM DO
        btn_kal_do = ttk.Button(okvir, text="\U0001F4C5", width=3)
        btn_kal_do.grid(row=12, column=2, sticky="w", padx=(5, 0))
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
            # Provera: datum DO mora biti >= datum OD
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
            if any(not r[k] for k in r):
                messagebox.showwarning("Upozorenje", "Popunite sva polja!", parent=win)
                return
            if indeks_izmene is None:
                self.baza["ljudi"].append(r)
            else:
                self.baza["ljudi"][indeks_izmene] = r
            sacuvaj_bazu(self.baza, self.godina)
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

    def dodaj_osobu(self):
        self.forma_osobe()

    def izmeni_osobu(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Izaberite unos u tabeli!")
            return
        # Koristi stvarni indeks umesto int(sel[0]) - 1
        idx = self.tree.index(sel[0])
        self.forma_osobe(self.baza["ljudi"][idx], indeks_izmene=idx)

    def obrisi_osobu(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Izaberite unos u tabeli!")
            return
        # Koristi stvarni indeks umesto int(sel[0]) - 1
        idx = self.tree.index(sel[0])
        ime = self.baza["ljudi"][idx]["ime_naziv"]
        if messagebox.askyesno("Brisanje", "Obrisati unos: " + ime + "?"):
            del self.baza["ljudi"][idx]
            sacuvaj_bazu(self.baza, self.godina)
            self.osvezi_tabelu()

    def generisi(self):
        generisi_xml(self.baza, self.godina)


if __name__ == "__main__":
    app = App()
    app.mainloop()
