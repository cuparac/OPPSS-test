"""GUI modul za OPPSS Generator.

Sadrži UndoStack klasu (privremeno, biće premeštena u controller.py).
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple

from model import Database


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


from view.main_window import MainWindow
