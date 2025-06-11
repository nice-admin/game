import subprocess
import sys
import os

if __name__ == "__main__":
    # Build the command for PyInstaller
    command = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--add-data", "data;data",
        "--name", "ALLANIMAL_GAME",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")
    ]
    print("Running:", " ".join(command))
    result = subprocess.run(command)
    if result.returncode == 0:
        print("Build succeeded.")
    else:
        print("Build failed.")
        sys.exit(result.returncode)
