import sys
from pathlib import Path

# Add the repository `backend` folder to sys.path so tests can import `app`
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
