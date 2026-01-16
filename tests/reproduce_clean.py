
import sys
from pathlib import Path

sys.path.append(str(Path.cwd() / "src/nikhil"))

try:
    from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager as PravahaLoggingManager
    from nibandha import LogRotationConfig
except ImportError as e:
    with open("logs/reproduce_error.txt", "w") as f:
        f.write(str(e))
    raise e

output_file = Path("logs/reproduce_result.txt")
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    f.write("--- REPRODUCTION REPORT ---\n")
    
    try:
        logger = PravahaLoggingManager.get_logger()
        f.write(f"Logger Name: {logger.name}\n")
        f.write(f"Logger Propagate: {logger.propagate}\n")
        
        nibandha_instance = PravahaLoggingManager.get_instance()
        if nibandha_instance:
            if nibandha_instance.rotation_config:
                 ts_format = nibandha_instance.rotation_config.timestamp_format
                 f.write(f"Timestamp Format (Instance): {ts_format}\n")
            else:
                 f.write("Timestamp Format (Instance): None (Rotation disabled)\n")
        else:
             f.write("Nibandha Instance: None\n")
             
        # Check default config from class
        default_config = LogRotationConfig()
        f.write(f"Default LogRotationConfig.timestamp_format: {default_config.timestamp_format}\n")

    except Exception as e:
        f.write(f"Error: {e}\n")
