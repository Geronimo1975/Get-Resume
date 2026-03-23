from django.test import TestCase

from ats.services import ATSScoringService


class ATSScoringServiceTest(TestCase):
    def setUp(self):
        self.service = ATSScoringService()
        self.full_cv = {
            "persoenliche_daten": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "email": "max@example.com",
                "telefon": "+49 170 1234567",
                "geburtsdatum": "1990-01-15",
                "stadt": "Berlin",
                "foto": "photo.jpg",
            },
            "berufserfahrung": {
                "eintraege": [
                    {
                        "position": "Senior Entwickler",
                        "unternehmen": "SAP SE",
                        "von": "2021-01",
                        "bis": "2023-06",
                        "beschreibung": "Entwicklung von Enterprise-Software mit Java und Spring Boot. Verantwortlich fuer Architekturentscheidungen.",
                    },
                    {
                        "position": "Entwickler",
                        "unternehmen": "Siemens AG",
                        "von": "2019-01",
                        "bis": "2020-12",
                        "beschreibung": "Backend-Entwicklung mit Python und Django. Implementierung von REST APIs und Datenbankoptimierung.",
                    },
                    {
                        "position": "Junior Entwickler",
                        "unternehmen": "Bosch GmbH",
                        "von": "2017-06",
                        "bis": "2018-12",
                        "beschreibung": "Mitarbeit an IoT-Projekten mit C++ und Python. Unterstuetzung bei der Testautomatisierung.",
                    },
                ],
            },
            "ausbildung": {
                "eintraege": [
                    {
                        "abschluss": "M.Sc. Informatik",
                        "institution": "TU Berlin",
                        "von": "2015",
                        "bis": "2017",
                    },
                ],
            },
            "kenntnisse": {
                "eintraege": [
                    {"name": "Python", "niveau": 5},
                    {"name": "Java", "niveau": 4},
                    {"name": "Django", "niveau": 4},
                ],
            },
            "sprachen": {
                "eintraege": [
                    {"name": "Deutsch", "niveau": "Muttersprache"},
                    {"name": "Englisch", "niveau": "C1"},
                ],
            },
            "unterschrift": {"vorhanden": True},
        }

    def test_full_cv_scores_above_70(self):
        """A complete CV with 3+ berufserfahrung entries should score >70."""
        result = self.service.score(self.full_cv)
        self.assertGreater(result["score"], 70)

    def test_empty_cv_scores_below_30(self):
        """An empty dict should score <30."""
        result = self.service.score({})
        self.assertLess(result["score"], 30)

    def test_keyword_match_with_job_description(self):
        """Keywords from JD found in CV content produce a score."""
        job_description = (
            "Wir suchen einen erfahrenen Python Entwickler mit Django "
            "Kenntnissen. Erfahrung mit REST APIs und Datenbankoptimierung "
            "ist von Vorteil."
        )
        result = self.service.score(self.full_cv, job_description=job_description)
        self.assertIsNotNone(result["categories"]["keyword_match"]["score"])
        self.assertGreater(result["categories"]["keyword_match"]["score"], 0)

    def test_keyword_match_null_without_job_description(self):
        """keyword_match score is None when no JD is provided."""
        result = self.service.score(self.full_cv)
        self.assertIsNone(result["categories"]["keyword_match"]["score"])

    def test_suggestions_are_german(self):
        """Empty CV generates German suggestions."""
        result = self.service.score({})
        suggestions = result["suggestions"]
        self.assertGreater(len(suggestions), 0)
        all_messages = " ".join(s["message"] for s in suggestions)
        german_words = ["fehlt", "Kein", "keine", "Keine"]
        has_german = any(word in all_messages for word in german_words)
        self.assertTrue(
            has_german,
            f"Suggestions should contain German words like 'fehlt', 'Kein', 'keine'. Got: {all_messages}",
        )

    def test_categories_present(self):
        """Result has all 5 category keys."""
        result = self.service.score(self.full_cv)
        expected_keys = {
            "completeness",
            "content_depth",
            "keyword_match",
            "formatting",
            "german_standards",
        }
        self.assertEqual(set(result["categories"].keys()), expected_keys)
