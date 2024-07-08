import tabula
import pandas as pd

# Define the path to the PDF file
pdf_path = "uploads/chrome.pdf"
first_name = "max"
last_name = "Attax"
test_code = 3

try:
    df_list = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    
    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Clean the DataFrame
    combined_df = combined_df[~combined_df["Question"].astype(str).str.contains("", na=False)]
    combined_df = combined_df.dropna(subset=["Question", "Section", "Correct Answer", "Your Answer", "Actions"])

    # Convert "Question" column to numeric for proper sorting
    combined_df["Question"] = pd.to_numeric(combined_df["Question"], errors='coerce')

    # Add the "Module" column
    combined_df['Module'] = ['1.1']*27 + ['1.2']*27 + ['2.1']*22 + ['2.2']*22

    # Sort the DataFrame by Section, Module, and Question
    combined_df = combined_df.sort_values(by=["Module", "Question"]).reset_index(drop=True)    

    # Print the entire DataFrame
    print(combined_df)

except Exception as e:
    print(f"An error occurred: {e}")
