import json
import shutil
import sys
import subprocess
from pathlib import Path

# Common Paths
ROOT_DIR = Path(__file__).parent.parent.parent
SRC_DIR = ROOT_DIR / "src" / "nikhil" / "pravaha" / "domain"
DOCS_DIR = ROOT_DIR / "docs" / "test"
REPORTS_DIR = ROOT_DIR / ".Nibandha" / "Pravaha" / "Report"
TEMPLATES_DIR = ROOT_DIR / "docs" / "test" / "templates"

def load_json(path: Path):
    """Safe JSON load."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

def parse_outcome(data):
    """
    Parse standard pytest-json-report summary.
    Returns (passed, failed, total)
    """
    summary = data.get("summary", {})
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    # Total includes errors and skipped
    total = passed + failed + summary.get("skipped", 0) + summary.get("error", 0)
    return passed, failed, total

def get_all_modules():
    """Dynamically find top-level domain modules."""
    if not SRC_DIR.exists():
        return ["Auth", "Bot", "Storage", "Workflow"] # Fallback
    
    modules = []
    for item in SRC_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("__"):
            modules.append(item.name.capitalize())
    return sorted(modules)

def get_module_doc(module_name: str, report_type: str = "unit") -> str:
    """
    Try to read docs/test/<module>/<report_type>_test_scenarios.md
    """
    # Map casing: Auth -> auth
    mod_lower = module_name.lower()
    doc_path = DOCS_DIR / mod_lower / f"{report_type}_test_scenarios.md"
    
    if doc_path.exists():
        try:
            return doc_path.read_text(encoding="utf-8")
        except Exception:
            return "*Error reading documentation.*"
    return "*No documentation found for this module.*"

def run_pytest(target: str, report_name: str, cov_target: str = None) -> Path:
    """
    Run pytest and return path to JSON report.
    report_name: e.g. 'unit' -> unit.json
    cov_target: path to measure coverage for
    """
    json_path = REPORTS_DIR / f"{report_name}.json"
    
    cmd = [
        sys.executable, "-m", "pytest",
        target,
        f"--json-report",
        f"--json-report-file={json_path}",
    ]
    
    if cov_target:
        # For unit tests, we usually list specific packages to cover
        # or just use --cov=src/nikhil/pravaha
        cmd.extend([
            f"--cov={cov_target}",
            "--cov-report=json", # This saves to coverage.json in CWD
            "--cov-report=term"
        ])

    print(f"Running {report_name} tests on {target}...")
    try:
        subprocess.run(cmd, check=False, env={**sys.modules['os'].environ})
    except Exception as e:
        print(f"Error running pytest: {e}")
        
    return json_path

def analyze_coverage(cov_data):
    """
    Analyze coverage.json produced by pytest-cov.
    Returns ({module: pct}, total_pct)
    """
    if not cov_data:
        return {}, 0.0
        
    totals = cov_data.get("totals", {})
    total_pct = totals.get("percent_covered", 0.0)
    
    files = cov_data.get("files", {})
    module_cov = {}
    
    # We want to aggregate by domain module: src/nikhil/pravaha/domain/<mod>/...
    # Key in files is absolute path usually.
    
    mod_stats = {} # mod: {hits: 0, lines: 0}
    
    for fpath, stats in files.items():
        # Normalize path separators
        fpath = fpath.replace("\\", "/")
        if "src/nikhil/pravaha/domain/" in fpath:
            parts = fpath.split("src/nikhil/pravaha/domain/")
            if len(parts) > 1:
                sub = parts[1] # e.g. auth/model/access_key.py
                mod_name = sub.split("/")[0].capitalize()
                
                if mod_name not in mod_stats:
                    mod_stats[mod_name] = {"hits": 0, "lines": 0}
                
                summary = stats.get("summary", {})
                mod_stats[mod_name]["hits"] += summary.get("covered_lines", 0)
                mod_stats[mod_name]["lines"] += summary.get("num_statements", 0)
                
    # Calculate percentages
    results = {}
    for mod, s in mod_stats.items():
        if s["lines"] > 0:
            results[mod] = (s["hits"] / s["lines"]) * 100
        else:
            results[mod] = 0.0
            
            
    return results, total_pct

def save_report(path: Path, content: str):
    """Saves content to the specified path, creating directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Report saved to: {path}")
    except Exception as e:
        print(f"Error saving report to {path}: {e}")
