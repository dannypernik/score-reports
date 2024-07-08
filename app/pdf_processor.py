import tabula
import pandas as pd
import json

def process_pdf(pdf_path, email, first_name, last_name, test_code):
    try:
        df_list = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        
        # Concatenate data
        combined_df = pd.concat(df_list, ignore_index=True)
        combined_df = combined_df[~combined_df["Question"].astype(str).str.contains("", na=False)]
        combined_df = combined_df.dropna(subset=["Question", "Section", "Correct Answer", "Your Answer", "Actions"])
        combined_df = combined_df.drop(columns=["Actions"])


        # Convert "Question" column to numeric for proper sorting
        combined_df["Question"] = pd.to_numeric(combined_df["Question"], errors='coerce')

        # Add the "Module" column
        combined_df['Module'] = ['1.1']*27 + ['1.2']*27 + ['2.1']*22 + ['2.2']*22

        combined_df = combined_df.sort_values(by=["Module", "Question"]).reset_index(drop=True)
        
        # Print the entire DataFrame
        print(combined_df)
        
        # Initialize the JSON structure
        student_answers = {
            'first_name': first_name,
            'last_name': last_name,
            'test_code': test_code,
            'answers': {
                'reading_writing': {
                    'module': {
                        '1.1': {},
                        '1.2': {}
                    }
                },
                'math': {
                    'module': {
                        '2.1': {},
                        '2.2': {}
                    }
                }
            }
        }
        
        # Map section names to keys used in the JSON structure
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