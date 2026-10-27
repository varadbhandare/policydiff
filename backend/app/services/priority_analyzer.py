from typing import NamedTuple
from app.services.change_classifier import ClassifiedChange


class PriorityAssessment(NamedTuple):
    priority: str          # Critical, High, Medium, Low
    rationale: str


class PriorityAnalyzer:
    @classmethod
    def assess_priority(cls, change: ClassifiedChange) -> PriorityAssessment:
        # 1. UNCHANGED rules
        if change.change_type == "UNCHANGED":
            return PriorityAssessment(
                priority="Low",
                rationale="Automated assessment: No material changes to rules, thresholds, or obligations were detected."
            )

        # Collect text and diff types for heuristic inspection
        old_text = (change.old_rule.raw_text if change.old_rule else "").lower()
        new_text = (change.new_rule.raw_text if change.new_rule else "").lower()
        combined_text = f"{old_text} {new_text}"
        diff_types = {d.entity_type for d in change.entity_diffs}

        # --- CRITICAL HEURISTICS ---
        # 1. Explicit prohibition changes (e.g. allowed -> prohibited, or barred)
        if "prohibition" in diff_types or "negation" in diff_types:
            if any(term in new_text for term in ["prohibited", "forbidden", "barred", "strict", "not permitted", "disallowed", "cannot"]):
                return PriorityAssessment(
                    priority="Critical",
                    rationale="Critical: A strict prohibition or negation has been introduced, significantly altering permitted student conduct."
                )

        # 2. Examination debarment, disqualification, or academic dismissal
        if any(term in combined_text for term in ["debar", "disqualif", "expulsion", "suspension", "malpractice", "cancel admission", "not eligible for examination"]):
            if change.change_type in ("ADDED", "MODIFIED"):
                return PriorityAssessment(
                    priority="Critical",
                    rationale="Critical: Directly impacts student examination eligibility, qualification status, or disciplinary standing."
                )

        # --- HIGH HEURISTICS ---
        # 3. Attendance percentage threshold changes (e.g. 75% -> 80%)
        if ("percentage" in diff_types or "threshold" in diff_types) and any(kw in combined_text for kw in ["attendance", "present", "biometric", "regular"]):
            return PriorityAssessment(
                priority="High",
                rationale="High: Minimum attendance percentage threshold has been revised, directly impacting course eligibility."
            )

        # 4. Dates & deadlines changes
        if "date" in diff_types or any(kw in combined_text for kw in ["deadline", "due date", "last date", "submission close"]):
            return PriorityAssessment(
                priority="High",
                rationale="High: Key submission deadline or calendar date has shifted; immediate compliance action may be needed."
            )

        # 5. Financial fee / penalty increases
        if "monetary" in diff_types:
            return PriorityAssessment(
                priority="High",
                rationale="High: Monetary fee, fine, or financial requirement has been modified."
            )

        # 6. Modality escalation ("may" -> "must", or new mandatory requirement)
        if "modality" in diff_types:
            if any(m in new_text for m in ["must", "shall", "mandatory", "required"]):
                return PriorityAssessment(
                    priority="High",
                    rationale="High: Policy changed from discretionary/optional to mandatory obligation."
                )

        # 7. ADDED rule in critical domains
        if change.change_type == "ADDED":
            if change.category in ("Attendance & Leaves", "Examinations & Grading", "Eligibility & Admission", "Financial & Fees"):
                return PriorityAssessment(
                    priority="High",
                    rationale=f"High: New rule established in the '{change.category}' domain that imposes new requirements."
                )
            return PriorityAssessment(
                priority="Medium",
                rationale="Medium: Newly introduced institutional rule that should be reviewed for procedural compliance."
            )

        # 8. REMOVED rule
        if change.change_type == "REMOVED":
            if change.category in ("Examinations & Grading", "Financial & Fees", "Eligibility & Admission"):
                return PriorityAssessment(
                    priority="High",
                    rationale=f"High: A rule regarding '{change.category}' was removed, which may remove an exemption, privilege, or procedure."
                )
            return PriorityAssessment(
                priority="Medium",
                rationale="Medium: Previous policy clause was omitted in the revised document."
            )

        # --- MEDIUM HEURISTICS ---
        if change.change_type == "MODIFIED":
            if diff_types:
                return PriorityAssessment(
                    priority="Medium",
                    rationale="Medium: Quantitative or condition adjustments detected between old and new policies."
                )
            return PriorityAssessment(
                priority="Medium",
                rationale="Medium: Significant rewording or semantic revision that may alter operational interpretation."
            )

        # Fallback LOW
        return PriorityAssessment(
            priority="Low",
            rationale="Low: Minor wording clarification or low-impact stylistic change."
        )
