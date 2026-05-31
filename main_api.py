# main_api.py is no longer needed.
# main.py IS the FastAPI app.
# Start the server with:
#
#   uvicorn main:app --reload --port 8000
#
# This file is kept only if other parts of your codebase import from it.

from main import app  # re-export so any existing imports don't break