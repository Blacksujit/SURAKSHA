import PyPDF2
import docx

def parse_document(uploaded_file):
    """Parses the uploaded document based on its file type."""
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == 'pdf':
        return parse_pdf(uploaded_file)
    elif file_type == 'docx':
        return parse_docx(uploaded_file)
    elif file_type == 'txt':
        return parse_txt(uploaded_file)
    else:
        raise ValueError("Unsupported file type")

def parse_pdf(uploaded_file):
    """Parses a PDF file and returns its text content."""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page].extract_text()
    return text

def parse_docx(uploaded_file):
    """Parses a DOCX file and returns its text content."""
    doc = docx.Document(uploaded_file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def parse_txt(uploaded_file):
    """Parses a TXT file and returns its content."""
    return uploaded_file.read().decode('utf-8')
