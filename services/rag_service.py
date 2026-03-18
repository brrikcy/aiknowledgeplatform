from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model= AutoModelForSeq2SeqLM.from_pretrained(model_name)

def generate_answer(question, context_chunks):

    context_text = "\n\n".join([
    f"Chunk {i+1}:\n{chunk}"
    for i, chunk in enumerate(context_chunks)
])
    prompt = f"""
Read the context and answer the question.

If the answer is not directly supported by the context, say:
"The information is not available in the provided documents"

Context:
{context_text}

Question:
{question}

Answer (based only on the context):
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = model.generate(
        **inputs,
        max_new_tokens=500,
        num_beams=4,
        early_stopping=True,
        temperature =0.3
    )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer
