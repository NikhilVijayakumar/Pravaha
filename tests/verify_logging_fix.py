
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path.cwd() / "src/nikhil"))

output_file = Path("logs/verify_result.txt")
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    f.write("--- VERIFICATION REPORT ---\n")
    try:
        # 1. Verify Import (Typo Fix)
        try:
            from pravaha.domain.logging.manager.logging_manager import PravahaLoggingManager
            f.write("✅ PASS: Import PravahaLoggingManager successful.\n")
        except ImportError:
            f.write("❌ FAIL: Could not import PravahaLoggingManager.\n")
            raise

        # 2. Verify Config (Timestamp Fix)
        # Note: We need to re-initialize or inspect the file directly because 
        # previous runs might have cached the config in memory if we were in the same process.
        # Since this is a new process, it should load from file.
        
        logger = PravahaLoggingManager.get_logger()
        nibandha_instance = PravahaLoggingManager.get_instance()
        
        if nibandha_instance and nibandha_instance.rotation_config:
            ts_format = nibandha_instance.rotation_config.timestamp_format
            if ts_format == "%Y-%m-%d":
                f.write(f"✅ PASS: Timestamp format is '{ts_format}'.\n")
            else:
                f.write(f"❌ FAIL: Timestamp format is '{ts_format}'. Expected '%Y-%m-%d'.\n")
        else:
             f.write("❌ FAIL: Nibandha instance or rotation config not loaded.\n")

    except Exception as e:
        f.write(f"❌ FAIL: Error during verification: {e}\n")
