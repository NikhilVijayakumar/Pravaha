import shutil
import datetime
import sys
import os

# Ensure script can import modules from parent directory if run from root
# But we are likely running as module: python -m scripts.reporting.run_all
# or python scripts/reporting/run_all.py -> path issues.

# Best compliant way:
# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.reporting import unit_report, e2e_report, overview, utils

def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting Modular Test Report Generation: {timestamp}")
    
    # 1. Clean Directory
    if utils.REPORTS_DIR.exists():
        shutil.rmtree(utils.REPORTS_DIR)
    utils.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. Run Unit Tests
    try:
        unit_report.run(timestamp)
    except Exception as e:
        print(f"Unit Report Failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. Run E2E Tests
    try:
        e2e_report.run(timestamp)
    except Exception as e:
        print(f"E2E Report Failed: {e}")
        traceback.print_exc()

    # 4. Overview
    try:
        overview.run(timestamp)
    except Exception as e:
        print(f"Overview Generation Failed: {e}")
        traceback.print_exc()
        
    print(f"\n[DONE] Reports generated at: {utils.REPORTS_DIR}")
    print(f"Main Dashboard: {utils.REPORTS_DIR / 'README.md'}")

if __name__ == "__main__":
    main()
