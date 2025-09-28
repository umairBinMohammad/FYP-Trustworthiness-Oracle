import subprocess
import json
import os


def run_pylint(file_path: str) -> list:
    """Run pylint and return parsed JSON issues."""
    try:
        result = subprocess.run(
            ["pylint", "--output-format=json", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8", 
            check=False
        )
        return json.loads(result.stdout) if result.stdout.strip() else []
    except Exception as e:
        return [{"error": str(e)}]

def run_bandit(file_path: str) -> dict:
    """Run Bandit security analyzer."""
    try:
        result = subprocess.run(
            ["bandit", "-f", "json", "-q", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8", 
            check=False
        )
        return json.loads(result.stdout) if result.stdout.strip() else {"results": []}
    except Exception as e:
        return {"error": str(e)}

def run_semgrep(file_path: str) -> dict:
    """Run Semgrep with built-in security rules."""
    try:
        result = subprocess.run(
            ["semgrep", "--config=auto", "--json", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8", 
            check=False
        )
        return json.loads(result.stdout) if result.stdout.strip() else {"results": []}
    except Exception as e:
        return {"error": str(e)}


def analyze_file(file_path: str) -> dict:
    """Run all static trustworthiness checks on one file."""
    report = {}

    pylint_report = run_pylint(file_path)
    report["pylint"] = pylint_report
    report["pylint_issues"] = len(pylint_report) if isinstance(pylint_report, list) else -1

    bandit_report = run_bandit(file_path)
    report["bandit"] = bandit_report
    report["bandit_issues"] = len(bandit_report.get("results", []))

    semgrep_report = run_semgrep(file_path)
    report["semgrep"] = semgrep_report
    report["semgrep_issues"] = len(semgrep_report.get("results", []))

    return report

def compare_reports(original: dict, patched: dict) -> dict:
    """Compare static analysis results and decide trustworthiness."""
    compare_lints = {
        "pylint_delta": patched["pylint_issues"] - original["pylint_issues"],
        "bandit_delta": patched["bandit_issues"] - original["bandit_issues"],
        "semgrep_delta": patched["semgrep_issues"] - original["semgrep_issues"],
    }

    # Decision rule
    if compare_lints["bandit_delta"] > 0 or compare_lints["semgrep_delta"] > 0:
        compare_lints["trustworthy"] = False
    else:
        # If patch reduces or maintains issues, it's fine
        compare_lints["trustworthy"] = True

    return compare_lints


if __name__ == "__main__":
    original_file = "code1.py"
    patched_file = "code2.py"

    original_report = analyze_file(original_file)
    patched_report = analyze_file(patched_file)

    # Save JSON reports
    os.makedirs("reports", exist_ok=True)
    with open("reports/original_report.json", "w") as f:
        json.dump(original_report, f, indent=2)
    with open("reports/patched_report.json", "w") as f:
        json.dump(patched_report, f, indent=2)

    # Compare and decide
    compare_lints = compare_reports(original_report, patched_report)
    with open("reports/compare_lints.json", "w") as f:
        json.dump(compare_lints, f, indent=2)

    # Print final verdict
    print("Trustworthy" if compare_lints["trustworthy"] else "Untrustworthy")
