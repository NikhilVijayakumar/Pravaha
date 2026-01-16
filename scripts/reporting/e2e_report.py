import json
from pathlib import Path
import datetime
from . import visualizer
from . import utils

def run(timestamp: str):
    """Execute E2E reporting flow."""
    print("--- Starting E2E Reporting ---")
    
    # 1. Run Tests
    json_path = utils.run_pytest(
        target="tests/e2e",
        report_name="e2e"
    )
    
    # 2. Load Data
    data = utils.load_json(json_path)
    
    # 3. Process Results
    e_tests = data.get("tests", [])
    passed, failed, total = utils.parse_outcome(data)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    # Group by Module
    # Path format: tests/e2e/domain/<module>/...
    module_results = {}
    
    # Scenarios for visualization
    scenarios = []
    durations = []
    
    outcome_counts = {"pass": passed, "fail": failed, "error": 0, "skipped": 0}
    
    for t in e_tests:
        # Extract Module
        parts = t["nodeid"].replace("\\", "/").split("/")
        mod = "Other"
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
        
        # Collect Visualization Metrics
        name = t["nodeid"].split("::")[-1]
        dur = 0.0
        if "call" in t: dur = t["call"].get("duration", 0)
        elif "setup" in t: dur = t["setup"].get("duration", 0)
        
        scenarios.append({"name": name, "duration": dur})
        durations.append(dur)

    # 4. Generate Visualizations
    visualizer.plot_e2e_outcome(outcome_counts, utils.REPORTS_DIR / "e2e_status.png")
    
    # Top 10 slowest scenarios
    slowest = sorted(scenarios, key=lambda x: x["duration"], reverse=True)[:10]
    visualizer.plot_e2e_durations(slowest, utils.REPORTS_DIR / "e2e_durations.png")

    # 5. Render Markdown
    render_markdown(timestamp, total, pass_rate, module_results, e_tests)
    print("--- E2E Report Complete ---")

def render_markdown(timestamp, total, pass_rate, module_results, all_tests):
    try:
        with open(utils.TEMPLATES_DIR / "e2e_report_template.md", encoding="utf-8") as f:
            tmpl = f.read()
    except FileNotFoundError:
         tmpl = "# E2E Report\nTemplate not found."
    
    # Module Breakdown Table
    mod_table = ""
    det_sections = ""
    
    sorted_mods = sorted(module_results.keys())
    
    for mod in sorted_mods:
        data = module_results[mod]
        mod_table += f"| {mod} | {data['total']} | {data['pass']} | {data['fail']} |\n"
        
        # Detailed Section construction
        det_sections += f"### Module: {mod}\n\n"
        if data['tests']:
            det_sections += "| Scenario | Status | Duration |\n| --- | :---: | :---: |\n"
            for t in data["tests"]:
                icon = "✅" if t["outcome"] == "passed" else "❌"
                # Simplify name: test_feature_discovery.py::TestClass::test_method -> test_method
                full_name = t["nodeid"].split("::")[-1]
                dur = 0.0
                if "call" in t: dur = t["call"].get("duration", 0)
                elif "setup" in t: dur = t["setup"].get("duration", 0)
                
                det_sections += f"| {full_name} | {icon} | {dur:.3f}s |\n"
            det_sections += "\n"
        else:
            det_sections += "*No scenarios executed.*\n\n"

    # Failures Section
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

    with open(utils.REPORTS_DIR / "e2e_report.md", "w", encoding="utf-8") as f:
        f.write(content)
