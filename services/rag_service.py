from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model= AutoModelForSeq2SeqLM.from_pretrained(model_name)


def generate_answer(question, context_chunks):

    context_text = "\n".join(context_chunks)

    prompt = f"""
    Answer the question using ONLY the information in the context below.

    Context:
    {context_text}

    Question: {question}

    Answer in a short paragraph:
    """

    inputs = tokenizer(prompt, return_tensors="pt", truncate=True)

    outputs = model.generate(
            **inputs,
            max_new_tokens=120)

    answer = tokenizer.decode(outputs[0],skip_special_tokens=True)

    return answer
