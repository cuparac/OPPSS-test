"""Widget komponente za view layer."""

from __future__ import annotations

import datetime
from typing import Any, Optional

import tkinter as tk
from tkinter import ttk

from model.validacije import konvertuj_datum, TELEFON_DOZVOLJENI_ZNAKOVI


def ocisti_telefon_unos(original: str) -> str:
    """Uklanja nedozvoljene znakove iz sadržaja polja za telefon.

    Ostavlja cifre, razmak, ``+``, ``-`` i ``/`` (radi lakšeg kucanja); sve
    ostalo (slova, interpunkcija) se uklanja. Pri snimanju se od ovoga
    zadržavaju samo cifre (vidi ``model.telefon_cifre``).

    Args:
        original: Trenutni sadržaj polja.

    Returns:
        Očišćen sadržaj polja.
    """
    return "".join(c for c in (original or "") if c in TELEFON_DOZVOLJENI_ZNAKOVI)


def vezi_samo_cifre_telefon(polje: tk.Entry) -> None:
    """Vezuje ``<KeyRelease>`` na polje telefona: uklanja nedozvoljene znakove.

    Zadržava poziciju kursora (umanjenu za broj uklonjenih znakova ispred
    njega), tako da kucanje usred broja ne skače na kraj polja.

    Args:
        polje: ``ttk.Entry`` widget za broj telefona.
    """
    def _ocisti(ev: Optional[tk.Event] = None) -> None:
        original = polje.get()
        ocisceno = ocisti_telefon_unos(original)
        if ocisceno != original:
            # Novi polozaj kursora = broj dozvoljenih znakova levo od njega,
            # pa kucanje usred broja ne skace na kraj polja.
            poz = polje.index("insert")
            novo = len(ocisti_telefon_unos(original[:poz]))
            polje.delete(0, "end")
            polje.insert(0, ocisceno)
            polje.icursor(novo)

    polje.bind("<KeyRelease>", _ocisti, add="+")


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
