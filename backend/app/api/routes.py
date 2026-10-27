import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import get_db
from app.database.models import ComparisonRecord, PolicyChangeRecord
from app.schemas.comparison import (
    ComparisonResponse,
    ComparisonSummary,
    ComparisonListItem,
    PolicyChangeSchema,
    ReviewUpdateRequest,
    EvaluationMetrics,
    EntityDiffItem,
)
from app.services.comparison_service import ComparisonService
from app.services.report_generator import ReportGenerator
from app.services.document_extractor import DocumentExtractionError, ScannedPdfError
from app.services.demo_generator import OLD_POLICY_TEXT, NEW_POLICY_TEXT
from app.evaluation.benchmark import evaluate_benchmark

router = APIRouter()
comparison_service = ComparisonService()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "nlp_engine": comparison_service.matcher.engine_name,
        "is_fallback": comparison_service.matcher.is_fallback,
    }


@router.post("/compare", response_model=ComparisonResponse)
async def compare_documents(
    old_file: UploadFile = File(...),
    new_file: UploadFile = File(...),
    title: str = Form("Academic Policy Comparison"),
    institution: Optional[str] = Form(None),
    old_version: str = Form("Previous Version"),
    new_version: str = Form("Updated Version"),
    db: Session = Depends(get_db),
):
    # Validate filenames and extensions
    old_ext = Path(old_file.filename).suffix.lower()
    new_ext = Path(new_file.filename).suffix.lower()

    if old_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Old file format '{old_ext}' is unsupported. Allowed: {list(settings.ALLOWED_EXTENSIONS)}",
        )
    if new_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"New file format '{new_ext}' is unsupported. Allowed: {list(settings.ALLOWED_EXTENSIONS)}",
        )

    # Read bytes with file size guard
    old_bytes = await old_file.read()
    new_bytes = await new_file.read()

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(old_bytes) > max_bytes:
        raise HTTPException(status_code=400, detail=f"Old file exceeds {settings.MAX_UPLOAD_SIZE_MB}MB size limit.")
    if len(new_bytes) > max_bytes:
        raise HTTPException(status_code=400, detail=f"New file exceeds {settings.MAX_UPLOAD_SIZE_MB}MB size limit.")

    if len(old_bytes) == 0:
        raise HTTPException(status_code=400, detail="Old document file is empty (0 bytes).")
    if len(new_bytes) == 0:
        raise HTTPException(status_code=400, detail="New document file is empty (0 bytes).")

    try:
        result = comparison_service.process_and_compare(
            db=db,
            old_file_bytes=old_bytes,
            old_filename=old_file.filename,
            new_file_bytes=new_bytes,
            new_filename=new_file.filename,
            title=title,
            institution=institution,
            old_version=old_version,
            new_version=new_version,
        )
        return result
    except ScannedPdfError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DocumentExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing policy comparison: {str(e)}")


@router.get("/comparisons", response_model=list[ComparisonListItem])
def list_comparisons(db: Session = Depends(get_db)):
    records = db.query(ComparisonRecord).order_by(ComparisonRecord.created_at.desc()).all()
    return records


@router.get("/comparisons/{comparison_id}", response_model=ComparisonResponse)
def get_comparison(comparison_id: str, db: Session = Depends(get_db)):
    rec = db.query(ComparisonRecord).filter(ComparisonRecord.id == comparison_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Comparison record not found")

    changes_db = db.query(PolicyChangeRecord).filter(PolicyChangeRecord.comparison_id == comparison_id).all()
    changes_schema = []

    for c in changes_db:
        diffs = []
        if c.entities_diff_json:
            try:
                raw_diffs = json.loads(c.entities_diff_json)
                diffs = [EntityDiffItem(**d) for d in raw_diffs]
            except Exception:
                diffs = []

        changes_schema.append(
            PolicyChangeSchema(
                id=c.id,
                comparison_id=c.comparison_id,
                change_type=c.change_type,
                category=c.category,
                priority=c.priority,
                priority_rationale=c.priority_rationale,
                old_text=c.old_text,
                new_text=c.new_text,
                old_section=c.old_section,
                new_section=c.new_section,
                old_page=c.old_page,
                new_page=c.new_page,
                similarity_score=c.similarity_score,
                alignment_confidence=c.alignment_confidence,
                explanation=c.explanation,
                reason=c.reason,
                entities_diff=diffs,
                is_reviewed=c.is_reviewed,
            )
        )

    # Sort schemas by priority
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    type_order = {"MODIFIED": 0, "ADDED": 1, "REMOVED": 2, "UNCHANGED": 3}
    changes_schema.sort(
        key=lambda x: (priority_order.get(x.priority, 99), type_order.get(x.change_type, 99))
    )

    summary = ComparisonSummary(
        total_changes=rec.total_changes,
        added_count=rec.added_count,
        removed_count=rec.removed_count,
        modified_count=rec.modified_count,
        unchanged_count=rec.unchanged_count,
        high_priority_count=rec.high_priority_count,
    )

    return ComparisonResponse(
        id=rec.id,
        title=rec.title,
        institution=rec.institution,
        old_filename=rec.old_filename,
        new_filename=rec.new_filename,
        old_version=rec.old_version,
        new_version=rec.new_version,
        created_at=rec.created_at,
        status=rec.status,
        summary=summary,
        nlp_engine=rec.nlp_engine,
        changes=changes_schema,
    )


@router.delete("/comparisons/{comparison_id}")
def delete_comparison(comparison_id: str, db: Session = Depends(get_db)):
    rec = db.query(ComparisonRecord).filter(ComparisonRecord.id == comparison_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Comparison record not found")
    db.delete(rec)
    db.commit()
    return {"message": "Comparison successfully deleted", "id": comparison_id}


@router.patch("/changes/{change_id}/review")
def update_review_status(change_id: str, body: ReviewUpdateRequest, db: Session = Depends(get_db)):
    rec = db.query(PolicyChangeRecord).filter(PolicyChangeRecord.id == change_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Change record not found")
    rec.is_reviewed = body.is_reviewed
    db.commit()
    return {"id": change_id, "is_reviewed": rec.is_reviewed}


@router.get("/comparisons/{comparison_id}/report/pdf")
def export_pdf_report(comparison_id: str, db: Session = Depends(get_db)):
    rec = db.query(ComparisonRecord).filter(ComparisonRecord.id == comparison_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Comparison record not found")
    changes = db.query(PolicyChangeRecord).filter(PolicyChangeRecord.comparison_id == comparison_id).all()

    pdf_bytes = ReportGenerator.generate_pdf(rec, changes)
    filename = f"PolicyDiff_Report_{rec.id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/comparisons/{comparison_id}/report/csv")
def export_csv_report(comparison_id: str, db: Session = Depends(get_db)):
    rec = db.query(ComparisonRecord).filter(ComparisonRecord.id == comparison_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Comparison record not found")
    changes = db.query(PolicyChangeRecord).filter(PolicyChangeRecord.comparison_id == comparison_id).all()

    csv_text = ReportGenerator.generate_csv(rec, changes)
    filename = f"PolicyDiff_Changes_{rec.id[:8]}.csv"
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/demo", response_model=ComparisonResponse)
def run_demo_comparison(db: Session = Depends(get_db)):
    # Check if a demo comparison already exists in database
    existing_demo = (
        db.query(ComparisonRecord)
        .filter(ComparisonRecord.title == "Apex University Academic Policy (2025 vs 2026)")
        .order_by(ComparisonRecord.created_at.desc())
        .first()
    )
    if existing_demo:
        return get_comparison(existing_demo.id, db)

    # Run real NLP comparison on the synthetic policy texts
    result = comparison_service.process_and_compare(
        db=db,
        old_file_bytes=OLD_POLICY_TEXT.encode("utf-8"),
        old_filename="Apex_University_Policy_2025.txt",
        new_file_bytes=NEW_POLICY_TEXT.encode("utf-8"),
        new_filename="Apex_University_Policy_2026.txt",
        title="Apex University Academic Policy (2025 vs 2026)",
        institution="Apex University Department of Academic Affairs",
        old_version="2025 Edition",
        new_version="2026 Edition",
    )
    return result


@router.get("/evaluation", response_model=EvaluationMetrics)
def run_evaluation():
    return evaluate_benchmark(comparison_service.matcher)
