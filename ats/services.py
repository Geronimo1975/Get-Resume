"""
ATS Scoring Service — orchestrates rule-based scoring across 5 categories.
"""

from ats.rules import (
    check_completeness,
    check_content_depth,
    check_formatting,
    check_german_standards,
    check_keyword_match,
)

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

CATEGORIES = [
    ("completeness", check_completeness, 0.30, False),
    ("content_depth", check_content_depth, 0.25, False),
    ("keyword_match", check_keyword_match, 0.20, True),
    ("formatting", check_formatting, 0.15, False),
    ("german_standards", check_german_standards, 0.10, False),
]


class ATSScoringService:
    def score(self, section_data, job_description=None):
        """
        Score a CV based on 5 rule categories.

        Args:
            section_data: dict of CV sections (persoenliche_daten, berufserfahrung, etc.)
            job_description: optional job description string for keyword matching

        Returns:
            dict with keys: score (int 0-100), categories (dict), suggestions (list)
        """
        categories = {}
        all_suggestions = []
        weighted_total = 0.0
        total_weight = 0.0

        for name, check_fn, weight, needs_jd in CATEGORIES:
            if needs_jd:
                cat_score, cat_suggestions = check_fn(section_data, job_description)
            else:
                cat_score, cat_suggestions = check_fn(section_data)

            categories[name] = {
                "score": cat_score,
                "weight": weight,
                "suggestions": cat_suggestions,
            }
            all_suggestions.extend(cat_suggestions)

            # If keyword_match returns None, exclude from weighted total
            if cat_score is not None:
                weighted_total += cat_score * weight
                total_weight += weight

        # Compute final score, redistributing weight if keyword_match is excluded
        if total_weight > 0:
            final_score = int(weighted_total / total_weight)
        else:
            final_score = 0

        # Sort suggestions by severity (high first)
        all_suggestions.sort(key=lambda s: SEVERITY_ORDER.get(s.get("severity", "low"), 2))

        return {
            "score": final_score,
            "categories": categories,
            "suggestions": all_suggestions,
        }
