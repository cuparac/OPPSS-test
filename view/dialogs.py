"""Dialog (prozor) komponente za view layer.

Sadrži Toplevel dijaloge: ProzorFiltera, ProzorPodnosioca,
ProzorPretrage, ProzorStatistike.
"""

from __future__ import annotations

from typing import Optional

import tkinter as tk
from tkinter import ttk, messagebox

from model import Database, validan_jmbg


class ProzorFiltera(tk.Toplevel):
    """Prozor za napredne filtere tabele.

    Attributes:
        parent: Glavni prozor.
        db: Database objekat.
        godina: Trenutna godina.
    """

    def __init__(self, parent: tk.Widget, db: Database, godina: str) -> None:
        """Inicijalizuje ProzorFiltera.

        Args:
            parent: Glavni prozor.
            db: Database objekat.
            godina: Trenutna godina.
        """
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.godina = godina
        self.title("Napredni filteri")
        self.geometry("400x350")
        self.grab_set()

        okvir = ttk.Frame(self, padding=20)
        okvir.pack(fill="both", expand=True)

        # Filter po vrsti prometa
        ttk.Label(okvir, text="Vrsta prometa:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.vrsta_var = tk.StringVar(value="Sve")
        ttk.Radiobutton(okvir, text="Sve", variable=self.vrsta_var, value="Sve").pack(anchor="w")
        ttk.Radiobutton(okvir, text="Poljoprivredni proizvodi/usluge", variable=self.vrsta_var, value="1").pack(anchor="w")
        ttk.Radiobutton(okvir, text="Sekundarne sirovine", variable=self.vrsta_var, value="2").pack(anchor="w")

        ttk.Separator(okvir, orient="horizontal").pack(fill="x", pady=10)

        # Filter po opštini
        ttk.Label(okvir, text="Opština:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        opstine = sorted(set(o.get("opstina", "") for o in db.ucitaj_ljude()))
        self.opstina_var = tk.StringVar(value="Sve")
        ttk.Combobox(okvir, textvariable=self.opstina_var, values=["Sve"] + opstine, state="readonly", width=35).pack(anchor="w")

        ttk.Separator(okvir, orient="horizontal").pack(fill="x", pady=10)

        # Filter po iznosu
        ttk.Label(okvir, text="Iznos (RSD):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.min_var = tk.StringVar(value="0")
        self.max_var = tk.StringVar(value="999999999")
        ttk.Label(okvir, text="Min:").pack(anchor="w")
        ttk.Entry(okvir, textvariable=self.min_var, width=15).pack(anchor="w")
        ttk.Label(okvir, text="Max:").pack(anchor="w")
        ttk.Entry(okvir, textvariable=self.max_var, width=15).pack(anchor="w")

        ttk.Separator(okvir, orient="horizontal").pack(fill="x", pady=10)

        # Filter po datumu
        ttk.Label(okvir, text="Datum:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.datum_var = tk.StringVar(value="Sve")
        ttk.Radiobutton(okvir, text="Sve", variable=self.datum_var, value="Sve").pack(anchor="w")
        ttk.Radiobutton(okvir, text="Samo ove godine", variable=self.datum_var, value="godina").pack(anchor="w")
        ttk.Radiobutton(okvir, text="Samo ovog meseca", variable=self.datum_var, value="mesec").pack(anchor="w")

        ttk.Separator(okvir, orient="horizontal").pack(fill="x", pady=10)

        btn_primeni = ttk.Button(okvir, text="Primeni filter", command=self.primeni)
        btn_primeni.pack(side="left", padx=5)
        btn_ocisti = ttk.Button(okvir, text="Očisti filter", command=self.ocisti)
        btn_ocisti.pack(side="left", padx=5)

    def primeni(self) -> None:
        """Primenjuje filtere na tabelu."""
        self.parent.filtriraj_tabelu(
            vrsta=self.vrsta_var.get() if self.vrsta_var.get() != "Sve" else None,
            opstina=self.opstina_var.get() if self.opstina_var.get() != "Sve" else None,
            min_iznos=self.min_var.get(),
            max_iznos=self.max_var.get(),
            datum_filter=self.datum_var.get() if self.datum_var.get() != "Sve" else None,
        )
        self.destroy()

    def ocisti(self) -> None:
        """Očisti filtere."""
        self.parent.filtriraj_tabelu()
        self.destroy()


class ProzorPodnosioca(tk.Toplevel):
    """Prozor za upravljanje podnosiocima prijave.

    Attributes:
        db: Database objekat.
        godina: Godina za koju se unosi podnosioc.
        entries: Rečnik polja za unos.
        podnosioci: Lista svih podnosioca.
        trenutni_id: ID trenutno izabranog podnosioca.
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
        self.grab_set()
        self.resizable(True, True)
        self.db = db
        self.godina = godina
        self.podnosioci = db.ucitaj_sve_podnosioca()
        self.trenutni_id: Optional[int] = None

        okvir = ttk.Frame(self, padding=20)
        okvir.pack(fill="both", expand=True)

        # Gornji deo - selektor podnosioca
        gornji = ttk.Frame(okvir)
        gornji.pack(fill="x", pady=(0, 10))
        ttk.Label(gornji, text="Podnosioc:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 5))
        self.podnosioc_var = tk.StringVar()
        self.podnosioc_combo = ttk.Combobox(gornji, textvariable=self.podnosioc_var, state="readonly", width=30)
        self.podnosioc_combo.pack(side="left", padx=5)
        self.podnosioc_combo.bind("<<ComboboxSelected>>", self._izabran_podnosioca)
        ttk.Button(gornji, text="- Obriši", command=self._obrisi_podnosioca).pack(side="left", padx=2)

        # Forma za podatke
        forma = ttk.Frame(okvir)
        forma.pack(fill="x", pady=10)
        ttk.Label(forma, text="Godina podnosenja: " + godina,
                  font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.entries = {}
        polja = [("naziv", "Naziv podnosioca:"),
                 ("pib_jmbg", "PIB (9 cifara) ili JMBG (13 cifara):"),
                 ("email", "E-posta:"), ("telefon", "Telefon:"),
                 ("jmbg", "JMBG podnosioca (13 cifara):")]
        for row, (key, label) in enumerate(polja, start=1):
            ttk.Label(forma, text=label).grid(row=row, column=0, sticky="w", pady=4)
            e = ttk.Entry(forma, width=40)
            e.grid(row=row, column=1, padx=10, pady=4)
            self.entries[key] = e
        self.status_jmbg = ttk.Label(forma, text="", font=("Segoe UI", 9), foreground="gray")
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
        dugmad.pack(fill="x", pady=15)
        ttk.Button(dugmad, text="Sacuvaj", command=self.sacuvaj).pack(side="left", padx=5)
        ttk.Button(dugmad, text="Ocisti sva polja", command=self.ocisti).pack(side="left", padx=5)
        for e in self.entries.values():
            e.bind("<Return>", lambda ev: self.sacuvaj())

        # Inicijalno učitaj podatke
        self._osvezi_listu()
        if self.podnosioci:
            self.podnosioc_combo.current(0)
            self._izabran_podnosioca()

    def _osvezi_listu(self) -> None:
        """Osvežava listu podnosioca u combobox-u."""
        self.podnosioci = self.db.ucitaj_sve_podnosioca()
        vrednosti = [f"{p['id']}: {p['naziv']}" for p in self.podnosioci]
        self.podnosioc_combo['values'] = vrednosti
        if self.podnosioci:
            if self.trenutni_id is None:
                self.podnosioc_combo.current(0)
            else:
                for i, p in enumerate(self.podnosioci):
                    if p['id'] == self.trenutni_id:
                        self.podnosioc_combo.current(i)
                        break

    def _izabran_podnosioca(self, event: Optional[tk.Event] = None) -> None:
        """Učitava podatke izabranog podnosioca u formu."""
        izbor = self.podnosioc_var.get()
        if not izbor:
            return
        try:
            id_str = izbor.split(":")[0]
            self.trenutni_id = int(id_str)
        except (ValueError, IndexError):
            return
        p = self.db.ucitaj_podnosioca(self.trenutni_id)
        if p:
            for key in self.entries:
                self.entries[key].delete(0, "end")
                self.entries[key].insert(0, p.get(key, ""))

    def _dodaj_podnosioca(self) -> None:
        """Dodaje novog podnosioca."""
        novi = {
            'naziv': f"Podnosilac {len(self.podnosioci) + 1}",
            'pib_jmbg': '',
            'email': '',
            'telefon': '',
            'jmbg': '',
        }
        id = self.db.dodaj_podnosioca(novi)
        self._osvezi_listu()
        self.podnosioc_var.set(f"{id}: {novi['naziv']}")
        self._izabran_podnosioca()
        messagebox.showinfo("Dodato", f"Novi podnosioc dodat (ID: {id}).", parent=self)

    def _obrisi_podnosioca(self) -> None:
        """Briše izabranog podnosioca."""
        if self.trenutni_id is None:
            messagebox.showwarning("Upozorenje", "Nije izabran podnosioc.", parent=self)
            return
        if not messagebox.askyesno("Potvrda brisanja",
                                   "Obrisati izabranog podnosioca?\n\n(Unosi osoba u tabeli ostaju netaknuti!)",
                                   parent=self):
            return
        self.db.obrisi_podnosioca(self.trenutni_id)
        self.trenutni_id = None
        self._osvezi_listu()
        if self.podnosioci:
            self.podnosioc_combo.current(0)
            self._izabran_podnosioca()
        else:
            for e in self.entries.values():
                e.delete(0, "end")

    def _postavi_aktivnog(self) -> None:
        """Postavlja izabranog podnosioca kao aktivnog."""
        if self.trenutni_id is None:
            messagebox.showwarning("Upozorenje", "Nije izabran podnosioc.", parent=self)
            return
        self.db.postavi_aktivnog(self.trenutni_id)
        self._osvezi_listu()
        messagebox.showinfo("Aktivno", "Izabrani podnosioc je sada aktivan.", parent=self)

    def sacuvaj(self) -> None:
        """Čuva podatke o podnosiocu u bazu."""
        if self.trenutni_id is None:
            messagebox.showwarning("Upozorenje", "Nije izabran podnosioc.", parent=self)
            return
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
        self.db.sacuvaj_podnosioca(d, self.trenutni_id)
        self._osvezi_listu()
        messagebox.showinfo("Sacuvano", "Podaci o podnosiocu su sacuvani.", parent=self)

    def ocisti(self) -> None:
        """Briše sve podatke o podnosiocu za izabranu godinu."""
        if self.trenutni_id is None:
            messagebox.showinfo("Ciscenje", "Nema podnosioca za čišćenje.", parent=self)
            return
        if messagebox.askyesno("Potvrda ciscenja",
                               "Obrisati SVE podatke o podnosiocu?\n\n(Unosi osoba u tabeli ostaju netaknuti!)",
                               parent=self):
            for e in self.entries.values():
                e.delete(0, "end")
            self.db.sacuvaj_podnosioca({'naziv': '', 'pib_jmbg': '', 'email': '', 'telefon': '', 'jmbg': ''}, self.trenutni_id)
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
