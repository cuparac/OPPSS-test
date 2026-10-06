"""GUI modul za OPPSS Generator (backward-compatibility shim).

``UndoStack`` i ``MainWindow`` su premešteni u MVC slojeve:

- ``UndoStack`` → ``controller.py``
- ``MainWindow`` → ``view/main_window.py``

Ovaj modul ostaje samo radi nazadne kompatibilnosti (``from gui import ...``).
"""

from __future__ import annotations

from controller import UndoStack
from view.main_window import MainWindow

__all__ = ["UndoStack", "MainWindow"]
