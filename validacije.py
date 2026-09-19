"""Validacione funkcije za OPPSS Generator.

Sadrži funkcije za proveru JMBG-a, EBS-a, konverziju datuma
i učitavanje XSD šeme.
"""

from __future__ import annotations

import datetime
from typing import Optional

from lxml import etree

# XSD šema je ugrađena u kod
XSD_CONTENT = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema elementFormDefault="qualified" targetNamespace="http://pid.purs.gov.rs" version="1.0.0"
           xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:tns="http://pid.purs.gov.rs">
    <xs:element name="PoreskaDeklaracija" type="tns:PoreskaDeklaracijaType"/>
    <xs:complexType name="PoreskaDeklaracijaType">
        <xs:sequence>
            <xs:element name="OPPPSSPrijava" maxOccurs="1" minOccurs="1" type="tns:OPPPSSPrijavaType"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="OPPPSSPrijavaType">
        <xs:sequence>
            <xs:element name="PodaciOPrijavi" maxOccurs="1" minOccurs="1" type="tns:PodaciOPrijaviType"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="PodaciOPrijaviType">
        <xs:sequence>
            <xs:element name="KlijentskaOznakaDeklaracije" maxOccurs="1" minOccurs="0" type="tns:String255Type"/>
            <xs:element name="PortalOznakaDeklaracije" maxOccurs="1" minOccurs="0" type="tns:String255Type"/>
            <xs:element name="PodaciOObrascu" maxOccurs="1" minOccurs="1" type="tns:PodaciOObrascuType"/>
            <xs:element name="PodaciOPodnosiocu" maxOccurs="1" minOccurs="1" type="tns:PodaciOPodnosiocuType"/>
            <xs:element name="PodaciOPrometu" minOccurs="1" maxOccurs="unbounded" type="tns:PodaciOPrometuType"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="PodaciOObrascuType">
        <xs:sequence>
            <xs:element name="PoreskiPeriod" type="xs:positiveInteger" maxOccurs="1" minOccurs="1"/>
            <xs:element name="IspravkaObavestenja" type="xs:boolean" maxOccurs="1" minOccurs="0"/>
            <xs:element name="JBIPKojaSeMenja" type="xs:long" maxOccurs="1" minOccurs="0"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="PodaciOPodnosiocuType">
        <xs:sequence>
            <xs:element name="PIBJMBG" type="tns:PIBJMBGTip" minOccurs="1" maxOccurs="1"/>
            <xs:element name="EPostaPodnosioca" type="tns:eMailAdresaType" minOccurs="1" maxOccurs="1"/>
            <xs:element name="TelefonPodnosioca" type="tns:String255Type" maxOccurs="1" minOccurs="1"/>
            <xs:element name="JMBGPodnosioca" type="tns:JMBGType" minOccurs="1" maxOccurs="1"/>
        </xs:sequence>
    </xs:complexType>
    <xs:complexType name="PodaciOPrometuType">
        <xs:sequence>
            <xs:element name="VrstaPrometa" type="xs:integer" minOccurs="1" maxOccurs="1"/>
            <xs:element name="VrstaIdentifikatora" type="xs:integer" minOccurs="1" maxOccurs="1"/>
            <xs:element name="Identifikator" type="tns:String255Type" minOccurs="1" maxOccurs="1"/>
            <xs:element name="ImeNaziv" type="tns:String255Type" minOccurs="1" maxOccurs="1"/>
            <xs:element name="Opstina" type="tns:String255Type" minOccurs="1" maxOccurs="1"/>
            <xs:element name="Adresa" type="tns:String255Type" minOccurs="1" maxOccurs="1"/>
            <xs:element name="EPosta" type="tns:eMailAdresaType" minOccurs="0" maxOccurs="1"/>
            <xs:element name="Telefon" type="tns:String255Type" minOccurs="1" maxOccurs="1"/>
            <xs:element name="BrojGazdinstva" type="tns:String255Type" minOccurs="0" maxOccurs="1"/>
            <xs:element name="NazivGazdinstva" type="tns:String255Type" minOccurs="0" maxOccurs="1"/>
            <xs:element name="Datum" type="xs:date" minOccurs="1" maxOccurs="1"/>
            <xs:element name="DatumDo" type="xs:date" minOccurs="1" maxOccurs="1"/>
            <xs:element name="IznosPrometa" type="xs:long" minOccurs="1" maxOccurs="1"/>
        </xs:sequence>
    </xs:complexType>
    <xs:simpleType name="PIBJMBGTip">
        <xs:restriction base="xs:string">
            <xs:pattern value="([0-9]{9}|[0-9]{13})"/>
        </xs:restriction>
    </xs:simpleType>
    <xs:simpleType name="JMBGType">
        <xs:restriction base="xs:string">
            <xs:pattern value="[0-9]{13}"/>
        </xs:restriction>
    </xs:simpleType>
    <xs:simpleType name="eMailAdresaType">
        <xs:restriction base="xs:string">
            <xs:pattern value="[^@]+@[^@]+\\.[^@]+"/>
        </xs:restriction>
    </xs:simpleType>
    <xs:simpleType name="String255Type">
        <xs:restriction base="xs:string">
            <xs:maxLength value="255"/>
        </xs:restriction>
    </xs:simpleType>
</xs:schema>'''


def validan_jmbg(jmbg: str) -> bool:
    """Proverava ispravnost JMBG-a.

    Args:
        jmbg: 13-cifreni matični broj

    Returns:
        True ako je JMBG ispravan, False inače

    Raises:
        ValueError: ako JMBG nije 13 cifara
    """
    if len(jmbg) != 13 or not jmbg.isdigit():
        raise ValueError("JMBG mora imati 13 cifara")

    dan = int(jmbg[0:2])
    mesec = int(jmbg[2:4])
    godina = int(jmbg[4:7])

    # Proveri oba raspona godina (1000-1999 i 2000-2999)
    for godina_base in [1000, 2000]:
        try:
            datetime.date(godina_base + godina, mesec, dan)
            break
        except ValueError:
            continue
    else:
        return False

    # Kontrolna cifra
    tezine = [7, 6, 5, 4, 3, 2]
    zbir = sum(int(jmbg[i]) * tezine[i % 6] for i in range(12))
    kontrolna = 11 - (zbir % 11)
    if kontrolna > 9:
        kontrolna = 0

    return kontrolna == int(jmbg[12])


def validan_ebs(ebs: str) -> bool:
    """Proverava ispravnost EBS-a.

    Args:
        ebs: 9-cifreni jedinstveni broj subjekta

    Returns:
        True ako je EBS ispravan, False inače
    """
    return len(ebs) == 9 and ebs.isdigit()


def konvertuj_datum(t: str) -> str:
    """Konvertuje datum između ISO (YYYY-MM-DD) i display (DD/MM/YYYY) formata.

    Args:
        t: Datum u ISO formatu (YYYY-MM-DD) ili display formatu (DD/MM/YYYY)

    Returns:
        Datum u drugom formatu (ISO ako je unet display, display ako je unet ISO)

    Raises:
        ValueError: ako format nije prepoznat
    """
    t = t.strip()

    # ISO format: YYYY-MM-DD
    if len(t) == 10 and t[4] == '-' and t[7] == '-':
        return f"{t[8:10]}/{t[5:7]}/{t[0:4]}"

    # Display format: DD/MM/YYYY -> ISO (YYYY-MM-DD)
    if len(t) == 10 and t[2] == '/' and t[5] == '/':
        return f"{t[6:10]}-{t[3:5]}-{t[0:2]}"

    raise ValueError(f"Nepoznat format datuma: {t}")


def get_xsd_schema() -> Optional[etree.XMLSchema]:
    """Učitava XSD šemu iz ugrađenog sadržaja.

    Returns:
        XMLSchema objekat ili None ako učitavanje ne uspe
    """
    try:
        xsd_root = etree.fromstring(XSD_CONTENT.encode('utf-8'))
        return etree.XMLSchema(xsd_root)
    except Exception:
        return None
