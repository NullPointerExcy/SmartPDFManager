import PyPDF2


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        first_page = reader.pages[0]
        text = first_page.extract_text()
        return text.strip()
