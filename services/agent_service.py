import os
import time
import uuid
from services.hybrid_search import hybrid_search
from services.reranker_service import rerank
from services.rag_service import generate_answer, generate_answer_stream
from services.logger_service import get_logger

logger = get_logger("agent_service")

RETRIEVAL_CONFIDENCE_THRESHOLD = float(os.getenv("RETRIEVAL_CONFIDENCE_THRESHOLD", "-9.0"))


def run_agent(query: str) -> dict:
    request_id = str(uuid.uuid4())
    total_start = time.perf_counter()

    logger.info("request started", extra={"extra": {
        "request_id": request_id,
        "query": query
    }})

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
        "duration_ms": rerank_ms,
        "top_score": reranked_results[0]["rerank_score"] if reranked_results else None
    }})

    if not reranked_results or reranked_results[0]["rerank_score"] < RETRIEVAL_CONFIDENCE_THRESHOLD:
        total_ms = round((time.perf_counter() - total_start) * 1000)
        logger.warning("no relevant documents found", extra={"extra": {
            "request_id": request_id,
            "top_score": reranked_results[0]["rerank_score"] if reranked_results else None,
            "total_ms": total_ms
        }})
        return {
            "question": query,
            "answer": "The information is not available in the provided documents.",
            "context": []
        }

    context_chunks = reranked_results

    t0 = time.perf_counter()
    answer = generate_answer(query, context_chunks)
    llm_ms = round((time.perf_counter() - t0) * 1000)

    total_ms = round((time.perf_counter() - total_start) * 1000)

    logger.info("request completed", extra={"extra": {
        "request_id": request_id,
        "search_ms": search_ms,
        "rerank_ms": rerank_ms,
        "llm_ms": llm_ms,
        "total_ms": total_ms
    }})

    return {
        "question": query,
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
        "duration_ms": rerank_ms,
        "top_score": reranked_results[0]["rerank_score"] if reranked_results else None
    }})

    if not reranked_results or reranked_results[0]["rerank_score"] < RETRIEVAL_CONFIDENCE_THRESHOLD:
        yield "The information is not available in the provided documents."
        return

    context_chunks = reranked_results

    t0 = time.perf_counter()
    for token in generate_answer_stream(query, context_chunks):
        yield token
    llm_ms = round((time.perf_counter() - t0) * 1000)

    total_ms = round((time.perf_counter() - total_start) * 1000)

    logger.info("stream request completed", extra={"extra": {
        "request_id": request_id,
        "search_ms": search_ms,
        "rerank_ms": rerank_ms,
        "llm_ms": llm_ms,
        "total_ms": total_ms
    }})
