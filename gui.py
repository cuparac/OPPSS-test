"""GUI modul za OPPSS Generator.

Sadrži sve GUI komponente: App, DatumEntry, Kalendar, Prozori.
"""

from __future__ import annotations

import datetime
import os
import shutil
import webbrowser
from typing import Any, Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from database import Database, migriraj_json_u_sqlite
from validacije import validan_jmbg, validan_ebs, konvertuj_datum, get_xsd_schema
from xml_generator import generisi_xml, generisi_html_izvestaj

import logging

logger = logging.getLogger(__name__)


class DatumEntry(ttk.Entry):
    """Polje za unos datuma sa automatskim formatiranjem.

    v15.1: Kursor se može pozicionirati bilo gde u polju.

    Attributes:
        master: Roditeljski widget.
    """

    def __init__(self, master: Optional[tk.Widget] = None, **kw: Any) -> None:
        """Inicijalizuje DatumEntry widget.

        Args:
            master: Roditeljski widget.
            **kw: Dodatni keyword argumenti za ttk.Entry.
        """
        super().__init__(master, **kw)
        self.bind("<KeyRelease>", self._fmt)
        self.configure(justify="center")

    def _fmt(self, ev: tk.Event) -> None:
        """Formatira datum prilikom kucanja.

        Args:
            ev: Tkinter event objekat.
        """
        if ev.keysym in ("BackSpace", "Delete", "Left", "Right", "Home", "End", "Tab", "Return"):
            return

        if len(ev.keysym) > 1 and ev.keysym not in ("space",):
            return

        pos = self.index("insert")
        text = self.get()
        digits_before_cursor = sum(1 for c in text[:pos] if c.isdigit())

        digits = "".join(x for x in text if x.isdigit())[:8]
        if len(digits) > 4:
            formatted = digits[:2] + "/" + digits[2:4] + "/" + digits[4:]
        elif len(digits) > 2:
            formatted = digits[:2] + "/" + digits[2:]
        else:
            formatted = digits

        self.delete(0, "end")
        self.insert(0, formatted)

        digit_count = 0
        for i, ch in enumerate(formatted):
            if ch.isdigit():
                digit_count += 1
                if digit_count >= digits_before_cursor:
                    self.icursor(min(i + 1, len(formatted)))
                    return

        self.icursor(0)

    def dobar_datum(self) -> bool:
        """Proverava da li je unet ispravan datum.

        Returns:
            True ako je datum ispravan, inače False.
        """
        return konvertuj_datum(self.get()) is not None and len(
            "".join(c for c in self.get() if c.isdigit())) == 8


class Kalendar(tk.Toplevel):
    """Kalendar widget za izbor datuma.

    Attributes:
        MESECI: Lista naziva meseci.
        DANI: Lista naziva dana u nedelji.
        entry: DatumEntry polje za koje se otvara kalendar.
        godina: Trenutna godina u kalendaru.
        mesec: Trenutni mesec u kalendaru.
    """

    MESECI = ["Januar", "Februar", "Mart", "April", "Maj", "Jun", "Jul",
              "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar"]
    DANI = ["Po", "Ut", "Sr", "Ce", "Pe", "Su", "Ne"]

    def __init__(self, entry: DatumEntry, x: int, y: int) -> None:
        """Inicijalizuje Kalendar prozor.

        Args:
            entry: DatumEntry polje za koje se otvara kalendar.
            x: X koordinata prozora.
            y: Y koordinata prozora.
        """
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

    def proveri_zatvori(self) -> None:
        """Proverava da li je prozor izgubio fokus i zatvara ga."""
        try:
            aktivan = self.focus_get()
        except Exception:
            aktivan = None
        if aktivan is None or not str(aktivan).startswith(str(self)):
            self.zatvori()

    def mes(self, s: int) -> None:
        """Menja mesec u kalendaru.

        Args:
            s: Broj meseci za promenu (pozitivno ili negativno).
        """
        self.mesec += s
        if self.mesec > 12:
            self.mesec, self.godina = 1, self.godina + 1
        elif self.mesec < 1:
            self.mesec, self.godina = 12, self.godina - 1
        self.crtaj()
        self.grab_set()

    def danas(self) -> None:
        """Postavlja datum na današnji datum."""
        t = datetime.date.today()
        self.izaberi(t.day, t.month, t.year)

    def crtaj(self) -> None:
        """Crta kalendar za trenutni mesec i godinu."""
        for w in self.gf.winfo_children():
            w.destroy()
        self.naslov.config(text=self.MESECI[self.mesec - 1] + " " + str(self.godina))
        for col, ime in enumerate(self.DANI):
            tk.Label(self.gf, text=ime, width=4, anchor="center",
                     font=("Segoe UI", 8, "bold"), bg="white").grid(row=0, column=col)
        start = datetime.date(self.godina, self.mesec, 1).weekday()
        dan, red = 1, 1
        import calendar as _cal
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

    def dugme(self, dan: int, red: int, kol: int) -> None:
        """Kreira dugme za dan u kalendaru.

        Args:
            dan: Dan u mesecu.
            red: Red u grid-u.
            kol: Kolona u grid-u.
        """
        b = tk.Label(self.gf, text=str(dan), width=4, anchor="center",
                     cursor="hand2", bg="white")
        b.grid(row=red, column=kol)
        b.bind("<Button-1>", lambda e, d=dan: self.izaberi(d, self.mesec, self.godina))
        b.bind("<Enter>", lambda e: b.config(background="#cce5ff"))
        b.bind("<Leave>", lambda e: b.config(background="white"))

    def izaberi(self, dan: int, mesec: int, godina: int) -> None:
        """Bira datum i upisuje ga u entry polje.

        Args:
            dan: Dan u mesecu.
            mesec: Mesec.
            godina: Godina.
        """
        self.entry.delete(0, "end")
        self.entry.insert(0, "%02d/%02d/%d" % (dan, mesec, godina))
        self.zatvori()
        self.entry.focus_set(); self.entry.icursor("end")

    def zatvori(self) -> None:
        """Zatvara kalendar prozor."""
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass


class ProzorPodnosioca(tk.Toplevel):
    """Prozor za unos i izmenu podataka o podnosiocu prijave.

    Attributes:
        db: Database objekat.
        godina: Godina za koju se unosi podnosioc.
        entries: Rečnik polja za unos.
    """

    def __init__(self, parent: tk.Widget, db: Database, godina: str) -> None:
        """Inicijalizuje ProzorPodnosioca.

        Args:
            parent: Roditeljski widget.
            db: Database objekat.
            godina: Godina za koju se unosi podnosioc.
        """
        super().__init__(parent)
        self.title("Podaci o podnosiocu prijave - " + godina + ". godina")
        self.grab_set(); self.resizable(False, False)
        self.db = db
        self.godina = godina
        p = db.ucitaj_podnosioca() or {}
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

        def proveri(event: Optional[tk.Event] = None) -> None:
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

    def sacuvaj(self) -> None:
        """Čuva podatke o podnosiocu u bazu."""
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

    def ocisti(self) -> None:
        """Briše sve podatke o podnosiocu za izabranu godinu."""
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
    """Prozor za pretragu unosa u bazi.

    Attributes:
        db: Database objekat.
        kriterijum: Combobox za izbor kriterijuma pretrage.
        vrednost: Entry polje za unos vrednosti pretrage.
        tree: Treeview za prikaz rezultata.
    """

    def __init__(self, parent: tk.Widget, db: Database) -> None:
        """Inicijalizuje ProzorPretrage.

        Args:
            parent: Roditeljski widget.
            db: Database objekat.
        """
        super().__init__(parent)
        self.title("Pretraga")
        self.db = db
        self.geometry("700x500")

        okvir = ttk.Frame(self, padding=10)
        okvir.pack(fill="both", expand=True)

        ttk.Label(okvir, text="Pretraga po:").grid(row=0, column=0, sticky="w")
        self.kriterijum = ttk.Combobox(okvir, values=["opstina", "ime", "identifikator", "iznos_od", "iznos_do", "datum_od", "datum_do"], width=15)
        self.kriterijum.grid(row=0, column=1, padx=5)
        self.kriterijum.current(0)

        self.vrednost = ttk.Entry(okvir, width=30)
        self.vrednost.grid(row=0, column=2, padx=5)

        ttk.Button(okvir, text="Pretraži", command=self.pretrazi).grid(row=0, column=3, padx=5)
        ttk.Button(okvir, text="Prikaži sve", command=self.prikazi_sve).grid(row=0, column=4, padx=5)

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

    def pretrazi(self) -> None:
        """Pretražuje bazu po odabranom kriterijumu i vrednosti."""
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

    def prikazi_sve(self) -> None:
        """Prikazuje sve unose iz baze."""
        ljudi = self.db.ucitaj_ljude()
        self.tree.delete(*self.tree.get_children())
        for r in ljudi:
            self.tree.insert("", "end", values=(
                r['id'], r['vrsta_identifikatora'], r['identifikator'],
                r['ime_naziv'], r['opstina'], r['datum'], r['iznos_prometa']
            ))


class ProzorStatistike(tk.Toplevel):
    """Prozor za prikaz statistike unosa.

    Attributes:
        db: Database objekat.
    """

    def __init__(self, parent: tk.Widget, db: Database) -> None:
        """Inicijalizuje ProzorStatistike.

        Args:
            parent: Roditeljski widget.
            db: Database objekat.
        """
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
    """Glavna aplikacija OPPSS Generator.

    Attributes:
        godina: Trenutna godina.
        db: Database objekat.
    """

    def __init__(self) -> None:
        """Inicijalizuje glavnu aplikaciju."""
        super().__init__()
        self.title("OPPSS Generator v15.3 GUI STANDALONE - ePorezi prijava")
        self.geometry("1000x700")

        self._godina = str(datetime.date.today().year)
        self.godina_var = tk.StringVar(value=self._godina)
        self.db = Database(self._godina)

        # Sortiranje
        self.sort_column: Optional[str] = None
        self.sort_reverse = False

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
        datoteka_meni.add_command(label="Import CSV", command=self.import_csv)
        datoteka_meni.add_separator()
        datoteka_meni.add_command(label="Izveštaj (HTML)", command=self.export_html)
        datoteka_meni.add_command(label="PDF izveštaj", command=self.export_pdf)
        datoteka_meni.add_command(label="XML izveštaj", command=self.export_xml)
        datoteka_meni.add_separator()
        datoteka_meni.add_command(label="Backup baze", command=self.backup_baze)
        datoteka_meni.add_separator()
        datoteka_meni.add_command(label="Izađi", command=self.quit)

        unos_meni = tk.Menu(meni, tearoff=0)
        meni.add_cascade(label="Unos", menu=unos_meni)
        unos_meni.add_command(label="Dodaj (Ctrl+N)", command=self.dodaj_osobu)
        unos_meni.add_command(label="Izmeni", command=self.izmeni_osobu)
        unos_meni.add_command(label="Obriši (Ctrl+D)", command=self.obrisi_osobu)
        unos_meni.add_separator()
        unos_meni.add_command(label="Obriši SVE", command=self.obrisi_sve)

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
            self.tree.heading(k, text=naslovi[k], command=lambda c=k: self.sort_by(c))
            self.tree.column(k, width=sirine[k])
        self.tree.pack(side="left", fill="both", expand=True)

        # Dvoklik na red u tabeli za izmenu
        self.tree.bind("<Double-1>", lambda e: self.izmeni_osobu())

        # Kontekstni meni
        self.context_menu_row = tk.Menu(self, tearoff=0)
        self.context_menu_row.add_command(label="✏️ Izmeni unos", command=self.izmeni_osobu)
        self.context_menu_row.add_command(label="🗑️ Obriši unos", command=self.obrisi_osobu)
        self.context_menu_row.add_separator()
        self.context_menu_row.add_command(label="📋 Kopiraj identifikator", command=self.kopiraj_id)
        self.context_menu_row.add_command(label="🔍 Pretraga po ID-ju", command=self.pretraga_po_id)

        self.context_menu_empty = tk.Menu(self, tearoff=0)
        self.context_menu_empty.add_command(label="➕ Dodaj novi", command=self.dodaj_osobu)
        self.context_menu_empty.add_command(label="🔄 Osveži", command=self.osvezi_sve)
        self.context_menu_empty.add_separator()
        self.context_menu_empty.add_command(label="📊 Statistika", command=self.statistika)

        self.tree.bind("<Button-3>", self.prikazi_kontekstni_meni)
        self.tree.bind("<Button-2>", self.prikazi_kontekstni_meni)  # macOS

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        # Dugmad
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=10, pady=5)
        ttk.Button(btns, text="+ Dodaj unos", command=self.dodaj_osobu).pack(side="left", padx=3)
        self.btn_izmeni = ttk.Button(btns, text="Izmeni", command=self.izmeni_osobu)
        self.btn_izmeni.pack(side="left", padx=3)
        ttk.Button(btns, text="Obriši", command=self.obrisi_osobu).pack(side="left", padx=3)
        ttk.Button(btns, text="Obriši SVE", command=self.obrisi_sve).pack(side="left", padx=3)
        self.ukupno_label = ttk.Label(btns, font=("Segoe UI", 11, "bold"))
        self.ukupno_label.pack(side="left", padx=30)
        ttk.Button(btns, text="Pretraga", command=self.pretraga).pack(side="left", padx=3)
        ttk.Button(btns, text="Statistika", command=self.statistika).pack(side="left", padx=3)
        ttk.Button(btns, text="Export CSV", command=self.export_csv).pack(side="left", padx=3)
        ttk.Button(btns, text="Backup", command=self.backup_baze).pack(side="left", padx=3)
        ttk.Button(btns, text="Izveštaj", command=self.export_html).pack(side="left", padx=3)
        ttk.Button(btns, text="GENERISI XML", command=self.generisi).pack(side="right", padx=3)

        # Status bar
        status_bar = ttk.Frame(self)
        status_bar.pack(fill="x", side="bottom")
        ttk.Label(status_bar, text="F1 = Pomoć | Ctrl+N = Novi | Ctrl+D = Obriši | Ctrl+F = Pretraga | Ctrl+G = XML | Ctrl+P = Podnosioc | Dvoklik = Izmeni | Desni klik = Meni",
                  font=("Segoe UI", 8), foreground="gray").pack(side="left", padx=10)

        self.osvezi_sve()

    def prikazi_kontekstni_meni(self, event: tk.Event) -> None:
        """Prikazuje kontekstni meni na osnovu pozicije klika.

        Args:
            event: Tkinter event objekat.
        """
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu_row.post(event.x_root, event.y_root)
        else:
            self.context_menu_empty.post(event.x_root, event.y_root)

    def kopiraj_id(self) -> None:
        """Kopira identifikator iz selektovanog reda u clipboard."""
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0])['values']
        if len(values) > 2:
            identifikator = str(values[2])
            self.clipboard_clear()
            self.clipboard_append(identifikator)
            messagebox.showinfo("Kopirano", f"Identifikator '{identifikator}' je kopiran u clipboard.")

    def pretraga_po_id(self) -> None:
        """Otvara pretragu sa identifikatorom iz selektovanog reda."""
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0])['values']
        if len(values) > 2:
            identifikator = str(values[2])
            win = ProzorPretrage(self, self.db)
            win.kriterijum.set("identifikator")
            win.vrednost.delete(0, "end")
            win.vrednost.insert(0, identifikator)
            win.pretrazi()

    def obrisi_sve(self) -> None:
        """Briše sve unose za izabranu godinu."""
        ljudi = self.db.ucitaj_ljude()
        if not ljudi:
            messagebox.showinfo("Brisanje", "Nema unosa za brisanje.")
            return

        if messagebox.askyesno("⚠️ BRISANJE SVIH UNOSA",
                               "Da li ste SIGURNI da želite da obrišete SVE unose za %s. godinu?\n\n"
                               "Broj unosa: %d\n"
                               "Ukupan iznos: %s RSD\n\n"
                               "OVA AKCIJA SE NE MOŽE PONIŠTITI!" % (
                                   self.godina,
                                   len(ljudi),
                                   format(sum(o['iznos_prometa'] for o in ljudi), ",").replace(",", "."))):
            if messagebox.askyesno("POTVRDA", "Jeste li zaista sigurni? Ovo će obrisati SVE podatke o osobama!"):
                self.db.obrisi_sve()
                self.osvezi_sve()
                messagebox.showinfo("Obrisano", "Svi unosi za %s. godinu su obrisani." % self.godina)

    def backup_baze(self) -> None:
        """Kreira backup SQLite baze."""
        db_file = self.db.db_file
        if not os.path.exists(db_file):
            messagebox.showerror("Greška", "Baza podataka ne postoji.")
            return

        backup_dir = filedialog.askdirectory(title="Odaberite folder za backup")
        if not backup_dir:
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"baza_{self.godina}_backup_{timestamp}.db")

        try:
            self.db.zatvori()
            shutil.copy2(db_file, backup_file)
            self.db = Database(self._godina)
            messagebox.showinfo("Backup", f"Backup uspešno kreiran:\n{backup_file}")
        except Exception as e:
            logger.error("Greška pri backup-u: %s", e)
            messagebox.showerror("Greška", f"Greška pri backup-u: {e}")
            self.db = Database(self._godina)

    def import_csv(self) -> None:
        """Import podataka iz CSV fajla."""
        fajl = filedialog.askopenfilename(
            title="Odaberite CSV fajl za import",
            filetypes=[("CSV fajlovi", "*.csv"), ("Svi fajlovi", "*.*")]
        )
        if not fajl:
            return

        uspeh, poruka, uneto = self.db.import_csv(fajl)
        if uspeh:
            self.osvezi_sve()
            messagebox.showinfo("Import", poruka)
        else:
            messagebox.showerror("Import", poruka)

    def export_html(self) -> None:
        """Generiše HTML izveštaj za štampu i otvara ga u pregledaču."""
        html = generisi_html_izvestaj(self, self.db, self.godina)

        fajl = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML fajlovi", "*.html"), ("Svi fajlovi", "*.*")],
            initialfile=f"OPPS_izvestaj_{self.godina}.html"
        )

        if fajl:
            with open(fajl, 'w', encoding='utf-8') as f:
                f.write(html)
            messagebox.showinfo("Izveštaj", f"Izveštaj sačuvan: {fajl}\n\nMožete ga otvoriti u pregledaču i štampati (Ctrl+P).")
            webbrowser.open(f"file://{os.path.abspath(fajl)}")

    def export_pdf(self) -> None:
        """Generiše HTML izveštaj i otvara ga u pregledaču za štampu (PDF preko pregledača).

        Ne zahteva dodatne biblioteke — koristi pregledač za štampu.
        """
        html = generisi_html_izvestaj(self, self.db, self.godina)

        fajl = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML fajlovi", "*.html"), ("Svi fajlovi", "*.*")],
            initialfile=f"OPPS_izvestaj_{self.godina}.html"
        )

        if fajl:
            with open(fajl, 'w', encoding='utf-8') as f:
                f.write(html)
            messagebox.showinfo("PDF izveštaj",
                f"Izveštaj sačuvan: {fajl}\n\n"
                "Otvorite ga u pregledaču i štampate (Ctrl+P).\n"
                "Odaberite 'Sačuvaj kao PDF' u dijalogu štampe.")
            webbrowser.open(f"file://{os.path.abspath(fajl)}")

    def export_xml(self) -> None:
        """Generiše XML fajl za upload na ePorezi portal."""
        xml = generisi_xml(self.db, self.godina)

        fajl = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML fajlovi", "*.xml"), ("Svi fajlovi", "*.*")],
            initialfile=f"OPPS_prijava_{self.godina}.xml"
        )

        if fajl:
            with open(fajl, 'w', encoding='utf-8') as f:
                f.write(xml)
            messagebox.showinfo("XML izveštaj", f"XML fajl sačuvan: {fajl}\n\nMožete ga upload-ovati na portal ePorezi.")

    def sort_by(self, col: str) -> None:
        """Sortira tabelu po odabranoj koloni.

        Args:
            col: Naziv kolone po kojoj se sortira.
        """
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        # Ažuriraj indikatore sortiranja u zaglavljima
        kolone = ("rb", "tip", "identifikator", "ime_naziv", "opstina", "adresa", "telefon", "datum", "iznos")
        naslovi = {"rb": "R.br", "tip": "Vrsta prometa", "identifikator": "JMBG/PIB/EBS",
                   "ime_naziv": "Ime / Naziv", "opstina": "Opština", "adresa": "Adresa",
                   "telefon": "Telefon", "datum": "Datum (od/do)", "iznos": "Iznos (RSD)"}

        for k in kolone:
            text = naslovi[k]
            if k == self.sort_column:
                text += " ▼" if self.sort_reverse else " ▲"
            self.tree.heading(k, text=text)

        self.osvezi_tabelu()

    def proveri_migraciju(self) -> None:
        """Proverava da li postoji stari JSON fajl za migraciju."""
        json_file = f"baza_{self.godina}.json"
        if os.path.exists(json_file):
            odgovor = messagebox.askyesno("Migracija",
                "Pronađen je stari JSON fajl. Želite li da ga migrirate u SQLite bazu?")
            if odgovor:
                self.migracija()

    def migracija(self) -> None:
        """Vrši migraciju podataka iz JSON fajla u SQLite bazu."""
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

    def export_csv(self) -> None:
        """Export podataka u CSV fajl."""
        fajl = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV fajlovi", "*.csv"), ("Svi fajlovi", "*.*")],
            initialfile=f"OPPS_{self.godina}.csv"
        )
        if fajl:
            self.db.export_csv(fajl)
            messagebox.showinfo("Export", f"CSV fajl sačuvan: {fajl}")

    def pretraga(self) -> None:
        """Otvara prozor za pretragu."""
        ProzorPretrage(self, self.db)

    def statistika(self) -> None:
        """Otvara prozor za statistiku."""
        ProzorStatistike(self, self.db)

    def prikazi_about(self) -> None:
        """Prikazuje informacije o aplikaciji."""
        import sys
        import platform
        messagebox.showinfo("O aplikaciji",
                            "OPPSS Generator v15.3 GUI STANDALONE\n\n"
                            "Aplikacija za generisanje OOPSS prijava\n"
                            "za portal ePorezi (Poreska uprava RS)\n\n"
                            "Verzija: 15.3\n"
                            "Baza: SQLite\n"
                            "XSD šema: ugrađena\n\n"
                            "Python: " + sys.version.split()[0] + "\n"
                            "Platforma: " + platform.system())

    def promeni_godinu(self) -> None:
        """Menja godinu i osvežava prikaz."""
        self.db.zatvori()
        self._godina = self.godina_var.get()
        self.db = Database(self._godina)
        self.sort_column = None
        self.sort_reverse = False
        self.osvezi_sve()

    @property
    def godina(self) -> str:
        """Vraća trenutnu godinu.

        Returns:
            Trenutna godina kao string.
        """
        return self._godina

    @godina.setter
    def godina(self, value: str) -> None:
        """Postavlja trenutnu godinu.

        Args:
            value: Nova godina kao string.
        """
        self._godina = value
        self.godina_var.set(value)

    def otvori_podnosioca(self) -> None:
        """Otvara prozor za podatke o podnosiocu."""
        ProzorPodnosioca(self, self.db, self.godina)
        self.osvezi_info()

    def osvezi_info(self) -> None:
        """Osvežava informacije o podnosiocu u glavnom prozoru."""
        p = self.db.ucitaj_podnosioca() or {}
        if p.get("pib_jmbg"):
            self.info_podnosioc.config(text="Podnosioc: %s   |   Godina: %s" % (p['pib_jmbg'], self.godina))
        else:
            self.info_podnosioc.config(text="[!] Podaci o podnosiocu NISU uneseni za %s. godinu!" % self.godina)

    def osvezi_tabelu(self) -> None:
        """Osvežava tabelu sa unosima."""
        self.tree.delete(*self.tree.get_children())
        ljudi = self.db.ucitaj_ljude()
        tipovi = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}

        # Sortiranje
        if self.sort_column:
            col_map = {"rb": "id", "tip": "vrsta_prometa", "identifikator": "identifikator",
                      "ime_naziv": "ime_naziv", "opstina": "opstina", "adresa": "adresa",
                      "telefon": "telefon", "datum": "datum", "iznos": "iznos_prometa"}
            sort_key = col_map.get(self.sort_column, "id")

            def get_sort_value(o: Dict[str, Any]) -> Any:
                val = o.get(sort_key, "")
                if sort_key == "iznos_prometa":
                    return int(val) if val else 0
                if sort_key == "id":
                    return int(val) if val else 0
                return str(val).lower() if val else ""

            ljudi.sort(key=get_sort_value, reverse=self.sort_reverse)

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

    def osvezi_sve(self) -> None:
        """Osvežava sve komponente glavnog prozora."""
        self.osvezi_tabelu()
        self.osvezi_info()

    def dodaj_osobu(self) -> None:
        """Otvara formu za dodavanje novog unosa."""
        self.forma_osobe()

    def izmeni_osobu(self) -> None:
        """Otvara formu za izmenu postojećeg unosa."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Izaberite unos u tabeli!")
            return
        id = int(sel[0])
        ljudi = self.db.ucitaj_ljude()
        osoba = next((o for o in ljudi if o['id'] == id), None)
        if osoba:
            self.forma_osobe(osoba, id)

    def obrisi_osobu(self) -> None:
        """Briše selektovani unos iz tabele."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Izaberite unos u tabeli!")
            return
        id = int(sel[0])
        ime = self.tree.item(sel[0])['values'][3]
        if messagebox.askyesno("Brisanje", "Obrisati unos: " + str(ime) + "?"):
            self.db.obrisi_osobu(id)
            self.osvezi_tabelu()

    def forma_osobe(self, podrazumevano: Optional[Dict[str, Any]] = None, indeks_izmene: Optional[int] = None) -> None:
        """Otvara formu za unos/izmenu osobe.

        Args:
            podrazumevano: Podrazumevani podaci za izmenu.
            indeks_izmene: ID unosa koji se menja.
        """
        win = tk.Toplevel(self)
        je_izmena = podrazumevano is not None
        win.title("Izmena unosa" if je_izmena else "Novi unos")
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

        def limit_za_tip() -> int:
            tip = entries["id_tip"].get()
            if tip == "JMBG":
                return 13
            elif tip == "EBS":
                return 9
            else:
                return 9

        def proveri_identifikator() -> None:
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

        def azuriraj_limit() -> None:
            lim = limit_za_tip()
            if len(entries["identifikator"].get()) > lim:
                entries["identifikator"].delete(lim, "end")
            proveri_identifikator()

        info_dupli = ttk.Label(okvir, text="", foreground="blue", font=("Segoe UI", 9))
        info_dupli.grid(row=3, column=2, sticky="w", padx=(5, 0))

        def na_kucanje(ev: Optional[tk.Event] = None) -> None:
            try:
                if ev is not None and ev.keysym in ("BackSpace", "Delete", "Left",
                                                    "Right", "Home", "End", "Tab", "Return"):
                    proveri_identifikator()
                    return
                lim = limit_za_tip()
                c = "".join(x for x in entries["identifikator"].get() if x.isdigit())[:lim]
                entries["identifikator"].delete(0, "end")
                entries["identifikator"].insert(0, c)
                proveri_identifikator()

                broj = entries["identifikator"].get().strip()
                if len(broj) == lim:
                    ljudi = self.db.ucitaj_ljude()
                    nadjen = next((o for o in ljudi if o["identifikator"] == broj), None)
                    if nadjen:
                        info_dupli.config(
                            text="⚠ Postoji unos sa ovim ID-jem (razlika u datumu/iznosu)",
                            foreground="orange")
                    else:
                        info_dupli.config(text="")
                else:
                    info_dupli.config(text="")
            except Exception as e:
                info_dupli.config(text="GRESKA: " + str(e), foreground="red")

        entries["identifikator"].bind("<KeyRelease>", na_kucanje)
        entries["id_tip"].bind("<<ComboboxSelected>>", lambda e: azuriraj_limit())
        proveri_identifikator()

        btn_kal_od = ttk.Button(okvir, text="\U0001F4C5", width=3)
        btn_kal_od.grid(row=10, column=2, sticky="w", padx=(5, 0))
        def otvori_kalendar_od() -> None:
            Kalendar(entries["datum_unos"], win.winfo_rootx() + 350, win.winfo_rooty() + 250)
        btn_kal_od.configure(command=otvori_kalendar_od)

        btn_kal_do = ttk.Button(okvir, text="\U0001F4C5", width=3)
        btn_kal_do.grid(row=11, column=2, sticky="w", padx=(5, 0))
        def otvori_kalendar_do() -> None:
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
                    datum_key = "datum" if key == "datum_unos" else "datum_do"
                    if podrazumevano.get(datum_key):
                        try:
                            w.insert(0, datetime.datetime.strptime(
                                podrazumevano[datum_key], "%Y-%m-%d").strftime("%d/%m/%Y"))
                        except ValueError:
                            pass
                    continue
                vrednost = podrazumevano.get(mapa.get(key, key), "")
                if hasattr(w, "set"):
                    w.set(vrednost)
                else:
                    w.insert(0, str(vrednost))
            azuriraj_limit()

        def sacuvaj() -> None:
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

            # Provera duplikata (identifikator + datum)
            if indeks_izmene is None:
                duplikat = self.db.ima_duplikat(broj_id, datum_iso)
                if duplikat:
                    odgovor = messagebox.askyesnocancel(
                        "UPOZORENJE - DUPLIKAT",
                        "Već postoji unos sa identifikatorom %s i datumom %s:\n\n"
                        "• Ime/Naziv: %s\n"
                        "• Opština: %s\n"
                        "• Datum: %s do %s\n"
                        "• Iznos: %s RSD\n\n"
                        "Zameni = obriši staro i snimi novo\n"
                        "Dodaj kao novi = snimi bez brisanja\n"
                        "Preskoči = nemoj ništa snimiti" % (
                            broj_id,
                            datum_iso,
                            duplikat.get('ime_naziv', ''),
                            duplikat.get('opstina', ''),
                            duplikat.get('datum', ''),
                            duplikat.get('datum_do', ''),
                            format(duplikat.get('iznos_prometa', 0), ",").replace(",", ".")),
                        parent=win)
                    if odgovor is None:  # Preskoči
                        return
                    elif not odgovor:  # Zameni
                        self.db.obrisi_osobu(duplikat['id'])
                    # True = Dodaj kao novi, nastavi sa snimanjem

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
        tekst_dugmeta = "Sačuvaj izmene" if je_izmena else "Sačuvaj"
        btn_sacuvaj = ttk.Button(dugmad, text=tekst_dugmeta, command=sacuvaj)
        btn_sacuvaj.pack(side="left", padx=5)
        ttk.Button(dugmad, text="Zatvori", command=win.destroy).pack(side="left", padx=5)

        redosled_tab = [entries[k] for k, _, _ in redovi] + [btn_sacuvaj]

        def tab_napred(ev: tk.Event) -> None:
            try:
                idx = redosled_tab.index(win.focus_get())
            except ValueError:
                idx = -1
            sledeci = redosled_tab[(idx + 1) % len(redosled_tab)]
            sledeci.focus_set()
            if isinstance(sledeci, ttk.Entry):
                sledeci.select_range(0, "end")
            return "break"

        def tab_nazad(ev: tk.Event) -> None:
            try:
                idx = redosled_tab.index(win.focus_get())
            except ValueError:
                idx = 0
            prethodni = redosled_tab[(idx - 1) % len(redosled_tab)]
            prethodni.focus_set()
            if isinstance(prethodni, ttk.Entry):
                prethodni.select_range(0, "end")
            return "break"

        def enter_sacuvaj(ev: tk.Event) -> str:
            sacuvaj()
            return "break"

        for w in redosled_tab[:-1]:
            w.bind("<Tab>", tab_napred)
            w.bind("<Shift-Tab>", tab_nazad)
            w.bind("<Return>", enter_sacuvaj)
        btn_sacuvaj.bind("<Return>", enter_sacuvaj)
        btn_sacuvaj.bind("<space>", enter_sacuvaj)
        entries["vrsta_tip"].focus_set()

    def generisi(self) -> None:
        """Generiše XML fajl iz baze podataka i čuva ga na disk."""
        xml = generisi_xml(self.db, self.godina)
        fajl = f"OPPS_prijava_{self.godina}.xml"
        with open(fajl, 'w', encoding='utf-8') as f:
            f.write(xml)
        messagebox.showinfo("XML generisan", f"XML fajl sačuvan: {fajl}\n\nMožete ga upload-ovati na portal ePorezi.")
