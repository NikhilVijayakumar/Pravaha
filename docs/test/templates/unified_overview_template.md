# Pravaha Test & Quality Report

**Generated:** {date}  
**Overall Status:** {overall_status}

---

## 📊 Quick Summary

| Category | Status | Key Metrics |
| :--- | :---: | :--- |
| **Unit Tests** | {unit_status} | {unit_passed}/{unit_total} passed ({unit_pass_rate}%) |
| **E2E Tests** | {e2e_status} | {e2e_passed}/{e2e_total} passed ({e2e_pass_rate}%) |
| **Code Coverage** | {coverage_status} | {coverage_total}% |
| **Type Safety** | {type_status} | {type_violations} errors |
| **Complexity** | {complexity_status} | {complexity_violations} violations |
| **Architecture** | {arch_status} | {arch_message} |

---

## 🧪 Test Reports

### Unit Tests
- **Total**: {unit_total} tests
- **Passed**: {unit_passed} ✅
- **Failed**: {unit_failed} ❌
- **Coverage**: {coverage_total}%

![Unit Outcomes](assets/unit_outcomes.png)

📄 [Detailed Unit Test Report](data/unit_report.md)

---

### E2E Tests
- **Total**: {e2e_total} scenarios
- **Passed**: {e2e_passed} ✅
- **Failed**: {e2e_failed} ❌

![E2E Status](assets/e2e_status.png)

📄 [Detailed E2E Report](data/e2e_report.md)

---

## 🔍 Code Quality Reports

### Type Safety (mypy)
- **Status**: {type_status}
- **Total Errors**: {type_violations}

![Type Errors](assets/type_errors_by_module.png)

📄 [Detailed Type Safety Report](data/type_safety_report.md)

---

### Complexity (ruff)
- **Status**: {complexity_status}
- **Violations**: {complexity_violations}

![Complexity](assets/complexity_distribution.png)

📄 [Detailed Complexity Report](data/complexity_report.md)

---

### Architecture (import-linter)
- **Status**: {arch_status}

![Architecture](assets/architecture_status.png)

📄 [Detailed Architecture Report](data/architecture_report.md)

---

## 🎯 Action Items

{action_items}

---

## 📂 Report Structure

```
Report/
  overview.md          ← You are here
  assets/              ← All visualizations and data files
  data/                ← Detailed reports
```
