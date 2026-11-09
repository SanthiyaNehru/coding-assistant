"""Simple RAG: chunk markdown docs, index with TF-IDF, retrieve top-k by cosine similarity.
No extra API key or model download needed. Can be swapped for embeddings + a vector DB later."""
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Retriever:
    def __init__(self, kb_dir: str = "knowledge_base"):
        self.chunks = []
        for p in sorted(Path(kb_dir).glob("*.md")):
            self._add(p.name, p.read_text(encoding="utf-8"))
        self._fit()

    def _add(self, source: str, text: str):
        for part in re.split(r"\n(?=#{1,3} )", text):
            part = part.strip()
            if len(part) > 40:
                self.chunks.append({"source": source, "text": part})

    def _fit(self):
        self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vec.fit_transform([c["text"] for c in self.chunks])

    def add_document(self, name: str, text: str):
        """Used when the student uploads their own notes."""
        self._add(name, text)
        self._fit()

    def search(self, query: str, k: int = 3, min_score: float = 0.05):
        if not self.chunks:
            return []
        scores = cosine_similarity(self.vec.transform([query]), self.matrix)[0]
        top = scores.argsort()[::-1][:k]
        return [{**self.chunks[i], "score": float(scores[i])} for i in top if scores[i] >= min_score]
