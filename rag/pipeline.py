"""Complete retrieval-augmented answer pipeline using only local models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from config import DATABASE_PATH, TOP_K, UNKNOWN_RELEVANCE_THRESHOLD
from rag.database import KnowledgeDatabase
from rag.embeddings import FoundryEmbeddingModel
from rag.llm import FoundryChatModel
from rag.retrieval import RetrievedChunk, SemanticRetriever


SYSTEM_PROMPT = """You are a strictly document-grounded study assistant.
Answer using only facts explicitly stated in the supplied document context.
Do not infer extra benefits, causes, examples, or explanations. Do not use general knowledge.
Before returning, ensure every factual claim can be traced directly to a context sentence.
If the context does not contain enough information, say exactly: "The information is not available in the provided documents."
Return exactly one short answer sentence. Reuse the context's wording where practical.
Do not add a conclusion, commentary, importance claim, or source citation; sources are shown separately."""

UNKNOWN_ANSWER = "The information is not available in the provided documents."


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
        f"[Source: {chunk.source}, chunk {chunk.chunk_index}]\n{chunk.content}"
        for chunk in chunks
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Document context:\n{context}\n\nQuestion: {question}\n\n"
                "Return only one directly supported answer sentence and nothing else."
            ),
        },
    ]


class RAGPipeline:
    """Keep both models loaded across multiple questions, then cleanly unload."""

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
            raise ValueError("Question cannot be empty.")
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
