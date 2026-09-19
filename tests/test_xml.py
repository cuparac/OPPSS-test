import pytest
from database import Database
from xml_generator import generisi_xml, generisi_html_izvestaj


@pytest.fixture
def db(tmp_path):
    database = Database("2026")
    database.db_file = str(tmp_path / "test.db")
    database.kreiraj_tabele()
    yield database
    database.zatvori()


class TestXMLGenerator:
    def test_generisi_xml(self, db):
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
        xml = generisi_xml(db, "2026")
        assert xml is not None
        assert "PoreskaDeklaracija" in xml

    def test_generisi_xml_validacija(self, db):
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
        xml = generisi_xml(db, "2026")
        # Proveri da li XML prolazi XSD validaciju
        from validacije import get_xsd_schema
        schema = get_xsd_schema()
        if schema:
            from lxml import etree
            root = etree.fromstring(xml.encode('utf-8'))
            assert schema.validate(root)


class TestHTMLIzvestaj:
    def test_generisi_html(self, db):
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
        html = generisi_html_izvestaj(None, db, "2026")
        assert html is not None
        assert "OPPSS Generator" in html
