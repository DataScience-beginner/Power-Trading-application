from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Use environment variables for CORS settings
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Use environment variable for allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to necessary methods
    allow_headers=["Authorization", "Content-Type"],  # Restrict to required headers
)

# Serve static files (e.g., favicon)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Power Trading Application Backend!"}