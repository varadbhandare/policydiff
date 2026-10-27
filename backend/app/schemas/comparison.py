from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class EntityDiffItem(BaseModel):
    entity_type: str  # percentage, date, monetary, threshold, modality, negation, eligibility
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    details: Optional[str] = None


class PolicyChangeSchema(BaseModel):
    id: str
    comparison_id: str
    change_type: str  # ADDED, REMOVED, MODIFIED, UNCHANGED
    category: str
    priority: str      # Critical, High, Medium, Low
    priority_rationale: Optional[str] = None
    old_text: Optional[str] = None
    new_text: Optional[str] = None
    old_section: Optional[str] = None
    new_section: Optional[str] = None
    old_page: Optional[int] = None
    new_page: Optional[int] = None
    similarity_score: float = 0.0
    alignment_confidence: float = 1.0
    explanation: str
    reason: Optional[str] = None
    entities_diff: list[EntityDiffItem] = []
    is_reviewed: bool = False

    model_config = ConfigDict(from_attributes=True)


class ComparisonSummary(BaseModel):
    total_changes: int
    added_count: int
    removed_count: int
    modified_count: int
    unchanged_count: int
    high_priority_count: int


class ComparisonResponse(BaseModel):
    id: str
    title: str
    institution: Optional[str] = None
    old_filename: str
    new_filename: str
    old_version: str
    new_version: str
    created_at: datetime
    status: str
    summary: ComparisonSummary
    nlp_engine: str
    changes: list[PolicyChangeSchema]

    model_config = ConfigDict(from_attributes=True)


class ComparisonListItem(BaseModel):
    id: str
    title: str
    institution: Optional[str] = None
    old_filename: str
    new_filename: str
    old_version: str
    new_version: str
    created_at: datetime
    total_changes: int
    high_priority_count: int
    added_count: int
    removed_count: int
    modified_count: int

    model_config = ConfigDict(from_attributes=True)


class ReviewUpdateRequest(BaseModel):
    is_reviewed: bool


class EvaluationMetrics(BaseModel):
    total_samples: int
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    per_class: dict[str, dict[str, float]]
    confusion_matrix: dict[str, dict[str, int]]
