import pytest
from app.services.rule_segmenter import RuleSegmenter, RuleUnit
from app.services.document_extractor import ExtractedDocument, ExtractedPage
from app.services.entity_extractor import EntityExtractor
from app.services.semantic_matcher import SemanticMatcher
from app.services.change_classifier import ChangeClassifier
from app.services.priority_analyzer import PriorityAnalyzer
from app.services.explanation_generator import ExplanationGenerator


@pytest.fixture
def matcher():
    return SemanticMatcher()


def test_rule_segmentation():
    sample_text = """Section 1: Academic Attendance
1.1 Students must attend at least 75% of classes.
1.2 Medical leaves require a doctor's certificate.

Section 2: Examination Fees
2.1 Every student must pay $100 per semester.
"""
    doc = ExtractedDocument(
        filename="policy.txt",
        file_type="txt",
        full_text=sample_text,
        pages=[ExtractedPage(page_number=1, text=sample_text)],
        total_characters=len(sample_text),
    )
    rules = RuleSegmenter.segment_document(doc)
    assert len(rules) >= 3
    assert any("75%" in r.raw_text for r in rules)
    assert any(r.section_heading == "Academic Attendance" or "Attendance" in r.section_heading for r in rules)


def test_percentage_threshold_detection():
    old_text = "Students must maintain at least 75% attendance to take examinations."
    new_text = "Students must maintain at least 80% attendance to take examinations."

    o_ent = EntityExtractor.extract_entities(old_text)
    n_ent = EntityExtractor.extract_entities(new_text)
    diffs = EntityExtractor.compute_differences(o_ent, n_ent)

    assert any(d.entity_type == "percentage" for d in diffs)
    pct_diff = next(d for d in diffs if d.entity_type == "percentage")
    assert "75%" in pct_diff.old_value
    assert "80%" in pct_diff.new_value


def test_deadline_date_change():
    old_text = "Submissions close on 15 July 2025."
    new_text = "Submissions close on 30 July 2026."

    o_ent = EntityExtractor.extract_entities(old_text)
    n_ent = EntityExtractor.extract_entities(new_text)
    diffs = EntityExtractor.compute_differences(o_ent, n_ent)

    assert any(d.entity_type == "date" for d in diffs)
    date_diff = next(d for d in diffs if d.entity_type == "date")
    assert "15 July" in date_diff.old_value
    assert "30 July" in date_diff.new_value


def test_negation_and_prohibition_detection():
    old_text = "Late submissions are permitted with a $25 fine."
    new_text = "Late submissions are strictly prohibited under any circumstances."

    o_ent = EntityExtractor.extract_entities(old_text)
    n_ent = EntityExtractor.extract_entities(new_text)
    diffs = EntityExtractor.compute_differences(o_ent, n_ent)

    assert any(d.entity_type in ("prohibition", "modality", "monetary") for d in diffs)


def test_modality_shift_discretionary_to_mandatory():
    old_text = "Students may submit an appeal to the committee."
    new_text = "Students must submit an appeal to the committee."

    o_ent = EntityExtractor.extract_entities(old_text)
    n_ent = EntityExtractor.extract_entities(new_text)
    diffs = EntityExtractor.compute_differences(o_ent, n_ent)

    assert any(d.entity_type == "modality" for d in diffs)


def test_change_classification_modified(matcher):
    o_rule = RuleUnit(
        id="o1",
        raw_text="Students must maintain at least 75% attendance.",
        normalized_text="students must maintain at least 75% attendance.",
        section_heading="Attendance",
        page_number=1,
        order_index=0,
    )
    n_rule = RuleUnit(
        id="n1",
        raw_text="Students must maintain at least 80% attendance.",
        normalized_text="students must maintain at least 80% attendance.",
        section_heading="Attendance",
        page_number=1,
        order_index=0,
    )

    matches, _, _ = matcher.align_rules([o_rule], [n_rule])
    assert len(matches) == 1
    classified = ChangeClassifier.classify_match(matches[0])
    assert classified.change_type == "MODIFIED"

    priority = PriorityAnalyzer.assess_priority(classified)
    assert priority.priority in ("High", "Critical")

    explanation = ExplanationGenerator.generate_explanation(classified)
    assert "75%" in explanation and "80%" in explanation


def test_change_classification_added():
    n_rule = RuleUnit(
        id="n1",
        raw_text="All students must take the mandatory AI Ethics module.",
        normalized_text="all students must take the mandatory ai ethics module.",
        section_heading="Curriculum",
        page_number=1,
        order_index=0,
    )
    classified = ChangeClassifier.classify_added(n_rule)
    assert classified.change_type == "ADDED"

    explanation = ExplanationGenerator.generate_explanation(classified)
    assert "new rule has been introduced" in explanation.lower()


def test_change_classification_removed():
    o_rule = RuleUnit(
        id="o1",
        raw_text="Theses must be hardbound in red leatherette cloth.",
        normalized_text="theses must be hardbound in red leatherette cloth.",
        section_heading="Submissions",
        page_number=1,
        order_index=0,
    )
    classified = ChangeClassifier.classify_removed(o_rule)
    assert classified.change_type == "REMOVED"

    explanation = ExplanationGenerator.generate_explanation(classified)
    assert "rescinded" in explanation.lower() or "removed" in explanation.lower()
