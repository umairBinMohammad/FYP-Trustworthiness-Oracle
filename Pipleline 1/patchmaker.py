import openai
import os
import shutil
import re

openai.api_key = "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"
folder_path = "Pipleline 1/Bug Tests"

def fix_and_explain_code(buggy_code):
    prompt = f"""
    You are a senior software engineer.
    The following code has a bug.
    1. Provide only the fixed code without extra explanation.
    2. Provide a detailed explanation of what was changed (after the fixed code, separated by a delimiter '---EXPLANATION---').
    3. If no bugs were found, the explanaton should be "NO BUGS FOUND".

    Code:
    {buggy_code}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message["content"]

# Clean up code output
def clean_code_block(text):
    # Remove triple backticks and language tags
    text = re.sub(r"^```(?:python)?", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"```$", "", text, flags=re.MULTILINE).strip()
    # Remove any leading 'Fixed Code:' label
    text = re.sub(r"^Fixed Code:\s*", "", text, flags=re.IGNORECASE).strip()
    return text

entries = os.scandir(folder_path)
for entry in entries:
    in_entries = os.scandir(folder_path + "/" + entry.name)
    for in_entry in in_entries:
        # Read buggy code
        if in_entry.name == "bug.py":
            with open(folder_path + "/" + entry.name + "/" + in_entry.name, "r", encoding="utf-8") as f:
                buggy_code = f.read()
                # Get fixed code + explanation
                result = fix_and_explain_code(buggy_code)
                if result == "NO BUGS FOUND":
                    fixed_code = ""
                    explanation = "No bugs were found"
                else: 
                    fixed_code, explanation = result.split("---EXPLANATION---", 1)
                    fixed_code = fixed_code.strip()
                    explanation = explanation.strip()
                print(explanation)
                # Clean the code output before saving
                fixed_code = clean_code_block(fixed_code)

                output_dir = folder_path + "/" + entry.name

                # Save patch in patch.py
                with open(output_dir + "/patch.py", "w", encoding="utf-8") as f:
                    f.write(fixed_code)

                # Save explanation in explanation.txt
                with open(output_dir + "/explanation.txt", "w", encoding="utf-8") as f:
                    f.write(explanation.strip())