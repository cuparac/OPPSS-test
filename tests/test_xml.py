import pytest
from database import Database
from xml_generator import generisi_xml, generisi_html_izvestaj


@pytest.fixture
def db(tmp_path):
    database = Database("2026")
    database.db_file = str(tmp_path / "test.db")
    database.kreiraj_tabele()
    database.sacuvaj_podnosioca({
        'pib_jmbg': '123456789',
        'email': 'test@example.com',
        'telefon': '0651234567',
        'jmbg': '1234567890123'
    })
    yield database
    database.zatvori()


PODACI = {
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


class TestXMLGenerator:
    def test_generisi_xml(self, db):
        db.dodaj_osobu(PODACI)
        xml = generisi_xml(db, "2026")
        assert xml is not None
        assert "PoreskaDeklaracija" in xml

    def test_generisi_xml_validacija(self, db):
        db.dodaj_osobu(PODACI)
        xml = generisi_xml(db, "2026")
        from validacije import get_xsd_schema
        schema = get_xsd_schema()
        if schema:
            from lxml import etree
            root = etree.fromstring(xml.encode('utf-8'))
            assert schema.validate(root)
        else:
            pytest.skip("XSD schema not available")

    def test_generisi_xml_bez_podnosioca(self, db):
        """generisi_xml mora da podigne ValueError ako podnosioc ne postoji."""
        # Ukloni podnosioca direktno iz baze
        c = db.conn.cursor()
        c.execute("DELETE FROM podnosioc WHERE godina = ?", ("2026",))
        db.conn.commit()
        with pytest.raises(ValueError, match="Podnosioc"):
            generisi_xml(db, "2026")


class TestHTMLIzvestaj:
    def test_generisi_html(self, db):
        db.dodaj_osobu(PODACI)
        html = generisi_html_izvestaj(None, db, "2026")
        assert html is not None
        assert "OPPSS Generator" in html
        assert "<!DOCTYPE html>" in html
        assert "<table>" in html
        assert "</table>" in html
        assert "Test Osoba" in html
        assert "Leskovac" in html

    def test_generisi_html_escaping(self, db):
        """Vrednosti sa HTML specijalnim karakterima moraju biti escaped."""
        podaci_injekcija = dict(PODACI)
        podaci_injekcija['ime_naziv'] = '<script>alert("xss")</script>'
        podaci_injekcija['opstina'] = 'Test & "Grad"'
        db.dodaj_osobu(podaci_injekcija)
        html = generisi_html_izvestaj(None, db, "2026")
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert "&amp;" in html
        assert "&quot;" in html
