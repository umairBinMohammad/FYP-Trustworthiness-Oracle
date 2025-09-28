import json

# Load your changes.json
with open("changes.json") as f:
    changes = json.load(f)

# Mapping rules
def to_natural_language(change: dict) -> str:
    ctype = change.get("type")
    
    if ctype == "var_rename":
        return f"Variable '{change['old']}' was renamed to '{change['new']}'."
    elif ctype == "var_value_change":
        return f"Value of variable '{change['target']}' changed from '{change['old']}' to '{change['new']}'."
    elif ctype == "condition_change":
        return f"Condition changed from '{change['old']}' to '{change['new']}'."
    elif ctype == "condition_added":
        return f"A new condition '{change['condition']}' was added in function '{change['function']}'."
    elif ctype == "statement_reordered":
        return f"Statement '{change['statement']}' moved from line {change['old_position']} to {change['new_position']} in function '{change['function']}'."
    elif ctype == "function_added":
        return f"Function '{change['function']}' was added."
    # Add more mappings as needed
    else:
        return f"Change of type '{ctype}' detected."


def convert_json_to_nlp(json_file: str, output_file: str):
    with open(json_file) as f:
        changes = json.load(f)

    with open(output_file, "w") as out:
        for func, func_changes in changes.items():
            out.write(f"Function: {func}\n")
            for change in func_changes:
                out.write(f"- {to_natural_language(change)}\n")
            out.write("\n")

if __name__ == "__main__":
    convert_json_to_nlp("changes.json", "nlp_output.txt")
    print("NLP output saved to nlp_output.txt.")
