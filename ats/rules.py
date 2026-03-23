"""
Rule-based ATS scoring functions.

Each function takes section_data (dict) and returns (score: int 0-100, suggestions: list[dict]).
Suggestions have keys: message (str, German), severity ("high"|"medium"|"low"), category (str).
"""

import re

# German stopwords to exclude from keyword matching
GERMAN_STOPWORDS = {
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "einem",
    "einer", "und", "oder", "aber", "als", "auch", "auf", "aus", "bei", "bis",
    "dass", "denn", "doch", "durch", "fuer", "gegen", "hat", "haben", "ich",
    "ihm", "ihn", "ihr", "ihre", "ihrem", "ihren", "ihrer", "ist", "kann",
    "mit", "nach", "nicht", "noch", "nur", "sich", "sie", "sind", "sollte",
    "ueber", "und", "von", "vor", "was", "wenn", "wer", "wie", "wir", "wird",
    "wurde", "zum", "zur", "sehr", "mehr", "schon", "etwa", "hier", "dort",
    "dann", "also", "damit", "diese", "dieser", "diesem", "diesen",
    "jede", "jeder", "jedem", "jeden", "alle", "allem", "allen", "aller",
    "man", "sein", "seine", "seinem", "seinen", "seiner", "werden",
    "worden", "sowie", "bzw", "etc", "usw",
}

ESSENTIAL_SECTIONS = [
    "persoenliche_daten",
    "berufserfahrung",
    "ausbildung",
    "kenntnisse",
]


def check_completeness(sections):
    """
    30% weight. Checks whether essential sections are present and non-empty.
    """
    score = 0
    suggestions = []
    section_weight = 100 / len(ESSENTIAL_SECTIONS)

    for section_key in ESSENTIAL_SECTIONS:
        section = sections.get(section_key)
        if section and isinstance(section, dict) and len(section) > 0:
            # Check that sections with eintraege actually have entries
            if "eintraege" in section:
                if isinstance(section["eintraege"], list) and len(section["eintraege"]) > 0:
                    score += section_weight
                else:
                    suggestions.append({
                        "message": f"Abschnitt '{_section_label(section_key)}' ist vorhanden, aber leer.",
                        "severity": "high",
                        "category": "completeness",
                    })
            else:
                score += section_weight
        else:
            suggestions.append({
                "message": f"Abschnitt '{_section_label(section_key)}' fehlt in Ihrem Lebenslauf.",
                "severity": "high",
                "category": "completeness",
            })

    # Bonus sections
    bonus_sections = ["sprachen", "weiterbildungen", "ehrenamt", "interessen"]
    bonus_present = sum(
        1 for s in bonus_sections
        if sections.get(s) and isinstance(sections[s], dict) and len(sections[s]) > 0
    )
    if bonus_present == 0 and score > 0:
        suggestions.append({
            "message": "Keine optionalen Abschnitte (Sprachen, Weiterbildungen, etc.) vorhanden.",
            "severity": "low",
            "category": "completeness",
        })

    return int(min(score, 100)), suggestions


def check_content_depth(sections):
    """
    25% weight. Checks quality and depth of content.
    """
    score = 0
    suggestions = []

    # Berufserfahrung: 3+ entries, each with beschreibung > 50 chars
    beruf = sections.get("berufserfahrung", {})
    entries = beruf.get("eintraege", []) if isinstance(beruf, dict) else []

    if len(entries) >= 3:
        score += 40
    elif len(entries) >= 1:
        score += 20
        suggestions.append({
            "message": f"Nur {len(entries)} Berufserfahrung-Eintra\u0308ge vorhanden. Mindestens 3 werden empfohlen.",
            "severity": "medium",
            "category": "content_depth",
        })
    else:
        suggestions.append({
            "message": "Keine Berufserfahrung eingetragen.",
            "severity": "high",
            "category": "content_depth",
        })

    # Check beschreibung depth
    good_descriptions = 0
    for entry in entries:
        beschreibung = entry.get("beschreibung", "")
        if isinstance(beschreibung, str) and len(beschreibung) > 50:
            good_descriptions += 1
        elif entry:
            suggestions.append({
                "message": f"Beschreibung bei '{entry.get('position', 'Eintrag')}' ist zu kurz. Mindestens 50 Zeichen empfohlen.",
                "severity": "medium",
                "category": "content_depth",
            })

    if entries:
        description_ratio = good_descriptions / len(entries)
        score += int(30 * description_ratio)

    # Ausbildung present
    ausbildung = sections.get("ausbildung", {})
    ausbildung_entries = ausbildung.get("eintraege", []) if isinstance(ausbildung, dict) else []
    if len(ausbildung_entries) >= 1:
        score += 20
    else:
        suggestions.append({
            "message": "Keine Ausbildung eingetragen.",
            "severity": "high",
            "category": "content_depth",
        })

    # Kenntnisse
    kenntnisse = sections.get("kenntnisse", {})
    kenntnisse_entries = kenntnisse.get("eintraege", []) if isinstance(kenntnisse, dict) else []
    if len(kenntnisse_entries) >= 3:
        score += 10
    elif len(kenntnisse_entries) >= 1:
        score += 5
        suggestions.append({
            "message": "Wenige Kenntnisse angegeben. Mindestens 3 werden empfohlen.",
            "severity": "low",
            "category": "content_depth",
        })
    else:
        suggestions.append({
            "message": "Keine Kenntnisse eingetragen.",
            "severity": "medium",
            "category": "content_depth",
        })

    return int(min(score, 100)), suggestions


def check_keyword_match(sections, job_description):
    """
    20% weight. Returns (None, []) if no JD.
    Otherwise extracts keywords and computes overlap percentage.
    """
    if not job_description or not isinstance(job_description, str) or len(job_description.strip()) == 0:
        return None, []

    suggestions = []

    # Extract keywords from job description (3+ char words, minus stopwords)
    jd_words = set()
    for word in re.findall(r"[a-zA-ZäöüÄÖÜß]+", job_description.lower()):
        if len(word) >= 3 and word not in GERMAN_STOPWORDS:
            jd_words.add(word)

    if not jd_words:
        return 0, []

    # Extract all text from CV sections
    cv_text = _extract_all_text(sections).lower()
    cv_words = set(re.findall(r"[a-zA-ZäöüÄÖÜß]+", cv_text))

    # Compute overlap
    matched = jd_words & cv_words
    overlap = len(matched) / len(jd_words) * 100 if jd_words else 0

    missing = jd_words - cv_words
    if missing:
        # Show up to 5 missing keywords
        missing_sample = sorted(missing)[:5]
        suggestions.append({
            "message": f"Fehlende Schluesselwoerter aus der Stellenanzeige: {', '.join(missing_sample)}",
            "severity": "medium",
            "category": "keyword_match",
        })

    return int(min(overlap, 100)), suggestions


def check_formatting(sections):
    """
    15% weight. Checks valid email, phone, date ranges.
    """
    score = 0
    suggestions = []

    persoenliche = sections.get("persoenliche_daten", {})
    if not isinstance(persoenliche, dict):
        persoenliche = {}

    # Valid email
    email = persoenliche.get("email", "")
    if isinstance(email, str) and "@" in email:
        score += 35
    else:
        suggestions.append({
            "message": "Keine gueltige E-Mail-Adresse angegeben.",
            "severity": "high",
            "category": "formatting",
        })

    # Valid phone (6+ digits)
    telefon = persoenliche.get("telefon", "")
    if isinstance(telefon, str):
        digits = re.findall(r"\d", telefon)
        if len(digits) >= 6:
            score += 25
        else:
            suggestions.append({
                "message": "Keine gueltige Telefonnummer angegeben (mindestens 6 Ziffern).",
                "severity": "high",
                "category": "formatting",
            })
    else:
        suggestions.append({
            "message": "Keine Telefonnummer angegeben.",
            "severity": "high",
            "category": "formatting",
        })

    # Check date ranges in berufserfahrung
    beruf = sections.get("berufserfahrung", {})
    entries = beruf.get("eintraege", []) if isinstance(beruf, dict) else []
    complete_dates = 0
    for entry in entries:
        von = entry.get("von", "")
        bis = entry.get("bis", "")
        if von and bis:
            complete_dates += 1
        elif von or bis:
            suggestions.append({
                "message": f"Unvollstaendiger Zeitraum bei '{entry.get('position', 'Eintrag')}'.",
                "severity": "medium",
                "category": "formatting",
            })

    if entries:
        date_ratio = complete_dates / len(entries)
        score += int(40 * date_ratio)
    elif not entries:
        # No entries to check dates on, partial credit
        pass

    return int(min(score, 100)), suggestions


def check_german_standards(sections):
    """
    10% weight. Checks photo, geburtsdatum, unterschrift, anti-chronological order.
    """
    score = 0
    suggestions = []

    persoenliche = sections.get("persoenliche_daten", {})
    if not isinstance(persoenliche, dict):
        persoenliche = {}

    # Photo present
    foto = persoenliche.get("foto", "")
    if foto:
        score += 25
    else:
        suggestions.append({
            "message": "Kein Bewerbungsfoto vorhanden. In Deutschland ist ein professionelles Foto ueblich.",
            "severity": "medium",
            "category": "german_standards",
        })

    # Geburtsdatum
    geburtsdatum = persoenliche.get("geburtsdatum", "")
    if geburtsdatum:
        score += 25
    else:
        suggestions.append({
            "message": "Kein Geburtsdatum angegeben. In deutschen Lebenslaeufen ist dies ueblich.",
            "severity": "low",
            "category": "german_standards",
        })

    # Unterschrift
    unterschrift = sections.get("unterschrift", {})
    if isinstance(unterschrift, dict) and unterschrift.get("vorhanden"):
        score += 25
    else:
        suggestions.append({
            "message": "Keine Unterschrift vorhanden. Eine Unterschrift erhoet die Serioesitaet.",
            "severity": "low",
            "category": "german_standards",
        })

    # Anti-chronological order check
    beruf = sections.get("berufserfahrung", {})
    entries = beruf.get("eintraege", []) if isinstance(beruf, dict) else []
    if len(entries) >= 2:
        dates = []
        for entry in entries:
            von = entry.get("von", "")
            if von:
                dates.append(von)
        if len(dates) >= 2:
            is_antichronological = all(
                dates[i] >= dates[i + 1] for i in range(len(dates) - 1)
            )
            if is_antichronological:
                score += 25
            else:
                suggestions.append({
                    "message": "Berufserfahrung ist nicht anti-chronologisch sortiert. Neueste Eintraege sollten zuerst stehen.",
                    "severity": "medium",
                    "category": "german_standards",
                })
        else:
            score += 25  # Can't verify, give benefit of doubt
    elif len(entries) == 1:
        score += 25  # Single entry is trivially sorted
    else:
        # No entries
        pass

    return int(min(score, 100)), suggestions


def _extract_all_text(sections):
    """Recursively extract all string values from nested dicts/lists."""
    texts = []

    def _walk(obj):
        if isinstance(obj, str):
            texts.append(obj)
        elif isinstance(obj, dict):
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    _walk(sections)
    return " ".join(texts)


SECTION_LABELS = {
    "persoenliche_daten": "Persoenliche Daten",
    "berufserfahrung": "Berufserfahrung",
    "ausbildung": "Ausbildung",
    "kenntnisse": "Kenntnisse",
    "sprachen": "Sprachen",
    "weiterbildungen": "Weiterbildungen",
    "ehrenamt": "Ehrenamt",
    "interessen": "Interessen",
    "unterschrift": "Unterschrift",
}


def _section_label(key):
    return SECTION_LABELS.get(key, key)
