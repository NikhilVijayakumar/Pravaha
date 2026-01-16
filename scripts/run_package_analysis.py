"""
Package Dependency Analysis Orchestrator

Main entry point for running package dependency analysis.
"""

from pathlib import Path
import sys

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from code_analysis.package_analyzer import PackageDependencyAnalyzer
from code_analysis.package_reporter import generate_package_dependency_report


def main():
    """Run package dependency analysis."""
    print("=" * 60)
    print("PACKAGE DEPENDENCY ANALYSIS")
    print("=" * 60)
    
    # Paths
    root_dir = Path(__file__).resolve().parent.parent
    
    report_dir = root_dir / ".Nibandha" / "Pravaha" / "Report" / "data"
    template_dir = root_dir / "docs" / "code_analysis" / "templates"
    
    print(f"Working directory: {root_dir}")
    print(f"Report directory: {report_dir}")
    
    # Ensure directories exist
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Initialize analyzer
    print("\n[1/2] Analyzing packages...")
    analyzer = PackageDependencyAnalyzer(root_dir)
    
    # 2. Run analysis
    analysis = analyzer.analyze()
    
    print(f"\n✅ Analysis complete:")
    print(f"   - Installed: {analysis['installed_count']} packages")
    print(f"   - Outdated: {analysis['outdated_count']} packages")
    print(f"   - Major updates: {analysis['major_updates']}")
    print(f"   - Minor updates: {analysis['minor_updates']}")
    print(f"   - Potentially unused: {analysis['unused_count']}")
    
    # 3. Generate report
    print("\n[2/2] Generating report...")
    generate_package_dependency_report(
        analysis,
        report_dir / "package_dependency_report.md",
        template_dir / "package_dependency_template.md"
    )
    
    print("\n" + "=" * 60)
    print("COMPLETE!")
    print(f"Report: {report_dir / 'package_dependency_report.md'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
