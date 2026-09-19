import pytest
import os
from database import Database, migriraj_json_u_sqlite


@pytest.fixture
def db(tmp_path):
    """Privremena baza za testove."""
    database = Database("2026")
    database.db_file = str(tmp_path / "test.db")
    database.kreiraj_tabele()
    yield database
    database.zatvori()


class TestDatabaseCRUD:
    def test_kreiraj_tabele(self, db):
        assert db.conn is not None

    def test_dodaj_osobu(self, db):
        podaci = {
            'vrsta_prometa': '1',
            'vrsta_identifikatora': '1',
            'identifikator': '2212994740010',
            'ime_naziv': 'Test Osoba',
            'opstina': 'Leskovac',
            'adresa': 'Test Adresa 1',
            'telefon': '0651234567',
            'datum': '2026-09-19',
            'datum_do': '2026-09-19',
            'iznos_prometa': 1000
        }
        db.dodaj_osobu(podaci)
        ljudi = db.ucitaj_ljude()
        assert len(ljudi) == 1
        assert ljudi[0]['ime_naziv'] == 'Test Osoba'

    def test_izmeni_osobu(self, db):
        podaci = {
            'vrsta_prometa': '1',
            'vrsta_identifikatora': '1',
            'identifikator': '2212994740010',
            'ime_naziv': 'Test Osoba',
            'opstina': 'Leskovac',
            'adresa': 'Test Adresa 1',
            'telefon': '0651234567',
            'datum': '2026-09-19',
            'datum_do': '2026-09-19',
            'iznos_prometa': 1000
        }
        db.dodaj_osobu(podaci)
        ljudi = db.ucitaj_ljude()
        id_osobe = ljudi[0]['id']

        podaci['ime_naziv'] = 'Izmenjena Osoba'
        db.izmeni_osobu(id_osobe, podaci)
        ljudi = db.ucitaj_ljude()
        assert ljudi[0]['ime_naziv'] == 'Izmenjena Osoba'

    def test_obrisi_osobu(self, db):
        podaci = {
            'vrsta_prometa': '1',
            'vrsta_identifikatora': '1',
            'identifikator': '2212994740010',
            'ime_naziv': 'Test Osoba',
            'opstina': 'Leskovac',
            'adresa': 'Test Adresa 1',
            'telefon': '0651234567',
            'datum': '2026-09-19',
            'datum_do': '2026-09-19',
            'iznos_prometa': 1000
        }
        db.dodaj_osobu(podaci)
        ljudi = db.ucitaj_ljude()
        id_osobe = ljudi[0]['id']
        db.obrisi_osobu(id_osobe)
        ljudi = db.ucitaj_ljude()
        assert len(ljudi) == 0


class TestDatabasePretraga:
    def test_pretraga_po_imenu(self, db):
        podaci = {
            'vrsta_prometa': '1',
            'vrsta_identifikatora': '1',
            'identifikator': '2212994740010',
            'ime_naziv': 'Milan Jankovic',
            'opstina': 'Leskovac',
            'adresa': 'Stanoja Glavasa 33',
            'telefon': '0652235790',
            'datum': '2026-09-09',
            'datum_do': '2026-09-09',
            'iznos_prometa': 10
        }
        db.dodaj_osobu(podaci)
        rezultati = db.pretraga("ime_naziv LIKE ?", ["%Milan%"])
        assert len(rezultati) == 1

    def test_pretraga_po_opstini(self, db):
        podaci = {
            'vrsta_prometa': '1',
            'vrsta_identifikatora': '1',
            'identifikator': '2212994740010',
            'ime_naziv': 'Test',
            'opstina': 'Leskovac',
            'adresa': 'Adresa',
            'telefon': '0651234567',
            'datum': '2026-09-19',
            'datum_do': '2026-09-19',
            'iznos_prometa': 100
        }
        db.dodaj_osobu(podaci)
        rezultati = db.pretraga("opstina = ?", ["Leskovac"])
        assert len(rezultati) == 1


class TestDatabaseStatistika:
    def test_statistika(self, db):
        podaci = {
            'vrsta_prometa': '1',
            'vrsta_identifikatora': '1',
            'identifikator': '2212994740010',
            'ime_naziv': 'Test',
            'opstina': 'Leskovac',
            'adresa': 'Adresa',
            'telefon': '0651234567',
            'datum': '2026-09-19',
            'datum_do': '2026-09-19',
            'iznos_prometa': 100
        }
        db.dodaj_osobu(podaci)
        stat = db.statistika()
        assert stat['ukupno'] == 1
        assert stat['ukupan_iznos'] == 100


class TestDatabaseCSV:
    def test_export_csv(self, db, tmp_path):
        podaci = {
            'vrsta_prometa': '1',
            'vrsta_identifikatora': '1',
            'identifikator': '2212994740010',
            'ime_naziv': 'Test',
            'opstina': 'Leskovac',
            'adresa': 'Adresa',
            'telefon': '0651234567',
            'datum': '2026-09-19',
            'datum_do': '2026-09-19',
            'iznos_prometa': 100
        }
        db.dodaj_osobu(podaci)
        csv_file = str(tmp_path / "test.csv")
        db.export_csv(csv_file)
        assert os.path.exists(csv_file)

    def test_import_csv(self, db, tmp_path):
        csv_file = str(tmp_path / "import.csv")
        with open(csv_file, 'w', encoding='utf-8-sig') as f:
            f.write("vrsta_prometa;vrsta_identifikatora;identifikator;ime_naziv;opstina;adresa;telefon;datum;datum_do;iznos_prometa\n")
            f.write("1;1;2212994740010;Test;Leskovac;Adresa;0651234567;2026-09-19;2026-09-19;100\n")
        db.import_csv(csv_file)
        ljudi = db.ucitaj_ljude()
        assert len(ljudi) == 1
