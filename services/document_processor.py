import fitz
import docx

def extract_text_from_txt(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def extract_text_from_pdf(file_path):

    text=""

    pdf=fitz.open(file_path)

    for page in pdf:
        text += page.get_text()

    return text

def extract_text_from_docx(file_path):
    doc=docx.Document(file_path)

    text=[]

    for paragraph in doc.paragraphs:
        text.append(paragraph.text)

    return "\n".join(text)


def extract_text(file_path):

    if file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)

    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)

    if file_path.endwith(".docx"):
        return extract_text_from_docx(file_path)

    return ""
