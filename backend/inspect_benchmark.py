import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.evaluation.benchmark import evaluate_benchmark
metrics = evaluate_benchmark()
print(f"Accuracy: {metrics.accuracy:.1%}")
print(f"Macro F1: {metrics.macro_f1:.1%}")
print("Per class:")
for k, v in metrics.per_class.items():
    print(f"  {k}: {v}")
print("Confusion matrix:")
for row_k, row_v in metrics.confusion_matrix.items():
    print(f"  {row_k}: {row_v}")
