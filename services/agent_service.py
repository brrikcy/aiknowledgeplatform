import os
import time
import uuid
import numpy as np
from services.hybrid_search import hybrid_search
from services.reranker_service import rerank
from services.rag_service import generate_answer, generate_answer_stream
from services.embedding_service import embedding_service
from services.logger_service import get_logger

logger = get_logger("agent_service")

INTENT_CLASSIFIER_ENABLED = os.getenv("INTENT_CLASSIFIER_ENABLED", "true").lower() == "true"

# Label embeddings computed once at startup — only if classifier is enabled
if INTENT_CLASSIFIER_ENABLED:
    _LABEL_KB = "find information about a specific person, their skills, experience, education, contact details, work history, projects, or any facts from uploaded documents and files"
    _LABEL_OOS = "hello hi good morning greeting thank you bye general knowledge about history science geography world events not related to any document"
    _kb_embedding = np.array(embedding_service.generate_embedding(_LABEL_KB))
    _oos_embedding = np.array(embedding_service.generate_embedding(_LABEL_OOS))


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def classify_intent(query: str) -> str:
    if not INTENT_CLASSIFIER_ENABLED:
        logger.info("classifier disabled — defaulting to knowledge_base_query")
        return "knowledge_base_query"

    query_embedding = np.array(embedding_service.generate_embedding(query))
    score_kb = _cosine_similarity(query_embedding, _kb_embedding)
    score_oos = _cosine_similarity(query_embedding, _oos_embedding)

    logger.info("intent scores", extra={"extra": {
        "knowledge_base_score": round(score_kb, 4),
        "out_of_scope_score": round(score_oos, 4)
    }})

    if score_kb > score_oos:
        return "knowledge_base_query"
    return "out_of_scope"

def run_agent(query: str) -> dict:
    request_id = str(uuid.uuid4())
    total_start = time.perf_counter()

    logger.info("request started", extra={"extra": {
        "request_id": request_id,
        "query": query
    }})

    t0 = time.perf_counter()
    intent = classify_intent(query)
    intent_ms = round((time.perf_counter() - t0) * 1000)

    logger.info("intent classified", extra={"extra": {
        "request_id": request_id,
        "intent": intent,
        "duration_ms": intent_ms
    }})

    if intent == "out_of_scope":
        total_ms = round((time.perf_counter() - total_start) * 1000)
        logger.info("request completed", extra={"extra": {
            "request_id": request_id,
            "total_ms": total_ms
        }})
        return {
            "question": query,
            "intent": intent,
            "answer": "This question is outside the scope of the internal knowledge base.",
            "context": []
        }

    t0 = time.perf_counter()
    search_results = hybrid_search(query)
    search_ms = round((time.perf_counter() - t0) * 1000)

    logger.info("hybrid search completed", extra={"extra": {
        "request_id": request_id,
        "results_count": len(search_results),
        "duration_ms": search_ms
    }})

    t0 = time.perf_counter()
    reranked_results = rerank(query, search_results)
    rerank_ms = round((time.perf_counter() - t0) * 1000)

    logger.info("reranking completed", extra={"extra": {
        "request_id": request_id,
        "results_count": len(reranked_results),
        "duration_ms": rerank_ms
    }})

    if not reranked_results:
        total_ms = round((time.perf_counter() - total_start) * 1000)
        logger.warning("no relevant documents found", extra={"extra": {
            "request_id": request_id,
            "total_ms": total_ms
        }})
        return {
            "question": query,
            "intent": intent,
            "answer": "No relevant documents found in the knowledge base.",
            "context": []
        }

    context_chunks = reranked_results

    t0 = time.perf_counter()
    answer = generate_answer(query, context_chunks)
    llm_ms = round((time.perf_counter() - t0) * 1000)

    total_ms = round((time.perf_counter() - total_start) * 1000)

    logger.info("request completed", extra={"extra": {
        "request_id": request_id,
        "intent_ms": intent_ms,
        "search_ms": search_ms,
        "rerank_ms": rerank_ms,
        "llm_ms": llm_ms,
        "total_ms": total_ms
    }})

    return {
        "question": query,
        "intent": intent,
        "answer": answer,
        "context": context_chunks
    }


def run_agent_stream(query: str):
    request_id = str(uuid.uuid4())
    total_start = time.perf_counter()

    logger.info("stream request started", extra={"extra": {
        "request_id": request_id,
        "query": query
    }})

    t0 = time.perf_counter()
    intent = classify_intent(query)
    intent_ms = round((time.perf_counter() - t0) * 1000)

    logger.info("intent classified", extra={"extra": {
        "request_id": request_id,
        "intent": intent,
        "duration_ms": intent_ms
    }})

    if intent == "out_of_scope":
        yield "This question is outside the scope of the internal knowledge base."
        return

    t0 = time.perf_counter()
    search_results = hybrid_search(query)
    search_ms = round((time.perf_counter() - t0) * 1000)

    logger.info("hybrid search completed", extra={"extra": {
        "request_id": request_id,
        "results_count": len(search_results),
        "duration_ms": search_ms
    }})

    t0 = time.perf_counter()
    reranked_results = rerank(query, search_results)
    rerank_ms = round((time.perf_counter() - t0) * 1000)

    logger.info("reranking completed", extra={"extra": {
        "request_id": request_id,
        "results_count": len(reranked_results),
        "duration_ms": rerank_ms
    }})

    if not reranked_results:
        yield "No relevant documents found in the knowledge base."
        return

    context_chunks = reranked_results

    t0 = time.perf_counter()
    for token in generate_answer_stream(query, context_chunks):
        yield token
    llm_ms = round((time.perf_counter() - t0) * 1000)

    total_ms = round((time.perf_counter() - total_start) * 1000)

    logger.info("stream request completed", extra={"extra": {
        "request_id": request_id,
        "intent_ms": intent_ms,
        "search_ms": search_ms,
        "rerank_ms": rerank_ms,
        "llm_ms": llm_ms,
        "total_ms": total_ms
    }})
