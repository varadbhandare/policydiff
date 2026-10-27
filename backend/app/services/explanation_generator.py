import re
from app.services.change_classifier import ClassifiedChange


class ExplanationGenerator:
    @classmethod
    def generate_explanation(cls, change: ClassifiedChange) -> str:
        if change.change_type == "UNCHANGED":
            return "This rule remains substantively equivalent in both policy versions, with no material changes to operational requirements."

        if change.change_type == "ADDED":
            new_text = change.new_rule.raw_text if change.new_rule else "New policy condition"
            snippet = cls._truncate_snippet(new_text)
            return (
                f"A new rule has been introduced under '{change.category}': \"{snippet}\". "
                "Stakeholders must review this newly added provision to ensure compliance."
            )

        if change.change_type == "REMOVED":
            old_text = change.old_rule.raw_text if change.old_rule else "Previous policy condition"
            snippet = cls._truncate_snippet(old_text)
            return (
                f"A previous rule under '{change.category}' has been rescinded: \"{snippet}\". "
                "This condition is no longer present in the updated document."
            )

        # For MODIFIED rules, ground the explanation strictly in detected diffs
        explanations = []

        for diff in change.entity_diffs:
            if diff.entity_type == "percentage":
                explanations.append(
                    f"The percentage requirement has changed from {diff.old_value} to {diff.new_value}. "
                    "Students must fulfill this updated threshold to remain eligible."
                )
            elif diff.entity_type == "date":
                explanations.append(
                    f"The specified deadline or date has shifted from {diff.old_value} to {diff.new_value}. "
                    "Ensure submissions or administrative actions are aligned with this new timeline."
                )
            elif diff.entity_type == "monetary":
                explanations.append(
                    f"The fee or financial obligation has changed from {diff.old_value} to {diff.new_value}."
                )
            elif diff.entity_type == "prohibition":
                explanations.append(
                    f"A major conduct or procedural restriction changed: status shifted from '{diff.old_value}' to '{diff.new_value}'."
                )
            elif diff.entity_type == "negation":
                explanations.append(
                    f"The logical condition of this rule has flipped ({diff.old_value} vs {diff.new_value}). "
                    "Please verify whether permission or prohibition has been reversed."
                )
            elif diff.entity_type == "modality":
                explanations.append(
                    f"Obligation level shifted from '{diff.old_value}' to '{diff.new_value}'. "
                    "This changes whether the action is mandatory or discretionary."
                )
            elif diff.entity_type == "eligibility":
                explanations.append(
                    f"Eligible student cohort changed from '{diff.old_value}' to '{diff.new_value}'. "
                    "Review applicable exemptions and scope."
                )
            elif diff.entity_type == "threshold":
                explanations.append(
                    f"Numerical parameter updated from {diff.old_value} to {diff.new_value}."
                )

        if explanations:
            return " ".join(explanations)

        # If no specific entities detected, explain based on similarity score
        score = change.similarity_score
        if score < 0.65:
            return (
                f"Needs Review: Significant wording revision detected (similarity score: {score:.0%}). "
                "The core sentence structure has changed substantially; administrative review is recommended."
            )
        else:
            return (
                f"The rule wording has been revised or paraphrased (similarity score: {score:.0%}) "
                "while addressing the same subject matter. Key numerical values and prohibitions remain consistent."
            )

    @staticmethod
    def _truncate_snippet(text: str, max_chars: int = 120) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[:max_chars].rstrip() + "..."
