import re
from typing import Optional
from pydantic import BaseModel
from app.schemas.comparison import EntityDiffItem


class ExtractedEntities(BaseModel):
    percentages: list[str] = []
    currencies: list[str] = []
    dates: list[str] = []
    quantities: list[str] = []  # e.g., "30 days", "3 credits", "2 semesters"
    modals: list[str] = []      # "must", "may", "shall", "required", etc.
    prohibitions: list[str] = [] # "prohibited", "forbidden", "barred", "not permitted"
    negations: list[str] = []   # "not", "no", "never", "cannot"
    eligibility_keywords: list[str] = [] # "final-year", "all students", etc.
    numbers: list[str] = []


class EntityExtractor:
    PERCENTAGE_REGEX = re.compile(r"\b(\d+(?:\.\d+)?%)(?!\w)", re.IGNORECASE)
    
    CURRENCY_REGEX = re.compile(
        r"([$€£₹]\s*\d+(?:,\d{3})*(?:\.\d+)?|\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:usd|eur|gbp|inr|dollars|cents)\b)",
        re.IGNORECASE
    )
    
    # Matches dates like: "15 July 2025", "15th July", "July 15, 2025", "2025-07-15", "15/07/2025"
    DATE_REGEX = re.compile(
        r"\b(?:"
        r"\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*(?:\d{4})?"
        r"|(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*\d{4})?"
        r"|\d{4}-\d{2}-\d{2}"
        r"|\d{1,2}/\d{1,2}/\d{2,4}"
        r")\b",
        re.IGNORECASE
    )

    QUANTITY_REGEX = re.compile(
        r"\b(\d+(?:\.\d+)?\s*(?:\w+\s+)?(?:credits?|days?|hours?|weeks?|months?|semesters?|attempts?|points?|cgpa|gpa|marks?|years?))\b|"
        r"\b(?:cgpa|gpa)\s+(?:of\s+)?(\d+(?:\.\d+)?)\b",
        re.IGNORECASE
    )

    NUMBER_REGEX = re.compile(r"\b(\d+(?:\.\d+)?(?:st|nd|rd|th)?)\b")

    MODAL_OBLIGATION = {"must", "shall", "mandatory", "required", "compulsory", "obligatory"}
    MODAL_PERMISSION = {"may", "can", "permitted", "allowed", "eligible", "optional"}
    MODAL_PROHIBITION = {"prohibited", "forbidden", "barred", "disallowed", "banned", "not allowed", "not permitted"}
    NEGATION_WORDS = {"not", "no", "never", "cannot", "neither", "nor", "without", "rarely"}
    
    ELIGIBILITY_PATTERNS = [
        re.compile(r"\b(all students)\b", re.IGNORECASE),
        re.compile(r"\b(final[- ]year)\b", re.IGNORECASE),
        re.compile(r"\b(first[- ]year|freshm[ae]n)\b", re.IGNORECASE),
        re.compile(r"\b(undergraduate|ug)\b", re.IGNORECASE),
        re.compile(r"\b(postgraduate|pg|graduate)\b", re.IGNORECASE),
        re.compile(r"\b(international students?)\b", re.IGNORECASE),
        re.compile(r"\b(full[- ]time)\b", re.IGNORECASE),
        re.compile(r"\b(part[- ]time)\b", re.IGNORECASE),
        re.compile(r"\b(scholarship recipients?)\b", re.IGNORECASE),
    ]

    @classmethod
    def extract_entities(cls, text: str) -> ExtractedEntities:
        if not text:
            return ExtractedEntities()

        text_lower = text.lower()
        words = set(re.findall(r"\b[a-z\-]+\b", text_lower))

        # Percentages
        percentages = [m.group(1) for m in cls.PERCENTAGE_REGEX.finditer(text)]

        # Currencies
        currencies = [m.group(1).strip() for m in cls.CURRENCY_REGEX.finditer(text)]

        # Dates
        dates = [m.group(0).strip() for m in cls.DATE_REGEX.finditer(text)]

        # Quantities
        quantities = [(m.group(1) or m.group(2)).strip() for m in cls.QUANTITY_REGEX.finditer(text) if (m.group(1) or m.group(2))]

        # Modals
        found_modals = sorted(list(words.intersection(cls.MODAL_OBLIGATION | cls.MODAL_PERMISSION)))
        
        # Prohibitions (words and phrases)
        found_prohibitions = []
        for prob in cls.MODAL_PROHIBITION:
            if prob in text_lower:
                found_prohibitions.append(prob)

        # Negations
        found_negations = sorted(list(words.intersection(cls.NEGATION_WORDS)))

        # Eligibility keywords
        found_eligibility = []
        for pat in cls.ELIGIBILITY_PATTERNS:
            match = pat.search(text)
            if match:
                found_eligibility.append(match.group(1).lower())

        # Raw numbers & ordinals
        numbers = [m.group(1) for m in cls.NUMBER_REGEX.finditer(text)]

        return ExtractedEntities(
            percentages=percentages,
            currencies=currencies,
            dates=dates,
            quantities=quantities,
            modals=found_modals,
            prohibitions=found_prohibitions,
            negations=found_negations,
            eligibility_keywords=found_eligibility,
            numbers=numbers,
        )

    @classmethod
    def compute_differences(
        cls, old_entities: ExtractedEntities, new_entities: ExtractedEntities
    ) -> list[EntityDiffItem]:
        diffs: list[EntityDiffItem] = []

        # 1. Percentage threshold differences
        if old_entities.percentages != new_entities.percentages:
            old_val = ", ".join(old_entities.percentages) or "None"
            new_val = ", ".join(new_entities.percentages) or "None"
            diffs.append(
                EntityDiffItem(
                    entity_type="percentage",
                    old_value=old_val,
                    new_value=new_val,
                    details=f"Numerical percentage threshold changed from {old_val} to {new_val}",
                )
            )

        # 2. Currency differences
        if old_entities.currencies != new_entities.currencies:
            old_val = ", ".join(old_entities.currencies) or "None"
            new_val = ", ".join(new_entities.currencies) or "None"
            diffs.append(
                EntityDiffItem(
                    entity_type="monetary",
                    old_value=old_val,
                    new_value=new_val,
                    details=f"Financial amount changed from {old_val} to {new_val}",
                )
            )

        # 3. Dates & Deadlines
        if old_entities.dates != new_entities.dates:
            old_val = ", ".join(old_entities.dates) or "None"
            new_val = ", ".join(new_entities.dates) or "None"
            diffs.append(
                EntityDiffItem(
                    entity_type="date",
                    old_value=old_val,
                    new_value=new_val,
                    details=f"Deadline / date changed from {old_val} to {new_val}",
                )
            )

        # 4. Quantities & Thresholds (credits, days, etc.)
        if old_entities.quantities != new_entities.quantities:
            old_val = ", ".join(old_entities.quantities) or "None"
            new_val = ", ".join(new_entities.quantities) or "None"
            diffs.append(
                EntityDiffItem(
                    entity_type="threshold",
                    old_value=old_val,
                    new_value=new_val,
                    details=f"Quantitative threshold changed from {old_val} to {new_val}",
                )
            )
        elif set(old_entities.numbers) != set(new_entities.numbers) and not old_entities.percentages and not old_entities.currencies:
            old_val = ", ".join(old_entities.numbers) or "None"
            new_val = ", ".join(new_entities.numbers) or "None"
            diffs.append(
                EntityDiffItem(
                    entity_type="threshold",
                    old_value=old_val,
                    new_value=new_val,
                    details=f"Numerical value changed from {old_val} to {new_val}",
                )
            )

        # 5. Modality / Obligation ("must" vs "may")
        old_obl = set(old_entities.modals) & cls.MODAL_OBLIGATION
        new_obl = set(new_entities.modals) & cls.MODAL_OBLIGATION
        old_perm = set(old_entities.modals) & cls.MODAL_PERMISSION
        new_perm = set(new_entities.modals) & cls.MODAL_PERMISSION

        if (old_perm and new_obl) or (old_obl and new_perm):
            diffs.append(
                EntityDiffItem(
                    entity_type="modality",
                    old_value=", ".join(old_entities.modals) or "standard",
                    new_value=", ".join(new_entities.modals) or "standard",
                    details="Shift in obligation strength between discretionary ('may') and mandatory ('must')",
                )
            )

        # 6. Prohibitions & Permissions
        if set(old_entities.prohibitions) != set(new_entities.prohibitions):
            old_val = ", ".join(old_entities.prohibitions) or "None"
            new_val = ", ".join(new_entities.prohibitions) or "None"
            diffs.append(
                EntityDiffItem(
                    entity_type="prohibition",
                    old_value=old_val,
                    new_value=new_val,
                    details=f"Explicit prohibition status changed: {old_val} -> {new_val}",
                )
            )

        # 7. Negations
        if bool(old_entities.negations) != bool(new_entities.negations):
            old_val = ", ".join(old_entities.negations) or "Affirmative"
            new_val = ", ".join(new_entities.negations) or "Affirmative"
            diffs.append(
                EntityDiffItem(
                    entity_type="negation",
                    old_value=old_val,
                    new_value=new_val,
                    details=f"Logical negation flipped: '{old_val}' vs '{new_val}'",
                )
            )

        # 8. Eligibility Scope (restrictive cohorts)
        restrictive_old = {k for k in old_entities.eligibility_keywords if k != "all students"}
        restrictive_new = {k for k in new_entities.eligibility_keywords if k != "all students"}
        if restrictive_old != restrictive_new:
            old_val = ", ".join(sorted(restrictive_old)) or "General (all students)"
            new_val = ", ".join(sorted(restrictive_new)) or "General (all students)"
            diffs.append(
                EntityDiffItem(
                    entity_type="eligibility",
                    old_value=old_val,
                    new_value=new_val,
                    details=f"Target student eligibility group modified: '{old_val}' -> '{new_val}'",
                )
            )

        return diffs
