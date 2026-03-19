
import sys
import os
from pathlib import Path

# Add scripts directory to path to allow imports
sys.path.append(str(Path(__file__).resolve().parent.parent))
print(sys.path)

from code_analysis import runner, generator
from reporting import utils

REPORT_DIR = Path(__file__).resolve().parent.parent.parent / ".Nibandha" / "Pravaha" / "Report" / "Quality"

def main():
    print("Starting Code Analysis...")
    
    # Ensure directory exists
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    # 1. Run Checks
    arch_results = runner.run_architecture_check()
    type_results = runner.run_type_check()
    cplx_results = runner.run_complexity_check()
    
    # 2. Generate Reports
    print("Generating Reports...")
    generator.generate_architecture_report(arch_results)
    generator.generate_type_safety_report(type_results)
    generator.generate_complexity_report(cplx_results)
    
    # 3. Overview
    generator.generate_overview(arch_results, type_results, cplx_results)
    
    print(f"\nCode Analysis Complete. Reports saved to: {REPORT_DIR}")

if __name__ == "__main__":
    main()
