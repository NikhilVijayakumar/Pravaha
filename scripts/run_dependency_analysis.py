"""
Dependency Analysis Orchestrator

Main entry point for running module dependency analysis.
"""

from pathlib import Path
import sys

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from code_analysis.dependency_scanner import ModuleDependencyScanner
from code_analysis.dependency_visualizer import visualize_dependency_graph, create_dependency_matrix
from code_analysis.dependency_reporter import generate_module_dependency_report


def main():
    """Run module dependency analysis."""
    print("=" * 60)
    print("MODULE DEPENDENCY ANALYSIS")
    print("=" * 60)
    
    # Paths
    root_dir = Path(__file__).parent.parent.parent
    source_dir = root_dir / "src" / "nikhil" / "pravaha" / "domain"
    
    report_dir = root_dir / ".Nibandha" / "Pravaha" / "Report" / "data"
    assets_dir = root_dir / ".Nibandha" / "Pravaha" / "Report" / "assets"
    template_dir = root_dir / "docs" / "code_analysis" / "templates"
    
    # Ensure directories exist
    report_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Scan modules
    print("\n[1/4] Scanning modules...")
    scanner = ModuleDependencyScanner(source_dir)
    dependencies = scanner.scan()
    
    print(f"✅ Found {len(dependencies)} modules")
    
    # 2. Analyze dependencies
    print("\n[2/4] Analyzing dependencies...")
    circular_deps = scanner.find_circular_dependencies()
    most_imported = scanner.get_most_imported(top_n=5)
    most_dependent = scanner.get_most_dependent(top_n=5)
    isolated = scanner.get_isolated_modules()
    
    print(f"   - Circular dependencies: {len(circular_deps)}")
    print(f"   - Isolated modules: {len(isolated)}")
    
    # 3. Generate visualizations
    print("\n[3/4] Generating visualizations...")
    visualize_dependency_graph(
        dependencies,
        assets_dir / "module_dependencies.png",
        circular_deps
    )
    
    try:
        create_dependency_matrix(
            dependencies,
            assets_dir / "dependency_matrix.png"
        )
    except Exception as e:
        print(f"   ⚠️ Could not create matrix: {e}")
    
    # 4. Generate report
    print("\n[4/4] Generating report...")
    generate_module_dependency_report(
        dependencies,
        circular_deps,
        most_imported,
        most_dependent,
        isolated,
        report_dir / "module_dependency_report.md",
        template_dir / "module_dependency_template.md"
    )
    
    print("\n" + "=" * 60)
    print("COMPLETE!")
    print(f"Report: {report_dir / 'module_dependency_report.md'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
