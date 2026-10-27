import re
import numpy as np
from typing import Optional, NamedTuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz
from app.services.rule_segmenter import RuleUnit


class AlignmentMatch(NamedTuple):
    old_rule: Optional[RuleUnit]
    new_rule: Optional[RuleUnit]
    similarity_score: float
    alignment_confidence: float
    lexical_similarity: float
    semantic_similarity: float


class SemanticMatcher:
    def __init__(self, force_fallback: bool = False):
        self.engine_name = "TF-IDF N-Gram + RapidFuzz Cosine Alignment"
        self.is_fallback = True
        self._transformer_model = None

        if not force_fallback:
            try:
                from sentence_transformers import SentenceTransformer
                self._transformer_model = SentenceTransformer("all-MiniLM-L6-v2")
                self.engine_name = "Sentence-Transformers (all-MiniLM-L6-v2)"
                self.is_fallback = False
            except Exception:
                # Graceful fallback without crashing
                self.engine_name = "Lightweight Fallback (TF-IDF & Fuzzy Cosine Alignment)"
                self.is_fallback = True

    def compute_similarity_matrix(
        self, old_texts: list[str], new_texts: list[str]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes composite similarity matrix between old and new texts.
        Returns: (composite_matrix, semantic_matrix, lexical_matrix)
        """
        n_old = len(old_texts)
        n_new = len(new_texts)

        if n_old == 0 or n_new == 0:
            empty = np.zeros((n_old, n_new))
            return empty, empty, empty

        # 1. Semantic embeddings / vector similarity
        if self._transformer_model is not None and not self.is_fallback:
            try:
                old_embeddings = self._transformer_model.encode(old_texts, convert_to_numpy=True)
                new_embeddings = self._transformer_model.encode(new_texts, convert_to_numpy=True)
                semantic_sim = cosine_similarity(old_embeddings, new_embeddings)
            except Exception:
                semantic_sim = self._tfidf_cosine_sim(old_texts, new_texts)
        else:
            semantic_sim = self._tfidf_cosine_sim(old_texts, new_texts)

        # 2. Lexical similarity matrix using RapidFuzz
        lexical_sim = np.zeros((n_old, n_new))
        for i, old_t in enumerate(old_texts):
            for j, new_t in enumerate(new_texts):
                # Token set ratio handles word reorderings and paraphrasing
                ratio = fuzz.token_set_ratio(old_t, new_t) / 100.0
                lexical_sim[i, j] = ratio

        # 3. Composite score (60% semantic + 40% lexical)
        composite_sim = 0.60 * semantic_sim + 0.40 * lexical_sim

        return composite_sim, semantic_sim, lexical_sim

    def _tfidf_cosine_sim(self, old_texts: list[str], new_texts: list[str]) -> np.ndarray:
        corpus = old_texts + new_texts
        # Combine word n-grams and character n-grams to capture both conceptual roots and exact terms
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            sublinear_tf=True,
            analyzer="word",
            token_pattern=r"(?u)\b\w+\b|[%\$€£]",
        )
        try:
            tfidf_all = vectorizer.fit_transform(corpus)
            old_tfidf = tfidf_all[: len(old_texts)]
            new_tfidf = tfidf_all[len(old_texts) :]
            return cosine_similarity(old_tfidf, new_tfidf)
        except Exception:
            return np.zeros((len(old_texts), len(new_texts)))

    def align_rules(
        self,
        old_rules: list[RuleUnit],
        new_rules: list[RuleUnit],
        match_threshold: float = 0.48,
    ) -> tuple[list[AlignmentMatch], list[RuleUnit], list[RuleUnit]]:
        """
        Performs bipartite alignment between old and new rules.
        Returns:
            aligned_matches: list of AlignmentMatch (both old and new present)
            unmatched_old: list of RuleUnit (REMOVED candidates)
            unmatched_new: list of RuleUnit (ADDED candidates)
        """
        if not old_rules and not new_rules:
            return [], [], []
        if not old_rules:
            return [], [], new_rules
        if not new_rules:
            return [], old_rules, []

        old_clean = [r.normalized_text for r in old_rules]
        new_clean = [r.normalized_text for r in new_rules]

        comp_matrix, sem_matrix, lex_matrix = self.compute_similarity_matrix(old_clean, new_clean)

        # Apply section heading boost
        for i, o_rule in enumerate(old_rules):
            for j, n_rule in enumerate(new_rules):
                if o_rule.section_heading and n_rule.section_heading:
                    o_sec = o_rule.section_heading.lower().strip()
                    n_sec = n_rule.section_heading.lower().strip()
                    if o_sec == n_sec:
                        comp_matrix[i, j] = min(1.0, comp_matrix[i, j] + 0.06)

        # Greedy bipartite matching from highest similarity down to match_threshold
        candidates = []
        for i in range(len(old_rules)):
            for j in range(len(new_rules)):
                score = comp_matrix[i, j]
                if score >= match_threshold:
                    candidates.append((score, i, j))

        # Sort candidates descending by score
        candidates.sort(key=lambda x: x[0], reverse=True)

        matched_old_indices = set()
        matched_new_indices = set()
        aligned_matches: list[AlignmentMatch] = []

        for score, i, j in candidates:
            if i not in matched_old_indices and j not in matched_new_indices:
                matched_old_indices.add(i)
                matched_new_indices.add(j)

                # Confidence heuristic based on match margin
                confidence = float(np.clip(score * 1.05, 0.50, 0.99))
                aligned_matches.append(
                    AlignmentMatch(
                        old_rule=old_rules[i],
                        new_rule=new_rules[j],
                        similarity_score=float(score),
                        alignment_confidence=round(confidence, 3),
                        lexical_similarity=float(lex_matrix[i, j]),
                        semantic_similarity=float(sem_matrix[i, j]),
                    )
                )

        unmatched_old = [old_rules[i] for i in range(len(old_rules)) if i not in matched_old_indices]
        unmatched_new = [new_rules[j] for j in range(len(new_rules)) if j not in matched_new_indices]

        return aligned_matches, unmatched_old, unmatched_new
