"""
Dependency Graph Visualizer

Creates visual representations of module dependencies.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, Set, List, Tuple

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("Warning: networkx not installed. Install with: pip install networkx")


def visualize_dependency_graph(
    dependencies: Dict[str, Set[str]],
    output_path: Path,
    circular_deps: List[Tuple[str, str]] = None
):
    """Generate a visual dependency graph."""
    
    if not HAS_NETWORKX:
        # Create a simple text-based fallback
        _create_text_visualization(dependencies, output_path)
        return
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes
    for module in dependencies.keys():
        G.add_node(module)
    
    # Add edges
    for module, deps in dependencies.items():
        for dep in deps:
            G.add_edge(module, dep)
    
    # Create figure
    plt.figure(figsize=(14, 10))
    
    # Use hierarchical layout
    try:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    except:
        pos = nx.circular_layout(G)
    
    # Color nodes by type (you can enhance this)
    node_colors = []
    for node in G.nodes():
        # Simple heuristic: color by name
        if node.lower() in ["auth", "security"]:
            node_colors.append("#e74c3c")  # Red
        elif node.lower() in ["storage", "database"]:
            node_colors.append("#3498db")  # Blue
        elif node.lower() in ["bot", "workflow"]:
            node_colors.append("#2ecc71")  # Green
        elif node.lower() in ["api", "provider"]:
            node_colors.append("#f39c12")  # Orange
        else:
            node_colors.append("#95a5a6")  # Gray
    
    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        edge_color="#95a5a6",
        alpha=0.5,
        arrows=True,
        arrowsize=15,
        arrowstyle="->",
        connectionstyle="arc3,rad=0.1"
    )
    
    # Highlight circular dependencies
    if circular_deps:
        circular_edges = []
        for module_a, module_b in circular_deps:
            if G.has_edge(module_a, module_b):
                circular_edges.append((module_a, module_b))
            if G.has_edge(module_b, module_a):
                circular_edges.append((module_b, module_a))
        
        if circular_edges:
            nx.draw_networkx_edges(
                G, pos,
                edgelist=circular_edges,
                edge_color="#e74c3c",
                width=3,
                alpha=0.8,
                arrows=True,
                arrowsize=20
            )
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=2000,
        alpha=0.9,
        edgecolors="black",
        linewidths=2
    )
    
    # Draw labels
    nx.draw_networkx_labels(
        G, pos,
        font_size=10,
        font_weight="bold",
        font_color="white"
    )
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color='#e74c3c', label='Auth/Security'),
        mpatches.Patch(color='#3498db', label='Storage/Database'),
        mpatches.Patch(color='#2ecc71', label='Bot/Workflow'),
        mpatches.Patch(color='#f39c12', label='API/Provider'),
        mpatches.Patch(color='#95a5a6', label='Other'),
    ]
    
    if circular_deps:
        legend_elements.append(
            mpatches.Patch(color='#e74c3c', label='⚠️ Circular Dependency', alpha=0.8)
        )
    
    plt.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    plt.title("Module Dependency Graph", fontsize=16, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Dependency graph saved to: {output_path}")


def _create_text_visualization(dependencies: Dict[str, Set[str]], output_path: Path):
    """Create a simple text-based visualization when networkx is not available."""
    plt.figure(figsize=(12, 8))
    plt.text(
        0.5, 0.5,
        "Module Dependency Graph\n\n"
        "⚠️ Install networkx for visual graph:\n"
        "pip install networkx\n\n"
        f"Modules: {len(dependencies)}\n"
        f"Dependencies: {sum(len(deps) for deps in dependencies.values())}",
        ha='center',
        va='center',
        fontsize=14,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )
    plt.axis('off')
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close()


def create_dependency_matrix(dependencies: Dict[str, Set[str]], output_path: Path):
    """Create a dependency matrix heatmap."""
    import numpy as np
    import seaborn as sns
    
    modules = sorted(dependencies.keys())
    n = len(modules)
    
    # Create adjacency matrix
    matrix = np.zeros((n, n))
    
    for i, module_from in enumerate(modules):
        for j, module_to in enumerate(modules):
            if module_to in dependencies[module_from]:
                matrix[i][j] = 1
    
    # Plot heatmap
    plt.figure(figsize=(10, 8))
    
    sns.heatmap(
        matrix,
        xticklabels=modules,
        yticklabels=modules,
        cmap="YlOrRd",
        cbar_kws={'label': 'Dependency'},
        linewidths=0.5,
        square=True
    )
    
    plt.title("Module Dependency Matrix", fontsize=14, fontweight='bold')
    plt.xlabel("Depends On", fontsize=12)
    plt.ylabel("Module", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close()
