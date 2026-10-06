"""Controller za OPPSS Generator (MVC).

Sadrži ``UndoStack`` (logika undo/redo) i ``Controller`` klasu koja povezuje
Model (baza, validacije, XML generator) i View (glavni prozor).

Controller prima događaje iz View-a, poziva Model i ažurira View rezultatima.
"""

from __future__ import annotations

import datetime
import logging
import os
import shutil
import webbrowser
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import tkinter as tk
from tkinter import messagebox, filedialog

from model import Database, migriraj_json_u_sqlite
from model import validan_jmbg, validan_ebs, konvertuj_datum
from model import generisi_xml, generisi_html_izvestaj, generisi_pdf_izvestaj
from view.dialogs import ProzorFiltera, ProzorPodnosioca, ProzorPretrage, ProzorStatistike

if TYPE_CHECKING:
    from view.main_window import MainWindow

logger = logging.getLogger(__name__)


class UndoStack:
    """Stack za undo/redo operacije.

    Attributes:
        undo_stack: Lista operacija za poništavanje.
        redo_stack: Lista operacija za ponavljanje.
    """

    def __init__(self) -> None:
        """Inicijalizuje UndoStack."""
        self.undo_stack: List[Tuple[str, Any]] = []
        self.redo_stack: List[Tuple[str, Any]] = []

    def push(self, operacija: str, podaci: Any) -> None:
        """Dodaje operaciju na undo stack.

        Args:
            operacija: Tip operacije ("dodaj", "izmeni", "obrisi").
            podaci: Podaci potrebni za poništavanje.
        """
        self.undo_stack.append((operacija, podaci))
        self.redo_stack.clear()

    def undo(self, db: Database) -> Optional[str]:
        """Poništava poslednju operaciju.

        Args:
            db: Database objekat.

        Returns:
            Poruka o operaciji ili None ako nema operacija.
        """
        if not self.undo_stack:
            return None
        operacija, podaci = self.undo_stack.pop()
        if operacija == "dodaj":
            db.obrisi_osobu(podaci['id'])
            self.redo_stack.append(("dodaj", podaci))
        elif operacija == "obrisi":
            db.dodaj_osobu(podaci)
            self.redo_stack.append(("obrisi", podaci))
        elif operacija == "izmeni":
            db.izmeni_osobu(podaci['id'], podaci['stari'])
            self.redo_stack.append(("izmeni", podaci))
        return f"Undo: {operacija}"

    def redo(self, db: Database) -> Optional[str]:
        """Ponavlja poslednju poništenu operaciju.

        Args:
            db: Database objekat.

        Returns:
            Poruka o operaciji ili None ako nema operacija.
        """
        if not self.redo_stack:
            return None
        operacija, podaci = self.redo_stack.pop()
        if operacija == "dodaj":
            db.dodaj_osobu(podaci)
            self.undo_stack.append(("dodaj", podaci))
        elif operacija == "obrisi":
            db.obrisi_osobu(podaci['id'])
            self.undo_stack.append(("obrisi", podaci))
        elif operacija == "izmeni":
            db.izmeni_osobu(podaci['id'], podaci['novi'])
            self.undo_stack.append(("izmeni", podaci))
        return f"Redo: {operacija}"


class Controller:
    """Poslovna logika OPPSS Generator-a.

    Povezuje Model (``Database``, validacije, XML generator) i View
    (``MainWindow``). View prosleđuje korisničke akcije Controller-u, a
    Controller poziva Model i osvežava View.

    Attributes:
        db: Database objekat (Model).
        view: Glavni prozor (View).
        undo_stack: UndoStack za undo/redo operacije.
    """

    def __init__(self, db: Database, view: "MainWindow") -> None:
        """Inicijalizuje Controller.

        Args:
            db: Database objekat.
            view: Glavni prozor (View).
        """
        self.db = db
        self.view = view
        self.undo_stack = UndoStack()

    # ------------------------------------------------------------------
    # Godina / migracija
    # ------------------------------------------------------------------
    def proveri_migraciju(self) -> None:
        """Proverava da li postoji stari JSON fajl za migraciju."""
        json_file = f"baza_{self.view.godina}.json"
        if os.path.exists(json_file):
            odgovor = messagebox.askyesno("Migracija",
                "Pronađen je stari JSON fajl. Želite li da ga migrirate u SQLite bazu?")
            if odgovor:
                self.migracija()

    def migracija(self) -> None:
        """Vrši migraciju podataka iz JSON fajla u SQLite bazu."""
        json_file = f"baza_{self.view.godina}.json"
        if not os.path.exists(json_file):
            messagebox.showinfo("Migracija", "Nema JSON fajla za migraciju.")
            return

        uspeh, poruka = migriraj_json_u_sqlite(self.view.godina)
        if uspeh:
            messagebox.showinfo("Migracija", poruka)
            self.view.osvezi_sve()
        else:
            messagebox.showerror("Migracija", poruka)

    def promeni_godinu(self) -> None:
        """Menja godinu i osvežava prikaz."""
        self.db.zatvori()
        self.view._godina = self.view.godina_var.get()
        self.db = Database(self.view._godina)
        self.view.db = self.db
        self.view.sort_column = None
        self.view.sort_reverse = False
        self.view.current_page = 0
        self.view.osvezi_sve()

    # ------------------------------------------------------------------
    # CRUD osoba
    # ------------------------------------------------------------------
    def dodaj_osobu(self) -> None:
        """Otvara formu za dodavanje novog unosa."""
        self.view.forma_osobe()

    def izmeni_osobu(self) -> None:
        """Otvara formu za izmenu postojećeg unosa."""
        sel = self.view.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Izaberite unos u tabeli!")
            return
        id = int(sel[0])
        ljudi = self.db.ucitaj_ljude()
        osoba = next((o for o in ljudi if o['id'] == id), None)
        if osoba:
            self.view.forma_osobe(osoba, id)

    def obrisi_osobu(self) -> None:
        """Briše selektovani unos iz tabele."""
        sel = self.view.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Izaberite unos u tabeli!")
            return
        id = int(sel[0])
        ime = self.view.tree.item(sel[0])['values'][3]
        if messagebox.askyesno("Brisanje", "Obrisati unos: " + str(ime) + "?"):
            ljudi = self.db.ucitaj_ljude()
            osoba = next((o for o in ljudi if o['id'] == id), None)
            if osoba:
                self.undo_stack.push("obrisi", osoba)
            self.db.obrisi_osobu(id)
            self.view.osvezi_tabelu()

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
                                   self.view.godina,
                                   len(ljudi),
                                   format(sum(o['iznos_prometa'] for o in ljudi), ",").replace(",", "."))):
            if messagebox.askyesno("POTVRDA", "Jeste li zaista sigurni? Ovo će obrisati SVE podatke o osobama!"):
                self.db.obrisi_sve()
                self.view.osvezi_sve()
                messagebox.showinfo("Obrisano", "Svi unosi za %s. godinu su obrisani." % self.view.godina)

    def sacuvaj_osobu(self, entries: Dict[str, Any], indeks_izmene: Optional[int] = None,
                      parent: Any = None) -> bool:
        """Validira i čuva unos osobe (dodavanje ili izmena).

        Args:
            entries: Rečnik widget-a forme (ključ -> widget).
            indeks_izmene: ID unosa koji se menja ili None za novi unos.
            parent: Roditeljski prozor za dijaloge.

        Returns:
            True ako je unos sačuvan, inače False.
        """
        vrste_pr = {"Poljoprivredni proizvodi/usluge": "1", "Sekundarne sirovine": "2"}
        vrste_id = {"JMBG": "1", "PIB": "0", "EBS": "5"}

        datum_iso = konvertuj_datum(entries["datum_unos"].get())
        if not datum_iso or not entries["datum_unos"].dobar_datum():
            messagebox.showerror("Greska", "Neispravan datum OD!\nKucajte 8 cifara: DDMMYYYY\nPrimer: 01012026", parent=parent)
            return False
        datum_do_iso = konvertuj_datum(entries["datum_do"].get())
        if not datum_do_iso or not entries["datum_do"].dobar_datum():
            messagebox.showerror("Greska", "Neispravan datum DO!\nKucajte 8 cifara: DDMMYYYY\nPrimer: 01012026", parent=parent)
            return False
        if datum_do_iso < datum_iso:
            messagebox.showerror("Greska", "Datum DO ne moze biti pre datuma OD!", parent=parent)
            return False
        broj_id = entries["identifikator"].get().strip()
        tip = entries["id_tip"].get()
        ocekivano = 13 if tip == "JMBG" else 9
        if not broj_id.isdigit() or len(broj_id) != ocekivano:
            messagebox.showerror("Greska", "Identifikator mora imati TACNO %d cifara!\n(Uneseno: %d)" % (ocekivano, len(broj_id)), parent=parent)
            return False
        if tip == "JMBG" and not validan_jmbg(broj_id):
            if not messagebox.askyesno("Upozorenje",
                                       "JMBG (%s) NE prolazi proveru kontrolne cifre!\n\nDa li IPAK zelite da sacuvate ovaj unos?" % broj_id,
                                       parent=parent):
                return False
        if tip == "EBS" and not validan_ebs(broj_id):
            if not messagebox.askyesno("Upozorenje",
                                       "EBS (%s) NIJE ispravan (mora imati 9 cifara)!\n\nDa li IPAK zelite da sacuvate ovaj unos?" % broj_id,
                                       parent=parent):
                return False
        try:
            iznos = int(entries["iznos_prometa"].get().strip())
            if iznos <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Greska", "Iznos mora biti pozitivan ceo broj!", parent=parent)
            return False

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
                    parent=parent)
                if odgovor is None:  # Preskoči
                    return False
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
                messagebox.showwarning("Upozorenje", "Popunite sva obavezna polja!", parent=parent)
                return False

        if indeks_izmene is not None:
            stari = next((o for o in self.db.ucitaj_ljude() if o['id'] == indeks_izmene), None)
            if stari:
                self.undo_stack.push("izmeni", {"id": indeks_izmene, "stari": stari, "novi": r})
            self.db.izmeni_osobu(indeks_izmene, r)
        else:
            self.db.dodaj_osobu(r)
            novi_id = self.db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            self.undo_stack.push("dodaj", {"id": novi_id, **r})
        self.view.osvezi_tabelu()
        return True

    # ------------------------------------------------------------------
    # Sortiranje / filtriranje
    # ------------------------------------------------------------------
    def sort_by(self, col: str) -> None:
        """Sortira tabelu po odabranoj koloni.

        Args:
            col: Naziv kolone po kojoj se sortira.
        """
        if self.view.sort_column == col:
            self.view.sort_reverse = not self.view.sort_reverse
        else:
            self.view.sort_column = col
            self.view.sort_reverse = False

        # Ažuriraj indikatore sortiranja u zaglavljima
        kolone = ("rb", "tip", "identifikator", "ime_naziv", "opstina", "adresa", "telefon", "datum", "iznos")
        naslovi = {"rb": "R.br", "tip": "Vrsta prometa", "identifikator": "JMBG/PIB/EBS",
                   "ime_naziv": "Ime / Naziv", "opstina": "Opština", "adresa": "Adresa",
                   "telefon": "Telefon", "datum": "Datum (od/do)", "iznos": "Iznos (RSD)"}

        for k in kolone:
            text = naslovi[k]
            if k == self.view.sort_column:
                text += " ▼" if self.view.sort_reverse else " ▲"
            self.view.tree.heading(k, text)

        # Ažuriraj status label (tooltip)
        if self.view.sort_column:
            smer = "opadajuće" if self.view.sort_reverse else "rastuće"
            self.view.sort_status.config(text=f"Sortirano po: {naslovi.get(self.view.sort_column, self.view.sort_column)} ({smer})")
        else:
            self.view.sort_status.config(text="")

        self.view.osvezi_tabelu()

    def filtriraj_tabelu(self, vrsta: Optional[str] = None, opstina: Optional[str] = None,
                         min_iznos: str = "0", max_iznos: str = "999999999",
                         datum_filter: Optional[str] = None) -> None:
        """Filtrira tabelu po zadatim kriterijumima.

        Args:
            vrsta: Vrsta prometa (1, 2 ili None za sve).
            opstina: Opština (string ili None za sve).
            min_iznos: Minimalni iznos (string).
            max_iznos: Maksimalni iznos (string).
            datum_filter: Filter po datumu ("godina", "mesec" ili None za sve).
        """
        self.view.tree.delete(*self.view.tree.get_children())
        ljudi = self.db.ucitaj_ljude()
        tipovi = {"1": "Poljoprivredni proizvodi/usluge", "2": "Sekundarne sirovine"}

        try:
            min_val = int(min_iznos) if min_iznos else 0
            max_val = int(max_iznos) if max_iznos else 999999999
        except ValueError:
            min_val = 0
            max_val = 999999999

        # Izračunaj granice za datum filter
        datum_od_limit = None
        datum_do_limit = None
        if datum_filter == "godina":
            datum_od_limit = f"{self.view.godina}-01-01"
            datum_do_limit = f"{self.view.godina}-12-31"
        elif datum_filter == "mesec":
            sada = datetime.datetime.now()
            datum_od_limit = sada.replace(day=1).strftime("%Y-%m-%d")
            # Poslednji dan meseca
            if sada.month == 12:
                sledeci = sada.replace(year=sada.year + 1, month=1, day=1)
            else:
                sledeci = sada.replace(month=sada.month + 1, day=1)
            datum_do_limit = (sledeci - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        for o in ljudi:
            if vrsta and o.get("vrsta_prometa") != vrsta:
                continue
            if opstina and o.get("opstina", "") != opstina:
                continue
            iznos = o.get("iznos_prometa", 0)
            if iznos < min_val or iznos > max_val:
                continue
            if datum_filter and datum_od_limit and datum_do_limit:
                datum = o.get("datum", "")
                if not datum or datum < datum_od_limit or datum > datum_do_limit:
                    continue

            prikaz = ""
            if o.get("datum"):
                try:
                    datum_od = datetime.datetime.strptime(o["datum"], "%Y-%m-%d").strftime("%d/%m/%Y")
                    datum_do = datetime.datetime.strptime(o.get("datum_do", o["datum"]), "%Y-%m-%d").strftime("%d/%m/%Y")
                    prikaz = datum_od + " - " + datum_do
                except ValueError:
                    prikaz = o["datum"]

            self.view.tree.insert("", "end", iid=str(o['id']),
                                  values=(o['id'], tipovi.get(o["vrsta_prometa"], "?"),
                                          o["identifikator"], o.get("ime_naziv", ""),
                                          o.get("opstina", ""), prikaz,
                                          format(o.get("iznos_prometa", 0), ",").replace(",", ".")))

    # ------------------------------------------------------------------
    # Dijalozi
    # ------------------------------------------------------------------
    def pretraga(self) -> None:
        """Otvara prozor za pretragu."""
        ProzorPretrage(self.view, self.db)

    def statistika(self) -> None:
        """Otvara prozor za statistiku."""
        ProzorStatistike(self.view, self.db)

    def pretraga_po_id(self) -> None:
        """Otvara pretragu sa identifikatorom iz selektovanog reda."""
        sel = self.view.tree.selection()
        if not sel:
            return
        values = self.view.tree.item(sel[0])['values']
        if len(values) > 2:
            identifikator = str(values[2])
            win = ProzorPretrage(self.view, self.db)
            win.kriterijum.set("identifikator")
            win.vrednost.delete(0, "end")
            win.vrednost.insert(0, identifikator)
            win.pretrazi()

    def otvori_podnosioca(self) -> None:
        """Otvara prozor za podatke o podnosiocu."""
        ProzorPodnosioca(self.view, self.db, self.view.godina)
        self.view.osvezi_info()

    def otvori_filtere(self) -> None:
        """Otvara prozor za napredne filtere."""
        ProzorFiltera(self.view, self.db, self.view.godina)

    def prikazi_about(self) -> None:
        """Prikazuje informacije o aplikaciji."""
        import sys
        import platform
        messagebox.showinfo("O aplikaciji",
                            "OPPSS Generator v15.7 GUI STANDALONE\n\n"
                            "Aplikacija za generisanje OOPSS prijava\n"
                            "za portal ePorezi (Poreska uprava RS)\n\n"
                            "Verzija: 15.7\n"
                            "Baza: SQLite\n"
                            "XSD šema: ugrađena\n\n"
                            "Python: " + sys.version.split()[0] + "\n"
                            "Platforma: " + platform.system())

    # ------------------------------------------------------------------
    # Export / generisanje
    # ------------------------------------------------------------------
    def export_csv(self) -> None:
        """Export podataka u CSV fajl."""
        fajl = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV fajlovi", "*.csv"), ("Svi fajlovi", "*.*")],
            initialfile=f"OPPS_{self.view.godina}.csv"
        )
        if fajl:
            self.db.export_csv(fajl)
            messagebox.showinfo("Export", f"CSV fajl sačuvan: {fajl}")

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
            self.view.osvezi_sve()
            messagebox.showinfo("Import", poruka)
        else:
            messagebox.showerror("Import", poruka)

    def export_html(self) -> None:
        """Generiše HTML izveštaj za štampu i otvara ga u pregledaču."""
        html = generisi_html_izvestaj(self.view, self.db, self.view.godina)

        fajl = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML fajlovi", "*.html"), ("Svi fajlovi", "*.*")],
            initialfile=f"OPPS_izvestaj_{self.view.godina}.html"
        )

        if fajl:
            with open(fajl, 'w', encoding='utf-8') as f:
                f.write(html)
            messagebox.showinfo("Izveštaj", f"Izveštaj sačuvan: {fajl}\n\nMožete ga otvoriti u pregledaču i štampati (Ctrl+P).")
            webbrowser.open(f"file://{os.path.abspath(fajl)}")

    def export_pdf(self) -> None:
        """Generiše pravi PDF izveštaj koristeći ReportLab."""
        fajl = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF fajlovi", "*.pdf"), ("Svi fajlovi", "*.*")],
            initialfile=f"OPPS_izvestaj_{self.view.godina}.pdf"
        )

        if fajl:
            try:
                generisi_pdf_izvestaj(self.db, self.view.godina, fajl)
                messagebox.showinfo("PDF izveštaj", f"PDF izveštaj sačuvan: {fajl}")
            except ImportError:
                messagebox.showerror("Greška", "ReportLab nije instaliran.\nInstalirajte: pip install reportlab")
            except Exception as e:
                messagebox.showerror("Greška", f"Greška pri generisanju PDF-a: {e}")

    def export_xml(self) -> None:
        """Generiše XML fajl za upload na ePorezi portal."""
        xml = generisi_xml(self.db, self.view.godina)

        fajl = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML fajlovi", "*.xml"), ("Svi fajlovi", "*.*")],
            initialfile=f"OPPS_prijava_{self.view.godina}.xml"
        )

        if fajl:
            with open(fajl, 'w', encoding='utf-8') as f:
                f.write(xml)
            messagebox.showinfo("XML izveštaj", f"XML fajl sačuvan: {fajl}\n\nMožete ga upload-ovati na portal ePorezi.")

    def generisi(self) -> None:
        """Generiše XML fajl iz baze podataka i čuva ga na disk."""
        xml = generisi_xml(self.db, self.view.godina)
        fajl = f"OPPS_prijava_{self.view.godina}.xml"
        with open(fajl, 'w', encoding='utf-8') as f:
            f.write(xml)
        messagebox.showinfo("XML generisan", f"XML fajl sačuvan: {fajl}\n\nMožete ga upload-ovati na portal ePorezi.")

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
        backup_file = os.path.join(backup_dir, f"baza_{self.view.godina}_backup_{timestamp}.db")

        try:
            self.db.zatvori()
            shutil.copy2(db_file, backup_file)
            self.db = Database(self.view._godina)
            self.view.db = self.db
            messagebox.showinfo("Backup", f"Backup uspešno kreiran:\n{backup_file}")
        except Exception as e:
            logger.error("Greška pri backup-u: %s", e)
            messagebox.showerror("Greška", f"Greška pri backup-u: {e}")
            self.db = Database(self.view._godina)
            self.view.db = self.db

    # ------------------------------------------------------------------
    # Undo / redo
    # ------------------------------------------------------------------
    def undo(self) -> None:
        """Poništava poslednju operaciju (Ctrl+Z)."""
        rezultat = self.undo_stack.undo(self.db)
        if rezultat:
            self.view.osvezi_sve()
            messagebox.showinfo("Undo", rezultat)
        else:
            messagebox.showinfo("Undo", "Nema operacija za poništavanje.")

    def redo(self) -> None:
        """Ponavlja poslednju poništenu operaciju (Ctrl+Y)."""
        rezultat = self.undo_stack.redo(self.db)
        if rezultat:
            self.view.osvezi_sve()
            messagebox.showinfo("Redo", rezultat)
        else:
            messagebox.showinfo("Redo", "Nema operacija za ponavljanje.")

    # ------------------------------------------------------------------
    # Drag & drop
    # ------------------------------------------------------------------
    def on_drop(self, event: tk.Event) -> None:
        """Obrada drag & drop XML fajla.

        Args:
            event: Tkinter event sa putanjom fajla.
        """
        try:
            putanja = event.data.strip()
            if putanja.startswith('{') and putanja.endswith('}'):
                putanja = putanja[1:-1]

            if not putanja.lower().endswith('.xml'):
                messagebox.showerror("Greška", "Fajl mora biti XML!")
                return

            from lxml import etree
            tree = etree.parse(putanja)
            root = tree.getroot()

            # Proveri da li je OPPSS struktura
            ns = "http://pid.purs.gov.rs"
            if root.tag != f"{{{ns}}}PoreskaDeklaracija":
                messagebox.showerror("Greška", "XML nije OPPSS struktura!")
                return

            # Učitaj podatke
            db = Database(self.view.godina)
            db.kreiraj_tabele()

            for prijava in root.findall(f"{{{ns}}}OPPPSSPrijava"):
                podaci = prijava.find(f"{{{ns}}}PodaciOPrijavi")
                if podaci is None:
                    continue

                # Podaci o podnosiocu
                podnosioc = podaci.find(f"{{{ns}}}PodaciOPodnosiocu")
                if podnosioc is not None:
                    pib = podnosioc.find(f"{{{ns}}}PIBJMBG")
                    email = podnosioc.find(f"{{{ns}}}EPostaPodnosioca")
                    telefon = podnosioc.find(f"{{{ns}}}TelefonPodnosioca")
                    jmbg = podnosioc.find(f"{{{ns}}}JMBGPodnosioca")
                    # Dodaj novog podnosioca iz XML-a i postavi kao aktivnog
                    novi_id = db.dodaj_podnosioca({
                        'naziv': 'Podnosilac (XML)',
                        'pib_jmbg': pib.text if pib is not None else '',
                        'email': email.text if email is not None else '',
                        'telefon': telefon.text if telefon is not None else '',
                        'jmbg': jmbg.text if jmbg is not None else '',
                    })
                    db.postavi_aktivnog(novi_id)

                # Podaci o prometu
                for promet in podaci.findall(f"{{{ns}}}PodaciOPrometu"):
                    vrsta_prometa = promet.find(f"{{{ns}}}VrstaPrometa")
                    vrsta_identifikatora = promet.find(f"{{{ns}}}VrstaIdentifikatora")
                    identifikator = promet.find(f"{{{ns}}}Identifikator")
                    ime_naziv = promet.find(f"{{{ns}}}ImeNaziv")
                    opstina = promet.find(f"{{{ns}}}Opstina")
                    adresa = promet.find(f"{{{ns}}}Adresa")
                    email_osobe = promet.find(f"{{{ns}}}EPosta")
                    telefon_osobe = promet.find(f"{{{ns}}}Telefon")
                    broj_gazdinstva = promet.find(f"{{{ns}}}BrojGazdinstva")
                    naziv_gazdinstva = promet.find(f"{{{ns}}}NazivGazdinstva")
                    datum = promet.find(f"{{{ns}}}Datum")
                    datum_do = promet.find(f"{{{ns}}}DatumDo")
                    iznos = promet.find(f"{{{ns}}}IznosPrometa")

                    db.dodaj_osobu({
                        'vrsta_prometa': vrsta_prometa.text if vrsta_prometa is not None else '1',
                        'vrsta_identifikatora': vrsta_identifikatora.text if vrsta_identifikatora is not None else '1',
                        'identifikator': identifikator.text if identifikator is not None else '',
                        'ime_naziv': ime_naziv.text if ime_naziv is not None else '',
                        'opstina': opstina.text if opstina is not None else '',
                        'adresa': adresa.text if adresa is not None else '',
                        'email_osobe': email_osobe.text if email_osobe is not None else '',
                        'telefon': telefon_osobe.text if telefon_osobe is not None else '',
                        'broj_gazdinstva': broj_gazdinstva.text if broj_gazdinstva is not None else '',
                        'naziv_gazdinstva': naziv_gazdinstva.text if naziv_gazdinstva is not None else '',
                        'datum': datum.text if datum is not None else '',
                        'datum_do': datum_do.text if datum_do is not None else '',
                        'iznos_prometa': int(iznos.text) if iznos is not None else 0,
                    })

            db.zatvori()
            self.view.osvezi_sve()
            messagebox.showinfo("Učitano", f"XML fajl učitan: {putanja}")

        except Exception as e:
            messagebox.showerror("Greška", f"Greška pri učitavanju XML-a: {e}")
