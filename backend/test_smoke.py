import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("1. Testing config & db...")
from app.core.config import settings
from app.database.database import engine, Base
from app.database.models import ComparisonRecord, PolicyChangeRecord
Base.metadata.create_all(bind=engine)
print("   Config & DB OK!")

print("2. Testing services...")
from app.services.text_preprocessor import TextPreprocessor
from app.services.entity_extractor import EntityExtractor
from app.services.rule_segmenter import RuleSegmenter
from app.services.semantic_matcher import SemanticMatcher
from app.services.change_classifier import ChangeClassifier
from app.services.priority_analyzer import PriorityAnalyzer
from app.services.explanation_generator import ExplanationGenerator
from app.services.demo_generator import OLD_POLICY_TEXT, NEW_POLICY_TEXT, generate_sample_files
from app.services.comparison_service import ComparisonService
from app.evaluation.benchmark import evaluate_benchmark
print("   Services imports OK!")

print("3. Generating sample files...")
paths = generate_sample_files()
print(f"   Sample files generated: {list(paths.keys())}")

print("4. Testing evaluation benchmark...")
metrics = evaluate_benchmark()
print(f"   Benchmark evaluation: Accuracy={metrics.accuracy:.1%}, Macro-F1={metrics.macro_f1:.1%}")

print("5. Smoke test completed successfully!")
