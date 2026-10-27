import re
from typing import Optional
from app.services.rule_segmenter import RuleUnit
from app.services.semantic_matcher import AlignmentMatch
from app.services.entity_extractor import EntityExtractor, ExtractedEntities
from app.schemas.comparison import EntityDiffItem


class ClassifiedChange:
    def __init__(
        self,
        change_type: str,
        category: str,
        similarity_score: float,
        alignment_confidence: float,
        old_rule: Optional[RuleUnit] = None,
        new_rule: Optional[RuleUnit] = None,
        old_entities: Optional[ExtractedEntities] = None,
        new_entities: Optional[ExtractedEntities] = None,
        entity_diffs: Optional[list[EntityDiffItem]] = None,
        reason: Optional[str] = None,
    ):
        self.change_type = change_type
        self.category = category
        self.similarity_score = similarity_score
        self.alignment_confidence = alignment_confidence
        self.old_rule = old_rule
        self.new_rule = new_rule
        self.old_entities = old_entities or ExtractedEntities()
        self.new_entities = new_entities or ExtractedEntities()
        self.entity_diffs = entity_diffs or []
        self.reason = reason or ""


class ChangeClassifier:
    CATEGORY_KEYWORDS = {
        "Attendance & Leaves": [
            "attendance", "leave", "absence", "absent", "medical leave", "duty leave",
            "shortage", "biometric", "regularity", "session", "class attendance"
        ],
        "Examinations & Grading": [
            "exam", "examination", "hall ticket", "invigilation", "revaluation",
            "grading", "grade", "gpa", "cgpa", "marks", "passing", "supplementary",
            "backlog", "evaluation", "answer script", "paper", "test"
        ],
        "Deadlines & Schedules": [
            "deadline", "submission", "due date", "calendar", "timeline", "schedule",
            "late submission", "late date", "closing date", "last date", "extension"
        ],
        "Financial & Fees": [
            "fee", "tuition", "fine", "penalty", "refund", "monetary", "payment",
            "dues", "scholarship amount", "stipend", "bursary", "$", "usd", "inr"
        ],
        "Eligibility & Admission": [
            "eligible", "eligibility", "admission", "prerequisite", "criteria",
            "qualifying", "qualification", "final-year", "undergraduate", "credit requirement"
        ],
        "Academic Integrity & Conduct": [
            "plagiarism", "malpractice", "misconduct", "disciplinary", "cheating",
            "unethical", "code of conduct", "ragging", "harassment", "expulsion", "suspension"
        ],
        "Administrative & Governance": [
            "dean", "registrar", "hod", "department", "committee", "office", "approval",
            "signature", "affidavit", "certificate", "id card", "portal"
        ],
    }

    @classmethod
    def categorize_text(cls, text: str, section_heading: Optional[str] = None) -> str:
        combined = f"{section_heading or ''} {text}".lower()
        
        # Check section heading first for explicit match
        if section_heading:
            sec_lower = section_heading.lower()
            for cat, keywords in cls.CATEGORY_KEYWORDS.items():
                if any(kw in sec_lower for kw in keywords):
                    return cat

        # Count keyword hits in combined text
        best_cat = "General Academic Policy"
        max_hits = 0
        for cat, keywords in cls.CATEGORY_KEYWORDS.items():
            hits = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", combined))
            if hits > max_hits:
                max_hits = hits
                best_cat = cat

        return best_cat if max_hits > 0 else "General Academic Policy"

    @classmethod
    def classify_match(cls, match: AlignmentMatch) -> ClassifiedChange:
        old_text = match.old_rule.raw_text if match.old_rule else ""
        new_text = match.new_rule.raw_text if match.new_rule else ""

        old_entities = EntityExtractor.extract_entities(old_text)
        new_entities = EntityExtractor.extract_entities(new_text)
        entity_diffs = EntityExtractor.compute_differences(old_entities, new_entities)

        section = match.new_rule.section_heading if match.new_rule else (match.old_rule.section_heading if match.old_rule else "")
        category = cls.categorize_text(f"{old_text} {new_text}", section)

        score = match.similarity_score
        lex_score = match.lexical_similarity

        # Check if substantive differences exist
        has_entity_changes = len(entity_diffs) > 0
        
        # A rule is UNCHANGED if no entities changed and lexical/semantic similarity is high enough
        # to confirm it is the same rule (even if paraphrased or active/passive voice)
        is_substantively_unchanged = (not has_entity_changes) and (score >= 0.60 or lex_score >= 0.68)

        if is_substantively_unchanged:
            # Substantively unchanged
            return ClassifiedChange(
                change_type="UNCHANGED",
                category=category,
                similarity_score=score,
                alignment_confidence=match.alignment_confidence,
                old_rule=match.old_rule,
                new_rule=match.new_rule,
                old_entities=old_entities,
                new_entities=new_entities,
                entity_diffs=[],
                reason="The rule wording and requirements remain substantively identical.",
            )

        # It is MODIFIED
        reason_parts = []
        if has_entity_changes:
            diff_descriptions = [d.details for d in entity_diffs if d.details]
            reason_parts.append("; ".join(diff_descriptions))
        else:
            reason_parts.append(f"Substantially revised wording or scope (semantic similarity: {score:.0%})")

        full_reason = ". ".join(reason_parts) if reason_parts else "Rule conditions or requirements revised."

        return ClassifiedChange(
            change_type="MODIFIED",
            category=category,
            similarity_score=score,
            alignment_confidence=match.alignment_confidence,
            old_rule=match.old_rule,
            new_rule=match.new_rule,
            old_entities=old_entities,
            new_entities=new_entities,
            entity_diffs=entity_diffs,
            reason=full_reason,
        )

    @classmethod
    def classify_added(cls, new_rule: RuleUnit) -> ClassifiedChange:
        new_entities = EntityExtractor.extract_entities(new_rule.raw_text)
        category = cls.categorize_text(new_rule.raw_text, new_rule.section_heading)

        return ClassifiedChange(
            change_type="ADDED",
            category=category,
            similarity_score=0.0,
            alignment_confidence=0.95,
            old_rule=None,
            new_rule=new_rule,
            old_entities=None,
            new_entities=new_entities,
            entity_diffs=[],
            reason="Newly introduced rule in the updated document with no corresponding previous provision.",
        )

    @classmethod
    def classify_removed(cls, old_rule: RuleUnit) -> ClassifiedChange:
        old_entities = EntityExtractor.extract_entities(old_rule.raw_text)
        category = cls.categorize_text(old_rule.raw_text, old_rule.section_heading)

        return ClassifiedChange(
            change_type="REMOVED",
            category=category,
            similarity_score=0.0,
            alignment_confidence=0.95,
            old_rule=old_rule,
            new_rule=None,
            old_entities=old_entities,
            new_entities=None,
            entity_diffs=[],
            reason="Rule from the previous policy has been omitted from the updated document.",
        )
