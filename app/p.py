import tabula
import pandas as pd

# Define the path to the PDF file
pdf_path = "uploads/chrome.pdf"

try:
    # Read PDF into a list of DataFrame
    df_list = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    
    # Print each DataFrame in the list
    for df in df_list:
        print(df)
except Exception as e:
    print(f"An error occurred: {e}")
