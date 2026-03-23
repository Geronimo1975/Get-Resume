"""
JSON content schemas for each section type.
These document the expected structure of Section.content for each SectionType.
Use for validation in forms/serializers.
"""

SECTION_CONTENT_SCHEMAS = {
    "persoenliche_daten": {
        "foto": "",
        "anrede": "",
        "vorname": "",
        "nachname": "",
        "geburtsdatum": "",
        "geburtsort": "",
        "staatsangehoerigkeit": "",
        "familienstand": "",
        "email": "",
        "telefon": "",
        "strasse": "",
        "plz": "",
        "stadt": "",
        "website": "",
        "linkedin": "",
        "xing": "",
    },
    "berufserfahrung": {
        "eintraege": [
            {
                "id": "",
                "position": "",
                "unternehmen": "",
                "ort": "",
                "von": "",
                "bis": "",
                "ist_aktuell": False,
                "beschreibung": "",
                "aufgaben": [],
            }
        ]
    },
    "ausbildung": {
        "eintraege": [
            {
                "id": "",
                "abschluss": "",
                "fachrichtung": "",
                "institution": "",
                "ort": "",
                "von": "",
                "bis": "",
                "note": "",
                "beschreibung": "",
            }
        ]
    },
    "kenntnisse": {
        "eintraege": [
            {
                "id": "",
                "name": "",
                "kategorie": "",
                "niveau": 3,
            }
        ]
    },
    "sprachen": {
        "eintraege": [
            {
                "id": "",
                "sprache": "",
                "niveau": "",
                "ist_muttersprache": False,
            }
        ]
    },
    "weiterbildungen": {
        "eintraege": [
            {
                "id": "",
                "titel": "",
                "anbieter": "",
                "datum": "",
                "beschreibung": "",
            }
        ]
    },
    "ehrenamt": {
        "eintraege": [
            {
                "id": "",
                "rolle": "",
                "organisation": "",
                "von": "",
                "bis": "",
                "beschreibung": "",
            }
        ]
    },
    "interessen": {
        "eintraege": [],
    },
    "unterschrift": {
        "ort": "",
        "datum": "",
        "unterschrift_bild": "",
    },
}
