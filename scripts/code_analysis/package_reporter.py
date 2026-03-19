"""
Package Dependency Report Generator

Generates markdown reports for package dependencies.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List


def generate_package_dependency_report(
    analysis: Dict,
    output_path: Path,
    template_path: Path
):
    """Generate the package dependency markdown report."""
    
    # Extract data
    installed_count = analysis["installed_count"]
    outdated_count = analysis["outdated_count"]
    up_to_date_count = analysis["up_to_date_count"]
    major_updates = analysis["major_updates"]
    minor_updates = analysis["minor_updates"]
    patch_updates = analysis["patch_updates"]
    unused_count = analysis["unused_count"]
    
    outdated_packages = analysis["outdated_packages"]
    unused_packages = analysis["unused_packages"]
    
    # Overall status
    if major_updates > 5:
        overall_status = "🔴 CRITICAL UPDATES NEEDED"
    elif outdated_count > 10:
        overall_status = "🟡 UPDATES AVAILABLE"
    elif outdated_count > 0:
        overall_status = "🟢 MOSTLY UP-TO-DATE"
    else:
        overall_status = "✅ ALL UP-TO-DATE"
    
    # Build package table
    package_table = ""
    
    # Sort by update type priority
    priority = {"MAJOR": 0, "MINOR": 1, "PATCH": 2, "UNKNOWN": 3}
    sorted_packages = sorted(
        outdated_packages,
        key=lambda x: (priority.get(x["update_type"], 99), x["name"])
    )
    
    for pkg in sorted_packages[:30]:  # Top 30
        status_icon = {
            "MAJOR": "🔴",
            "MINOR": "🟡",
            "PATCH": "🟢",
            "UNKNOWN": "⚪"
        }.get(pkg["update_type"], "⚪")
        
        package_table += f"| `{pkg['name']}` | {pkg['version']} | {pkg['latest_version']} | {status_icon} {pkg['update_type']} |\n"
    
    if not package_table:
        package_table = "| N/A | N/A | N/A | ✅ All up-to-date |\n"
    
    # Major updates detail
    major_updates_detail = ""
    major_pkgs = [p for p in outdated_packages if p["update_type"] == "MAJOR"]
    
    if major_pkgs:
        for pkg in major_pkgs[:10]:
            major_updates_detail += f"- **{pkg['name']}**: {pkg['version']} → {pkg['latest_version']}\n"
    else:
        major_updates_detail = "✅ No major updates pending!"
    
    # Unused dependencies detail
    unused_deps_detail = ""
    if unused_packages:
        for pkg in unused_packages:
            unused_deps_detail += f"- `{pkg}`\n"
        unused_deps_detail += "\n> **⚠️ Important**: Some packages may be runtime dependencies (pytest plugins, dev tools). Please review carefully before removing."
    else:
        unused_deps_detail = "✅ No obviously unused dependencies detected!"
    
    # Action items
    action_items = []
    
    if major_updates > 0:
        action_items.append(f"- 🔴 **Review {major_updates} major updates** - may contain breaking changes")
    
    if minor_updates > 3:
        action_items.append(f"- 🟡 **Update {minor_updates} packages** with minor version bumps")
    
    if unused_count > 0:
        action_items.append(f"- 🧹 **Review {unused_count} potentially unused dependencies**")
    
    if not action_items:
        action_items.append("- ✅ Dependencies are well-maintained!")
    
    action_items_text = "\n".join(action_items)
    
    # Load template
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
    else:
        template = _get_default_template()
    
    # Render
    content = template.format(
        date=datetime.now().strftime("%Y-%m-%d"),
        overall_status=overall_status,
        installed_count=installed_count,
        up_to_date=up_to_date_count,
        outdated=outdated_count,
        major_updates=major_updates,
        minor_updates=minor_updates,
        patch_updates=patch_updates,
        unused=unused_count,
        package_table=package_table,
        major_updates_detail=major_updates_detail,
        unused_deps_detail=unused_deps_detail,
        action_items=action_items_text
    )
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Package dependency report saved to: {output_path}")


def _get_default_template() -> str:
    """Return default template if file not found."""
    return """# Package Dependency Report

**Date:** {date}  
**Overall Status:** {overall_status}

---

## 📦 Package Status Overview

| Status | Count |
| :--- | :---: |
| **Total Installed** | {installed_count} |
| 🟢 **Up-to-date** | {up_to_date} |
| 🔴 **Major Updates** | {major_updates} |
| 🟡 **Minor Updates** | {minor_updates} |
| 🟢 **Patch Updates** | {patch_updates} |
| ⚠️ **Potentially Unused** | {unused} |

---

## 📊 Package Details

| Package | Current | Latest | Status |
| :--- | :---: | :---: | :---: |
{package_table}

---

## 🔴 Major Version Updates

{major_updates_detail}

---

## ⚠️ Potentially Unused Dependencies

{unused_deps_detail}

---

## 🛠️ Action Items

{action_items}

---

## 💡 Tips

- **Major updates** may have breaking changes - review changelog first
- **Minor updates** usually safe but test thoroughly
- **Patch updates** typically just bug fixes
- Run `pip install --upgrade <package>` to update
- Use `pip install <package>==<version>` for specific versions
"""
