from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model= AutoModelForSeq2SeqLM.from_pretrained(model_name)

def generate_answer(question, context_chunks):

    context_text = "\n\n".join(context_chunks)

    prompt = f"""
Answer the question using the context below.

Context:
{context_text}

Question:
{question}

Provide a clear sentence answering the question based only on the context.
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = model.generate(
        **inputs,
        max_new_tokens=80,
        num_beams=4,
        early_stopping=True
    )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer
