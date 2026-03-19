
import sys
import os
import re
from pathlib import Path
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Add scripts directory to path to allow imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from reporting import utils

# Templates Directory
TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "docs" / "code_analysis" / "templates"
BASE_REPORT_DIR = Path(__file__).resolve().parent.parent.parent / ".Nibandha" / "Pravaha" / "Report"
REPORT_DIR = BASE_REPORT_DIR / "quality"
ASSETS_DIR = BASE_REPORT_DIR / "assets" / "quality"
DATA_DIR = BASE_REPORT_DIR / "assets" / "data"

def setup_style():
    """Set the aesthetic style of the plots."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["font.size"] = 12

def plot_type_errors_by_module(module_errors, output_path: Path):
    """Generate a bar chart showing type errors per module."""
    setup_style()
    
    if not module_errors:
        return
    
    df = pd.DataFrame(list(module_errors.items()), columns=["Module", "Errors"])
    df = df.sort_values("Errors", ascending=False)
    
    plt.figure()
    
    # Color based on severity
    colors = []
    for val in df["Errors"]:
        if val == 0: colors.append("#2ecc71")  # Green
        elif val < 20: colors.append("#f1c40f")  # Yellow
        else: colors.append("#e74c3c")  # Red
    
    ax = sns.barplot(data=df, x="Module", y="Errors", palette=colors, hue="Module", legend=False)
    
    plt.title("Type Errors by Module", fontsize=14, fontweight='bold')
    plt.ylabel("Number of Errors")
    plt.xlabel("Module")
    plt.xticks(rotation=45, ha="right")
    
    # Add value labels on bars
    for i, v in enumerate(df["Errors"]):
        ax.text(i, v + 1, str(v), ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_error_categories(category_stats, output_path: Path):
    """Generate a pie chart showing error distribution by category."""
    setup_style()
    
    if not category_stats:
        return
    
    # Get top 8 categories, group rest as "Other"
    sorted_cats = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
    
    if len(sorted_cats) > 8:
        top_cats = dict(sorted_cats[:8])
        other_count = sum(count for _, count in sorted_cats[8:])
        if other_count > 0:
            top_cats["other"] = other_count
    else:
        top_cats = dict(sorted_cats)
    
    labels = list(top_cats.keys())
    sizes = list(top_cats.values())
    
    # Use a nice color palette
    colors = plt.cm.Set3(range(len(labels)))
    
    plt.figure(figsize=(10, 8))
    wedges, texts, autotexts = plt.pie(
        sizes, 
        labels=labels, 
        colors=colors, 
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10}
    )
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.title("Error Distribution by Category", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_complexity_distribution(complexity_violations, output_path: Path):
    """Generate visualization for complexity violations."""
    setup_style()
    
    if not complexity_violations or sum(complexity_violations.values()) == 0:
        # Create a simple "No violations" chart
        plt.figure()
        plt.text(0.5, 0.5, "✅ No Complexity Violations\nAll functions below threshold (10)", 
                ha='center', va='center', fontsize=14, color='#2ecc71', fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=100)
        plt.close()
        return
    
    df = pd.DataFrame(list(complexity_violations.items()), columns=["Module", "Violations"])
    
    plt.figure()
    ax = sns.barplot(data=df, x="Module", y="Violations", color="#e74c3c", hue="Module", legend=False)
    
    plt.title("Complexity Violations by Module", fontsize=14, fontweight='bold')
    plt.ylabel("Number of Violations (>10)")
    plt.xlabel("Module")
    plt.xticks(rotation=45, ha="right")
    
    for i, v in enumerate(df["Violations"]):
        ax.text(i, v + 0.5, str(int(v)), ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_architecture_status(status, output_path: Path):
    """Generate a simple status indicator for architecture."""
    setup_style()
    
    plt.figure(figsize=(8, 6))
    
    if status == "PASS":
        color = "#2ecc71"
        icon = "✅"
        msg = "Clean Architecture\nCompliant"
    else:
        color = "#e74c3c"
        icon = "❌"
        msg = "Architecture Violations\nDetected"
    
    plt.text(0.5, 0.5, f"{icon}\n{msg}", 
            ha='center', va='center', fontsize=16, color=color, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def parse_mypy_output(output):
    """Parses mypy output to count errors per module and by category."""
    module_stats = {}
    category_stats = {}
    
    # Regex to extract file path and error code from mypy output
    # Example: src/nikhil/pravaha/domain/auth/service.py:10: error: ... [import-untyped]
    pattern = re.compile(r"src[\\/](?:nikhil[\\/])?pravaha[\\/]([^:]+):.*error:.*\[([^\]]+)\]")
    
    for line in output.splitlines():
        if "error:" not in line:
            continue
            
        match = pattern.search(line)
        if match:
            # Extract basic module path (e.g., domain/auth/service.py)
            rel_path = match.group(1).replace("\\", "/")
            parts = rel_path.split("/")
            
            # Simple module naming: domain/auth -> Auth, infrastructure/db -> Infrastructure
            # If it starts with domain, take 2nd part. Else take 1st.
            if parts[0] == "domain" and len(parts) > 1:
                module_name = parts[1].capitalize()
            elif parts[0] in ["api", "infrastructure"]:
                module_name = parts[0].capitalize()
            else:
                module_name = parts[0].capitalize()
                
            module_stats[module_name] = module_stats.get(module_name, 0) + 1
            
            # Track error categories
            error_code = match.group(2)
            category_stats[error_code] = category_stats.get(error_code, 0) + 1
            
    return module_stats, category_stats

def parse_ruff_output(output):
    """Parses ruff output to find complexity violations."""
    module_stats = {}
    
    # Example: src/nikhil/pravaha/domain/bot/manager.py:45:5: C901 'BotManager.run' is too complex (12)
    pattern = re.compile(r"src[\\/](?:nikhil[\\/])?pravaha[\\/]([^:]+):.*C901.*complex \(\d+\)")
    
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
             rel_path = match.group(1).replace("\\", "/")
             parts = rel_path.split("/")
             
             if parts[0] == "domain" and len(parts) > 1:
                module_name = parts[1].capitalize()
             elif parts[0] in ["api", "infrastructure"]:
                module_name = parts[0].capitalize()
             else:
                module_name = parts[0].capitalize()
                
             module_stats[module_name] = module_stats.get(module_name, 0) + 1
    
    return module_stats

def generate_type_safety_report(runner_data):
    """Generates the Type Safety report."""
    template_path = TEMPLATE_DIR / "type_safety_report_template.md"
    if not template_path.exists():
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Parse data with categories
    errors_by_module, errors_by_category = parse_mypy_output(runner_data["output"])
    
    # Generate visualizations
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    plot_type_errors_by_module(errors_by_module, ASSETS_DIR / "type_errors_by_module.png")
    plot_error_categories(errors_by_category, ASSETS_DIR / "error_categories.png")
    
    # Build module status
    total_errors = runner_data["violation_count"]
    overall_status = "🟢 PASS" if total_errors == 0 else "🔴 FAIL"
    
    # Build category breakdown table
    category_table = "| Error Type | Count | Percentage |\n| :--- | :---: | :---: |\n"
    sorted_categories = sorted(errors_by_category.items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_categories[:10]:  # Top 10
        pct = (count / total_errors * 100) if total_errors > 0 else 0
        category_table += f"| `{cat}` | {count} | {pct:.1f}% |\n"
    
    # Create formatted error output (limit to first 30 lines for readability)
    error_lines = [line for line in runner_data["output"].splitlines() if "error:" in line]
    detailed_errors = "\n".join(error_lines[:30])
    if len(error_lines) > 30:
        detailed_errors += f"\n\n... and {len(error_lines) - 30} more errors"
    
    # Format as code block
    detailed_errors = f"```\n{detailed_errors}\n```"
    
    # Render
    content = template.format(
        date=datetime.now().strftime("%Y-%m-%d"),
        overall_status=overall_status,
        total_errors=total_errors,
        category_table=category_table,
        api_status="🟢 PASS" if errors_by_module.get("Api", 0) == 0 else "🔴 FAIL",
        api_errors=errors_by_module.get("Api", 0),
        auth_status="🟢 PASS" if errors_by_module.get("Auth", 0) == 0 else "🔴 FAIL",
        auth_errors=errors_by_module.get("Auth", 0),
        bot_status="🟢 PASS" if errors_by_module.get("Bot", 0) == 0 else "🔴 FAIL",
        bot_errors=errors_by_module.get("Bot", 0),
        config_status="🟢 PASS" if errors_by_module.get("Config", 0) == 0 else "🔴 FAIL",
        config_errors=errors_by_module.get("Config", 0),
        llm_status="🟢 PASS" if errors_by_module.get("Llm", 0) == 0 else "🔴 FAIL",
        llm_errors=errors_by_module.get("Llm", 0),
        logging_status="🟢 PASS" if errors_by_module.get("Pravaha_logging", 0) == 0 else "🔴 FAIL",
        logging_errors=errors_by_module.get("Pravaha_logging", 0),
        storage_status="🟢 PASS" if errors_by_module.get("Storage", 0) == 0 else "🔴 FAIL",
        storage_errors=errors_by_module.get("Storage", 0),
        workflow_status="🟢 PASS" if errors_by_module.get("Workflow", 0) == 0 else "🔴 FAIL",
        workflow_errors=errors_by_module.get("Workflow", 0),
        detailed_errors=detailed_errors
    )
    
    utils.save_report(REPORT_DIR / "type_safety_report.md", content)

def generate_complexity_report(runner_data):
    """Generates the Complexity report."""
    template_path = TEMPLATE_DIR / "complexity_report_template.md"
    content = ""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    violations = parse_ruff_output(runner_data["output"])
    
    # Generate visualization
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    plot_complexity_distribution(violations, ASSETS_DIR / "complexity_distribution.png")
    
    # Determine overall status
    total_violations = sum(violations.values())
    overall_status = "🟢 PASS" if total_violations == 0 else "🔴 FAIL"
    
    # Format detailed output
    detailed_output = runner_data["output"] if runner_data["output"].strip() else "No complexity violations found."
    
    mapping = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "overall_status": overall_status,
        "total_violations": total_violations,
        "top_complex_functions": f"```\n{detailed_output}\n```",
        "api_status": "🟢" if violations.get("Api", 0) == 0 else "🔴", 
        "api_avg": "-", "api_max": "-", "api_violations": violations.get("Api", 0),
        "auth_status": "🟢" if violations.get("Auth", 0) == 0 else "🔴", 
        "auth_avg": "-", "auth_max": "-", "auth_violations": violations.get("Auth", 0),
        "bot_status": "🟢" if violations.get("Bot", 0) == 0 else "🔴", 
        "bot_avg": "-", "bot_max": "-", "bot_violations": violations.get("Bot", 0),
        "config_status": "🟢" if violations.get("Config", 0) == 0 else "🔴", 
        "config_avg": "-", "config_max": "-", "config_violations": violations.get("Config", 0),
        "llm_status": "🟢" if violations.get("Llm", 0) == 0 else "🔴", 
        "llm_avg": "-", "llm_max": "-", "llm_violations": violations.get("Llm", 0),
        "logging_status": "🟢" if violations.get("Log", 0) == 0 else "🔴", 
        "logging_avg": "-", "logging_max": "-", "logging_violations": violations.get("Log", 0),
        "storage_status": "🟢" if violations.get("Storage", 0) == 0 else "🔴", 
        "storage_avg": "-", "storage_max": "-", "storage_violations": violations.get("Storage", 0),
        "workflow_status": "🟢" if violations.get("Workflow", 0) == 0 else "🔴", 
        "workflow_avg": "-", "workflow_max": "-", "workflow_violations": violations.get("Workflow", 0),
    }

    try:
        content = content.format(**mapping)
    except KeyError as e:
        print(f"Warning: Missing key in complexity template: {e}")
        
    utils.save_report(REPORT_DIR / "complexity_report.md", content)

def generate_architecture_report(runner_data):
    """Generates Architecture report."""
    template_path = TEMPLATE_DIR / "architecture_report_template.md"
    content = ""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Generate visualization
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    plot_architecture_status(runner_data["status"], ASSETS_DIR / "architecture_status.png")
    
    # Import linter output is unstructured text mostly
    # Check if the error is due to missing .importlinter file
    output_text = runner_data["output"]
    if "cannot find the file" in output_text.lower() or "no such file" in output_text.lower():
        detailed_violations = "⚠️ **Configuration Missing**\n\n" + \
                            "The `.importlinter` configuration file was not found in the project root.\n\n" + \
                            "To enable architecture validation, create `.importlinter` with:\n" + \
                            "```ini\n[importlinter]\nroot_package = nikhil.pravaha\n\n" + \
                            "[importlinter:contract:1]\nname = Domain layer must not import Infrastructure\n" + \
                            "type = forbidden\nsource_modules =\n    nikhil.pravaha.domain\n" + \
                            "forbidden_modules =\n    nikhil.pravaha.infrastructure\n    nikhil.pravaha.api\n```"
        status = "⚠️ NOT CONFIGURED"
    elif runner_data["status"] == "PASS":
        detailed_violations = "✅ **No violations detected**\n\nAll architecture constraints are satisfied."
        status = "🟢 PASS"
    else:
        detailed_violations = f"```\n{output_text}\n```"
        status = "🔴 FAIL"
    
    mapping = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "overall_status": status,
        "domain_infra_violations": "-", "domain_infra_status": status,
        "domain_api_violations": "-", "domain_api_status": status,
        "detailed_violations": detailed_violations,
        
        # Default all modules to pass for now as parsing import-linter is complex
        "api_status": "🟢", "api_violations": 0,
        "auth_status": "🟢", "auth_violations": 0,
        "bot_status": "🟢", "bot_violations": 0,
        "config_status": "🟢", "config_violations": 0,
        "llm_status": "🟢", "llm_violations": 0,
        "logging_status": "🟢", "logging_violations": 0,
        "storage_status": "🟢", "storage_violations": 0,
        "workflow_status": "🟢", "workflow_violations": 0,
    }
    
    try:
        content = content.format(**mapping)
    except KeyError as e:
        print(f"Warning: Missing key in architecture template: {e}")

    utils.save_report(REPORT_DIR / "architecture_report.md", content)

def generate_overview(arch_data, type_data, cplx_data):
    """Generates Quality Overview."""
    template_path = TEMPLATE_DIR / "quality_overview_template.md"
    content = ""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    mapping = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "overall_status": "🟢 HEALTHY" if all(x["status"] == "PASS" for x in [arch_data, type_data, cplx_data]) else "🟡 ISSUES DETECTED",
        "arch_status": arch_data["status"], "arch_violations": 0, # TODO parse
        "struct_status": "⚪ N/A", "struct_violations": "-",
        "type_status": type_data["status"], "type_violations": type_data["violation_count"],
        "cplx_status": cplx_data["status"], "cplx_violations": cplx_data["violation_count"],
    }
    
    try:
        content = content.format(**mapping)
    except KeyError:
        pass
        
    utils.save_report(REPORT_DIR / "quality_overview.md", content)
