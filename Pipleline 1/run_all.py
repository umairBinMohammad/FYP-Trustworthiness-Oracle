# run_all.py
import subprocess
import os
import sys

def run_script(script_name):
    """Runs a Python script using subprocess."""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    print(f"▶️ Running {script_name}...")
    try:
        subprocess.run(["python", script_path], check=True)
        print(f"✅ {script_name} finished successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} failed with exit code {e.returncode}")
        sys.exit(1)  # Stop further execution if a script fails

if __name__ == "__main__":
    tests_path = "../Pipeline 1/Bug Tests"
    # Run analyser.py to create changes.json
    run_script("analyser.py")

    # Run json_to_nlp.py to create nlp_output.txt
    run_script("json_to_nlp.py")

    # Run comparison.py to compare explanation.txt and nlp_output.txt
    run_script("comparison.py")