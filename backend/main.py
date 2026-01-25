from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# Update allowed origins to include the frontend-react's URL
allowed_origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # Added for frontend-react
    "http://127.0.0.1:3001"   # Added for frontend-react
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Updated to include frontend-react
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods for now
    allow_headers=["*"]  # Allow all headers for now
)

# Update the static files directory to use an absolute path
static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Power Trading Application Backend!"}