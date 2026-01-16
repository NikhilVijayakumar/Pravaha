"""
Module Dependency Report Generator

Generates markdown reports for module dependencies.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Set, List, Tuple


def generate_module_dependency_report(
    dependencies: Dict[str, Set[str]],
    circular_deps: List[Tuple[str, str]],
    most_imported: List[Tuple[str, int]],
    most_dependent: List[Tuple[str, int]],
    isolated: List[str],
    output_path: Path,
    template_path: Path
):
    """Generate the module dependency markdown report."""
    
    # Calculate statistics
    total_modules = len(dependencies)
    total_deps = sum(len(deps) for deps in dependencies.values())
    circular_count = len(circular_deps)
    isolated_count = len(isolated)
    
    # Build tables
    top_imported_table = ""
    for module, count in most_imported:
        top_imported_table += f"| **{module}** | {count} modules |\n"
    
    if not top_imported_table:
        top_imported_table = "| N/A | 0 |\n"
    
    top_importers_table = ""
    for module, count in most_dependent:
        top_importers_table += f"| **{module}** | {count} modules |\n"
    
    if not top_importers_table:
        top_importers_table = "| N/A | 0 |\n"
    
    # Circular dependencies list
    circular_deps_list = ""
    if circular_deps:
        for module_a, module_b in circular_deps:
            circular_deps_list += f"- ⚠️ **{module_a}** ↔️ **{module_b}**\n"
    else:
        circular_deps_list = "✅ No circular dependencies detected!"
    
    # Isolated modules list
    isolated_modules_list = ""
    if isolated:
        for module in isolated:
            isolated_modules_list += f"- `{module}`\n"
    else:
        isolated_modules_list = "✅ No isolated modules!"
    
    # Overall status
    if circular_count > 0:
        overall_status = "⚠️ ISSUES DETECTED"
    elif total_modules == 0:
        overall_status = "⚪ NO MODULES"
    else:
        overall_status = "✅ HEALTHY"
    
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
        total_modules=total_modules,
        total_deps=total_deps,
        circular_deps=circular_count,
        isolated=isolated_count,
        top_imported=top_imported_table,
        top_importers=top_importers_table,
        circular_deps_list=circular_deps_list,
        isolated_modules_list=isolated_modules_list
    )
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Module dependency report saved to: {output_path}")


def _get_default_template() -> str:
    """Return default template if file not found."""
    return """# Module Dependency Report

**Date:** {date}  
**Overall Status:** {overall_status}

---

## 🕸️ Dependency Graph

![Module Dependencies](../assets/module_dependencies.png)

---

## 📊 Dependency Summary

| Metric | Value |
| :--- | :---: |
| **Total Modules** | {total_modules} |
| **Total Dependencies** | {total_deps} |
| **Circular Dependencies** | {circular_deps} |
| **Isolated Modules** | {isolated} |

---

## 🔗 Key Dependencies

### Most Imported Modules
| Module | Imported By |
| :--- | :---: |
{top_imported}

### Most Dependent Modules
| Module | Imports |
| :--- | :---: |
{top_importers}

---

## ⚠️ Issues

### Circular Dependencies
{circular_deps_list}

### Isolated Modules
{isolated_modules_list}

---

## 🛠️ Action Items

- Review and refactor circular dependencies
- Consider if isolated modules should be integrated or removed
- Document key module relationships
"""
