from llama_cpp import Llama
import os
MODEL_PATH = os.getenv("MODEL_PATH", "models/Phi-3-mini-4k-instruct-Q4_K_M.gguf")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_batch=512,
    n_threads=4,
    verbose=False
)

def generate_answer(question: str, context_chunks: list[str]) -> str:
    context_text = "\n\n".join(
        f"Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)
    )

    if len(context_text) > 2000:
        context_text = context_text[:2000]

    response = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Answer the question using ONLY "
                    "the provided context. If the answer is not in the context, "
                    "say exactly: 'The information is not available in the provided documents.'"
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

def generate_answer_stream(question: str,context_chunks: list[str]):
    context_text = "\n\n".join(
            f"Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)
        )
    if len(context_text)>2000:
        context_text=context_text[:2000]

    stream = llm.create_chat_completion(
            messages=[
                {
                    "role" : "system",
                    "content" : (
                        "You are a helpful assistant. Answer the question using ONLY "
                        "the provided context. If the answer is not in the context,"
                        "say exactly: 'The information is not available in the provided documents'"
                    )
                },

                {
                    "role" : "user",
                    "content" : f"Context:\n{context_text}\n\nQuestion: {question}"
                }
            ],

            max_tokens=200,
            temperature=0.2,
            top_p=0.95,
            repeat_penalty=1.1,
            stream=True
        )

    for chunk in stream:
        delta = chunk["choices"][0]["delta"].get("content","")
        if delta:
            yield delta

