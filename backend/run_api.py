import sys
from pathlib import Path
import uvicorn

# Add project root to PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
