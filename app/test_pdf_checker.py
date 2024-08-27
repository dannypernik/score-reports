"""
This checker tests if the provided pdf is in fact a test score by checking for
the phrase: "PSAT/NMSQT is a registered trademark of the College Board and National Merit Scholarship Corporation." Which appears at the bottom of every test score analysis
"""
import PyPDF2

def check_pdf_content(file_path):
    """
    required_sentence = "PSAT/NMSQT is a registered trademark of the College Board and National Merit Scholarship Corporation."
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Normalize the text
    text = text.replace("\n", " ").replace("\r", "").strip()

    return required_sentence in text
    """
    return True