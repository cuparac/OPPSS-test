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
