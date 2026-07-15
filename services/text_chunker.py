import re

def split_into_sentences(text: str) -> list[str]:
    text=text.strip()
    if not text:
        return []

    sentence_endings = re.compile(r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])\n+')
    sentences = sentence_endings.split(text)

    result=[]
    for s in sentences:
        s=s.strip()
        if s:
            result.append(s)

    return result

def chunk_text(text: str, chunk_size: int=500, overlap_sentences: int =1) -> list[str]:
    sentences = split_into_sentences(text)

    if not sentences:
        return []

    chunks = []
    current_chunk =  []
    current_length =0

    for sentence in sentences:
        sentence_length = len(sentence)

        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append("".join(current_chunk))

            overlap = current_chunk[-overlap_sentences:] if overlap_sentences > 0 else []
            current_chunk = overlap.copy()
            current_length = sum(len(s) for s in current_chunk)

        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append("".join(current_chunk))

    return chunks

