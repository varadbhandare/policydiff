import datetime
import json
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class ComparisonRecord(Base):
    __tablename__ = "comparisons"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=True)
    old_filename = Column(String(255), nullable=False)
    new_filename = Column(String(255), nullable=False)
    old_version = Column(String(100), default="Old Policy")
    new_version = Column(String(100), default="New Policy")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    status = Column(String(50), default="completed")
    
    total_changes = Column(Integer, default=0)
    added_count = Column(Integer, default=0)
    removed_count = Column(Integer, default=0)
    modified_count = Column(Integer, default=0)
    unchanged_count = Column(Integer, default=0)
    high_priority_count = Column(Integer, default=0)
    
    nlp_engine = Column(String(100), default="TF-IDF + RapidFuzz Cosine Alignment")
    
    changes = relationship("PolicyChangeRecord", back_populates="comparison", cascade="all, delete-orphan")


class PolicyChangeRecord(Base):
    __tablename__ = "policy_changes"

    id = Column(String(36), primary_key=True, index=True)
    comparison_id = Column(String(36), ForeignKey("comparisons.id"), nullable=False, index=True)
    
    change_type = Column(String(50), nullable=False)  # ADDED, REMOVED, MODIFIED, UNCHANGED
    category = Column(String(100), nullable=False)     # Attendance, Examinations, etc.
    priority = Column(String(50), nullable=False)     # Critical, High, Medium, Low
    priority_rationale = Column(Text, nullable=True)
    
    old_text = Column(Text, nullable=True)
    new_text = Column(Text, nullable=True)
    old_section = Column(String(255), nullable=True)
    new_section = Column(String(255), nullable=True)
    old_page = Column(Integer, nullable=True)
    new_page = Column(Integer, nullable=True)
    
    similarity_score = Column(Float, default=0.0)
    alignment_confidence = Column(Float, default=1.0)
    
    explanation = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    entities_diff_json = Column(Text, nullable=True)  # JSON-encoded extracted diffs
    
    is_reviewed = Column(Boolean, default=False)
    
    comparison = relationship("ComparisonRecord", back_populates="changes")
