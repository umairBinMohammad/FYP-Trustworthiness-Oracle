import openai
import re

OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

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