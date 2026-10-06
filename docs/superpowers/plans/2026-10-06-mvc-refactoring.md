# MVC Refaktoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Razdvojiti gui.py na Model, View i Controller slojeve

**Architecture:** Minimalni MVC - Model (baza, validacije, XML), View (GUI komponente), Controller (logika)

**Tech Stack:** Python 3.6+, tkinter, SQLite, lxml, matplotlib, reportlab

**Spec:** docs/superpowers/specs/2026-10-06-mvc-refactoring-design.md

## Global Constraints

- Python 3.6+ compatibility
- tkinter za GUI
- SQLite za bazu
- lxml za XML
- matplotlib za grafikone
- reportlab za PDF
- Grana: mvc-preview
- Ne menjati CLI verziju

---

### Task 1: Model Layer Setup

**Files:**
- Create: `model/__init__.py`
- Move: `database.py` → `model/database.py`
- Move: `validacije.py` → `model/validacije.py`
- Move: `xml_generator.py` → `model/xml_generator.py`

**Interfaces:**
- Consumes: nothing
- Produces: `model.database.Database`, `model.validacije`, `model.xml_generator`

- [ ] **Step 1: Create model/ folder**

```bash
mkdir -p model
```

- [ ] **Step 2: Move database.py to model/**

```bash
git mv database.py model/database.py
```

- [ ] **Step 3: Move validacije.py to model/**

```bash
git mv validacije.py model/validacije.py
```

- [ ] **Step 4: Move xml_generator.py to model/**

```bash
git mv xml_generator.py model/xml_generator.py
```

- [ ] **Step 5: Create model/__init__.py**

```python
"""Model layer - baza, validacije, XML generator."""
from .database import Database, migriraj_json_u_sqlite
from .validacije import validan_jmbg, validan_ebs, konvertuj_datum, get_xsd_schema
from .xml_generator import generisi_xml, generisi_html_izvestaj, generisi_pdf_izvestaj

__all__ = [
    'Database', 'migriraj_json_u_sqlite',
    'validan_jmbg', 'validan_ebs', 'konvertuj_datum', 'get_xsd_schema',
    'generisi_xml', 'generisi_html_izvestaj', 'generisi_pdf_izvestaj',
]
```

- [ ] **Step 6: Test import**

```bash
python -c "from model import Database, validan_jmbg, generisi_xml; print('OK')"
```

Expected: OK

- [ ] **Step 7: Commit**

```bash
git add model/
git commit -m "refactor: prebaceni model fajlovi u model/ folder"
```

---

### Task 2: View Widgets Extraction

**Files:**
- Create: `view/__init__.py`
- Create: `view/widgets.py`
- Modify: `gui.py` (remove widget classes)

**Interfaces:**
- Consumes: nothing
- Produces: `view.widgets.DatumEntry`, `view.widgets.Kalendar`

- [ ] **Step 1: Create view/ folder**

```bash
mkdir -p view
```

- [ ] **Step 2: Create view/__init__.py**

```python
"""View layer - GUI komponente."""
```

- [ ] **Step 3: Extract DatumEntry and Kalendar to view/widgets.py**

Copy classes `DatumEntry` and `Kalendar` from `gui.py` to `view/widgets.py`. Add necessary imports.

- [ ] **Step 4: Test import**

```bash
python -c "from view.widgets import DatumEntry, Kalendar; print('OK')"
```

Expected: OK

- [ ] **Step 5: Commit**

```bash
git add view/
git commit -m "refactor: izdvojeni widget-i u view/widgets.py"
```

---

### Task 3: View Dialogs Extraction

**Files:**
- Create: `view/dialogs.py`
- Modify: `gui.py` (remove dialog classes)

**Interfaces:**
- Consumes: `view.widgets.DatumEntry`, `view.widgets.Kalendar`
- Produces: `view.dialogs.ProzorPodnosioca`, `view.dialogs.ProzorFiltera`, `view.dialogs.ProzorPretrage`, `view.dialogs.ProzorStatistike`, `view.dialogs.ProzorUnosa`

- [ ] **Step 1: Extract dialog classes to view/dialogs.py**

Copy classes `ProzorPodnosioca`, `ProzorFiltera`, `ProzorPretrage`, `ProzorStatistike`, `ProzorUnosa` from `gui.py` to `view/dialogs.py`. Add necessary imports.

- [ ] **Step 2: Test import**

```bash
python -c "from view.dialogs import ProzorPodnosioca, ProzorFiltera; print('OK')"
```

Expected: OK

- [ ] **Step 3: Commit**

```bash
git add view/dialogs.py
git commit -m "refactor: izdvojeni prozori u view/dialogs.py"
```

---

### Task 4: View Main Window Extraction

**Files:**
- Create: `view/main_window.py`
- Modify: `gui.py` (remove App class)

**Interfaces:**
- Consumes: `view.widgets`, `view.dialogs`
- Produces: `view.main_window.MainWindow`

- [ ] **Step 1: Extract App class to view/main_window.py**

Copy class `App` from `gui.py` to `view/main_window.py` as `MainWindow`. Add necessary imports.

- [ ] **Step 2: Test import**

```bash
python -c "from view.main_window import MainWindow; print('OK')"
```

Expected: OK

- [ ] **Step 3: Commit**

```bash
git add view/main_window.py
git commit -m "refactor: izdvojena MainWindow u view/main_window.py"
```

---

### Task 5: Controller Creation

**Files:**
- Create: `controller.py`
- Modify: `gui.py` (remove all logic)

**Interfaces:**
- Consumes: `model`, `view`
- Produces: `controller.Controller`

- [ ] **Step 1: Create controller.py with Controller class**

Create `controller.py` with `Controller` class that:
- Takes `model` and `view` as dependencies
- Contains all business logic from `App`
- Contains `UndoStack`
- Methods: `dodaj_osobu()`, `izmeni_osobu()`, `obrisi_osobu()`, etc.

- [ ] **Step 2: Test import**

```bash
python -c "from controller import Controller; print('OK')"
```

Expected: OK

- [ ] **Step 3: Commit**

```bash
git add controller.py
git commit -m "refactor: kreiran controller.py sa logikom"
```

---

### Task 6: Entry Point Update

**Files:**
- Create: `opps_generator_gui_v16.py`
- Modify: `opps_generator_gui_v15.9.py` (keep for reference)

**Interfaces:**
- Consumes: `controller.Controller`, `view.main_window.MainWindow`, `model.database.Database`
- Produces: runnable application

- [ ] **Step 1: Create opps_generator_gui_v16.py**

```python
"""OPPSS Generator v16 GUI - Entry point (MVC)."""

from __future__ import annotations

import logging
import os
import sys
import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('opps_generator.log'),
        logging.StreamHandler()
    ]
)

from model.database import Database
from view.main_window import MainWindow
from controller import Controller

if __name__ == "__main__":
    logging.info("OPPSS Generator v16 (MVC) pokrenut")
    
    db = Database(str(datetime.date.today().year))
    view = MainWindow()
    controller = Controller(db, view)
    view.set_controller(controller)
    
    view.mainloop()
```

- [ ] **Step 2: Test application startup**

```bash
python opps_generator_gui_v16.py
```

Expected: Application starts without errors

- [ ] **Step 3: Commit**

```bash
git add opps_generator_gui_v16.py
git commit -m "feat: kreiran v16 entry point sa MVC arhitekturom"
```

---

### Task 7: Integration Testing

**Files:**
- Test: manual testing of all features

**Interfaces:**
- Consumes: all previous tasks
- Produces: working application

- [ ] **Step 1: Test CRUD operations**

- [ ] Dodaj novi unos
- [ ] Izmeni postojeći unos
- [ ] Obriši unos
- [ ] Obriši sve unose

- [ ] **Step 2: Test search and filters**

- [ ] Pretraga po opštini, imenu, identifikatoru, iznosu
- [ ] Filter po vrsti prometa, opštini, datumu

- [ ] **Step 3: Test export**

- [ ] Export CSV
- [ ] Export HTML
- [ ] Export PDF
- [ ] Export XML

- [ ] **Step 4: Test undo/redo**

- [ ] Ctrl+Z (undo)
- [ ] Ctrl+Y (redo)

- [ ] **Step 5: Test podnosioc**

- [ ] Izbor podnosioca
- [ ] Brisanje podnosioca

- [ ] **Step 6: Test dark theme**

- [ ] Uključi dark theme
- [ ] Isključi dark theme

- [ ] **Step 7: Test tabovi i grafikoni**

- [ ] Svi unosi tab
- [ ] Po opštini tab
- [ ] Po vrsti prometa tab
- [ ] Po datumu tab
- [ ] Grafikoni tab

- [ ] **Step 8: Test paginacija**

- [ ] Prva strana
- [ ] Prethodna strana
- [ ] Sledeća strana
- [ ] Poslednja strana

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "test: integraciono testiranje MVC verzije"
```
