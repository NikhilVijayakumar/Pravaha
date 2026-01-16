# Type Safety Report

**Date:** {date}  
**Tool:** `mypy --strict`  
**Status:** {overall_status}

---

## 📊 Summary

| Metric | Value |
| :--- | :---: |
| **Total Errors** | {total_errors} |
| **Status** | {overall_status} |

---

## 📊 Error Categories

{category_table}

![Error Categories](../assets/error_categories.png)

---

## 🛡️ Type Coverage by Module

| Module | Status | Errors |
| :--- | :---: | :---: |
| **Api** | {api_status} | {api_errors} |
| **Auth** | {auth_status} | {auth_errors} |
| **Bot** | {bot_status} | {bot_errors} |
| **Config** | {config_status} | {config_errors} |
| **Llm** | {llm_status} | {llm_errors} |
| **Pravaha_logging** | {logging_status} | {logging_errors} |
| **Storage** | {storage_status} | {storage_errors} |
| **Workflow** | {workflow_status} | {workflow_errors} |

---

## 📉 Error Distribution

![Type Errors by Module](../assets/quality/type_errors_by_module.png)

---

## 🚫 Critical Type Errors

<details>
<summary>Click to expand error details</summary>

{detailed_errors}

</details>

---

## 🛠️ Action Items

- [ ] Add missing type hints to function signatures
- [ ] Resolve `Any` types in strict modules
- [ ] Add return type annotations where missing
