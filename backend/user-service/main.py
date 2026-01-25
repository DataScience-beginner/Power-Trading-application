from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.logger import logger

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

@app.get("/")
def read_root():
    return {"message": "User Service is running"}

@app.post("/register")
def register_user(user: User):
    # Placeholder for user registration logic
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    return {"message": f"User {user.username} registered successfully"}

@app.post("/login")
def login_user(user: User):
    # Placeholder for user authentication logic
    if user.username != "testuser" or user.password != "testpass":
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful"}

@app.get("/profile")
def get_profile(username: str):
    logger.info(f"Fetching profile for username: {username}")
    # Placeholder for fetching user profile
    if username != "testuser":
        logger.error(f"User {username} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User {username} found, returning profile")
    return {"username": username, "email": "testuser@example.com"}