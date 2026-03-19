# Module Dependency Report

**Date:** {date}  
**Overall Status:** {overall_status}

---

## 📊 Executive Summary

| Metric | Value | Status |
| :--- | :---: | :---: |
| **Total Modules** | {total_modules} | |
| **Total Dependencies** | {total_deps} | |
| **Circular Dependencies** | {circular_deps} | {circular_status} |
| **Isolated Modules** | {isolated} | {isolated_status} |
| **Average Dependencies/Module** | {avg_deps} | |

---

## 🕸️ Dependency Visualization

![Module Dependencies](../assets/module_dependencies.png)

> **Legend:** Arrows show import relationships. Red edges indicate circular dependencies.

---

## 📈 Dependency Matrix

![Dependency Matrix](../assets/dependency_matrix.png)

> **How to Read:** Rows show modules, columns show their dependencies. Darker cells indicate stronger coupling.

---

## 🔗 Key Dependencies

### Most Imported Modules
*These modules are used by many others - changes here have wide impact*

| Module | Imported By | Impact Level |
| :--- | :---: | :---: |
{top_imported}

### Most Dependent Modules  
*These modules import many others - higher coupling*

| Module | Imports | Coupling Level |
| :--- | :---: | :---: |
{top_importers}

---

## ⚠️ Architecture Issues

### Circular Dependencies
{circular_deps_list}

> **Impact:** Circular dependencies make code harder to test, refactor, and understand. Consider breaking these cycles.

### Isolated Modules
{isolated_modules_list}

> **Note:** Isolated modules may indicate dead code or missing integration points.

---

## 🛠️ Actionitems

### High Priority
{high_priority_items}

### Recommendations
{recommendations}

---

## 💡 Best Practices

- **Reduce Circular Dependencies**: Use dependency inversion or introduce interfaces
- **Monitor Coupling**: Modules importing many others may need refactoring
- **Document Key Modules**: Highly imported modules should have comprehensive docs
- **Regular Reviews**: Run this report monthly to track architectural drift

---

## 📂 Module Details

<details>
<summary>Click to expand full dependency list</summary>

{detailed_dependency_list}

</details>
