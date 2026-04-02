import time
import uuid
from services.hybrid_search import hybrid_search
from services.reranker_service import rerank
from services.rag_service import generate_answer, generate_answer_stream, llm
from services.logger_service import get_logger

logger = get_logger("agent_service")

INTENT_PROMPT = """Your job is to classify the user's question into exactly one of these categories:

1. knowledge_base_query — the question is asking about specific information, facts, people, documents, or topics that would be found in an internal document database.
2. out_of_scope — the question is a greeting, small talk, general knowledge question, or anything not related to searching internal documents.

Respond with ONLY one of these two words, nothing else:
knowledge_base_query
out_of_scope

User question: {query}

Category:"""


def classify_intent(query: str) -> str:
    response = llm.create_chat_completion(
        messages=[
            {
                "role": "user",
                "content": INTENT_PROMPT.format(query=query)
            }
        ],
        max_tokens=10,
        temperature=0.0
    )
    raw = response["choices"][0]["message"]["content"].strip().lower()

    if "knowledge_base_query" in raw:
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

    context_chunks = [r["chunk_text"] for r in reranked_results]

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

    context_chunks = [r["chunk_text"] for r in reranked_results]

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
