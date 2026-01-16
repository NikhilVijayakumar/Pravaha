
import os
import json
import pytest
import datetime
import shutil
import pandas as pd
import seaborn as sns
import sys
import matplotlib.pyplot as plt
from pathlib import Path

# Config
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
REPORTS_DIR = PROJECT_ROOT / ".Nibandha/Pravaha/Report"
TEMPLATES_DIR = PROJECT_ROOT / "docs/test/templates"
DOCS_TEST_DIR = PROJECT_ROOT / "docs/test"

def run_tests(suite_dir: Path):
    """Run tests for a specific suite and return the path to the json report."""
    suite_dir.mkdir(parents=True, exist_ok=True)
    
    # Update Environment to include source paths
    # We need 'src/nikhil' in path so 'import pravaha' works (if using namespace style)
    # OR 'src' if using 'import nikhil.pravaha'
    # Based on test files: from pravaha... -> implies src/nikhil needs to be in path
    env = os.environ.copy()
    src_ptr = PROJECT_ROOT / "src" / "nikhil"
    src_root = PROJECT_ROOT / "src"
    
    # Add both to be safe
    current_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_ptr};{src_root};{current_path}"
    
    # We must patch sys.path for the in-process pytest run as well
    sys.path.insert(0, str(src_root))
    sys.path.insert(0, str(src_ptr))
    
    # 1. Unit Tests + Coverage
    print("Running Unit Tests with Coverage...")
    unit_json = suite_dir / "unit.json"
    cov_json = suite_dir / "coverage.json"
    
    # Run ALL unit tests
    unit_targets = ["tests/unit"]
    
    pytest.main([
        "--json-report",
        f"--json-report-file={unit_json}",
        "--cov=src/nikhil/pravaha",
        f"--cov-report=json:{cov_json}",
        *unit_targets
    ])

    # 2. E2E Tests
    print("Running E2E Tests...")
    e2e_json = suite_dir / "e2e.json"
    
    # Similarly, target our stable E2E suite
    e2e_targets = ["tests/e2e"]
    
    pytest.main([
        "--json-report",
        f"--json-report-file={e2e_json}",
        *e2e_targets
    ])

    return unit_json, e2e_json, cov_json

def _load_json(path: Path):
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def _parse_outcome(data):
    summary = data.get("summary", {})
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    total = passed + failed + summary.get("skipped", 0) + summary.get("error", 0)
    return passed, failed, total

def get_module_doc(module_name: str, doc_type: str = "unit") -> str:
    """Read specific documentation file for a module."""
    # Map module name to directory (e.g. Auth -> auth)
    dir_name = module_name.lower()
    doc_path = DOCS_TEST_DIR / dir_name / f"{doc_type}_test_scenarios.md"
    
    if not doc_path.exists():
        return "*No documentation found for this module.*"
        
    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
            return content
    except Exception as e:
        return f"*Error reading documentation: {e}*"

def get_all_modules() -> list[str]:
    """Discover all domain modules."""
    domain_dir = PROJECT_ROOT / "src/nikhil/pravaha/domain"
    if not domain_dir.exists():
        return []
    
    modules = []
    for d in domain_dir.iterdir():
        if d.is_dir() and not d.name.startswith("__"):
            modules.append(d.name.capitalize())
    return sorted(modules)

def analyze_coverage(cov_data):
    """Analyze coverage data and return a dict of {Module: Coverage%}."""
    files = cov_data.get("files", {})
    module_stats = {}
    
    # Initialize with all known modules
    for mod in get_all_modules():
        module_stats[mod] = {"hits": 0, "lines": 0}

    if files:
        for fname, metrics in files.items():
            # src/nikhil/pravaha/domain/xyz/...
            parts = fname.replace("\\", "/").split("/")
            if "domain" in parts:
                idx = parts.index("domain")
                if idx + 1 < len(parts):
                    mod_name = parts[idx + 1].capitalize()
                    
                    if mod_name not in module_stats:
                        module_stats[mod_name] = {"hits": 0, "lines": 0}
                        
                    module_stats[mod_name]["hits"] += metrics["summary"]["covered_lines"]
                    module_stats[mod_name]["lines"] += metrics["summary"]["num_statements"]
    
    # Calculate percentages
    results = {}
    total_hits = 0
    total_lines = 0
    
    for mod, data in module_stats.items():
        pct = (data["hits"] / data["lines"] * 100) if data["lines"] > 0 else 0
        results[mod] = pct
        total_hits += data["hits"]
        total_lines += data["lines"]
        
    total_cov = (total_hits / total_lines * 100) if total_lines > 0 else 0
    return results, total_cov

def generate_visualizations(suite_dir: Path, unit_res, e2e_res, cov_map):
    """Generate charts for the report."""
    sns.set_theme(style="whitegrid")
    
    # 1. Coverage Chart
    if cov_map:
        plot_data = [{"Module": mod, "Coverage": pct} for mod, pct in cov_map.items()]
        
        if plot_data:
            df = pd.DataFrame(plot_data)
            plt.figure(figsize=(10, 5))
            sns.barplot(data=df, x="Module", y="Coverage", palette="viridis")
            plt.title("Code Coverage by Module")
            plt.ylim(0, 100)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(suite_dir / "coverage_chart.png")
            plt.close()

    # 2. Test Distribution (Combined)
    u_pass, u_fail, u_tot = _parse_outcome(unit_res)
    e_pass, e_fail, e_tot = _parse_outcome(e2e_res)
    
    labels = ['Unit Passed', 'Unit Failed', 'E2E Passed', 'E2E Failed']
    sizes = [u_pass, u_fail, e_pass, e_fail]
    colors = ['#66BB6A', '#EF5350', '#42A5F5', '#AB47BC']
    
    # Filter zeros
    clean_labels = [l for l, s in zip(labels, sizes) if s > 0]
    clean_sizes = [s for s in sizes if s > 0]
    clean_colors = [c for l, s, c in zip(labels, sizes, colors) if s > 0]

    plt.figure(figsize=(6, 6))
    if clean_sizes:
        plt.pie(clean_sizes, labels=clean_labels, colors=clean_colors, autopct='%1.1f%%')
    else:
        plt.text(0.5, 0.5, "No Tests Run", ha='center')
        
    plt.title("Total Test Distribution")
    plt.savefig(suite_dir / "distribution_chart.png")
    plt.close()
    
    # 3. E2E Specific Pie
    plt.figure(figsize=(4, 4))
    e_sizes = [e_pass, e_fail]
    e_labels = ['Passed', 'Failed']
    if sum(e_sizes) > 0:
        plt.pie(e_sizes, labels=e_labels, colors=['#42A5F5', '#AB47BC'], autopct='%1.1f%%')
        plt.title("E2E Status")
    plt.savefig(suite_dir / "e2e_status.png")
    plt.close()

def render_reports(suite_dir: Path, unit_res, e2e_res, cov_map, total_cov, timestamp):
    """Render the Markdown files."""
    
    # --- PROCESS DATA ---
    all_modules = get_all_modules()
    
    # Unit Data Processing
    u_tests = unit_res.get("tests", [])
    u_passed, u_failed, u_total = _parse_outcome(unit_res)
    u_rate = (u_passed / u_total * 100) if u_total > 0 else 0
    
    # Group results by module
    module_results = {mod: {"total": 0, "pass": 0, "fail": 0, "tests": []} for mod in all_modules}
    # Also catch unknown modules
    module_results["Unknown"] = {"total": 0, "pass": 0, "fail": 0, "tests": []}
    
    for t in u_tests:
        # path extraction: tests/unit/domain/<module>/...
        # OR src/nikhil/pravaha/domain/<module>/... if nodeid is source-based (rare in pytest json)
        # usually: tests/unit/domain/auth/test_auth.py::TestClass::test_method
        parts = t["nodeid"].replace("\\", "/").split("/")
        mod = "Unknown"
        if "domain" in parts:
            idx = parts.index("domain")
            if idx + 1 < len(parts):
                mod = parts[idx + 1].capitalize()
        
        if mod not in module_results:
            module_results[mod] = {"total": 0, "pass": 0, "fail": 0, "tests": []}
        
        module_results[mod]["total"] += 1
        if t["outcome"] == "passed":
            module_results[mod]["pass"] += 1
        else:
            module_results[mod]["fail"] += 1
        module_results[mod]["tests"].append(t)

    # Clean up "Unknown" if empty
    if module_results["Unknown"]["total"] == 0:
        del module_results["Unknown"]

    # E2E Data
    e_tests = e2e_res.get("tests", [])
    e_passed, e_failed, e_total = _parse_outcome(e2e_res)
    e_rate = (e_passed / e_total * 100) if e_total > 0 else 0
    
    total_duration = unit_res.get("duration", 0) + e2e_res.get("duration", 0)
    
    # --- RENDER OVERVIEW ---
    try:
        with open(TEMPLATES_DIR / "overview_report_template.md", encoding="utf-8") as f:
            ov_tmpl = f.read()
    except FileNotFoundError:
        ov_tmpl = "# Overview\nFile not found."

    crit_issues = ""
    if u_failed > 0:
        crit_issues += f"- ❌ **{u_failed} Unit Test Failures** detected.\n"
    if e_failed > 0:
        crit_issues += f"- ❌ **{e_failed} E2E Test Failures** detected.\n"
    if not crit_issues:
        crit_issues = "✅ No critical issues found."

    ov_content = ov_tmpl.format(
        date=timestamp,
        total_duration=total_duration,
        suite_status="✅ Passing" if (u_failed + e_failed) == 0 else "❌ Failing",
        unit_pass_rate=u_rate,
        e2e_pass_rate=e_rate,
        coverage_total=total_cov,
        critical_issues=crit_issues
    )
    
    with open(suite_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(ov_content)

    # --- RENDER UNIT REPORT ---
    try:
        with open(TEMPLATES_DIR / "unit_report_template.md", encoding="utf-8") as f:
            u_tmpl = f.read()
    except FileNotFoundError:
        u_tmpl = "# Unit Report\nTemplate not found."

    # Module Table construction
    mod_table = ""
    det_sections = ""
    
    for mod in sorted(module_results.keys()):
        data = module_results[mod]
        cov_val = cov_map.get(mod, 0)
        
        # Color code coverage
        cov_str = f"{cov_val:.1f}%"
        if cov_val < 50 and data['total'] > 0:
            cov_str = f"🔴 {cov_str}"
        elif cov_val > 80:
            cov_str = f"🟢 {cov_str}"
        
        mod_table += f"| {mod} | {data['total']} | {data['pass']} | {data['fail']} | {cov_str} |\n"
        
        # Detailed Section
        det_sections += f"### Module: {mod}\n\n"
        
        # 1. Documentation
        det_sections += "#### Documentation Scenarios\n\n"
        det_sections += get_module_doc(mod, "unit")
        det_sections += "\n\n"

        # 2. Test Execution
        if data['tests']:
            det_sections += "#### Execution Results\n\n"
            det_sections += "| Test Case | Status | Duration |\n| --- | :---: | :---: |\n"
            for t in data["tests"]:
                icon = "✅" if t["outcome"] == "passed" else "❌"
                clean_name = t["nodeid"].split("::")[-1]
                
                # Safe duration access
                duration = 0.0
                if "call" in t:
                    duration = t["call"].get("duration", 0)
                elif "setup" in t:
                    duration = t["setup"].get("duration", 0)
                    
                det_sections += f"| {clean_name} | {icon} | {duration:.3f}s |\n"
            det_sections += "\n"
        else:
            det_sections += "*No tests executed for this module.*\n\n"

    # Failures
    failures = ""
    for t in u_tests:
        if t["outcome"] != "passed":
            clean_name = t["nodeid"]
            longrepr = t.get("longrepr", "No Traceback")
            if isinstance(longrepr, dict):
                longrepr = json.dumps(longrepr, indent=2)
            failures += f"### {clean_name}\n```\n{longrepr}\n```\n"

    u_content = u_tmpl.format(
        date=timestamp,
        total=u_total,
        pass_rate=u_rate,
        module_table=mod_table,
        detailed_sections=det_sections,
        failures_section=failures if failures else "*No Failures*"
    )
    
    with open(suite_dir / "unit_report.md", "w", encoding="utf-8") as f:
        f.write(u_content)

    # --- RENDER E2E REPORT ---
    try:
        with open(TEMPLATES_DIR / "e2e_report_template.md", encoding="utf-8") as f:
            e_tmpl = f.read()
    except FileNotFoundError:
         e_tmpl = "# E2E Report\nTemplate not found."
    
    scen_table = ""
    for t in e_tests:
        icon = "✅" if t["outcome"] == "passed" else "❌"
        name = t["nodeid"].split("::")[-1]
        
        # Safe duration access
        duration = 0.0
        if "call" in t:
            duration = t["call"].get("duration", 0)
        elif "setup" in t:
            duration = t["setup"].get("duration", 0)
            
        scen_table += f"| {name} | {icon} {t['outcome']} | {duration:.3f}s |\n"

    e_failures = ""
    for t in e_tests:
        if t["outcome"] != "passed":
            longrepr = t.get("longrepr", "No Traceback")
            if isinstance(longrepr, dict):
                longrepr = json.dumps(longrepr, indent=2)
            e_failures += f"### {t['nodeid']}\n```\n{longrepr}\n```\n"

    e_content = e_tmpl.format(
        date=timestamp,
        total=e_total,
        pass_rate=e_rate,
        scenario_table=scen_table,
        failures_section=e_failures if e_failures else "*No Failures*"
    )
    
    with open(suite_dir / "e2e_report.md", "w", encoding="utf-8") as f:
        f.write(e_content)

    return suite_dir / "README.md"

def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    suite_dir = REPORTS_DIR
    
    # Clean up existing
    if suite_dir.exists():
        shutil.rmtree(suite_dir)
    suite_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting Test Suite Run: {timestamp}")
    print(f"Artifacts will be saved to: {suite_dir}")
    
    # 1. Run
    u_path, e_path, c_path = run_tests(suite_dir)
    
    # 2. Load
    u_data = _load_json(u_path)
    e_data = _load_json(e_path)
    c_data = _load_json(c_path)
    
    # 3. Analyze Coverage
    cov_map, total_cov = analyze_coverage(c_data)
    
    # 4. Visualize
    generate_visualizations(suite_dir, u_data, e_data, cov_map)
    
    # 5. Render
    final_report = render_reports(suite_dir, u_data, e_data, cov_map, total_cov, timestamp)
    
    print(f"\n[DONE] Report Generation Complete!")
    print(f"Open the overview: {final_report}")

if __name__ == "__main__":
    main()
