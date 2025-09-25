#!/bin/bash

#==============================================================================
# SLURM Job Parameters
# These are your tutor's settings for the job.
#==============================================================================
#SBATCH --job-name=ModelDownload
#SBATCH --account=al49
#SBATCH --time=18:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=8192
#SBATCH --cpus-per-task=16
#SBATCH --partition=gpu
#SBATCH --gres=gpu:2

#==============================================================================
# Setup and Execution
# This section ensures everything runs correctly in a clean environment.
#==============================================================================
#echo "Starting job on host: $(hostname)"
#echo "Current directory: $(pwd)"
#echo "Job ID: $SLURM_JOB_ID"

# Load the miniforge3 module, which is the base for your environment.
module load miniforge3

# Set the environment variables. This is the crucial step.
# It ensures the Python script uses the scratch directory for caching.
# We are using the full absolute paths to avoid any ambiguity.
export HF_HOME=".cache/huggingface"
export PIP_CACHE_DIR=".cache/pip"

# Create the cache directories. This is idempotent, so it won't fail if they exist.
#mkdir -p "$HF_HOME"
#mkdir -p "$PIP_CACHE_DIR"

# Verify the environment variables are set before starting the script.
#echo "HF_HOME is set to: $HF_HOME"
#echo "PIP_CACHE_DIR is set to: $PIP_CACHE_DIR"

# Activate your Python virtual environment.
# We use the full path to ensure it's found from any directory.
source venv/bin/activate

# Check if the virtual environment is active.
# This will show a path like /path/to/venv/bin/python
which python

# Run your Python script.
python --version
python "$SLURM_SUBMIT_DIR/my_script.py"
# Optional: Deactivate your environment.
#deactivate

echo "Job finished."