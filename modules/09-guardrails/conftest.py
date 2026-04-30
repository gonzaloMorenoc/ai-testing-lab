import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Prevent pytest from collecting test-named functions inside src/ modules.
# pii_canary.test_no_system_prompt_leak is a public API function, not a test.
collect_ignore_glob = ["src/*.py"]
