import openai
import os
import shutil
import re

openai.api_key = "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"

bug_dir = os.path.join("Bug Tests", "Test 1")
bug_file_path = os.path.join(bug_dir, "bug.py")

# Read buggy code
with open(bug_file_path, "r", encoding="utf-8") as f:
    buggy_code = f.read()

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

# Get fixed code + explanation
result = fix_and_explain_code(buggy_code)

# Prepare output directory (two levels up from Bug Tests/Test 1)
output_dir = os.path.abspath(os.path.join(bug_dir, "..", ".."))

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

# Save patch in patch.py
patch_file_path = os.path.join(output_dir, "patch.py")
with open(patch_file_path, "w", encoding="utf-8") as f:
    f.write(fixed_code)

# Save explanation in explanation.txt
explanation_file_path = os.path.join(output_dir, "explanation.txt")
with open(explanation_file_path, "w", encoding="utf-8") as f:
    f.write(explanation.strip())

print(f"Files created in '{output_dir}':\n- patch.py (fixed code)\n- explanation.txt (explanation)\n- bug.py (original)")