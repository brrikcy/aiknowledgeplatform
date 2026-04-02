from services.hybrid_search import hybrid_search
from services.reranker_service import rerank
from services.rag_service import generate_answer,llm,generate_answer_stream

INTENT_PROMPT = """Your job is to classify the user's question into exactly one of these categories:

    1. knowledge_base_query - the question is asking about specific information, facts, people, documents, or topics that would be found in an internal document database.
    2. out of scope - the question is a greeting, small talk, general knowledge question, or anything not related to searching internal documents.
    Respond with ONLY one of these two words, nothing else:
    knowledge_base_query
    out-of_scope

    User question: {query}

    Category: """

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
    intent = classify_intent(query)

    if intent == "out_of_scope":
        return {
            "question": query,
            "intent": intent,
            "answer": "This question is outside the scope of the internal knowledge base.",
            "context": []
        }

    search_results = hybrid_search(query)
    reranked_results = rerank(query, search_results)

    if not reranked_results:
        return {
            "question": query,
            "intent": intent,
            "answer": "No relevant documents found in the knowledge base.",
            "context": []
        }

    context_chunks = [r["chunk_text"] for r in reranked_results]
    answer = generate_answer(query, context_chunks)

    return {
        "question": query,
        "intent": intent,
        "answer": answer,
        "context": context_chunks
    }

def run_agent_stream(query:str):
    intent=classify_intent(query)

    if intent == "out_of_scope":
        yield "This question is outside the scope of internal knowledge base."
        return

    search_results=hybrid_search(query)
    reranked_results=rerank(query, search_results)

    if not reranked_results:
        yield "No relevant documents found in the knowledge base."
        return

    context_chunks=[r["chunk_text"] for r in reranked_results]

    for token in generate_answer_stream(query, context_chunks):
        yield token
