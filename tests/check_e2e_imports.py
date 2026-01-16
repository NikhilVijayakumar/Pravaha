
import sys
import traceback

print("Checking imports...")
try:
    from pravaha.domain.llm.protocol import llm_config_protocol
    print("PASS: llm_config_protocol")
except ImportError as e:
    print(f"FAIL: llm_config_protocol - {e}")

try:
    from pravaha.domain.llm.protocol.llm_config_protocol import LLMConfigManagerProtocol
    print("PASS: LLMConfigManagerProtocol")
except ImportError as e:
    print(f"FAIL: LLMConfigManagerProtocol - {e}")

try:
    from pravaha_example.service.server import app
    print("PASS: pravaha_example")
except ImportError as e:
    print(f"FAIL: pravaha_example - {e}")
except Exception as e:
    print(f"FAIL: pravaha_example (runtime) - {e}")
