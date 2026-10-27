import re
from typing import Optional
from pydantic import BaseModel
from app.services.document_extractor import ExtractedDocument
from app.services.text_preprocessor import TextPreprocessor


class RuleUnit(BaseModel):
    id: str
    rule_number: Optional[str] = None
    section_heading: str = "General Policy"
    page_number: int = 1
    raw_text: str
    normalized_text: str
    order_index: int


class RuleSegmenter:
    # Heading patterns: "Section 1: ...", "1. Title", "ARTICLE 2 - ...", etc.
    HEADING_PATTERNS = [
        re.compile(r"^(?:section|sec\.|article|chapter|part)\s+[\w\d]+[\.:\s\-]+(.+)$", re.IGNORECASE),
        re.compile(r"^(\d+[\.\)]\s+[A-Z][A-Za-z0-9\s,\-–]{3,60})$"),
        re.compile(r"^([A-Z\s\-_–:]{4,60})$"),  # ALL CAPS HEADER
        re.compile(r"^([A-Z][A-Za-z0-9\s,\-–]{3,50}:)$"), # Header ending with colon
    ]

    # Rule item patterns: "1.1 ...", "a) ...", "(i) ...", "Rule 2: ..."
    RULE_ITEM_PATTERNS = [
        re.compile(r"^(\d+(?:\.\d+)+)\s+(.+)$"),       # 1.1 or 2.3.1
        re.compile(r"^(\([a-z0-9]+\))\s+(.+)$", re.IGNORECASE), # (a) or (1) or (i)
        re.compile(r"^([a-z]\))\s+(.+)$", re.IGNORECASE),        # a) or b)
        re.compile(r"^(?:rule|clause|policy)\s+(\d+[\.\:]?)\s+(.+)$", re.IGNORECASE),
        re.compile(r"^[•\-\*]\s+(.+)$"),              # Bullet point
    ]

    @classmethod
    def segment_document(cls, doc: ExtractedDocument) -> list[RuleUnit]:
        rule_units: list[RuleUnit] = []
        current_section = "General Policy"
        order_idx = 0

        for page in doc.pages:
            page_text = page.text
            lines = [l.strip() for l in page_text.split("\n") if l.strip()]
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Check if this line is a section heading
                is_heading = False
                for pattern in cls.HEADING_PATTERNS:
                    match = pattern.match(line)
                    if match and len(line) < 80:
                        # Don't treat a long sentence as a heading
                        extracted_heading = match.group(1).strip() if match.groups() else line
                        current_section = extracted_heading.rstrip(":")
                        is_heading = True
                        break
                
                if is_heading:
                    i += 1
                    continue

                # Check if this is a numbered or bulleted rule item
                rule_num: Optional[str] = None
                rule_text = line
                for pattern in cls.RULE_ITEM_PATTERNS:
                    match = pattern.match(line)
                    if match:
                        if len(match.groups()) == 2:
                            rule_num = match.group(1).strip()
                            rule_text = match.group(2).strip()
                        elif len(match.groups()) == 1:
                            rule_text = match.group(1).strip()
                        break

                # Combine subsequent indented or wrapped lines if they are continuations of this rule
                combined_text = [rule_text]
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    # Check if next_line is a new heading or new bullet/numbered rule
                    next_is_heading = any(p.match(next_line) and len(next_line) < 80 for p in cls.HEADING_PATTERNS)
                    next_is_rule = any(p.match(next_line) for p in cls.RULE_ITEM_PATTERNS)
                    
                    if next_is_heading or next_is_rule:
                        break
                    
                    # If line looks like a continuation (e.g. doesn't start with capital or previous didn't end with period)
                    if not combined_text[-1].endswith((".", "!", "?")) or len(combined_text[-1]) < 60:
                        combined_text.append(next_line)
                        j += 1
                    else:
                        break

                full_rule_str = " ".join(combined_text)
                i = j

                # Now, if the rule contains multiple distinct sentences, we can either keep as unit or sentence-split
                # Splitting long paragraphs into sentence units while keeping rule context ensures precise diffs
                sentences = TextPreprocessor.split_into_sentences(full_rule_str)
                if not sentences:
                    sentences = [full_rule_str]

                for s_idx, sentence in enumerate(sentences):
                    if len(sentence.strip()) < 8:
                        continue  # Skip trivial artifacts

                    unit_id = f"p{page.page_number}_r{order_idx + 1}"
                    sub_rule_num = f"{rule_num} (s{s_idx + 1})" if (rule_num and len(sentences) > 1) else rule_num

                    rule_units.append(
                        RuleUnit(
                            id=unit_id,
                            rule_number=sub_rule_num,
                            section_heading=current_section,
                            page_number=page.page_number,
                            raw_text=sentence,
                            normalized_text=TextPreprocessor.clean_for_comparison(sentence),
                            order_index=order_idx,
                        )
                    )
                    order_idx += 1

        return rule_units
