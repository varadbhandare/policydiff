from app.evaluation.benchmark import evaluate_benchmark, BENCHMARK_DATASET


def test_benchmark_dataset_integrity():
    assert len(BENCHMARK_DATASET) >= 15
    for s in BENCHMARK_DATASET:
        assert s.id.startswith("GT-")
        assert s.expected_type in ("ADDED", "REMOVED", "MODIFIED", "UNCHANGED")
        assert s.expected_priority in ("Critical", "High", "Medium", "Low")


def test_evaluation_metrics_thresholds():
    metrics = evaluate_benchmark()
    assert metrics.total_samples == len(BENCHMARK_DATASET)
    # The NLP pipeline achieves over 85% accuracy and F1 score on the benchmark suite
    assert metrics.accuracy >= 0.85
    assert metrics.macro_f1 >= 0.85
    assert "MODIFIED" in metrics.per_class
    assert "ADDED" in metrics.per_class
    assert "REMOVED" in metrics.per_class
    assert "UNCHANGED" in metrics.per_class
