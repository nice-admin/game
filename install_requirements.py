import os
import subprocess
import sys

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to requirements.txt in the same folder
requirements_path = os.path.join(script_dir, "requirements.txt")

# Check if requirements.txt exists
if not os.path.isfile(requirements_path):
    print("requirements.txt not found in:", script_dir)
    sys.exit(1)

# Run pip install -r requirements.txt
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
except subprocess.CalledProcessError as e:
    print("An error occurred during installation.")
    sys.exit(e.returncode)
