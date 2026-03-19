import json
from pathlib import Path
import datetime
from . import visualizer
from . import utils

def run(timestamp: str):
    """Execute Overview reporting flow."""
    print("--- Generating Overview Dashboard ---")
    
    # Load all data
    unit_data = utils.load_json(utils.REPORTS_DIR / "unit.json")
    e2e_data = utils.load_json(utils.REPORTS_DIR / "e2e.json")
    cov_data = utils.load_json(utils.REPORTS_DIR / "coverage.json")
    
    # Parse outcomes
    u_passed, u_failed, u_total = utils.parse_outcome(unit_data)
    e_passed, e_failed, e_total = utils.parse_outcome(e2e_data)
    
    u_rate = (u_passed / u_total * 100) if u_total > 0 else 0
    e_rate = (e_passed / e_total * 100) if e_total > 0 else 0
    
    # Analyze Coverage
    _, total_cov = utils.analyze_coverage(cov_data)
    
    # Visualize
    visualizer.plot_suite_distribution(
        (u_passed, u_failed),
        (e_passed, e_failed),
        utils.REPORTS_DIR / "distribution_chart.png"
    )
    
    # Render
    render_markdown(timestamp, u_failed, e_failed, u_rate, e_rate, total_cov)
    print("--- Overview Complete ---")

def render_markdown(timestamp, u_failed, e_failed, u_rate, e_rate, total_cov):
    try:
        with open(utils.TEMPLATES_DIR / "overview_report_template.md", encoding="utf-8") as f:
            ov_tmpl = f.read()
    except FileNotFoundError:
        ov_tmpl = "# Overview\nTemplate not found."

    crit_issues = ""
    if u_failed > 0:
        crit_issues += f"- ❌ **{u_failed} Unit Test Failures** detected.\n"
    if e_failed > 0:
        crit_issues += f"- ❌ **{e_failed} E2E Test Failures** detected.\n"
    if not crit_issues:
        crit_issues = "✅ No critical issues found."

    # Total Duration approximation (if we had it, but utils.parse_outcome doesn't return it)
    # We can skip or calculate if needed. The template asks for {total_duration}.
    # Let's set it to 0.0s for now or read from json if possible.
    total_duration = 0.0 # Placeholder
    
    ov_content = ov_tmpl.format(
        date=timestamp,
        total_duration=total_duration,
        suite_status="✅ Passing" if (u_failed + e_failed) == 0 else "❌ Failing",
        unit_pass_rate=u_rate,
        e2e_pass_rate=e_rate,
        coverage_total=total_cov,
        critical_issues=crit_issues
    )
    
    with open(utils.REPORTS_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write(ov_content)
