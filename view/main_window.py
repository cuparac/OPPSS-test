"""Glavni prozor OPPSS Generator aplikacije (View layer).

``MainWindow`` sadrži samo GUI (widget-e, tabele, menije). Poslovnu logiku
delegira na ``controller.Controller`` preko tankih metoda koje prosleđuju
korisničke akcije.
"""

from __future__ import annotations

import datetime
import logging
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Any, Dict, Optional

from model import Database, validan_jmbg, validan_ebs
from view.widgets import DatumEntry, Kalendar
from view.dialogs import (ProzorFiltera, ProzorPodnosioca, ProzorPretrage,
                          ProzorStatistike, ProzorDuplikata)

logger = logging.getLogger(__name__)


class MainWindow(tk.Tk):
    """Glavna aplikacija OPPSS Generator (View).

    Attributes:
        godina: Trenutna godina.
        db: Database objekat (referentna kopija koju održava Controller).
        controller: Controller objekat (postavlja se preko set_controller).
    """

    def __init__(self) -> None:
        """Inicijalizuje glavnu aplikaciju (samo GUI)."""
        super().__init__()
        self.title("OPPSS Generator v16 GUI STANDALONE - ePorezi prijava")
        self.geometry("1000x700")

        self._godina = str(datetime.date.today().year)
        self.godina_var = tk.StringVar(value=self._godina)
        self.db = Database(self._godina)

        # Controller se postavlja nakon kreiranja view-a
        self.controller: Optional[Any] = None

        # Sortiranje
        self.sort_column: Optional[str] = None
        self.sort_reverse = False

        self.bind("<Control-n>", lambda e: self.dodaj_osobu())
        self.bind("<Control-d>", lambda e: self.obrisi_osobu())
        self.bind("<Control-g>", lambda e: self.generisi())
        self.bind("<Control-p>", lambda e: self.otvori_podnosioca())
        self.bind("<Control-f>", lambda e: self.pretraga())
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())
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
        self.alat_meni = alat_meni
        alat_meni.add_command(label="Pretraga (Ctrl+F)", command=self.pretraga)
        alat_meni.add_command(label="Napredni filteri", command=self.otvori_filtere)
        alat_meni.add_command(label="Statistika", command=self.statistika)
        alat_meni.add_command(label="Migracija JSON → SQLite", command=self.migracija)

        pomoc_meni = tk.Menu(meni, tearoff=0)
        meni.add_cascade(label="Pomoć", menu=pomoc_meni)
        pomoc_meni.add_command(label="O aplikaciji (F1)", command=self.prikazi_about)

        # Dark theme toggle
        self.dark_theme = False
        alat_meni.add_separator()
        self.theme_menu_item = alat_meni.add_command(label="🌙 Dark theme", command=self.promeni_temu)

        # Drag & drop (Windows)
        try:
            import windnd
            self.drop_target_register(tk.DND_FILES)
            self.dnd_bind('<<Drop>>', self.on_drop)
        except ImportError:
            pass

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

        # Notebook sa tabovima
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Tab 1: Svi unosi
        tab_svi = ttk.Frame(notebook)
        notebook.add(tab_svi, text="Svi unosi")
        kolone = ("rb", "tip", "identifikator", "ime_naziv", "opstina", "adresa", "telefon", "datum", "iznos")
        naslovi = {"rb": "R.br", "tip": "Vrsta prometa", "identifikator": "JMBG/PIB/EBS",
                   "ime_naziv": "Ime / Naziv", "opstina": "Opština", "adresa": "Adresa",
                   "telefon": "Telefon", "datum": "Datum (od/do)", "iznos": "Iznos (RSD)"}
        sirine = {"rb": 45, "tip": 165, "identifikator": 115, "ime_naziv": 170,
                  "opstina": 120, "adresa": 140, "telefon": 105, "datum": 100, "iznos": 95}
        self.tree = ttk.Treeview(tab_svi, columns=kolone, show="headings", height=12)
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

        sb = ttk.Scrollbar(tab_svi, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        # Status label za sortiranje
        self.sort_status = ttk.Label(tab_svi, text="", font=("Segoe UI", 9), foreground="gray")
        self.sort_status.pack(fill="x", padx=10, pady=(0, 5))

        # Paginacija
        self.page_size = 100
        self.current_page = 0
        self.total_pages = 0
        self.paginacija_frame = ttk.Frame(tab_svi)
        self.paginacija_frame.pack(fill="x", padx=10, pady=(0, 5))
        ttk.Button(self.paginacija_frame, text="<< Prva", command=self.prva_strana).pack(side="left", padx=2)
        ttk.Button(self.paginacija_frame, text="< Prethodna", command=self.prethodna_strana).pack(side="left", padx=2)
        self.page_label = ttk.Label(self.paginacija_frame, text="Strana 1/1", font=("Segoe UI", 9))
        self.page_label.pack(side="left", padx=10)
        ttk.Button(self.paginacija_frame, text="Sledeća >", command=self.sledeca_strana).pack(side="left", padx=2)
        ttk.Button(self.paginacija_frame, text="Poslednja >>", command=self.poslednja_strana).pack(side="left", padx=2)

        # Tab 2: Po opštini
        tab_opstine = ttk.Frame(notebook)
        notebook.add(tab_opstine, text="Po opštini")
        kolone_opstine = ("opstina", "broj", "iznos")
        self.tree_opstine = ttk.Treeview(tab_opstine, columns=kolone_opstine, show="headings", height=12)
        for k in kolone_opstine:
            self.tree_opstine.heading(k, text=k.capitalize())
            self.tree_opstine.column(k, width=150)
        self.tree_opstine.pack(side="left", fill="both", expand=True)
        sb_opstine = ttk.Scrollbar(tab_opstine, orient="vertical", command=self.tree_opstine.yview)
        sb_opstine.pack(side="right", fill="y")
        self.tree_opstine.configure(yscrollcommand=sb_opstine.set)

        # Tab 3: Po vrsti prometa
        tab_vrste = ttk.Frame(notebook)
        notebook.add(tab_vrste, text="Po vrsti prometa")
        kolone_vrste = ("vrsta", "broj", "iznos")
        self.tree_vrste = ttk.Treeview(tab_vrste, columns=kolone_vrste, show="headings", height=12)
        for k in kolone_vrste:
            self.tree_vrste.heading(k, text=k.capitalize())
            self.tree_vrste.column(k, width=150)
        self.tree_vrste.pack(side="left", fill="both", expand=True)
        sb_vrste = ttk.Scrollbar(tab_vrste, orient="vertical", command=self.tree_vrste.yview)
        sb_vrste.pack(side="right", fill="y")
        self.tree_vrste.configure(yscrollcommand=sb_vrste.set)

        # Tab 4: Po datumu
        tab_datumi = ttk.Frame(notebook)
        notebook.add(tab_datumi, text="Po datumu")
        kolone_datumi = ("datum", "broj", "iznos")
        self.tree_datumi = ttk.Treeview(tab_datumi, columns=kolone_datumi, show="headings", height=12)
        for k in kolone_datumi:
            self.tree_datumi.heading(k, text=k.capitalize())
            self.tree_datumi.column(k, width=150)
        self.tree_datumi.pack(side="left", fill="both", expand=True)
        sb_datumi = ttk.Scrollbar(tab_datumi, orient="vertical", command=self.tree_datumi.yview)
        sb_datumi.pack(side="right", fill="y")
        self.tree_datumi.configure(yscrollcommand=sb_datumi.set)

        # Tab 5: Grafikoni
        tab_grafikoni = ttk.Frame(notebook)
        notebook.add(tab_grafikoni, text="Grafikoni")
        self.grafikoni_frame = ttk.Frame(tab_grafikoni)
        self.grafikoni_frame.pack(fill="both", expand=True)

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

        # Ako je controller već postavljen, osveži prikaz
        if self.controller is not None:
            self.osvezi_sve()

    # ------------------------------------------------------------------
    # Controller wiring
    # ------------------------------------------------------------------
    def set_controller(self, controller: Any) -> None:
        """Povezuje Controller sa ovim View-om i osvežava prikaz.

        Args:
            controller: Controller objekat.
        """
        self.controller = controller
        self.db = controller.db
        self.osvezi_sve()
        self.proveri_migraciju()

    def _ctrl(self) -> Any:
        """Vraća Controller ili None ako još nije postavljen.

        Returns:
            Controller objekat ili None.
        """
        return self.controller

    # ------------------------------------------------------------------
    # Delegacije na Controller (korisničke akcije)
    # ------------------------------------------------------------------
    def dodaj_osobu(self) -> None:
        """Delegira dodavanje novog unosa Controller-u."""
        if self.controller:
            self.controller.dodaj_osobu()

    def izmeni_osobu(self) -> None:
        """Delegira izmenu unosa Controller-u."""
        if self.controller:
            self.controller.izmeni_osobu()

    def obrisi_osobu(self) -> None:
        """Delegira brisanje unosa Controller-u."""
        if self.controller:
            self.controller.obrisi_osobu()

    def obrisi_sve(self) -> None:
        """Delegira brisanje svih unosa Controller-u."""
        if self.controller:
            self.controller.obrisi_sve()

    def pretraga(self) -> None:
        """Delegira otvaranje pretrage Controller-u."""
        if self.controller:
            self.controller.pretraga()

    def pretraga_po_id(self) -> None:
        """Delegira pretragu po ID-ju Controller-u."""
        if self.controller:
            self.controller.pretraga_po_id()

    def statistika(self) -> None:
        """Delegira otvaranje statistike Controller-u."""
        if self.controller:
            self.controller.statistika()

    def otvori_podnosioca(self) -> None:
        """Delegira otvaranje prozora podnosioca Controller-u."""
        if self.controller:
            self.controller.otvori_podnosioca()

    def otvori_filtere(self) -> None:
        """Delegira otvaranje filtera Controller-u."""
        if self.controller:
            self.controller.otvori_filtere()

    def filtriraj_tabelu(self, vrsta: Optional[str] = None, opstina: Optional[str] = None,
                         min_iznos: str = "0", max_iznos: str = "999999999",
                         datum_filter: Optional[str] = None) -> None:
        """Delegira filtriranje tabele Controller-u."""
        if self.controller:
            self.controller.filtriraj_tabelu(vrsta, opstina, min_iznos, max_iznos, datum_filter)

    def sort_by(self, col: str) -> None:
        """Delegira sortiranje tabele Controller-u."""
        if self.controller:
            self.controller.sort_by(col)

    def export_csv(self) -> None:
        """Delegira CSV export Controller-u."""
        if self.controller:
            self.controller.export_csv()

    def import_csv(self) -> None:
        """Delegira CSV import Controller-u."""
        if self.controller:
            self.controller.import_csv()

    def export_html(self) -> None:
        """Delegira HTML izveštaj Controller-u."""
        if self.controller:
            self.controller.export_html()

    def export_pdf(self) -> None:
        """Delegira PDF izveštaj Controller-u."""
        if self.controller:
            self.controller.export_pdf()

    def export_xml(self) -> None:
        """Delegira XML izveštaj Controller-u."""
        if self.controller:
            self.controller.export_xml()

    def generisi(self) -> None:
        """Delegira generisanje XML-a Controller-u."""
        if self.controller:
            self.controller.generisi()

    def backup_baze(self) -> None:
        """Delegira backup baze Controller-u."""
        if self.controller:
            self.controller.backup_baze()

    def undo(self) -> None:
        """Delegira undo Controller-u."""
        if self.controller:
            self.controller.undo()

    def redo(self) -> None:
        """Delegira redo Controller-u."""
        if self.controller:
            self.controller.redo()

    def promeni_godinu(self) -> None:
        """Delegira promenu godine Controller-u."""
        if self.controller:
            self.controller.promeni_godinu()

    def migracija(self) -> None:
        """Delegira migraciju Controller-u."""
        if self.controller:
            self.controller.migracija()

    def proveri_migraciju(self) -> None:
        """Delegira proveru migracije Controller-u."""
        if self.controller:
            self.controller.proveri_migraciju()

    def prikazi_about(self) -> None:
        """Delegira prikaz 'O aplikaciji' Controller-u."""
        if self.controller:
            self.controller.prikazi_about()

    def on_drop(self, event: tk.Event) -> None:
        """Delegira drag & drop obradu Controller-u."""
        if self.controller:
            self.controller.on_drop(event)

    # ------------------------------------------------------------------
    # GUI: tabele, tabovi, grafikoni, info
    # ------------------------------------------------------------------
    def _popuni_iz_duplikata(self, entries: Dict[str, Any], osoba: Dict[str, Any],
                             zadrzi_datume: bool = False) -> None:
        """Popunjava formu podacima postojećeg unosa iz baze.

        Koristi se u dva slučaja:
        - korisnik izabere "Ne snimaj" u prozoru za duplikat (isti JMBG i datum)
        - korisnik ukuca JMBG/PIB/EBS koji već postoji (prepis podataka za novi
          period) — tada se datumi i iznos NE prepisuju

        Args:
            entries: Rečnik widget-a forme (ključ -> widget).
            osoba: Dict sa postojećim unosom iz baze.
            zadrzi_datume: Ako je True, polja datuma i iznosa ostaju netaknuta.
        """
        vrste_pr = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}
        vrste_id = {"1": "JMBG", "0": "PIB", "5": "EBS"}

        for key, w in entries.items():
            if key in ("datum_unos", "datum_do"):
                if zadrzi_datume:
                    continue
                datum_key = "datum" if key == "datum_unos" else "datum_do"
                w.delete(0, "end")
                vrednost = osoba.get(datum_key, "")
                if vrednost:
                    try:
                        w.insert(0, datetime.datetime.strptime(vrednost, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    except ValueError:
                        w.insert(0, str(vrednost))
                continue

            if key == "iznos_prometa" and zadrzi_datume:
                continue

            if key == "vrsta_tip":
                vrednost = vrste_pr.get(str(osoba.get("vrsta_prometa", "")), "")
            elif key == "id_tip":
                vrednost = vrste_id.get(str(osoba.get("vrsta_identifikatora", "")), "")
            else:
                vrednost = osoba.get(key, "")

            if hasattr(w, "set"):
                if vrednost != "" and vrednost is not None:
                    w.set(str(vrednost))
            elif hasattr(w, "delete"):
                w.delete(0, "end")
                w.insert(0, str(vrednost if vrednost is not None else ""))

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

    def osvezi_info(self) -> None:
        """Osvežava informacije o podnosiocu u glavnom prozoru."""
        p = self.db.ucitaj_podnosioca() or {}
        if p.get("pib_jmbg"):
            naziv = p.get('naziv', '')
            self.info_podnosioc.config(text="Podnosioc: %s (%s)   |   Godina: %s" % (naziv, p['pib_jmbg'], self.godina))
        else:
            self.info_podnosioc.config(text="[!] Podaci o podnosiocu NISU uneseni za %s. godinu!" % self.godina)

    def osvezi_tabelu(self) -> None:
        """Osvežava tabelu sa unosima (sa paginacijom)."""
        self.tree.delete(*self.tree.get_children())
        tipovi = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}

        # Ukupan broj unosa i stranica
        ukupno_unosa = self.db.broj_unosa()
        self.total_pages = max(1, (ukupno_unosa + self.page_size - 1) // self.page_size)
        if self.current_page >= self.total_pages:
            self.current_page = self.total_pages - 1
        if self.current_page < 0:
            self.current_page = 0

        # Učitaj stranicu
        offset = self.current_page * self.page_size
        ljudi = self.db.ucitaj_ljude_stranicu(offset, self.page_size)

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

        for i, o in enumerate(ljudi, offset + 1):
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
        self.ukupno_label.config(text="%d unosa | Ukupno: %s RSD" % (ukupno_unosa, format(ukupno, ",").replace(",", ".")))
        self.page_label.config(text="Strana %d/%d" % (self.current_page + 1, self.total_pages))

    def prva_strana(self) -> None:
        """Ide na prvu stranicu."""
        self.current_page = 0
        self.osvezi_tabelu()

    def prethodna_strana(self) -> None:
        """Ide na prethodnu stranicu."""
        if self.current_page > 0:
            self.current_page -= 1
            self.osvezi_tabelu()

    def sledeca_strana(self) -> None:
        """Ide na sledeću stranicu."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.osvezi_tabelu()

    def poslednja_strana(self) -> None:
        """Ide na poslednju stranicu."""
        self.current_page = self.total_pages - 1
        self.osvezi_tabelu()

    def osvezi_sve(self) -> None:
        """Osvežava sve komponente glavnog prozora."""
        if self.controller is None:
            return
        self.osvezi_tabelu()
        self.osvezi_tabove()
        self.osvezi_info()

    def osvezi_tabove(self) -> None:
        """Osvežava tabove (Po opštini, Po vrsti prometa, Po datumu, Grafikoni)."""
        ljudi = self.db.ucitaj_ljude()

        # Po opštini
        self.tree_opstine.delete(*self.tree_opstine.get_children())
        po_opstini: Dict[str, Dict[str, Any]] = {}
        for o in ljudi:
            opstina = o.get("opstina", "") or "Bez opštine"
            if opstina not in po_opstini:
                po_opstini[opstina] = {"broj": 0, "iznos": 0}
            po_opstini[opstina]["broj"] += 1
            po_opstini[opstina]["iznos"] += o.get("iznos_prometa", 0)
        for opstina, podaci in sorted(po_opstini.items()):
            self.tree_opstine.insert("", "end", values=(
                opstina, podaci["broj"], format(podaci["iznos"], ",").replace(",", ".")))

        # Po vrsti prometa
        self.tree_vrste.delete(*self.tree_vrste.get_children())
        tipovi = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}
        po_vrsti: Dict[str, Dict[str, Any]] = {}
        for o in ljudi:
            vrsta = tipovi.get(o.get("vrsta_prometa", ""), "Ostalo")
            if vrsta not in po_vrsti:
                po_vrsti[vrsta] = {"broj": 0, "iznos": 0}
            po_vrsti[vrsta]["broj"] += 1
            po_vrsti[vrsta]["iznos"] += o.get("iznos_prometa", 0)
        for vrsta, podaci in sorted(po_vrsti.items()):
            self.tree_vrste.insert("", "end", values=(
                vrsta, podaci["broj"], format(podaci["iznos"], ",").replace(",", ".")))

        # Po datumu
        self.tree_datumi.delete(*self.tree_datumi.get_children())
        po_datumu: Dict[str, Dict[str, Any]] = {}
        for o in ljudi:
            datum = o.get("datum", "") or "Bez datuma"
            if datum not in po_datumu:
                po_datumu[datum] = {"broj": 0, "iznos": 0}
            po_datumu[datum]["broj"] += 1
            po_datumu[datum]["iznos"] += o.get("iznos_prometa", 0)
        for datum, podaci in sorted(po_datumu.items()):
            self.tree_datumi.insert("", "end", values=(
                datum, podaci["broj"], format(podaci["iznos"], ",").replace(",", ".")))

        # Grafikoni
        self.osvezi_grafikone(po_opstini, po_vrsti)

    def osvezi_grafikone(self, po_opstini: Dict[str, Dict[str, Any]], po_vrsti: Dict[str, Dict[str, Any]]) -> None:
        """Osvežava grafikone u tabu Grafikoni.

        Args:
            po_opstini: Dict sa podacima po opštini
            po_vrsti: Dict sa podacima po vrsti prometa
        """
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            # Matplotlib nije instaliran - prikazuje se poruka
            for widget in self.grafikoni_frame.winfo_children():
                widget.destroy()
            ttk.Label(self.grafikoni_frame, text="Matplotlib nije instaliran.\nInstalirajte: pip install matplotlib",
                      font=("Segoe UI", 12), foreground="gray").pack(expand=True)
            return

        # Obriši prethodne grafikone
        for widget in self.grafikoni_frame.winfo_children():
            widget.destroy()

        if not po_opstini and not po_vrsti:
            ttk.Label(self.grafikoni_frame, text="Nema podataka za grafikone.",
                      font=("Segoe UI", 12), foreground="gray").pack(expand=True)
            return

        # Kreiraj figure
        fig = Figure(figsize=(10, 8), dpi=100)

        # Grafikon 1: Bar chart po opštini (iznos)
        if po_opstini:
            ax1 = fig.add_subplot(221)
            opstine = list(po_opstini.keys())
            iznosi = [po_opstini[o]["iznos"] for o in opstine]
            ax1.barh(opstine, iznosi, color="#4a90d9")
            ax1.set_title("Iznos po opštini")
            ax1.set_xlabel("RSD")

        # Grafikon 2: Bar chart po vrsti prometa (iznos)
        if po_vrsti:
            ax2 = fig.add_subplot(222)
            vrste = list(po_vrsti.keys())
            iznosi_vrsta = [po_vrsti[v]["iznos"] for v in vrste]
            ax2.bar(vrste, iznosi_vrsta, color="#e74c3c")
            ax2.set_title("Iznos po vrsti prometa")
            ax2.set_ylabel("RSD")

        # Grafikon 3: Pie chart po vrsti prometa (broj)
        if po_vrsti:
            ax3 = fig.add_subplot(223)
            vrste = list(po_vrsti.keys())
            brojevi = [po_vrsti[v]["broj"] for v in vrste]
            ax3.pie(brojevi, labels=vrste, autopct="%1.1f%%", startangle=90)
            ax3.set_title("Broj po vrsti prometa")

        # Grafikon 4: Bar chart po opštini (broj)
        if po_opstini:
            ax4 = fig.add_subplot(224)
            opstine = list(po_opstini.keys())
            brojevi_opstina = [po_opstini[o]["broj"] for o in opstine]
            ax4.bar(opstine, brojevi_opstina, color="#2ecc71")
            ax4.set_title("Broj po opštini")
            ax4.set_ylabel("Broj")

        fig.tight_layout()

        # Prikazi u Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.grafikoni_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def promeni_temu(self) -> None:
        """Menja između svetle i tamne teme (čisto GUI)."""
        self.dark_theme = not self.dark_theme
        style = ttk.Style()

        # Ažuriraj tekst dugme u meniju
        theme_idx = self.alat_meni.index("end")
        if theme_idx is not None:
            self.alat_meni.entryconfigure(theme_idx, label="☀️ Light theme" if self.dark_theme else "🌙 Dark theme")

        if self.dark_theme:
            # Tamna tema
            style.theme_use("clam")
            style.configure(".", background="#2b2b2b", foreground="#ffffff")
            style.configure("TFrame", background="#2b2b2b")
            style.configure("TLabel", background="#2b2b2b", foreground="#ffffff")
            style.configure("TButton", background="#3c3c3c", foreground="#ffffff")
            style.configure("TEntry", fieldbackground="#3c3c3c", foreground="#ffffff")
            style.configure("TCombobox", fieldbackground="#3c3c3c", foreground="#ffffff")
            style.configure("Treeview", background="#3c3c3c", foreground="#ffffff", fieldbackground="#3c3c3c")
            style.configure("Treeview.Heading", background="#4a4a4a", foreground="#ffffff")
            style.configure("TNotebook", background="#2b2b2b")
            style.configure("TNotebook.Tab", background="#3c3c3c", foreground="#ffffff")
            style.configure("TLabelframe", background="#2b2b2b", foreground="#ffffff")
            style.configure("TLabelframe.Label", background="#2b2b2b", foreground="#ffffff")
            style.configure("TSeparator", background="#2b2b2b")
            style.configure("TScrollbar", background="#3c3c3c", troughcolor="#2b2b2b")
            style.configure("TRadiobutton", background="#2b2b2b", foreground="#ffffff")
            style.configure("TCheckbutton", background="#2b2b2b", foreground="#ffffff")
            style.configure("TMenu", background="#3c3c3c", foreground="#ffffff")
            self.configure(background="#2b2b2b")
            # Kontekstni meniji
            self.context_menu_row.configure(background="#3c3c3c", foreground="#ffffff")
            self.context_menu_empty.configure(background="#3c3c3c", foreground="#ffffff")
        else:
            # Svetla tema
            style.theme_use("clam")
            style.configure(".", background="#f0f0f0", foreground="#000000")
            style.configure("TFrame", background="#f0f0f0")
            style.configure("TLabel", background="#f0f0f0", foreground="#000000")
            style.configure("TButton", background="#e0e0e0", foreground="#000000")
            style.configure("TEntry", fieldbackground="#ffffff", foreground="#000000")
            style.configure("TCombobox", fieldbackground="#ffffff", foreground="#000000")
            style.configure("Treeview", background="#ffffff", foreground="#000000", fieldbackground="#ffffff")
            style.configure("Treeview.Heading", background="#e0e0e0", foreground="#000000")
            style.configure("TNotebook", background="#f0f0f0")
            style.configure("TNotebook.Tab", background="#e0e0e0", foreground="#000000")
            style.configure("TLabelframe", background="#f0f0f0", foreground="#000000")
            style.configure("TLabelframe.Label", background="#f0f0f0", foreground="#000000")
            style.configure("TSeparator", background="#f0f0f0")
            style.configure("TScrollbar", background="#e0e0e0", troughcolor="#f0f0f0")
            style.configure("TRadiobutton", background="#f0f0f0", foreground="#000000")
            style.configure("TCheckbutton", background="#f0f0f0", foreground="#000000")
            style.configure("TMenu", background="#e0e0e0", foreground="#000000")
            self.configure(background="#f0f0f0")
            # Kontekstni meniji
            self.context_menu_row.configure(background="#e0e0e0", foreground="#000000")
            self.context_menu_empty.configure(background="#e0e0e0", foreground="#000000")

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

    # ------------------------------------------------------------------
    # Forma za unos/izmenu osobe (GUI + delegacija validacije/snimanja)
    # ------------------------------------------------------------------
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
        entries: Dict[str, Any] = {}
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
                    nadjen = self.db.pronadji_po_identifikatoru(broj)
                    if nadjen:
                        # Popuni podatke iz prethodnog unosa istog JMBG/PIB/EBS —
                        # datumi i iznos se NE prepisuju (novi period je različit).
                        self._popuni_iz_duplikata(entries, nadjen, zadrzi_datume=True)
                        info_dupli.config(
                            text="↻ Podaci prepisani iz prethodnog unosa — unesite datum/iznos",
                            foreground="#0a6b0a")
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
            ok = False
            if self.controller:
                ishod = self.controller.sacuvaj_osobu(entries, indeks_izmene, parent=win)
                if ishod == "duplikat":
                    # Postoji unos sa istim identifikatorom i datumom - pokaži
                    # prozor sa tri jasne opcije (Zameni / Dodaj kao novi / Ne snimaj).
                    dlg = ProzorDuplikata(win, entries["identifikator"].get().strip(),
                                          self.controller._podaci_za_snimanje["datum"],
                                          self.controller._duplikat)
                    if dlg.rezultat == "zameni":
                        ok = self.controller.resi_duplikat("zameni")
                    elif dlg.rezultat == "dodaj":
                        ok = self.controller.resi_duplikat("dodaj")
                    else:
                        # "Ne snimaj" - popuni polja podacima postojećeg unosa
                        # da korisnik vidi šta je već u bazi i može da izmeni.
                        self._popuni_iz_duplikata(entries, dlg.podaci)
                        self.controller.resi_duplikat("preskoci")
                        return
                elif ishod == "snimljeno":
                    ok = True
            if not ok:
                return
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

        def tab_napred(ev: tk.Event) -> str:
            try:
                idx = redosled_tab.index(win.focus_get())
            except ValueError:
                idx = -1
            sledeci = redosled_tab[(idx + 1) % len(redosled_tab)]
            sledeci.focus_set()
            if isinstance(sledeci, ttk.Entry):
                sledeci.select_range(0, "end")
            return "break"

        def tab_nazad(ev: tk.Event) -> str:
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
