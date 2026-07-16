from llama_cpp import Llama
import os
MODEL_PATH = os.getenv("MODEL_PATH", "models/Phi-3-mini-4k-instruct-Q4_K_M.gguf")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_batch=512,
    n_threads=4,
    verbose=False
)


def generate_answer(question: str, context_chunks: list) -> str:
    context_parts = []
    for i, chunk in enumerate(context_chunks):
        if isinstance(chunk, dict):
            description = chunk.get("document_description", "")
            text = chunk.get("chunk_text", "")
            if description:
                context_parts.append(f"Chunk {i+1} [Source: {description}]:\n{text}")
            else:
                context_parts.append(f"Chunk {i+1}:\n{text}")
        else:
            context_parts.append(f"Chunk {i+1}:\n{chunk}")

    context_text = "\n\n".join(context_parts)

    if len(context_text) > 2000:
        context_text = context_text[:2000]

    response = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Answer the question using ONLY "
                    "the provided context. Each chunk is labeled with its source. "
                    "If the answer is not in the context, say exactly: "
                    "'The information is not available in the provided documents.'"
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion: {question}"
            }
        ],
        max_tokens=200,
        temperature=0.2,
        top_p=0.95,
        repeat_penalty=1.1
    )

    answer = response["choices"][0]["message"]["content"].strip()
    return answer


def generate_answer_stream(question: str, context_chunks: list):
    context_parts = []
    for i, chunk in enumerate(context_chunks):
        if isinstance(chunk, dict):
            description = chunk.get("document_description", "")
            text = chunk.get("chunk_text", "")
            if description:
                context_parts.append(f"Chunk {i+1} [Source: {description}]:\n{text}")
            else:
                context_parts.append(f"Chunk {i+1}:\n{text}")
        else:
            context_parts.append(f"Chunk {i+1}:\n{chunk}")

    context_text = "\n\n".join(context_parts)

    if len(context_text) > 2000:
        context_text = context_text[:2000]

    stream = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Answer the question using ONLY "
                    "the provided context. Each chunk is labeled with its source. "
                    "If the answer is not in the context, say exactly: "
                    "'The information is not available in the provided documents.'"
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion: {question}"
            }
        ],
        max_tokens=200,
        temperature=0.2,
        top_p=0.95,
        repeat_penalty=1.1,
        stream=True
    )

    for chunk in stream:
        delta = chunk["choices"][0]["delta"].get("content", "")
        if delta:
            yield delta




def generate_document_description(filename: str, text_preview: str) -> str:
    base_name = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").strip()

    prompt = f"""Given the following filename and document content preview, write exactly one sentence describing what this document is about. Be specific. Do not add any explanation.

Filename: {base_name}
Content preview: {text_preview[:500]}

One sentence description:"""

    response = llm.create_chat_completion(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=60,
        temperature=0.1,
        repeat_penalty=1.1
    )

    description = response["choices"][0]["message"]["content"].strip()

    # Fallback to filename-based description if LLM returns empty or garbage
    if not description or len(description) < 10:
        description = base_name

    return description

