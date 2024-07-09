import pdfplumber
import pandas as pd

# Path to the PDF
pdf_path = "uploads/safari.pdf"  # Ensure this is the correct path to your PDF

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
    return text

def parse_text_to_dataframe(text):
    lines = text.split('\n')
    data = []
    for line in lines:
        if any(keyword in line for keyword in ["Correct", "Incorrect", "Omitted"]):
            parts = line.split()
            try:
                question = parts[0]
                section = " ".join(parts[1:-3])
                correct_answer = parts[-3]
                your_answer = " ".join(parts[-2:])
                data.append([question, section, correct_answer, your_answer])
            except IndexError:
                print(f"Could not parse line: {line}")
    return pd.DataFrame(data, columns=["Question", "Section", "Correct Answer", "Your Answer"])

try:
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Parse the text to create a DataFrame
    parsed_df = parse_text_to_dataframe(text)
    
    # Convert "Question" column to numeric for proper sorting
    parsed_df["Question"] = pd.to_numeric(parsed_df["Question"], errors='coerce')
    
    # Determine the lengths needed for the Module column
    n1_1 = min(len(parsed_df), 27)
    n1_2 = min(len(parsed_df) - n1_1, 27)
    n2_1 = min(len(parsed_df) - n1_1 - n1_2, 22)
    n2_2 = max(0, len(parsed_df) - n1_1 - n1_2 - n2_1)

    # Add the "Module" column dynamically
    parsed_df['Module'] = ['1.1']*n1_1 + ['1.2']*n1_2 + ['2.1']*n2_1 + ['2.2']*n2_2

    parsed_df = parsed_df.sort_values(by=["Module", "Question"]).reset_index(drop=True)
    
    # Print the cleaned DataFrame
    print(parsed_df)
    
except Exception as e:
    print(f"An error occurred: {e}")
