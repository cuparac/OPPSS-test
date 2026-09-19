"""XML i HTML generator za OPPSS Generator.

Sadrži funkcije za generisanje XML prijava za ePorezi portal
i HTML izveštaja za štampu.
"""

from __future__ import annotations

import html
from typing import Any

from lxml import etree

from database import Database
from validacije import get_xsd_schema

# Namespace za XML
NS = "http://pid.purs.gov.rs"


def generisi_xml(db: Database, godina: str) -> str:
    """Generiše XML prijavu za ePorezi portal.

    Args:
        db: Database objekat
        godina: Godina za koju se generiše prijava

    Returns:
        XML string

    Raises:
        ValueError: ako podnosioc nije registrovan ili XML ne prolazi XSD validaciju
    """
    podnosioc = db.ucitaj_podnosioca()
    if podnosioc is None:
        raise ValueError(
            f"Podnosioc za godinu {godina} nije registrovan. "
            "Prvo registrujte podnosioca pre generisanja XML prijave."
        )
    ljudi = db.ucitaj_ljude()

    # Kreiranje XML strukture
    root = etree.Element(f"{{{NS}}}PoreskaDeklaracija")
    prijava = etree.SubElement(root, f"{{{NS}}}OPPPSSPrijava")
    podaci_prijavi = etree.SubElement(prijava, f"{{{NS}}}PodaciOPrijavi")

    # Podaci o obrascu
    podaci_obrasca = etree.SubElement(podaci_prijavi, f"{{{NS}}}PodaciOObrascu")
    period = etree.SubElement(podaci_obrasca, f"{{{NS}}}PoreskiPeriod")
    period.text = godina

    # Podaci o podnosiocu
    podaci_podnosioca = etree.SubElement(podaci_prijavi, f"{{{NS}}}PodaciOPodnosiocu")
    pib = etree.SubElement(podaci_podnosioca, f"{{{NS}}}PIBJMBG")
    pib.text = podnosioc.get('pib_jmbg', '')
    email = etree.SubElement(podaci_podnosioca, f"{{{NS}}}EPostaPodnosioca")
    email.text = podnosioc.get('email', '')
    telefon = etree.SubElement(podaci_podnosioca, f"{{{NS}}}TelefonPodnosioca")
    telefon.text = podnosioc.get('telefon', '')
    jmbg = etree.SubElement(podaci_podnosioca, f"{{{NS}}}JMBGPodnosioca")
    jmbg.text = podnosioc.get('jmbg', '')

    # Podaci o prometu
    for osoba in ljudi:
        podaci_prometa = etree.SubElement(podaci_prijavi, f"{{{NS}}}PodaciOPrometu")

        vrsta_prometa = etree.SubElement(podaci_prometa, f"{{{NS}}}VrstaPrometa")
        vrsta_prometa.text = str(osoba.get('vrsta_prometa', '1'))

        vrsta_identifikatora = etree.SubElement(podaci_prometa, f"{{{NS}}}VrstaIdentifikatora")
        vrsta_identifikatora.text = str(osoba.get('vrsta_identifikatora', '1'))

        identifikator = etree.SubElement(podaci_prometa, f"{{{NS}}}Identifikator")
        identifikator.text = str(osoba.get('identifikator', ''))

        ime_naziv = etree.SubElement(podaci_prometa, f"{{{NS}}}ImeNaziv")
        ime_naziv.text = str(osoba.get('ime_naziv', ''))

        opstina = etree.SubElement(podaci_prometa, f"{{{NS}}}Opstina")
        opstina.text = str(osoba.get('opstina', ''))

        adresa = etree.SubElement(podaci_prometa, f"{{{NS}}}Adresa")
        adresa.text = str(osoba.get('adresa', ''))

        # EPosta je opcionalna - dodaj samo ako postoji
        email_osobe = osoba.get('email_osobe', '')
        if email_osobe:
            email_el = etree.SubElement(podaci_prometa, f"{{{NS}}}EPosta")
            email_el.text = str(email_osobe)

        telefon_osobe = etree.SubElement(podaci_prometa, f"{{{NS}}}Telefon")
        telefon_osobe.text = str(osoba.get('telefon', ''))

        broj_gazdinstva = etree.SubElement(podaci_prometa, f"{{{NS}}}BrojGazdinstva")
        broj_gazdinstva.text = str(osoba.get('broj_gazdinstva', ''))

        naziv_gazdinstva = etree.SubElement(podaci_prometa, f"{{{NS}}}NazivGazdinstva")
        naziv_gazdinstva.text = str(osoba.get('naziv_gazdinstva', ''))

        datum = etree.SubElement(podaci_prometa, f"{{{NS}}}Datum")
        datum.text = str(osoba.get('datum', ''))

        datum_do = etree.SubElement(podaci_prometa, f"{{{NS}}}DatumDo")
        datum_do.text = str(osoba.get('datum_do', ''))

        iznos = etree.SubElement(podaci_prometa, f"{{{NS}}}IznosPrometa")
        iznos.text = str(osoba.get('iznos_prometa', 0))

    # Validacija
    schema = get_xsd_schema()
    if schema:
        if not schema.validate(root):
            raise ValueError("XML ne prolazi XSD validaciju")

    return etree.tostring(root, pretty_print=True, encoding='unicode')


def generisi_html_izvestaj(app: Any, db: Database, godina: str) -> str:
    """Generiše HTML izveštaj za štampu.

    Args:
        app: GUI aplikacija (može None za CLI)
        db: Database objekat
        godina: Godina za koju se generiše izveštaj

    Returns:
        HTML string
    """
    ljudi = db.ucitaj_ljude()
    stat = db.statistika()

    godina_esc = html.escape(godina)
    ukupno_esc = html.escape(str(stat['ukupno']))
    ukupan_iznos_esc = html.escape(str(stat['ukupan_iznos']))

    html_str = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OPPSS Generator - Izveštaj {godina_esc}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .statistika {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>OPPSS Generator - Izveštaj {godina_esc}</h1>
    <div class="statistika">
        <p><strong>Ukupno unosa:</strong> {ukupno_esc}</p>
        <p><strong>Ukupan iznos:</strong> {ukupan_iznos_esc}</p>
    </div>
    <table>
        <tr>
            <th>ID</th>
            <th>Ime/Naziv</th>
            <th>Opština</th>
            <th>Datum</th>
            <th>Iznos</th>
        </tr>
"""

    for osoba in ljudi:
        id_esc = html.escape(str(osoba.get('id', '')))
        ime_esc = html.escape(str(osoba.get('ime_naziv', '')))
        opstina_esc = html.escape(str(osoba.get('opstina', '')))
        datum_esc = html.escape(str(osoba.get('datum', '')))
        iznos_esc = html.escape(str(osoba.get('iznos_prometa', 0)))
        html_str += f"""        <tr>
            <td>{id_esc}</td>
            <td>{ime_esc}</td>
            <td>{opstina_esc}</td>
            <td>{datum_esc}</td>
            <td>{iznos_esc}</td>
        </tr>
"""

    html_str += """    </table>
</body>
</html>"""

    return html_str
