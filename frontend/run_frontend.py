import os
import shutil
import subprocess
from pathlib import Path


def resolve_npm_command():
    candidates = ["npm.cmd", "npm.exe", "npm.bat", "npm"]
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def start_frontend():
    root = Path(__file__).resolve().parent
    os.chdir(root)

    npm_command = resolve_npm_command()
    if not npm_command:
        raise FileNotFoundError("npm was not found in PATH. Install Node.js and ensure npm is available.")

    subprocess.Popen(
        [npm_command, "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"],
        cwd=root,
    )
    print("Frontend dev server started at http://127.0.0.1:5173")


if __name__ == "__main__":
    start_frontend()
