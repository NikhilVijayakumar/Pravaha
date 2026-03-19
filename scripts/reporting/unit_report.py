import json
from pathlib import Path
import datetime
from . import visualizer
from . import utils

def run(timestamp: str):
    """Execute unit reporting flow."""
    print("--- Starting Unit Test Reporting ---")
    
    # 1. Run Tests
    json_path = utils.run_pytest(
        target="tests/unit",
        report_name="unit",
        cov_target="src/nikhil/pravaha"
    )
    
    # 2. Load Data
    data = utils.load_json(json_path)
    
    # Load Coverage
    cov_path = Path("coverage.json") # Created in CWD by pytest-cov
    cov_data = utils.load_json(cov_path)
    cov_map, _ = utils.analyze_coverage(cov_data)
    
    # Move coverage.json to report dir for safekeeping
    if cov_path.exists():
        dest = utils.REPORTS_DIR / "coverage.json"
        try:
             # Using read/write instead of shutil.move to avoid cross-device errors
            dest.write_text(cov_path.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception:
            pass

    # 3. Process Results
    all_modules = utils.get_all_modules()
    u_tests = data.get("tests", [])
    passed, failed, total = utils.parse_outcome(data)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    # Group results
    module_results = {mod: {"total": 0, "pass": 0, "fail": 0, "error": 0, "tests": []} for mod in all_modules}
    module_results["Unknown"] = {"total": 0, "pass": 0, "fail": 0, "error": 0, "tests": []}
    
    durations = []
    
    for t in u_tests:
        # Determine module from nodeid
        parts = t["nodeid"].replace("\\", "/").split("/")
        mod = "Unknown"
        if "domain" in parts:
            idx = parts.index("domain")
            if idx + 1 < len(parts):
                mod = parts[idx + 1].capitalize()
        
        if mod not in module_results:
            module_results[mod] = {"total": 0, "pass": 0, "fail": 0, "error": 0, "tests": []}
            
        module_results[mod]["total"] += 1
        if t["outcome"] == "passed":
            module_results[mod]["pass"] += 1
        else:
            if "error" in t.get("keywords", []): # Heuristic for error
                module_results[mod]["error"] += 1
            else:
                module_results[mod]["fail"] += 1
                
        module_results[mod]["tests"].append(t)
        
        # Collect duration
        if "call" in t:
            durations.append(t["call"].get("duration", 0))
        elif "setup" in t:
            durations.append(t["setup"].get("duration", 0))

    if module_results["Unknown"]["total"] == 0:
        del module_results["Unknown"]

    # 4. Generate Visualizations
    visualizer.plot_module_outcomes(module_results, utils.REPORTS_DIR / "unit_outcomes.png")
    visualizer.plot_coverage(cov_map, utils.REPORTS_DIR / "unit_coverage.png")
    visualizer.plot_test_duration_distribution(durations, utils.REPORTS_DIR / "unit_durations.png")

    # 5. Render Markdown
    render_markdown(timestamp, total, pass_rate, module_results, cov_map, u_tests)
    print("--- Unit Test Report Complete ---")

def render_markdown(timestamp, total, pass_rate, module_results, cov_map, all_tests):
    # Template loading
    try:
        with open(utils.TEMPLATES_DIR / "unit_report_template.md", encoding="utf-8") as f:
            tmpl = f.read()
    except FileNotFoundError:
        tmpl = "# Unit Report\nTemplate not found."

    # Module Table
    mod_table = ""
    det_sections = ""
    
    for mod in sorted(module_results.keys()):
        data = module_results[mod]
        cov_val = cov_map.get(mod, 0)
        
        cov_str = f"{cov_val:.1f}%"
        if cov_val < 50 and data['total'] > 0:
            cov_str = f"🔴 {cov_str}"
        elif cov_val > 80:
            cov_str = f"🟢 {cov_str}"
            
        mod_table += f"| {mod} | {data['total']} | {data['pass']} | {data['fail'] + data['error']} | {cov_str} |\n"
        
        # Detailed Section
        det_sections += f"### Module: {mod}\n\n"
        det_sections += "#### Documentation Scenarios\n\n"
        det_sections += utils.get_module_doc(mod, "unit")
        det_sections += "\n\n"
        
        if data['tests']:
            det_sections += "#### Execution Results\n\n"
            det_sections += "| Test Case | Status | Duration |\n| --- | :---: | :---: |\n"
            for t in data["tests"]:
                icon = "✅" if t["outcome"] == "passed" else "❌"
                clean_name = t["nodeid"].split("::")[-1]
                dur = 0.0
                if "call" in t: dur = t["call"].get("duration", 0)
                elif "setup" in t: dur = t["setup"].get("duration", 0)
                
                det_sections += f"| {clean_name} | {icon} | {dur:.3f}s |\n"
            det_sections += "\n"
        else:
            det_sections += "*No tests executed for this module.*\n\n"

    # Failures
    failures = ""
    for t in all_tests:
        if t["outcome"] != "passed":
            longrepr = t.get("longrepr", "No Traceback")
            if isinstance(longrepr, dict):
                longrepr = json.dumps(longrepr, indent=2)
            failures += f"### {t['nodeid']}\n```\n{longrepr}\n```\n"

    content = tmpl.format(
        date=timestamp,
        total=total,
        pass_rate=pass_rate,
        module_table=mod_table,
        detailed_sections=det_sections,
        failures_section=failures if failures else "*No Failures*"
    )
    
    with open(utils.REPORTS_DIR / "unit_report.md", "w", encoding="utf-8") as f:
        f.write(content)
