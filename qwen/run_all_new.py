# run_all.py
import os
import subprocess
import sys
import shutil
import patchmaker # The model will be loaded automatically when this module is imported

MAIN_PATH = os.path.dirname(os.path.abspath(__file__))
EXTERNAL_PATH = os.path.abspath(os.path.join(MAIN_PATH, "..", "external"))
ALL_BUGS_ROOT = os.path.join(MAIN_PATH, "all_bugs")
BUGSINPY_ROOT = os.path.join(EXTERNAL_PATH, "bugsinpy", "projects")

def run_script(script_name):
    """Runs a Python script using subprocess."""
    script_path = os.path.join(MAIN_PATH, script_name)
    try:
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError:
        sys.exit(1)  # Stop further execution if a script fails

def get_modified_file_from_patch(patch_file):
    with open(patch_file, "r", encoding="utf-8") as f:
        first_line = f.readline()
        match = None
        if first_line.startswith("diff"):
            parts = first_line.split()
            for part in parts:
                if part.startswith("b/"):
                    match = part[2:]
                    break
        return match

def copy_and_patch_buggy_file(buggy_file_path):
    # Copy buggy file to main/code1.py
    shutil.copyfile(buggy_file_path, os.path.join(MAIN_PATH, "code1.py"))
    # Generate patched file using patchmaker.py
    with open(buggy_file_path, "r", encoding="utf-8") as f:
        buggy_code = f.read()
    
    # Fix the code using the patchmaker
    result = patchmaker.fix_and_explain_code(buggy_code)
    
    # Handle the case where no bug was found
    if result.strip().endswith("NO BUGS FOUND"):
        fixed_code = ""
    else:
        # Split the response and clean the fixed code block
        fixed_code, _ = result.split("---EXPLANATION---", 1)
        fixed_code = patchmaker.clean_code_block(fixed_code)
    
    with open(os.path.join(MAIN_PATH, "code2.py"), "w", encoding="utf-8") as f:
        f.write(fixed_code)

if __name__ == "__main__":
    # Loop through all projects in all_bugs
    for project_name in os.listdir(ALL_BUGS_ROOT):
        project_path = os.path.join(ALL_BUGS_ROOT, project_name)
        if not os.path.isdir(project_path):
            continue
        # Loop through all bugs in the project
        for bug_number in os.listdir(project_path):
            bug_path = os.path.join(project_path, bug_number)
            if not os.path.isdir(bug_path):
                continue
            print(f"Processing project: {project_name}, bug: {bug_number}")

            # Find corresponding bugsinpy folder
            bugsinpy_proj_path = os.path.join(BUGSINPY_ROOT, project_name, "bugs", bug_number)
            patch_file = os.path.join(bugsinpy_proj_path, "bug_patch.txt")
            if not os.path.exists(patch_file):
                print(f"Patch file not found: {patch_file}")
                continue

            modified_file_rel = get_modified_file_from_patch(patch_file)
            if not modified_file_rel:
                print("Could not determine modified file from patch.")
                continue

            modified_file_rel = modified_file_rel.replace("/", os.sep).replace("\\", os.sep)

            # Locate buggy file in all_bugs/project/bug/buggy
            buggy_file_path = os.path.join(bug_path, "buggy", project_name, modified_file_rel)
            if not os.path.exists(buggy_file_path):
                print(f"Buggy file not found: {buggy_file_path}")
                continue

            # Copy buggy file and generate patch
            copy_and_patch_buggy_file(buggy_file_path)

            # Change cwd to main before running analysis scripts
            os.chdir(MAIN_PATH)

            # Run analyser.py, json_to_nlp.py, comparison.py
            run_script("analyser.py")
            run_script("json_to_nlp.py")
            run_script("comparison.py")
