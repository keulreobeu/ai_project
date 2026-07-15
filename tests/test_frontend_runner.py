import importlib.util
import os
from pathlib import Path


def load_run_frontend_module():
    module_path = Path(__file__).resolve().parents[1] / "frontend" / "run_frontend.py"
    spec = importlib.util.spec_from_file_location("run_frontend", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolve_npm_command_returns_a_available_command():
    module = load_run_frontend_module()
    command = module.resolve_npm_command()

    assert command is not None
    assert command.lower().endswith(("npm", "npm.cmd", "npm.exe", "npm.bat"))

    if os.name == "nt":
        assert command.lower().endswith(("npm.cmd", "npm.exe", "npm.bat")) or command.lower().endswith("npm")
