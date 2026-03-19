# Logic Complexity Report

**Date:** {date}  
**Tool:** `ruff (C901)`  
**Status:** {overall_status}

---

## 📊 Summary

| Metric | Value |
| :--- | :---: |
| **Total Violations** | {total_violations} |
| **Max Allowed Complexity** | 10 |
| **Status** | {overall_status} |

---

## 🧠 Complexity Score by Module

| Module | Status | Avg Complexity | Max Complexity | Violations (>10) |
| :--- | :---: | :---: | :---: | :---: |
| **Api** | {api_status} | {api_avg} | {api_max} | {api_violations} |
| **Auth** | {auth_status} | {auth_avg} | {auth_max} | {auth_violations} |
| **Bot** | {bot_status} | {bot_avg} | {bot_max} | {bot_violations} |
| **Config** | {config_status} | {config_avg} | {config_max} | {config_violations} |
| **Llm** | {llm_status} | {llm_avg} | {llm_max} | {llm_violations} |
| **Pravaha_logging** | {logging_status} | {logging_avg} | {logging_max} | {logging_violations} |
| **Storage** | {storage_status} | {storage_avg} | {storage_max} | {storage_violations} |
| **Workflow** | {workflow_status} | {workflow_avg} | {workflow_max} | {workflow_violations} |

---

## 📉 Complexity Distribution

![Complexity Distribution](../assets/quality/complexity_distribution.png)

---

## 🐢 Most Complex Functions

<details>
<summary>Click to expand detailed violations</summary>

{top_complex_functions}

</details>

---

## 🛠️ Action Items

- [ ] Refactor high-complexity functions into smaller helpers
- [ ] Apply Strategy pattern to reduce `if/else` chains  
- [ ] Use early returns to reduce nesting depth
