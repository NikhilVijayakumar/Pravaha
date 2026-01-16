# Report Visualization Specification

This document defines the standard visual style and supported plot types for **Pravaha** reports. We utilize `seaborn` and `matplotlib` to generate high-quality, aesthetically pleasing visualizations that enhance the readability of our Markdown reports.

## 🎨 Visual Style Guide

To maintain consistency across all reports (Test, Architecture, Quality), we adhere to the following style guidelines.

### Theme & Aesthetics
*   **Base Style**: `seaborn.set_theme(style="whitegrid")`
*   **Context**: `notebook` (scaled for readability)
*   **Font Size**: 12pt primary, 10pt labels.
*   **Figure Size**: Standard `(10, 6)` inches.
*   **DPI**: 100 (optimized for web/markdown embedding).

### Color Palettes
We use semantic coloring to convey meaning instantly.

| Context | Color Code | Visual Representation | Meaning |
| :--- | :--- | :--- | :--- |
| **Pass / Healthy** | `#2ecc71` | 🟢 Emerald Green | Success, Safe, Low Complexity |
| **Fail / Critical** | `#e74c3c` | 🔴 Alizarin Red | Failure, Error, High Complexity |
| **Warning / Caution** | `#f1c40f` | 🟡 Sunflower Yellow | Warning, Medium Complexity |
| **Neutral / Info** | `#3498db` | 🔵 Peter River Blue | Distribution, Info, Metrics |
| **Skipped / N/A** | `#95a5a6` | ⚪ Concrete Grey | Skipped, Ignored |

---

## 📊 Supported Plot Types

### 1. Stacked Bar Chart (Outcomes)
**Use Case**: Visualizing categorical breakdowns (Pass/Fail) across items (Modules).
*   **X-Axis**: Modules (e.g., Auth, Storage).
*   **Y-Axis**: Count of Tests/Violations.
*   **Hue**: Status (Pass, Fail, Error).
*   **Library**: `pandas.plot(kind='bar', stacked=True)`

### 2. Gradient Bar Chart (Metrics)
**Use Case**: Visualizing continuous metrics where value implies health (e.g., Coverage, Complexity).
*   **X-Axis**: Modules.
*   **Y-Axis**: Percentage or Score.
*   **Color Logic**:
    *   **Coverage**: <50% (Red), 50-80% (Yellow), >80% (Green).
    *   **Complexity**: <6 (Green), 6-10 (Yellow), >10 (Red).
*   **Library**: `seaborn.barplot` with custom palette.

### 3. Distribution Histogram
**Use Case**: Understanding the spread of data points (e.g., Test Durations).
*   **X-Axis**: Duration (seconds) or Complexity Score.
*   **Y-Axis**: Frequency Count.
*   **Features**: Kernel Density Estimate (KDE) curve overlay.
*   **Library**: `seaborn.histplot(kde=True)`

### 4. Donut / Pie Chart (Overall Status)
**Use Case**: High-level summary of a binary or ternary state (Passed vs Failed).
*   **Sections**: Pass, Fail, Error/Skip.
*   **Labeling**: Percentage strings (`%1.1f%%`).
*   **Library**: `matplotlib.pyplot.pie`

---

## 📈 Implementation in Reports

### Test Reporting (`scripts/reporting/visualizer.py`)

| Plot File | Type | Description |
| :--- | :--- | :--- |
| `unit_outcomes.png` | Stacked Bar | Pass/Fail counts per module. |
| `unit_coverage.png` | Gradient Bar | Code coverage % per module. |
| `unit_durations.png` | Histogram | Test execution time distribution. |
| `e2e_status.png` | Pie Chart | E2E Scenario Pass/Fail ratio. |
| `e2e_durations.png` | Bar Chart | Top 10 slowest scenarios. |

### Quality Reporting (Proposed)

| Plot File | Type | Description |
| :--- | :--- | :--- |
| `type_errors.png` | Stacked Bar | Mypy errors vs total files per module. |
| `complexity_dist.png` | Histogram | Distribution of McCabe complexity scores. |
| `arch_violations.png` | Pie Chart | Ratio of compliant vs violating modules. |

## 🛠️ Usage Example

```python
import seaborn as sns
import matplotlib.pyplot as plt

def setup_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (10, 6)
    
def plot_outcome(data):
    setup_style()
    # ... plotting logic ...
    plt.savefig("report.png", dpi=100)
    plt.close()
```
