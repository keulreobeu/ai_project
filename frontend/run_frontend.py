import os
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
os.chdir(root)
subprocess.Popen(["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"], cwd=root)
print("Frontend dev server started at http://127.0.0.1:5173")
