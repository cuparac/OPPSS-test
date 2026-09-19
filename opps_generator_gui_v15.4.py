"""OPPSS Generator v15.3 GUI - Entry point.

Pokreće se sa: python opps_generator_gui_v15.3.py
"""

from __future__ import annotations

import logging
import os
import sys

# Konfiguracija logginga
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('opps_generator.log'),
        logging.StreamHandler()
    ]
)

from gui import App

if __name__ == "__main__":
    logging.info("OPPSS Generator v15.4 pokrenut")
    app = App()
    app.mainloop()
