
import subprocess
import shutil
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Define base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
VENV_DIR = BASE_DIR / "venv"
SCRIPTS_DIR = VENV_DIR / "Scripts"

# Helper to find executable in venv
def get_executable(name):
    """Finds the executable path in the virtual environment or system path."""
    if SCRIPTS_DIR.exists():
        exe_path = SCRIPTS_DIR / f"{name}.exe"
        if exe_path.exists():
            return str(exe_path)
    
    # Fallback to system path provided it is in the environment
    which = shutil.which(name)
    if which:
        return which
        
    return name

def run_command(command, cwd=None):
    """Runs a shell command and returns the output and exit code."""
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            cwd=cwd or BASE_DIR,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1

def run_architecture_check():
    """Runs import-linter for validation."""
    print("Running Architecture Check (import-linter)...")
    cmd = [get_executable("import-linter")]
    stdout, stderr, code = run_command(cmd)
    
    return {
        "tool": "import-linter",
        "command": "import-linter",
        "status": "PASS" if code == 0 else "FAIL",
        "output": stdout + stderr,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def run_type_check():
    """Runs mypy for strict type checking."""
    print("Running Type Check (mypy)...")
    cmd = [get_executable("mypy"), "--strict", "src/nikhil/pravaha"]
    stdout, stderr, code = run_command(cmd)
    
    # Simple parsing of errors
    error_count = stdout.count("error:")
    
    return {
        "tool": "mypy",
        "command": "mypy --strict src/nikhil/pravaha",
        "status": "PASS" if code == 0 else "FAIL",
        "output": stdout + stderr,
        "violation_count": error_count,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def run_complexity_check():
    """Runs ruff for complexity checking."""
    print("Running Complexity Check (ruff)...")
    # Note: ruff doesn't have --max-complexity flag
    # We use C901 rule and filter results, complexity threshold is set in pyproject.toml or ruff.toml
    cmd = [get_executable("ruff"), "check", "--select", "C901", "src/nikhil/pravaha"]
    stdout, stderr, code = run_command(cmd)
    
    # Simple parsing: ruff outputs one line per violation usually
    # C901 is the code for complexity
    violation_count = stdout.count("C901")
    
    return {
        "tool": "ruff",
        "command": "ruff check --select C901 src/nikhil/pravaha",
        "status": "PASS" if code == 0 else "FAIL",
        "output": stdout + stderr,
        "violation_count": violation_count,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
