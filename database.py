"""Database modul za OPPSS Generator.

Sadrži Database klasu za SQLite operacije i funkciju za migraciju JSON → SQLite.
"""

from __future__ import annotations

import csv
import datetime
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional


class Database:
    """SQLite baza podataka za OPPSS Generator.

    Attributes:
        godina: Godina kao string (npr. "2026")
        db_file: Putanja do SQLite fajla
        conn: SQLite konekcija
    """

    def __init__(self, godina: str) -> None:
        """Inicijalizuje Database.

        Args:
            godina: Godina kao string (npr. "2026")
        """
        self.godina = godina
        self._db_file = f"baza_{godina}.db"
        self.conn = sqlite3.connect(self._db_file)
        self.conn.row_factory = sqlite3.Row
        self.kreiraj_tabele()

    @property
    def db_file(self) -> str:
        """Putanja do SQLite fajla."""
        return self._db_file

    @db_file.setter
    def db_file(self, putanja: str) -> None:
        """Postavlja putanju do SQLite fajla i ponovo se povezuje.

        Args:
            putanja: Nova putanja do SQLite fajla
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        self._db_file = putanja
        self.conn = sqlite3.connect(putanja)
        self.conn.row_factory = sqlite3.Row

    def kreiraj_tabele(self) -> None:
        """Kreira tabele ako ne postoje."""
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS podnosioc (
            godina TEXT PRIMARY KEY,
            pib_jmbg TEXT,
            email TEXT,
            telefon TEXT,
            jmbg TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ljudi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            godina TEXT,
            vrsta_prometa TEXT,
            vrsta_identifikatora TEXT,
            identifikator TEXT,
            ime_naziv TEXT,
            opstina TEXT,
            adresa TEXT,
            email_osobe TEXT,
            telefon TEXT,
            broj_gazdinstva TEXT,
            naziv_gazdinstva TEXT,
            datum TEXT,
            datum_do TEXT,
            iznos_prometa INTEGER,
            FOREIGN KEY (godina) REFERENCES podnosioc(godina)
        )''')
        self.conn.commit()

    def ucitaj_podnosioca(self) -> Optional[Dict[str, str]]:
        """Učitava podatke o podnosiocu.

        Returns:
            Dict sa podacima o podnosiocu ili None
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM podnosioc WHERE godina = ?", (self.godina,))
        row = c.fetchone()
        if row:
            return dict(row)
        return None

    def sacuvaj_podnosioca(self, podaci: Dict[str, str]) -> None:
        """Čuva podatke o podnosiocu.

        Args:
            podaci: Dict sa podacima (pib_jmbg, email, telefon, jmbg)
        """
        c = self.conn.cursor()
        c.execute('''INSERT OR REPLACE INTO podnosioc (godina, pib_jmbg, email, telefon, jmbg)
                     VALUES (?, ?, ?, ?, ?)''',
                  (self.godina, podaci['pib_jmbg'], podaci['email'],
                   podaci['telefon'], podaci['jmbg']))
        self.conn.commit()

    def ucitaj_ljude(self) -> List[Dict[str, Any]]:
        """Učitava sve unose za trenutnu godinu.

        Returns:
            List sa svim unosima
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM ljudi WHERE godina = ? ORDER BY id", (self.godina,))
        return [dict(row) for row in c.fetchall()]

    def dodaj_osobu(self, podaci: Dict[str, Any]) -> None:
        """Dodaje novi unos.

        Args:
            podaci: Dict sa podacima o osobi
        """
        c = self.conn.cursor()
        c.execute('''INSERT INTO ljudi (godina, vrsta_prometa, vrsta_identifikatora,
                     identifikator, ime_naziv, opstina, adresa, email_osobe,
                     telefon, broj_gazdinstva, naziv_gazdinstva, datum, datum_do, iznos_prometa)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (self.godina, podaci['vrsta_prometa'], podaci['vrsta_identifikatora'],
                   podaci['identifikator'], podaci['ime_naziv'], podaci['opstina'],
                   podaci['adresa'], podaci.get('email_osobe', ''), podaci['telefon'],
                   podaci.get('broj_gazdinstva', ''), podaci.get('naziv_gazdinstva', ''),
                   podaci['datum'], podaci['datum_do'], podaci['iznos_prometa']))
        self.conn.commit()

    def izmeni_osobu(self, id: int, podaci: Dict[str, Any]) -> None:
        """Menja postojeći unos.

        Args:
            id: ID unosa
            podaci: Dict sa novim podacima
        """
        c = self.conn.cursor()
        c.execute('''UPDATE ljudi SET vrsta_prometa=?, vrsta_identifikatora=?,
                     identifikator=?, ime_naziv=?, opstina=?, adresa=?,
                     email_osobe=?, telefon=?, broj_gazdinstva=?, naziv_gazdinstva=?,
                     datum=?, datum_do=?, iznos_prometa=? WHERE id=?''',
                  (podaci['vrsta_prometa'], podaci['vrsta_identifikatora'],
                   podaci['identifikator'], podaci['ime_naziv'], podaci['opstina'],
                   podaci['adresa'], podaci.get('email_osobe', ''), podaci['telefon'],
                   podaci.get('broj_gazdinstva', ''), podaci.get('naziv_gazdinstva', ''),
                   podaci['datum'], podaci['datum_do'], podaci['iznos_prometa'], id))
        self.conn.commit()

    def obrisi_osobu(self, id: int) -> None:
        """Briše unos.

        Args:
            id: ID unosa
        """
        c = self.conn.cursor()
        c.execute("DELETE FROM ljudi WHERE id = ?", (id,))
        self.conn.commit()

    def obrisi_sve(self) -> int:
        """Briše sve unose za trenutnu godinu.

        Returns:
            Broj obrisanih unosa
        """
        c = self.conn.cursor()
        c.execute("DELETE FROM ljudi WHERE godina = ?", (self.godina,))
        broj = c.rowcount
        self.conn.commit()
        return broj

    def pretraga(self, uslov: str, parametri: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Pretražuje unose.

        Args:
            uslov: SQL WHERE uslov
            parametri: Lista parametara

        Returns:
            List sa rezultatima
        """
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM ljudi WHERE godina = ? AND {uslov}",
                  (self.godina, *(parametri or [])))
        return [dict(row) for row in c.fetchall()]

    def statistika(self) -> Dict[str, Any]:
        """Vraća statistiku za trenutnu godinu.

        Returns:
            Dict sa statistikom (ukupno, ukupan_iznos, po_opstini, po_vrsti_prometa)
        """
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*), COALESCE(SUM(iznos_prometa), 0) FROM ljudi WHERE godina = ?",
                  (self.godina,))
        row = c.fetchone()
        ukupno = row[0]
        ukupan_iznos = row[1]

        c.execute("SELECT opstina, COUNT(*), SUM(iznos_prometa) FROM ljudi WHERE godina = ? GROUP BY opstina",
                  (self.godina,))
        po_opstini = {r[0]: {'broj': r[1], 'iznos': r[2]} for r in c.fetchall()}

        c.execute("SELECT vrsta_prometa, COUNT(*), SUM(iznos_prometa) FROM ljudi WHERE godina = ? GROUP BY vrsta_prometa",
                  (self.godina,))
        po_vrsti_prometa = {r[0]: {'broj': r[1], 'iznos': r[2]} for r in c.fetchall()}

        return {
            'ukupno': ukupno,
            'ukupan_iznos': ukupan_iznos,
            'po_opstini': po_opstini,
            'po_vrsti_prometa': po_vrsti_prometa
        }

    def export_csv(self, fajl_putanja: str) -> None:
        """Izvozi podatke u CSV fajl.

        Args:
            fajl_putanja: Putanja do CSV fajla
        """
        ljudi = self.ucitaj_ljude()
        if not ljudi:
            return

        with open(fajl_putanja, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=ljudi[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(ljudi)

    def import_csv(self, fajl_putanja: str) -> tuple:
        """Uvozi podatke iz CSV fajla.

        Args:
            fajl_putanja: Putanja do CSV fajla

        Returns:
            Tuple (uspeh: bool, poruka: str, broj: int)
        """
        broj = 0
        try:
            with open(fajl_putanja, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    # Konvertuj datum u ISO format
                    for polje in ['datum', 'datum_do']:
                        if polje in row and row[polje]:
                            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d.%m.%Y']:
                                try:
                                    row[polje] = datetime.datetime.strptime(row[polje].strip(), fmt).strftime('%Y-%m-%d')
                                    break
                                except ValueError:
                                    continue

                    # Konvertuj iznos u int
                    if 'iznos_prometa' in row:
                        row['iznos_prometa'] = int(row['iznos_prometa'])

                    self.dodaj_osobu(row)
                    broj += 1
            return (True, f"Uvezeno {broj} unosa.", broj)
        except Exception as e:
            return (False, f"Greška pri uvozu: {e}", 0)

    def zatvori(self) -> None:
        """Zatvara konekciju sa bazom."""
        if self.conn:
            self.conn.close()


def migriraj_json_u_sqlite(godina: str) -> tuple:
    """Migrira JSON bazu u SQLite.

    Args:
        godina: Godina za koju se vrši migracija

    Returns:
        Tuple (uspeh: bool, poruka: str)
    """
    json_file = f"baza_{godina}.json"
    if not os.path.exists(json_file):
        return (False, "Nema JSON fajla za migraciju.")

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        db = Database(godina)
        db.kreiraj_tabele()

        if 'podnosioc' in data:
            db.sacuvaj_podnosioca(data['podnosioc'])

        for osoba in data.get('ljudi', []):
            db.dodaj_osobu(osoba)

        db.zatvori()
        os.rename(json_file, f"{json_file}.backup")
        return (True, "Migracija uspešno završena.")
    except Exception as e:
        return (False, f"Greška pri migraciji: {e}")
