"""Yalnızca yerel modelleri kullanan tam RAG cevap hattı."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from config import DATABASE_PATH, TOP_K, UNKNOWN_RELEVANCE_THRESHOLD
from rag.database import KnowledgeDatabase
from rag.embeddings import FoundryEmbeddingModel
from rag.llm import FoundryChatModel
from rag.retrieval import RetrievedChunk, SemanticRetriever


SYSTEM_PROMPT = """Sen yalnızca belgelere dayanan bir Türkçe çalışma asistanısın.
Soruyu, sağlanan belge bağlamında açıkça yazan olguları kullanarak Türkçe cevapla.
Bağlam başka bir dilde olsa bile cevabın doğal ve anlaşılır Türkçe olmalıdır.
Ek yarar, neden, örnek veya açıklama çıkarımı yapma; genel bilgini kullanma.
Cevabı vermeden önce her olgusal iddianın doğrudan bir bağlam cümlesine dayandığını doğrula.
Bağlamdaki teknik terimleri, kısaltmaları ve kod adlarını değiştirmeden koru.
Soru bir liste istiyorsa bağlamda verilen ilgili öğeleri eksiksiz belirt.
Bağlam yeterli bilgi içermiyorsa yalnızca şunu söyle: "Bu bilgi sağlanan belgelerde bulunmuyor."
En fazla iki kısa cevap cümlesi döndür. Mümkün olduğunda bağlamdaki ifadeleri doğru biçimde Türkçeye aktar.
Sonuç, yorum, önem iddiası veya kaynak atfı ekleme; kaynaklar ayrıca gösterilecektir."""

UNKNOWN_ANSWER = "Bu bilgi sağlanan belgelerde bulunmuyor."


class ChatProvider(Protocol):
    def load(self) -> None: ...

    def complete_messages(self, messages: list[dict[str, str]]) -> str: ...

    def close(self) -> None: ...


@dataclass(frozen=True, slots=True)
class AnswerResult:
    answer: str
    sources: list[str]
    retrieved_chunks: list[RetrievedChunk]
    used_fallback: bool = False


def build_messages(question: str, chunks: list[RetrievedChunk]) -> list[dict[str, str]]:
    context = "\n\n".join(
        f"[Kaynak: {chunk.source}, parça {chunk.chunk_index}]\n{chunk.content}"
        for chunk in chunks
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Belge bağlamı:\n{context}\n\nSoru: {question}\n\n"
                "Doğrudan cevap ver; en fazla iki Türkçe cümle kullan ve teknik terimleri aynen koru."
            ),
        },
    ]


class RAGPipeline:
    """İki modeli birden çok soru boyunca yüklü tut ve sonunda temizle."""

    def __init__(
        self,
        database: KnowledgeDatabase | None = None,
        embedding_model: FoundryEmbeddingModel | None = None,
        chat_model: ChatProvider | None = None,
    ) -> None:
        self.database = database or KnowledgeDatabase(DATABASE_PATH)
        self.embedding_model = embedding_model or FoundryEmbeddingModel()
        self.chat_model = chat_model or FoundryChatModel()
        self.retriever = SemanticRetriever(self.database, self.embedding_model)
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        """Her iki yerel model de hazırsa doğru döndür."""
        return self._loaded

    def load(self) -> None:
        if self._loaded:
            return
        self.embedding_model.load()
        try:
            self.chat_model.load()
        except Exception:
            self.embedding_model.close()
            raise
        self._loaded = True

    def answer_query(self, question: str, top_k: int = TOP_K) -> AnswerResult:
        if not question.strip():
            raise ValueError("Soru boş olamaz.")
        self.load()
        chunks = self.retriever.get_top_chunks(question, top_k=top_k)
        if chunks[0].score < UNKNOWN_RELEVANCE_THRESHOLD:
            return AnswerResult(
                answer=UNKNOWN_ANSWER,
                sources=[],
                retrieved_chunks=chunks,
                used_fallback=True,
            )
        answer = self.chat_model.complete_messages(build_messages(question, chunks))
        sources = list(dict.fromkeys(chunk.source for chunk in chunks))
        return AnswerResult(answer=answer, sources=sources, retrieved_chunks=chunks)

    def close(self) -> None:
        try:
            self.chat_model.close()
        finally:
            self.embedding_model.close()
            self._loaded = False

    def __enter__(self) -> "RAGPipeline":
        self.load()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
