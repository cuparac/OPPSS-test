"""Database modul za OPPSS Generator.

Sadrži Database klasu za SQLite operacije i funkciju za migraciju JSON → SQLite.
"""

from __future__ import annotations

import csv
import datetime
import json
import logging
import os
import shutil
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from .validacije import konvertuj_datum


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
        self._auto_backup()

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
        """Kreira tabele ako ne postoje. Vrši migraciju ako je potrebno."""
        c = self.conn.cursor()

        # Migracija stare tabele podnosioc (godina PK -> id PK)
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='podnosioc'")
        if c.fetchone():
            c.execute("PRAGMA table_info(podnosioc)")
            columns = [row[1] for row in c.fetchall()]
            if 'godina' in columns and 'id' not in columns:
                # Stara struktura - migriraj
                c.execute("ALTER TABLE podnosioc RENAME TO podnosioc_stara")
                c.execute('''CREATE TABLE podnosioc (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    naziv TEXT NOT NULL,
                    pib_jmbg TEXT,
                    email TEXT,
                    telefon TEXT,
                    jmbg TEXT,
                    aktivan INTEGER DEFAULT 0
                )''')
                c.execute('''INSERT INTO podnosioc (naziv, pib_jmbg, email, telefon, jmbg, aktivan)
                             SELECT 'Podnosilac ' || godina, pib_jmbg, email, telefon, jmbg, 1 FROM podnosioc_stara''')
                c.execute("DROP TABLE podnosioc_stara")
                logging.info("Migracija tabele podnosioc: dodat id PK, naziv, aktivan")
        else:
            c.execute('''CREATE TABLE IF NOT EXISTS podnosioc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                naziv TEXT NOT NULL,
                pib_jmbg TEXT,
                email TEXT,
                telefon TEXT,
                jmbg TEXT,
                aktivan INTEGER DEFAULT 0
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
            iznos_prometa INTEGER
        )''')

        # Migracija: ranije je postojalo UNIQUE ograničenje na
        # (identifikator, datum, godina), zbog koga nisu mogla da postoje dva
        # ista unosa. Opcija "Dodaj kao novi" u prozoru za duplikat to zahteva,
        # pa se ograničenje uklanja prepisivanjem tabele.
        c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='ljudi'")
        red = c.fetchone()
        if red and red[0] and "UNIQUE" in red[0].upper():
            c.execute("ALTER TABLE ljudi RENAME TO ljudi_stara")
            c.execute('''CREATE TABLE ljudi (
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
                iznos_prometa INTEGER
            )''')
            c.execute('''INSERT INTO ljudi (id, godina, vrsta_prometa, vrsta_identifikatora,
                             identifikator, ime_naziv, opstina, adresa, email_osobe,
                             telefon, broj_gazdinstva, naziv_gazdinstva, datum, datum_do,
                             iznos_prometa)
                         SELECT id, godina, vrsta_prometa, vrsta_identifikatora,
                             identifikator, ime_naziv, opstina, adresa, email_osobe,
                             telefon, broj_gazdinstva, naziv_gazdinstva, datum, datum_do,
                             iznos_prometa
                         FROM ljudi_stara''')
            c.execute("DROP TABLE ljudi_stara")
            logging.info("Migracija tabele ljudi: uklonjeno UNIQUE ograničenje "
                         "(dozvoljeni isti identifikator i datum)")

        # Indeksi za bržu pretragu
        c.execute('CREATE INDEX IF NOT EXISTS idx_ljudi_godina ON ljudi(godina)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_ljudi_identifikator ON ljudi(identifikator)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_ljudi_datum ON ljudi(datum)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_ljudi_opstina ON ljudi(opstina)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_ljudi_vrsta_prometa ON ljudi(vrsta_prometa)')
        self.conn.commit()

    def _auto_backup(self) -> None:
        """Automatski backup baze pri pokretanju. Briše stari backup pre kreiranja novog."""
        try:
            if os.path.exists(self._db_file):
                # Obriši sve stare backup fajlove za ovu godinu
                import glob
                stari_backup = glob.glob(f"backup_baza_{self.godina}_*.db")
                for fajl in stari_backup:
                    try:
                        os.remove(fajl)
                        logging.info("Obrisan stari backup: %s", fajl)
                    except Exception as e:
                        logging.warning("Nije moguće obrisati stari backup %s: %s", fajl, e)

                # Kreiraj novi backup
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"backup_baza_{self.godina}_{timestamp}.db"
                shutil.copy2(self._db_file, backup_file)
                logging.info("Auto-backup baze: %s", backup_file)
        except Exception as e:
            logging.warning("Auto-backup nije uspeo: %s", e)

    def ucitaj_podnosioca(self, id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Učitava podatke o podnosiocu.

        Args:
            id: ID podnosioca. Ako None, vraća aktivnog podnosioca.

        Returns:
            Dict sa podacima o podnosiocu ili None
        """
        c = self.conn.cursor()
        if id is not None:
            c.execute("SELECT * FROM podnosioc WHERE id = ?", (id,))
        else:
            c.execute("SELECT * FROM podnosioc WHERE aktivan = 1 LIMIT 1")
        row = c.fetchone()
        if row:
            return dict(row)
        return None

    def ucitaj_sve_podnosioca(self) -> List[Dict[str, Any]]:
        """Učitava sve podnosiose.

        Returns:
            List sa svim podnosiocima
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM podnosioc ORDER BY id")
        return [dict(row) for row in c.fetchall()]

    def dodaj_podnosioca(self, podaci: Dict[str, str]) -> int:
        """Dodaje novog podnosioca.

        Args:
            podaci: Dict sa podacima (naziv, pib_jmbg, email, telefon, jmbg)

        Returns:
            ID novog podnosioca
        """
        c = self.conn.cursor()
        # Red se upisuje sa eksplicitnim id-jem = prvi slobodan broj, tako da se
        # id obrisanog podnosioca ponovo koristi (SQLite bi inače, zbog
        # AUTOINCREMENT, nastavio od najvećeg ikad upotrebljenog broja).
        # Kandidati: 1 (ako je slobodan) i svaki id+1 iza kog postoji rupa.
        c.execute('''INSERT INTO podnosioc (id, naziv, pib_jmbg, email, telefon, jmbg, aktivan)
                     VALUES ((SELECT COALESCE(MIN(k), 1) FROM (
                                 SELECT 1 AS k WHERE NOT EXISTS
                                     (SELECT 1 FROM podnosioc WHERE id = 1)
                                 UNION ALL
                                 SELECT id + 1 FROM podnosioc x WHERE NOT EXISTS
                                     (SELECT 1 FROM podnosioc y WHERE y.id = x.id + 1)
                             )),
                             ?, ?, ?, ?, ?, ?)''',
                  (podaci['naziv'], podaci['pib_jmbg'], podaci['email'],
                   podaci['telefon'], podaci['jmbg'], 0))
        self.conn.commit()
        if c.lastrowid is None:
            raise RuntimeError("Neuspešno dodavanje podnosioca")
        return c.lastrowid

    def sacuvaj_podnosioca(self, podaci: Dict[str, str], id: Optional[int] = None) -> None:
        """Čuva podatke o podnosiocu.

        Args:
            podaci: Dict sa podacima (naziv, pib_jmbg, email, telefon, jmbg)
            id: ID podnosioca. Ako None, ažurira aktivnog podnosioca.
        """
        c = self.conn.cursor()
        if id is not None:
            c.execute('''UPDATE podnosioc SET naziv=?, pib_jmbg=?, email=?, telefon=?, jmbg=?
                         WHERE id=?''',
                      (podaci['naziv'], podaci['pib_jmbg'], podaci['email'],
                       podaci['telefon'], podaci['jmbg'], id))
        else:
            c.execute('''UPDATE podnosioc SET naziv=?, pib_jmbg=?, email=?, telefon=?, jmbg=?
                         WHERE aktivan=1''',
                      (podaci['naziv'], podaci['pib_jmbg'], podaci['email'],
                       podaci['telefon'], podaci['jmbg']))
        self.conn.commit()

    def obrisi_podnosioca(self, id: int) -> None:
        """Briše podnosioca.

        Ako je obrisani podnosilac bio aktivan, prvi preostali postaje aktivan —
        bez toga baza ostaje bez aktivnog podnosioca i generisanje XML prijave
        prijavljuje da podnosilac nije registrovan iako postoji.

        Args:
            id: ID podnosioca
        """
        c = self.conn.cursor()
        c.execute("SELECT aktivan FROM podnosioc WHERE id = ?", (id,))
        red = c.fetchone()
        c.execute("DELETE FROM podnosioc WHERE id = ?", (id,))
        if red is not None and red[0] == 1:
            c.execute("SELECT MIN(id) FROM podnosioc")
            sledeci = c.fetchone()[0]
            if sledeci is not None:
                c.execute("UPDATE podnosioc SET aktivan = 1 WHERE id = ?", (sledeci,))
        self.conn.commit()

    def postavi_aktivnog(self, id: int) -> None:
        """Postavlja aktivnog podnosioca.

        Args:
            id: ID podnosioca
        """
        c = self.conn.cursor()
        c.execute("UPDATE podnosioc SET aktivan = 0")
        c.execute("UPDATE podnosioc SET aktivan = 1 WHERE id = ?", (id,))
        self.conn.commit()

    def ucitaj_ljude(self) -> List[Dict[str, Any]]:
        """Učitava sve unose za trenutnu godinu.

        Returns:
            List sa svim unosima
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM ljudi WHERE godina = ? ORDER BY id", (self.godina,))
        return [dict(row) for row in c.fetchall()]

    def ucitaj_ljude_stranicu(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Učitava stranicu unosa za trenutnu godinu (lazy loading).

        Args:
            offset: Početni redni broj (0-based).
            limit: Broj unosa po stranici.

        Returns:
            List sa unosima za traženu stranicu
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM ljudi WHERE godina = ? ORDER BY id LIMIT ? OFFSET ?",
                  (self.godina, limit, offset))
        return [dict(row) for row in c.fetchall()]

    def broj_unosa(self) -> int:
        """Vraća ukupan broj unosa za trenutnu godinu.

        Returns:
            Ukupan broj unosa
        """
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM ljudi WHERE godina = ?", (self.godina,))
        return c.fetchone()[0]

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

    def pronadji_po_identifikatoru(self, identifikator: str) -> Optional[Dict[str, Any]]:
        """Vraća poslednji unet unos sa datim identifikatorom (JMBG/PIB/EBS).

        Koristi se za popunjavanje forme kod ponovnog unosa iste osobe: dovoljno
        je ukucati JMBG, a ostali podaci se prepišu iz prethodnog unosa — datumi
        i iznos ostaju da se unesu za novi period.

        Args:
            identifikator: JMBG/PIB/EBS.

        Returns:
            Dict sa poslednjim takvim unosom ili None.
        """
        c = self.conn.cursor()
        c.execute('''SELECT * FROM ljudi WHERE identifikator = ? AND godina = ?
                     ORDER BY id DESC LIMIT 1''',
                  (identifikator, self.godina))
        row = c.fetchone()
        if row:
            return dict(row)
        return None

    def ima_duplikat(self, identifikator: str, datum: str) -> Optional[Dict[str, Any]]:
        """Proverava da li već postoji unos sa istim identifikatorom i datumom.

        Args:
            identifikator: JMBG/PIB/EBS
            datum: Datum u ISO formatu (YYYY-MM-DD)

        Returns:
            Dict sa postojećim unosom ili None
        """
        c = self.conn.cursor()
        c.execute('''SELECT * FROM ljudi WHERE identifikator = ? AND datum = ? AND godina = ?''',
                  (identifikator, datum, self.godina))
        row = c.fetchone()
        if row:
            return dict(row)
        return None

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

    def pretrazi_po(self, kriterijum: str, vrednost: str) -> List[Dict[str, Any]]:
        """Pretražuje unose po imenovanom kriterijumu iz ProzorPretrage.

        Kriterijumi dijaloga nisu imena kolona u bazi ('ime' -> ime_naziv,
        'iznos_od' -> iznos_prometa >= ...), pa se ovde prevode u SQL uslov i
        parametre. Bez ovog prevoda pretraga je pucala sa
        ``no such column: ime`` / ``Incorrect number of bindings``.

        Args:
            kriterijum: "opstina", "ime", "identifikator", "iznos_od",
                "iznos_do", "datum_od" ili "datum_do".
            vrednost: Uneta vrednost.

        Returns:
            List sa rezultatima.
        """
        vrednost = (vrednost or "").strip()
        if kriterijum == "opstina":
            return self.pretraga("opstina LIKE ?", [f"%{vrednost}%"])
        if kriterijum == "ime":
            return self.pretraga("ime_naziv LIKE ?", [f"%{vrednost}%"])
        if kriterijum == "identifikator":
            return self.pretraga("identifikator LIKE ?", [f"%{vrednost}%"])
        if kriterijum in ("iznos_od", "iznos_do"):
            try:
                broj = int(vrednost)
            except ValueError:
                return []
            if kriterijum == "iznos_od":
                return self.pretraga("iznos_prometa >= ?", [broj])
            return self.pretraga("iznos_prometa <= ?", [broj])
        if kriterijum in ("datum_od", "datum_do"):
            # datumi se u bazi čuvaju kao ISO (YYYY-MM-DD)
            try:
                datum = konvertuj_datum(vrednost)
            except ValueError:
                return []
            if kriterijum == "datum_od":
                return self.pretraga("datum >= ?", [datum])
            return self.pretraga("datum <= ?", [datum])
        # Nepoznat kriterijum — pretraži po identifikatoru (bezbedan fallback)
        return self.pretraga("identifikator LIKE ?", [f"%{vrednost}%"])

    def statistika(self) -> Dict[str, Any]:
        """Vraća statistiku za trenutnu godinu.

        Returns:
            Dict sa statistikom: ukupno, ukupan_iznos, po_opstini i po_vrsti_prometa
            (obe grupacije kao lista reči sa ključevima 'opstina'/'vrsta_prometa',
            'broj' i 'iznos', spremna za prikaz u ProzorStatistike)
        """
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*), COALESCE(SUM(iznos_prometa), 0) FROM ljudi WHERE godina = ?",
                  (self.godina,))
        row = c.fetchone()
        ukupno = row[0]
        ukupan_iznos = row[1]

        c.execute("SELECT opstina, COUNT(*), COALESCE(SUM(iznos_prometa), 0) FROM ljudi "
                  "WHERE godina = ? GROUP BY opstina ORDER BY opstina",
                  (self.godina,))
        po_opstini = [{'opstina': r[0] or "Bez opštine", 'broj': r[1], 'iznos': r[2]}
                      for r in c.fetchall()]

        c.execute("SELECT vrsta_prometa, COUNT(*), COALESCE(SUM(iznos_prometa), 0) FROM ljudi "
                  "WHERE godina = ? GROUP BY vrsta_prometa ORDER BY vrsta_prometa",
                  (self.godina,))
        po_vrsti_prometa = [{'vrsta_prometa': r[0], 'broj': r[1], 'iznos': r[2]}
                            for r in c.fetchall()]

        return {
            'ukupno': ukupno,
            'ukupan_iznos': ukupan_iznos,
            'po_opstini': po_opstini,
            'po_vrsti_prometa': po_vrsti_prometa,
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
            p = data['podnosioc']
            db.dodaj_podnosioca({
                'naziv': f"Podnosilac {godina}",
                'pib_jmbg': p.get('pib_jmbg', ''),
                'email': p.get('email', ''),
                'telefon': p.get('telefon', ''),
                'jmbg': p.get('jmbg', ''),
            })
            # Postavi prvog podnosioca kao aktivnog
            podnosioci = db.ucitaj_sve_podnosioca()
            if podnosioci:
                db.postavi_aktivnog(podnosioci[0]['id'])

        for osoba in data.get('ljudi', []):
            db.dodaj_osobu(osoba)

        db.zatvori()
        os.rename(json_file, f"{json_file}.backup")
        return (True, "Migracija uspešno završena.")
    except Exception as e:
        return (False, f"Greška pri migraciji: {e}")
