from typing import NamedTuple
from app.services.rule_segmenter import RuleUnit
from app.services.semantic_matcher import SemanticMatcher
from app.services.change_classifier import ChangeClassifier
from app.services.priority_analyzer import PriorityAnalyzer
from app.schemas.comparison import EvaluationMetrics


class GroundTruthSample(NamedTuple):
    id: str
    old_text: str | None
    new_text: str | None
    section: str
    expected_type: str        # ADDED, REMOVED, MODIFIED, UNCHANGED
    expected_priority: str    # Critical, High, Medium, Low
    notes: str


BENCHMARK_DATASET: list[GroundTruthSample] = [
    GroundTruthSample(
        id="GT-01",
        old_text="Students must maintain at least 75% attendance to be eligible for end-semester examinations.",
        new_text="Students must maintain at least 80% attendance to be eligible for end-semester examinations.",
        section="Attendance & Leaves",
        expected_type="MODIFIED",
        expected_priority="High",
        notes="Numerical threshold change (75% -> 80%) with otherwise identical phrasing",
    ),
    GroundTruthSample(
        id="GT-02",
        old_text="Course drop applications must be submitted on or before 15 September 2025.",
        new_text="Course drop applications must be submitted on or before 30 September 2025.",
        section="Deadlines & Schedules",
        expected_type="MODIFIED",
        expected_priority="High",
        notes="Specific calendar deadline shifted forward by 15 days",
    ),
    GroundTruthSample(
        id="GT-03",
        old_text="Late submission of assignments is permitted with an administrative fine of $25.",
        new_text="Late submission of assignments is not permitted under any circumstances.",
        section="Academic Regulations",
        expected_type="MODIFIED",
        expected_priority="Critical",
        notes="Negation and permission reversed from allowed with fine to strictly prohibited",
    ),
    GroundTruthSample(
        id="GT-04",
        old_text="The examination re-evaluation fee shall be $50 per paper.",
        new_text="The examination re-evaluation fee shall be $75 per paper.",
        section="Financial & Fees",
        expected_type="MODIFIED",
        expected_priority="High",
        notes="Financial fee increase from $50 to $75",
    ),
    GroundTruthSample(
        id="GT-05",
        old_text="Students may submit an appeal to the grievance committee regarding grade disputes.",
        new_text="Students must submit a formal appeal to the grievance committee within 7 days of grade publication.",
        section="Examinations & Grading",
        expected_type="MODIFIED",
        expected_priority="High",
        notes="Modality shifted from discretionary ('may') to mandatory ('must') with timeframe constraint",
    ),
    GroundTruthSample(
        id="GT-06",
        old_text="All enrolled undergraduate students are eligible to apply for merit scholarships.",
        new_text="Only final-year undergraduate students with a minimum CGPA of 3.8 are eligible to apply for merit scholarships.",
        section="Eligibility & Admission",
        expected_type="MODIFIED",
        expected_priority="High",
        notes="Eligibility narrowed from all students to final-year students with GPA threshold",
    ),
    GroundTruthSample(
        id="GT-07",
        old_text="Students are required to attend all laboratory practical sessions with proper laboratory coats.",
        new_text="Proper laboratory coats must be worn by all students during scheduled laboratory practical sessions.",
        section="Attendance & Safety",
        expected_type="UNCHANGED",
        expected_priority="Low",
        notes="Passive vs active voice paraphrasing with identical operational mandate",
    ),
    GroundTruthSample(
        id="GT-08",
        old_text="The academic council shall convene twice annually to review degree qualifications.",
        new_text="The academic council meets twice every year in order to review degree qualifications.",
        section="Administrative & Governance",
        expected_type="UNCHANGED",
        expected_priority="Low",
        notes="Syntactic variation with identical semantic conditions",
    ),
    GroundTruthSample(
        id="GT-09",
        old_text=None,
        new_text="All graduating students must complete a mandatory 2-credit Artificial Intelligence and Research Ethics seminar.",
        section="Curriculum Requirements",
        expected_type="ADDED",
        expected_priority="High",
        notes="Brand new mandatory curriculum clause in the new document",
    ),
    GroundTruthSample(
        id="GT-10",
        old_text=None,
        new_text="Biometric attendance logs must be registered no later than 09:15 AM each instructional morning.",
        section="Attendance & Leaves",
        expected_type="ADDED",
        expected_priority="High",
        notes="Brand new attendance logging rule",
    ),
    GroundTruthSample(
        id="GT-11",
        old_text="Physical copies of doctoral dissertations must be bound in maroon leatherette cloth prior to viva voce.",
        new_text=None,
        section="Administrative & Governance",
        expected_type="REMOVED",
        expected_priority="Medium",
        notes="Obsolete physical binding clause removed in updated paperless regulations",
    ),
    GroundTruthSample(
        id="GT-12",
        old_text="Undergraduate students may request printed paper transcripts from the registrar window for $10.",
        new_text=None,
        section="Financial & Fees",
        expected_type="REMOVED",
        expected_priority="High",
        notes="Physical transcript request rule deleted",
    ),
    GroundTruthSample(
        id="GT-13",
        old_text="Possession of mobile phones during university examinations will result in immediate disqualification and debarment.",
        new_text="Possession of mobile phones or smartwatches during university examinations will result in immediate disqualification and debarment.",
        section="Examinations & Grading",
        expected_type="MODIFIED",
        expected_priority="Critical",
        notes="Expanded scope of debarment penalty to include smartwatches",
    ),
    GroundTruthSample(
        id="GT-14",
        old_text="A maximum of 2 backlog course attempts are permitted per academic term.",
        new_text="A maximum of 3 backlog course attempts are permitted per academic term.",
        section="Examinations & Grading",
        expected_type="MODIFIED",
        expected_priority="Medium",
        notes="Quantitative attempt threshold increased from 2 to 3",
    ),
    GroundTruthSample(
        id="GT-15",
        old_text="Tuition installment payments must be remitted by the 5th day of every calendar month.",
        new_text="Tuition installment payments must be remitted by the 10th day of every calendar month.",
        section="Financial & Fees",
        expected_type="MODIFIED",
        expected_priority="Medium",
        notes="Calendar date shift from 5th to 10th day",
    ),
    GroundTruthSample(
        id="GT-16",
        old_text="Students must display their official institutional identity card when entering the university library.",
        new_text="Valid university identity cards must be visibly carried upon entry to the campus library.",
        section="Administrative & Governance",
        expected_type="UNCHANGED",
        expected_priority="Low",
        notes="Equivalent administrative identification rule",
    ),
]


def evaluate_benchmark(matcher: SemanticMatcher | None = None) -> EvaluationMetrics:
    matcher = matcher or SemanticMatcher()
    y_true = []
    y_pred = []

    classes = ["ADDED", "REMOVED", "MODIFIED", "UNCHANGED"]
    confusion: dict[str, dict[str, int]] = {c1: {c2: 0 for c2 in classes} for c1 in classes}

    for sample in BENCHMARK_DATASET:
        expected = sample.expected_type
        y_true.append(expected)

        if sample.old_text is None and sample.new_text is not None:
            # ADDED
            n_rule = RuleUnit(
                id=sample.id,
                raw_text=sample.new_text,
                normalized_text=sample.new_text.lower(),
                section_heading=sample.section,
                page_number=1,
                order_index=0,
            )
            classified = ChangeClassifier.classify_added(n_rule)
            predicted = classified.change_type
        elif sample.old_text is not None and sample.new_text is None:
            # REMOVED
            o_rule = RuleUnit(
                id=sample.id,
                raw_text=sample.old_text,
                normalized_text=sample.old_text.lower(),
                section_heading=sample.section,
                page_number=1,
                order_index=0,
            )
            classified = ChangeClassifier.classify_removed(o_rule)
            predicted = classified.change_type
        else:
            # Compare pair
            o_rule = RuleUnit(
                id=f"{sample.id}_old",
                raw_text=sample.old_text,
                normalized_text=sample.old_text.lower(),
                section_heading=sample.section,
                page_number=1,
                order_index=0,
            )
            n_rule = RuleUnit(
                id=f"{sample.id}_new",
                raw_text=sample.new_text,
                normalized_text=sample.new_text.lower(),
                section_heading=sample.section,
                page_number=1,
                order_index=0,
            )
            matches, _, _ = matcher.align_rules([o_rule], [n_rule], match_threshold=0.30)
            if matches:
                classified = ChangeClassifier.classify_match(matches[0])
                predicted = classified.change_type
            else:
                predicted = "ADDED"

        y_pred.append(predicted)
        if expected in confusion and predicted in confusion[expected]:
            confusion[expected][predicted] += 1

    # Compute precision, recall, F1 per class and macro average
    per_class = {}
    precisions = []
    recalls = []
    f1s = []

    total_correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    accuracy = total_correct / len(y_true) if y_true else 0.0

    for c in classes:
        tp = confusion[c][c]
        fp = sum(confusion[other][c] for other in classes if other != c)
        fn = sum(confusion[c][other] for other in classes if other != c)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        per_class[c] = {
            "precision": round(prec, 3),
            "recall": round(rec, 3),
            "f1_score": round(f1, 3),
            "support": sum(confusion[c].values()),
        }
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

    macro_precision = round(sum(precisions) / len(precisions), 3)
    macro_recall = round(sum(recalls) / len(recalls), 3)
    macro_f1 = round(sum(f1s) / len(f1s), 3)

    return EvaluationMetrics(
        total_samples=len(y_true),
        accuracy=round(accuracy, 3),
        macro_precision=macro_precision,
        macro_recall=macro_recall,
        macro_f1=macro_f1,
        per_class=per_class,
        confusion_matrix=confusion,
    )
