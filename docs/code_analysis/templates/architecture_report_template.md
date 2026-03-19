# Clean Architecture Report

**Date:** {date}  
**Tool:** `import-linter`  
**Status:** {overall_status}

---

## 📊 Summary

![Architecture Status](../assets/quality/architecture_status.png)

---

## 🏗️ Layer Dependency Summary

| Violation Type | Count | Status |
| :--- | :---: | :---: |
| **Domain → Infrastructure** | {domain_infra_violations} | {domain_infra_status} |
| **Domain → API** | {domain_api_violations} | {domain_api_status} |

---

## 📦 Module Breakdown (Dependency Compliance)

| Module | Status | Violations |
| :--- | :---: | :---: |
| **Api** | {api_status} | {api_violations} |
| **Auth** | {auth_status} | {auth_violations} |
| **Bot** | {bot_status} | {bot_violations} |
| **Config** | {config_status} | {config_violations} |
| **Llm** | {llm_status} | {llm_violations} |
| **Pravaha_logging** | {logging_status} | {logging_violations} |
| **Storage** | {storage_status} | {storage_violations} |
| **Workflow** | {workflow_status} | {workflow_violations} |

---

## 🚫 Detailed Violations

{detailed_violations}

---

## 🛠️ Action Items

- [ ] Refactor imports in `domain` to remove `infrastructure` dependencies
- [ ] Use `Protocol` interfaces to invert dependencies
- [ ] Ensure all external framework usage is isolated to factory layer
