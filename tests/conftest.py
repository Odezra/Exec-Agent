# Auto-adjust PYTHONPATH so that the project root is on sys.path
# Load .env so tests pick up environment variables from the .env file
import os, sys
from dotenv import load_dotenv
load_dotenv()

# Calculate project root (parent of this tests/ directory)
_TESTS_DIR = os.path.dirname(__file__)
_PROJECT_ROOT = os.path.abspath(os.path.join(_TESTS_DIR, os.pardir))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)