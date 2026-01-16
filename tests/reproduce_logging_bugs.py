
import sys
import os
from pathlib import Path
import logging
import shutil
import time

# Add src/nikhil to sys.path to mimic installation structure if needed
# Assuming the user runs this from the root of the workspace
sys.path.append(str(Path.cwd() / "src/nikhil"))

try:
    from pravaha.domain.logging.manager.logging_manager import PravahaLoggingManager
except ImportError:
    # Try alternate import if structure is different
    from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager as PravahaLoggingManager

def test_propagation():
    print("\n--- Testing Logger Propagation ---")
    logger = PravahaLoggingManager.get_logger()
    
    print(f"Logger Name: {logger.name}")
    print(f"Logger Propagate: {logger.propagate}")
    
    if logger.propagate:
        print("❌ FAIL: Logger propagation is True. Logs will leak to root.")
    else:
        print("✅ PASS: Logger propagation is False.")

def test_timestamp_format():
    print("\n--- Testing Timestamp Format ---")
    # We need to check what file was created.
    # Nibandha stores logs in .Nibandha/Pravaha/logs or .Nibandha/Pravaha/logs/data (if rotation)
    
    nibandha_instance = PravahaLoggingManager.get_instance()
    if not nibandha_instance:
         print("❌ FAIL: Nibandha not initialized.")
         return

    # Check config
    if nibandha_instance.rotation_config:
         ts_format = nibandha_instance.rotation_config.timestamp_format
         print(f"Timestamp Format in Config: {ts_format}")
         if ts_format == "%Y-%m-%d":
             print("✅ PASS: Timestamp format is '%Y-%m-%d'.")
         else:
             print(f"❌ FAIL: Timestamp format is '{ts_format}'. Expected '%Y-%m-%d'.")
    else:
        print("ℹ️ Info: Rotation not enabled/configured. Checking default behavior.")
        # If rotation is not enabled, it uses single file.
        # But we want to verify the *bug* which was about rotation config default.
        
        # Let's inspect the default LogRotationConfig by importing it from nibandha
        from nibandha import LogRotationConfig
        default_config = LogRotationConfig()
        print(f"Default LogRotationConfig.timestamp_format: {default_config.timestamp_format}")
        
        if default_config.timestamp_format == "%Y-%m-%d":
             print("✅ PASS: Default LogRotationConfig fixes the issue.")
        else:
             print(f"❌ FAIL: Default LogRotationConfig has '{default_config.timestamp_format}'.")

if __name__ == "__main__":
    # Clean up previous logs for clear test? 
    # Maybe not, as we want to see if it appends. But for now just checking config.
    
    try:
        test_propagation()
        test_timestamp_format()
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()
