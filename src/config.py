import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project Root Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DOCS_DIR = DATA_DIR / "synthetic_docs"
TEST_CASES_FILE = DATA_DIR / "test_cases.json"
REBUTTALS_DIR = DATA_DIR / "rebuttals"

# Ensure runtime directories exist
SYNTHETIC_DOCS_DIR.mkdir(parents=True, exist_ok=True)
REBUTTALS_DIR.mkdir(parents=True, exist_ok=True)