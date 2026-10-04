import re
from typing import List


class TextPreprocessingError(Exception):
    """Raised when the input text is empty or unusable after cleaning."""


def normalize_unicode_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)
    text = re.sub(r"[\t\v]+", " ", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    return text


def remove_extraction_artifacts(text: str) -> str:
    text = re.sub(r"(?m)^\s*[•●\-–—]+\s*$", "", text)
    text = re.sub(r"(?m)^\s*Page\s*\d+\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*\d+\s*$", "", text)
    text = re.sub(r"(?i)\bPDF\b", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    normalized = text.replace("。", ". ").replace("၊", "၊ ")
    normalized = normalized.replace("\n", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    sentence_pattern = r"[^.!?]+[.!?]*"
    sentences = [sent.strip() for sent in re.findall(sentence_pattern, normalized) if sent.strip()]
    if not sentences:
        return [normalized] if normalized else []
    return sentences


def preprocess_text(text: str) -> dict:
    if text is None or not str(text).strip():
        raise TextPreprocessingError("Input text is empty and cannot be preprocessed.")

    cleaned = normalize_unicode_whitespace(str(text))
    cleaned = remove_extraction_artifacts(cleaned)
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
    cleaned = re.sub(r"\n +", "\n", cleaned)
    sentences = split_into_sentences(cleaned)

    if not cleaned.strip() or not sentences:
        raise TextPreprocessingError("No usable Myanmar text remains after preprocessing.")

    return {
        "original_text": str(text),
        "cleaned_text": cleaned,
        "sentence_count": len(sentences),
        "sentences": sentences,
    }
