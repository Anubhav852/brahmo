from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main import process_dashboard_request  # Importing the unified logic

app = FastAPI()

# Enable CORS: This allows your React app (localhost:3000) 
# to communicate with your FastAPI backend (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/dashboard/{user_id}/{node_id}")
async def get_dashboard(user_id: str, node_id: str):
    # Now this endpoint is just a thin wrapper around your core logic
    return process_dashboard_request(user_id, node_id)