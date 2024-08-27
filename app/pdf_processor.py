import tabula
import pandas as pd
import json
"""
if file is safari or chrome, this script should read the pdf, and 
"""

def process_pdf(pdf_path, email, first_name, last_name, math_score, reading_writing_score, total_score, test_code):
    try:
        # The first correct answers for module 2 that differ from module 3
        if test_code == '1':
            rw_mod_2_ans = ['C']
            m_mod_2_ans = ['B']
        elif test_code == '2':
            rw_mod_2_ans = ['B']
            m_mod_2_ans = ['B', 'B', 'B']
        elif test_code == '3':
            rw_mod_2_ans = ['B']
            m_mod_2_ans = ['B']
        elif test_code == '4':
            rw_mod_2_ans = ['D']
            m_mod_2_ans = ['B']
        elif test_code == '5':
            rw_mod_2_ans = ['C']
            m_mod_2_ans = ['B', 'C']
        elif test_code == '6':
            rw_mod_2_ans = ['A', 'C']
            m_mod_2_ans = ['B', 'B']
        else:
            raise ValueError("Invalid test code")

        df_list = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        
        # Concatenate data
        combined_df = pd.concat(df_list, ignore_index=True)
        combined_df = combined_df[~combined_df["Question"].astype(str).str.contains("", na=False)]
        combined_df = combined_df.dropna(subset=["Question", "Section", "Correct Answer", "Your Answer", "Actions"])
        combined_df = combined_df.drop(columns=["Actions"])
        combined_df["Question"] = pd.to_numeric(combined_df["Question"], errors='coerce')
        combined_df['Module'] = ['1.1']*27 + ['1.2']*27 + ['2.1']*22 + ['2.2']*22
        combined_df = combined_df.sort_values(by=["Module", "Question"]).reset_index(drop=True)
        
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

        # Determine the correct module for 1.2 and 2.2 based on answers
        def determine_module(section, correct_ans, module):
            length = len(correct_ans)
            given_ans = [row['Correct Answer'] for _, row in combined_df.iterrows() if row['Section'] == section and row['Module'] == module][:length]
            if given_ans == correct_ans:
                return '2'
            else:
                return '3'

        rw_module_1_2_or_3 = determine_module('Reading and Writing', rw_mod_2_ans, '1.2')
        m_module_1_2_or_3 = determine_module('Math', m_mod_2_ans, '1.2')

        rw_module_2_2_or_3 = determine_module('Reading and Writing', rw_mod_2_ans, '2.2')
        m_module_2_2_or_3 = determine_module('Math', m_mod_2_ans, '2.2')

        # Adjust the modules for 1.2 and 2.2 based on determined values
        combined_df.loc[(combined_df['Section'] == 'Reading and Writing') & (combined_df['Module'] == '1.2'), 'Module'] = f'{rw_module_1_2_or_3}'
        combined_df.loc[(combined_df['Section'] == 'Math') & (combined_df['Module'] == '1.2'), 'Module'] = f'{m_module_1_2_or_3}'

        combined_df.loc[(combined_df['Section'] == 'Reading and Writing') & (combined_df['Module'] == '2.2'), 'Module'] = f'{rw_module_2_2_or_3}'
        combined_df.loc[(combined_df['Section'] == 'Math') & (combined_df['Module'] == '2.2'), 'Module'] = f'{m_module_2_2_or_3}'

        # Adjust 1.1 and 2.1 modules
        combined_df.loc[combined_df['Module'] == '1.1', 'Module'] = '1'
        combined_df.loc[combined_df['Module'] == '2.1', 'Module'] = '1'

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