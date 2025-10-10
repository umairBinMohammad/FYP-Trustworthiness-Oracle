import subprocess
import json


def run_radon(file_path):
    """
    Run radon CC (cyclomatic complexity) and MI (maintainability index).
    Returns parsed results as dict.
    """
    results = {}

    # Cyclomatic Complexity
    cc_cmd = ["radon", "cc", "-j", file_path]
    cc_output = subprocess.check_output(cc_cmd, text=True)
    results["cc"] = json.loads(cc_output)

    # Maintainability Index
    mi_cmd = ["radon", "mi", "-j", file_path]
    mi_output = subprocess.check_output(mi_cmd, text=True)
    results["mi"] = json.loads(mi_output)

    return results

def extract_avg_mi(mi_dict):
    """Extract average MI from radon output."""
    mi_values = [filedata["mi"] for filedata in mi_dict.values()]
    return sum(mi_values) / len(mi_values) if mi_values else 0

def extract_avg_cc(cc_dict):
    """Extract average Cyclomatic Complexity from radon output."""
    complexities = [item["complexity"] for blocks in cc_dict.values() for item in blocks]
    return sum(complexities) / len(complexities) if complexities else 0

def compare_complexity(original, patched):
    """
    Compare complexity & maintainability.
    Returns Trustworthy/Untrustworthy.
    """
    mi_original = extract_avg_mi(original["mi"])
    mi_patched = extract_avg_mi(patched["mi"])

    cc_original = extract_avg_cc(original["cc"])
    cc_patched = extract_avg_cc(patched["cc"])

    decision = "Trustworthy"

    # If MI dropped significantly (> 30 points), or complexity increased too much
    if mi_patched < mi_original - 30:
        decision = "Untrustworthy"
    elif cc_patched > cc_original + 3:  
        decision = "Untrustworthy"

    return {
        "mi_original": mi_original,
        "mi_patched": mi_patched,
        "cc_original": cc_original,
        "cc_patched": cc_patched,
        "decision": decision
    }

if __name__ == "__main__":
    # Hardcode your file names here
    orig_file = "code1.py"
    patched_file = "code2.py"

    original_results = run_radon(orig_file)
    patched_results = run_radon(patched_file)

    comparison = compare_complexity(original_results, patched_results)

    print("\n=== Complexity & Maintainability Check ===")
    print(f"Original MI Avg: {comparison['mi_original']:.2f}")
    print(f"Patched  MI Avg: {comparison['mi_patched']:.2f}")
    print(f"Original CC Avg: {comparison['cc_original']:.2f}")
    print(f"Patched  CC Avg: {comparison['cc_patched']:.2f}")
    print(f"\nDecision: {comparison['decision']}")
