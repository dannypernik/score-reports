import pdfplumber
import pandas as pd
import json

# Path to the PDF
pdf_path = "uploads/safari.pdf"  # Ensure this is the correct path to your PDF

# Example input data (replace with actual data if available)
first_name = "max"
last_name = "Attax"
test_code = 1
math_score = 0  # Placeholder, replace with actual score
reading_writing_score = 0  # Placeholder, replace with actual score
total_score = 0  # Placeholder, replace with actual score

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
    combined_df = parse_text_to_dataframe(text)
    
    # Convert "Question" column to numeric for proper sorting
    combined_df["Question"] = pd.to_numeric(combined_df["Question"], errors='coerce')
    
    # Determine the lengths needed for the Module column
    n1_1 = min(len(combined_df), 27)
    n1_2 = min(len(combined_df) - n1_1, 27)
    n2_1 = min(len(combined_df) - n1_1 - n1_2, 22)
    n2_2 = max(0, len(combined_df) - n1_1 - n1_2 - n2_1)

    # Add the "Module" column dynamically
    combined_df['Module'] = ['1.1']*n1_1 + ['1.2']*n1_2 + ['2.1']*n2_1 + ['2.2']*n2_2

    combined_df = combined_df.sort_values(by=["Module", "Question"]).reset_index(drop=True)
    
    # Print the cleaned DataFrame
    print(combined_df)

    # Example correct answers for rw_mod_2 and m_mod_2
    rw_mod_2_ans = ['C']
    m_mod_2_ans = ['B']

    # Function to determine the correct module
    def determine_module(section, correct_ans, module):
        length = len(correct_ans)
        given_ans = combined_df[(combined_df['Section'] == section) & (combined_df['Module'] == module)]['Correct Answer'][:length].tolist()
        return '2' if given_ans == correct_ans else '3'

    # Determine the correct module for 1.2 and 2.2 based on answers
    rw_module_1_2_or_3 = determine_module('Reading and Writing', rw_mod_2_ans, '1.2')
    m_module_1_2_or_3 = determine_module('Math', m_mod_2_ans, '1.2')
    rw_module_2_2_or_3 = determine_module('Reading and Writing', rw_mod_2_ans, '2.2')
    m_module_2_2_or_3 = determine_module('Math', m_mod_2_ans, '2.2')

    # Adjust the modules for 1.2 and 2.2 based on determined values
    combined_df.loc[(combined_df['Section'] == 'Reading and Writing') & (combined_df['Module'] == '1.2'), 'Module'] = rw_module_1_2_or_3
    combined_df.loc[(combined_df['Section'] == 'Math') & (combined_df['Module'] == '1.2'), 'Module'] = m_module_1_2_or_3
    combined_df.loc[(combined_df['Section'] == 'Reading and Writing') & (combined_df['Module'] == '2.2'), 'Module'] = rw_module_2_2_or_3
    combined_df.loc[(combined_df['Section'] == 'Math') & (combined_df['Module'] == '2.2'), 'Module'] = m_module_2_2_or_3

    # Adjust 1.1 and 2.1 modules
    combined_df.loc[combined_df['Module'] == '1.1', 'Module'] = '1'
    combined_df.loc[combined_df['Module'] == '2.1', 'Module'] = '1'

    # Print the final DataFrame
    print(combined_df)

    # Construct the student answers dictionary
    student_answers = {
        'first_name': first_name,
        'last_name': last_name,
        'test_code': test_code,
        'math_score': math_score,
        'reading_writing_score': reading_writing_score,
        'score': total_score,
        'answers': {
            'reading_writing': {
                'module': {
                    '1': {},
                    '2': {},
                    '3': {}
                }
            },
            'math': {
                'module': {
                    '1': {},
                    '2': {},
                    '3': {}
                }
            }
        }
    }
    
    section_mapping = {
        'Reading and Writing': 'reading_writing',
        'Math': 'math'
    }

    # Populate the JSON structure
    for _, row in combined_df.iterrows():
        section = section_mapping[row['Section']]
        question = str(int(row['Question']))
        module = row['Module']
        
        if module not in student_answers['answers'][section]['module']:
            student_answers['answers'][section]['module'][module] = {}
        
        student_answers['answers'][section]['module'][module][question] = {
            'correct_answer': row['Correct Answer'],
            'your_answer': row['Your Answer'],
        }
    
    # Save the JSON data to a file
    with open("sorted_data.json", "w") as json_file:
        json.dump(student_answers, json_file, indent=4)
    
    print("DataFrame successfully cleaned, sorted, and saved to sorted_data.json")

except Exception as e:
    print(f"An error occurred: {e}")
