import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.rule_segmenter import RuleUnit
from app.services.semantic_matcher import SemanticMatcher
from app.services.change_classifier import ChangeClassifier
from app.services.entity_extractor import EntityExtractor
from app.evaluation.benchmark import BENCHMARK_DATASET

matcher = SemanticMatcher()

for s in BENCHMARK_DATASET:
    if s.expected_type == "UNCHANGED":
        o = RuleUnit(id="o", raw_text=s.old_text, normalized_text=s.old_text.lower(), order_index=0)
        n = RuleUnit(id="n", raw_text=s.new_text, normalized_text=s.new_text.lower(), order_index=0)
        matches, _, _ = matcher.align_rules([o], [n], match_threshold=0.3)
        m = matches[0]
        o_ent = EntityExtractor.extract_entities(s.old_text)
        n_ent = EntityExtractor.extract_entities(s.new_text)
        diffs = EntityExtractor.compute_differences(o_ent, n_ent)
        print(f"{s.id}: composite_sim={m.similarity_score:.3f}, lex_sim={m.lexical_similarity:.3f}, sem_sim={m.semantic_similarity:.3f}, diffs={len(diffs)}")
