import sys
import argparse

import uvicorn

from src.main import app


if __name__ == "__main__":
    reload = sys.argv[1] if len(sys.argv) > 1 else "False"

    parser = argparse.ArgumentParser(description="FastAPI with Cache Redis")
    parser.add_argument("--reload", type=str, default="False", help="Enable reload mode (set to 'debug' for debug level logging)")

    options = parser.parse_args()

    if options.reload:
        uvicorn.run("src.__main__:app", host="0.0.0.0", port=8001, ws="none", reload=True, log_level="debug")
    else:
        uvicorn.run("src.__main__:app", host="0.0.0.0", port=8001, ws="none", reload=False, log_level="debug")
