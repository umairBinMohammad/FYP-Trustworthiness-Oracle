# import subprocess
# import json
# import os

# def run_command(cmd, desc):
#     """Run a shell command and print/log output."""
#     print(f"\n=== {desc} ===")
#     try:
#         result = subprocess.run(cmd, capture_output=True, text=True, check=False)
#         if result.stdout:
#             print(result.stdout.strip())
#         if result.stderr:
#             print("stderr:", result.stderr.strip())
#         return result
#     except Exception as e:
#         print(f"Error running {desc}: {e}")
#         return None


# def main():
#     os.makedirs("pipeline_reports", exist_ok=True)

#     # Step 1: Code + Explanation Check (Part 1 files)
#     run_command(["python", "analyser.py"], "Code Diff & Change Extraction")
#     run_command(["python", "json_to_nlp.py"], "Convert JSON → NLP Output")
#     run_command(["python", "comparison.py"], "Explanation vs NLP Match")

#     # Step 2: Linters & Security Check (Part 2 file)
#     run_command(["python", "static_analysis.py"], "Linting & Security Checks")

#     # Step 3: Complexity & Maintainability Check (Part 3 file)
#     run_command(["python", "complexity_analysis.py"], "Complexity & Maintainability Check")

#     print("\n=== Pipeline Complete ✅ ===")


# if __name__ == "__main__":
#     main()











import subprocess
import json
import os
import sys

# Ensure UTF-8 printing works on Windows
sys.stdout.reconfigure(encoding="utf-8")


def run_command(cmd, desc):
    """Run a shell command and print/log output. Returns captured stdout."""
    print(f"\n=== {desc} ===")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print("stderr:", result.stderr.strip())
        return result.stdout.strip() if result.stdout else ""
    except Exception as e:
        print(f"Error running {desc}: {e}")
        return ""


def is_trustworthy(output: str) -> bool:
    """Check if the script output contains 'Trustworthy'."""
    return "trustworthy" in output.lower()


def main():
    os.makedirs("pipeline_reports", exist_ok=True)

    # Track results
    decisions = {}

    # Step 1: Code + Explanation Check
    run_command(["python", "analyser.py"], "Code Diff & Change Extraction")
    run_command(["python", "json_to_nlp.py"], "Convert JSON → NLP Output")
    comparison_out = run_command(["python", "comparison.py"], "Explanation vs NLP Match")
    decisions["comparison"] = is_trustworthy(comparison_out)

    # Step 2: Linters & Security Check
    static_out = run_command(["python", "static_analysis.py"], "Linting & Security Checks")
    decisions["static_analysis"] = is_trustworthy(static_out)

    # Step 3: Complexity & Maintainability Check
    complexity_out = run_command(["python", "complexity_analysis.py"], "Complexity & Maintainability Check")
    decisions["complexity"] = is_trustworthy(complexity_out)

    # Print per-part decision
    print("\n=== Individual Decisions ===")
    for part, result in decisions.items():
        print(f"{part}: {'Trustworthy ✅' if result else 'Untrustworthy ❌'}")

    # Final decision
    if all(decisions.values()):
        print("\n=== FINAL DECISION: Trustworthy ✅ ===")
    else:
        print("\n=== FINAL DECISION: Untrustworthy ❌ ===")


if __name__ == "__main__":
    main()
