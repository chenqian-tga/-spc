from pathlib import Path
import sys


WORK_DIR = Path(__file__).resolve().parent / "work"
if str(WORK_DIR) not in sys.path:
    sys.path.insert(0, str(WORK_DIR))

from streamlit_spc_app import main


if __name__ == "__main__":
    main()
