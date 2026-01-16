import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def setup_style():
    """Set the aesthetic style of the plots."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["font.size"] = 12

def plot_module_outcomes(module_data, output_path: Path):
    """
    Generate a stacked bar chart of Pass/Fail/Error counts per module.
    module_data: dict {module_name: {'pass': int, 'fail': int, 'error': int}}
    """
    setup_style()
    
    # Transform to DataFrame
    data_list = []
    for mod, counts in module_data.items():
        data_list.append({"Module": mod, "Outcome": "Pass", "Count": counts.get("pass", 0)})
        data_list.append({"Module": mod, "Outcome": "Fail", "Count": counts.get("fail", 0)})
        data_list.append({"Module": mod, "Outcome": "Error", "Count": counts.get("error", 0)})
        
    df = pd.DataFrame(data_list)
    
    if df.empty:
        return

    # Create plot
    plt.figure()
    # Pivot for stacked bar
    try:
        df_pivot = df.pivot(index="Module", columns="Outcome", values="Count")
    except ValueError:
        return # Handle duplicate entries if any

    # Reorder columns to ensure consistent colors
    cols = [c for c in ["Pass", "Fail", "Error"] if c in df_pivot.columns]
    df_pivot = df_pivot[cols]
    
    colors = {"Pass": "#2ecc71", "Fail": "#e74c3c", "Error": "#f1c40f"}
    custom_palette = [colors[c] for c in cols]
    
    if not df_pivot.empty:
        ax = df_pivot.plot(kind="bar", stacked=True, color=custom_palette, width=0.8)
        
        plt.title("Test Outcome by Module")
        plt.xlabel("Module")
        plt.ylabel("Test Count")
        plt.xticks(rotation=45, ha="right")
        plt.legend(title="Outcome")
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=100)
    plt.close()

def plot_coverage(module_data, output_path: Path):
    """
    Generate a bar chart for coverage percentage per module.
    module_data: dict {module_name: coverage_float}
    """
    setup_style()
    
    df = pd.DataFrame(list(module_data.items()), columns=["Module", "Coverage"])
    
    if df.empty:
        return

    plt.figure()
    # Color condition: <50 red, <80 yellow, >=80 green
    colors = []
    for val in df["Coverage"]:
        if val < 50: colors.append("#e74c3c")
        elif val < 80: colors.append("#f1c40f")
        else: colors.append("#2ecc71")
        
    ax = sns.barplot(data=df, x="Module", y="Coverage", palette=colors)
    
    plt.title("Code Coverage by Module")
    plt.ylabel("Coverage (%)")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 100)
    
    # Add value labels
    for i, v in enumerate(df["Coverage"]):
        ax.text(i, v + 1, f"{v:.1f}%", ha='center', fontsize=10)
        
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_test_duration_distribution(test_durations, output_path: Path):
    """
    Generate a histogram of test durations.
    test_durations: list of floats (seconds)
    """
    setup_style()
    
    if not test_durations:
        return

    df = pd.DataFrame(test_durations, columns=["Duration"])
    
    plt.figure()
    sns.histplot(data=df, x="Duration", bins=30, kde=True, color="#3498db")
    
    plt.title("Test Duration Distribution")
    plt.xlabel("Duration (seconds)")
    plt.ylabel("Count")
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_e2e_outcome(counts, output_path: Path):
    """
    Generate a pie chart for E2E outcomes.
    counts: dict {'pass': int, 'fail': int}
    """
    setup_style()
    
    labels = []
    sizes = []
    colors = []
    
    mapping = {"pass": "#2ecc71", "fail": "#e74c3c", "error": "#f1c40f", "skipped": "#95a5a6"}
    
    for k, v in counts.items():
        if v > 0:
            labels.append(k.title())
            sizes.append(v)
            colors.append(mapping.get(k, "#bdc3c7"))
            
    if not sizes:
        return

    plt.figure()
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title("E2E Scenario Outcomes")
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_e2e_durations(scenarios, output_path: Path):
    """
    Bar chart of duration per scenario.
    scenarios: list of dict {'name': str, 'duration': float}
    """
    setup_style()
    
    df = pd.DataFrame(scenarios)
    if df.empty:
        return

    plt.figure()
    ax = sns.barplot(data=df, x="name", y="duration", hue="name", legend=False, palette="viridis")
    
    plt.title("E2E Scenario Durations")
    plt.xlabel("Scenario")
    plt.ylabel("Time (s)")
    plt.xticks(rotation=45, ha="right")
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_suite_distribution(unit_counts, e2e_counts, output_path: Path):
    """
    Generate a pie chart for total test distribution (Unit vs E2E).
    unit_counts: (pass, fail)
    e2e_counts: (pass, fail)
    """
    setup_style()
    
    labels = ['Unit Passed', 'Unit Failed', 'E2E Passed', 'E2E Failed']
    sizes = [unit_counts[0], unit_counts[1], e2e_counts[0], e2e_counts[1]]
    colors = ['#66BB6A', '#EF5350', '#42A5F5', '#AB47BC']
    
    # Filter zeros
    clean_labels = [l for l, s in zip(labels, sizes) if s > 0]
    clean_sizes = [s for s in sizes if s > 0]
    clean_colors = [c for l, s, c in zip(labels, sizes, colors) if s > 0]

    plt.figure()
    if clean_sizes:
        plt.pie(clean_sizes, labels=clean_labels, colors=clean_colors, autopct='%1.1f%%')
    else:
        plt.text(0.5, 0.5, "No Tests Run", ha='center')
        
    plt.title("Total Test Distribution")
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_failure_heatmap(module_data, output_path: Path):
    """Generate a heatmap showing failure rates by module."""
    setup_style()
    
    if not module_data:
        return
    
    # Calculate failure rates
    data_list = []
    for mod, stats in module_data.items():
        total = stats.get("pass", 0) + stats.get("fail", 0) + stats.get("error", 0)
        if total > 0:
            fail_rate = (stats.get("fail", 0) + stats.get("error", 0)) / total * 100
            data_list.append({"Module": mod, "Failure Rate": fail_rate, "Total": total})
    
    if not data_list:
        return
    
    df = pd.DataFrame(data_list)
    df = df.sort_values("Failure Rate", ascending=False)
    
    plt.figure(figsize=(10, 6))
    
    # Color code by severity
    colors = []
    for rate in df["Failure Rate"]:
        if rate == 0: colors.append("#2ecc71")
        elif rate < 25: colors.append("#f1c40f")
        elif rate < 50: colors.append("#e67e22")
        else: colors.append("#e74c3c")
    
    ax = sns.barplot(data=df, x="Module", y="Failure Rate", palette=colors, hue="Module", legend=False)
    
    plt.title("Test Failure Rate by Module", fontsize=14, fontweight='bold')
    plt.ylabel("Failure Rate (%)")
    plt.xlabel("Module")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 100)
    
    # Add value labels
    for i, v in enumerate(df["Failure Rate"]):
        ax.text(i, v + 2, f"{v:.1f}%", ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()
