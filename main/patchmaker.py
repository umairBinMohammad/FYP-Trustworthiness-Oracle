import openai
import re

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

def clean_code_block(text):
    # Remove triple backticks and language tags
    text = re.sub(r"^```(?:python)?", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"```$", "", text, flags=re.MULTILINE).strip()
    # Remove any leading 'Fixed Code:' label
    text = re.sub(r"^Fixed Code:\s*", "", text, flags=re.IGNORECASE).strip()
    return text