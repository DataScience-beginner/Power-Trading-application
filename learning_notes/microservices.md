# Microservices Architecture

## Overview
Microservices architecture is a design approach where an application is composed of small, independent services that communicate with each other. Each service is responsible for a specific functionality and can be developed, deployed, and scaled independently.

### Key Benefits:
1. **Fault Isolation**: If one service fails, it does not bring down the entire application.
2. **Scalability**: Individual services can be scaled independently based on demand.
3. **Flexibility**: Different services can use different technologies and programming languages.
4. **Ease of Deployment**: Services can be deployed independently, enabling faster updates.

## User Service
The `user-service` is the first microservice in the Power Trading Application. It is responsible for managing user-related functionalities such as registration, login, and profile management.

### Endpoints:
1. `POST /register`: Registers a new user.
2. `POST /login`: Authenticates a user.
3. `GET /profile`: Fetches the profile of a user.

### Error Handling:
- Proper error messages are returned for scenarios such as:
  - Missing required fields.
  - Invalid credentials.
  - User not found.

### Steps to Run Locally:
1. Navigate to the `user-service` directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the service:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Test the endpoints using Postman or curl.

### Next Steps:
- Add database integration for user data.
- Implement token-based authentication for secure login.
- Write unit tests for the service.

## Testing User Service

### Endpoints Tested:
1. **Health Check**:
   - Endpoint: `GET /`
   - Response: `{ "message": "User Service is running" }`

2. **Register User**:
   - Endpoint: `POST /register`
   - Request Body:
     ```json
     {
       "username": "testuser",
       "password": "testpass"
     }
     ```
   - Response: `{ "message": "User testuser registered successfully" }`

3. **Login User**:
   - Endpoint: `POST /login`
   - Request Body:
     ```json
     {
       "username": "testuser",
       "password": "testpass"
     }
     ```
   - Response: `{ "message": "Login successful" }`

4. **Get Profile**:
   - Endpoint: `GET /profile`
   - Query Parameters: `username=testuser`
   - Response: `{ "username": "testuser", "email": "testuser@example.com" }`

### Observations:
- All endpoints returned the expected responses.
- Error handling was verified for invalid inputs and worked as expected.