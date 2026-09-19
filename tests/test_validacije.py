import pytest
from validacije import validan_jmbg, validan_ebs, konvertuj_datum, get_xsd_schema


class TestJMBG:
    def test_valid_jmbg(self):
        assert validan_jmbg("2212994740010") is True

    def test_invalid_jmbg_wrong_date(self):
        assert validan_jmbg("3212994740010") is False

    def test_invalid_jmbg_wrong_control(self):
        assert validan_jmbg("2212994740011") is False

    def test_invalid_jmbg_too_short(self):
        with pytest.raises(ValueError):
            validan_jmbg("123")


class TestEBS:
    def test_valid_ebs(self):
        assert validan_ebs("123456789") is True

    def test_invalid_ebs_too_short(self):
        assert validan_ebs("123") is False

    def test_invalid_ebs_non_numeric(self):
        assert validan_ebs("abcdefghi") is False


class TestKonvertujDatum:
    def test_iso_to_display(self):
        assert konvertuj_datum("2026-09-19") == "19/09/2026"

    def test_display_to_iso(self):
        assert konvertuj_datum("19/09/2026") == "2026-09-19"

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            konvertuj_datum("not-a-date")


class TestXSDSchema:
    def test_get_xsd_schema(self):
        schema = get_xsd_schema()
        assert schema is not None
