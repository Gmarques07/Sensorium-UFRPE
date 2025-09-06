import uvicorn
from backend.main import app
import os

if __name__ == "__main__":
    # Disable reload in Docker environment
    reload = os.getenv("DISABLE_RELOAD", "false").lower() != "true"
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=reload)
