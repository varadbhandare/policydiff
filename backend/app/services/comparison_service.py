import uuid
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.services.document_extractor import DocumentExtractor, ExtractedDocument
from app.services.rule_segmenter import RuleSegmenter, RuleUnit
from app.services.semantic_matcher import SemanticMatcher
from app.services.change_classifier import ChangeClassifier, ClassifiedChange
from app.services.priority_analyzer import PriorityAnalyzer
from app.services.explanation_generator import ExplanationGenerator
from app.database.models import ComparisonRecord, PolicyChangeRecord
from app.schemas.comparison import (
    ComparisonResponse,
    ComparisonSummary,
    PolicyChangeSchema,
    EntityDiffItem,
)


class ComparisonService:
    def __init__(self, matcher: SemanticMatcher | None = None):
        self.matcher = matcher or SemanticMatcher()

    def process_and_compare(
        self,
        db: Session,
        old_file_bytes: bytes,
        old_filename: str,
        new_file_bytes: bytes,
        new_filename: str,
        title: str = "Policy Comparison",
        institution: str | None = None,
        old_version: str = "Old Policy",
        new_version: str = "New Policy",
    ) -> ComparisonResponse:
        # 1. Ingestion
        old_doc = DocumentExtractor.extract_from_bytes(old_file_bytes, old_filename)
        new_doc = DocumentExtractor.extract_from_bytes(new_file_bytes, new_filename)

        # 2. Rule & Sentence Segmentation
        old_rules = RuleSegmenter.segment_document(old_doc)
        new_rules = RuleSegmenter.segment_document(new_doc)

        # 3. Cross-version alignment
        aligned_matches, unmatched_old, unmatched_new = self.matcher.align_rules(
            old_rules, new_rules
        )

        # 4. Change Classification & Enrichment
        classified_changes: list[ClassifiedChange] = []

        # Process aligned matches (UNCHANGED or MODIFIED)
        for match in aligned_matches:
            c = ChangeClassifier.classify_match(match)
            classified_changes.append(c)

        # Process removed rules
        for o_rule in unmatched_old:
            c = ChangeClassifier.classify_removed(o_rule)
            classified_changes.append(c)

        # Process added rules
        for n_rule in unmatched_new:
            c = ChangeClassifier.classify_added(n_rule)
            classified_changes.append(c)

        # Sort changes by priority weight (Critical first, then High, Medium, Low) and type
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        type_order = {"MODIFIED": 0, "ADDED": 1, "REMOVED": 2, "UNCHANGED": 3}

        # 5. Build schemas and calculate statistics
        comparison_id = str(uuid.uuid4())
        change_schemas: list[PolicyChangeSchema] = []
        change_records: list[PolicyChangeRecord] = []

        added_cnt = 0
        removed_cnt = 0
        modified_cnt = 0
        unchanged_cnt = 0
        high_priority_cnt = 0

        for c in classified_changes:
            p_assessment = PriorityAnalyzer.assess_priority(c)
            explanation = ExplanationGenerator.generate_explanation(c)

            if c.change_type == "ADDED":
                added_cnt += 1
            elif c.change_type == "REMOVED":
                removed_cnt += 1
            elif c.change_type == "MODIFIED":
                modified_cnt += 1
            elif c.change_type == "UNCHANGED":
                unchanged_cnt += 1

            if p_assessment.priority in ("Critical", "High"):
                high_priority_cnt += 1

            change_id = str(uuid.uuid4())
            entities_json = json.dumps([d.model_dump() for d in c.entity_diffs])

            old_text = c.old_rule.raw_text if c.old_rule else None
            new_text = c.new_rule.raw_text if c.new_rule else None
            old_sec = c.old_rule.section_heading if c.old_rule else None
            new_sec = c.new_rule.section_heading if c.new_rule else None
            old_page = c.old_rule.page_number if c.old_rule else None
            new_page = c.new_rule.page_number if c.new_rule else None

            schema_obj = PolicyChangeSchema(
                id=change_id,
                comparison_id=comparison_id,
                change_type=c.change_type,
                category=c.category,
                priority=p_assessment.priority,
                priority_rationale=p_assessment.rationale,
                old_text=old_text,
                new_text=new_text,
                old_section=old_sec,
                new_section=new_sec,
                old_page=old_page,
                new_page=new_page,
                similarity_score=round(c.similarity_score, 3),
                alignment_confidence=round(c.alignment_confidence, 3),
                explanation=explanation,
                reason=c.reason,
                entities_diff=c.entity_diffs,
                is_reviewed=False,
            )
            change_schemas.append(schema_obj)

            rec_obj = PolicyChangeRecord(
                id=change_id,
                comparison_id=comparison_id,
                change_type=c.change_type,
                category=c.category,
                priority=p_assessment.priority,
                priority_rationale=p_assessment.rationale,
                old_text=old_text,
                new_text=new_text,
                old_section=old_sec,
                new_section=new_sec,
                old_page=old_page,
                new_page=new_page,
                similarity_score=round(c.similarity_score, 3),
                alignment_confidence=round(c.alignment_confidence, 3),
                explanation=explanation,
                reason=c.reason,
                entities_diff_json=entities_json,
                is_reviewed=False,
            )
            change_records.append(rec_obj)

        # Sort schemas logically
        change_schemas.sort(
            key=lambda x: (
                priority_order.get(x.priority, 99),
                type_order.get(x.change_type, 99),
            )
        )

        total_changes = added_cnt + removed_cnt + modified_cnt

        summary = ComparisonSummary(
            total_changes=total_changes,
            added_count=added_cnt,
            removed_count=removed_cnt,
            modified_count=modified_cnt,
            unchanged_count=unchanged_cnt,
            high_priority_count=high_priority_cnt,
        )

        # 6. Persist to SQLite
        comparison_record = ComparisonRecord(
            id=comparison_id,
            title=title or "Policy Document Comparison",
            institution=institution,
            old_filename=old_filename,
            new_filename=new_filename,
            old_version=old_version,
            new_version=new_version,
            created_at=datetime.now(timezone.utc),
            status="completed",
            total_changes=total_changes,
            added_count=added_cnt,
            removed_count=removed_cnt,
            modified_count=modified_cnt,
            unchanged_count=unchanged_cnt,
            high_priority_count=high_priority_cnt,
            nlp_engine=self.matcher.engine_name,
        )
        db.add(comparison_record)
        for r in change_records:
            db.add(r)
        db.commit()

        return ComparisonResponse(
            id=comparison_id,
            title=comparison_record.title,
            institution=comparison_record.institution,
            old_filename=comparison_record.old_filename,
            new_filename=comparison_record.new_filename,
            old_version=comparison_record.old_version,
            new_version=comparison_record.new_version,
            created_at=comparison_record.created_at,
            status=comparison_record.status,
            summary=summary,
            nlp_engine=comparison_record.nlp_engine,
            changes=change_schemas,
        )
