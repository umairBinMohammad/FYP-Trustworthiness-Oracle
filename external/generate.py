#!/usr/bin/env python3
import os
import subprocess

# Directory outside your Git repo where all projects will be stored
OUTPUT_DIR = os.path.expanduser("~/projects/all_bugs")

# Map of project names to number of bugs
PROJECTS_BUGS = {
    "pysnooper": 3,
    "ansible": 18,
    "black": 23,
    "cookiecutter": 4,
    "fastapi": 16,
    "httpie": 5,
    "keras": 45,
    "luigi": 33,
    "matplotlib": 30,
    "pandas": 169,
    "sanic": 5,
    "scrapy": 40,
    "spacy": 10,
    "thefuck": 32,
    "tornado": 16,
    "tqdm": 9,
    "youtube-dl": 43
}

# Path to BugsInPy checkout command
CHECKOUT_CMD = os.path.expanduser("~/repos/BugsInPy/framework/bin/bugsinpy-checkout")

def run_cmd(cmd):
    """Run a shell command and print output."""
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def checkout_project_bug(project, bug_id):
    """Checkout both buggy (v0) and fixed (v1) versions of a bug."""
    bug_dir = os.path.join(OUTPUT_DIR, project, str(bug_id))
    buggy_dir = os.path.join(bug_dir, "buggy")
    fixed_dir = os.path.join(bug_dir, "fixed")

    os.makedirs(buggy_dir, exist_ok=True)
    os.makedirs(fixed_dir, exist_ok=True)

    # Checkout buggy version (v0)
    print(f"\n▶️ Checking out {project}, bug {bug_id}, version 0 (buggy)...")
    run_cmd([CHECKOUT_CMD, "-p", project, "-v", "0", "-i", str(bug_id), "-w", buggy_dir])

    # Checkout fixed version (v1)
    print(f"\n▶️ Checking out {project}, bug {bug_id}, version 1 (fixed)...")
    run_cmd([CHECKOUT_CMD, "-p", project, "-v", "1", "-i", str(bug_id), "-w", fixed_dir])

def checkout_all():
    """Checkout all projects and all their bugs."""
    for project, bug_count in PROJECTS_BUGS.items():
        print(f"\n=== Processing project: {project} ===")
        for bug_id in range(1, bug_count + 1):
            try:
                checkout_project_bug(project, bug_id)
            except subprocess.CalledProcessError as e:
                print(f"❌ Error on {project} bug {bug_id}: {e}")
                continue

if __name__ == "__main__":
    checkout_all()

