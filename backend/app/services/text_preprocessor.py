import re
import unicodedata
from typing import NamedTuple


class CleanedSentence(NamedTuple):
    original: str
    normalized: str


class TextPreprocessor:
    # Common abbreviations in academic / policy texts to protect from sentence splitting
    ABBREVIATIONS = {
        "dr.", "prof.", "mr.", "mrs.", "ms.", "e.g.", "i.e.", "etc.",
        "sec.", "no.", "vol.", "dept.", "approx.", "vs.", "al.", "art.",
        "para.", "sub-sec.", "ref.", "reg.", "inc.", "co."
    }

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Applies NFKC normalization and whitespace cleanup while preserving case and numbers."""
        if not text:
            return ""
        # Unicode normalization
        normalized = unicodedata.normalize("NFKC", text)
        # Normalize non-breaking spaces and irregular tabs
        normalized = normalized.replace("\xa0", " ").replace("\t", " ")
        # Replace carriage returns
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse multiple spaces but preserve single newlines
        normalized = re.sub(r"[ ]{2,}", " ", normalized)
        return normalized.strip()

    @classmethod
    def clean_for_comparison(cls, text: str) -> str:
        """
        Produces a normalized representation for lexical / semantic comparison.
        Preserves critical policy keywords: must, may, not, dates, percentages, numbers.
        """
        text = cls.normalize_text(text).lower()
        # Clean excessive punctuation while keeping essential ones: %, $, ., ,, -, /
        text = re.sub(r"[\"'\(\)\[\]\{\}]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @classmethod
    def split_into_sentences(cls, paragraph: str) -> list[str]:
        """
        Splits a paragraph into coherent sentences while avoiding false splits on abbreviations,
        decimal numbers (e.g., 75.5%), or section indices (e.g., 3.1).
        """
        text = cls.normalize_text(paragraph)
        if not text:
            return []

        # Replace known abbreviations temporarily with a marker
        protected = text
        for abbr in cls.ABBREVIATIONS:
            pattern = re.compile(re.escape(abbr), re.IGNORECASE)
            protected = pattern.sub(abbr.replace(".", "§DOT§"), protected)

        # Protect decimals like 75.5% or 3.1
        protected = re.sub(r'(\d+)\.(\d+)', r'\1§DOT§\2', protected)

        # Protect rule numbering like 1. or 2. at start or after space
        protected = re.sub(r'(^|\s)(\d+)\.(\s)', r'\1\2§DOT§\3', protected)

        # Sentence split on punctuation followed by whitespace and uppercase or end of string
        parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\(\[])', protected)

        results = []
        for part in parts:
            restored = part.replace("§DOT§", ".").strip()
            if restored:
                results.append(restored)

        return results
