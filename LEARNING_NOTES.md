# Learning Notes

## CORS (Cross-Origin Resource Sharing)
CORS is a security feature implemented by web browsers to prevent unauthorized access to resources on a different domain. It ensures that only trusted domains can access your server's resources.

### Key Concepts:
1. **Same-Origin Policy**: By default, browsers block requests made from one domain to another for security reasons. CORS allows you to bypass this restriction for trusted domains.
2. **Preflight Requests**: For certain types of requests (e.g., `PUT`, `DELETE`), browsers send a preflight request to the server to check if the actual request is allowed.
3. **CORS Headers**: Servers respond with specific headers to indicate which domains, methods, and headers are allowed.

### Implementation in FastAPI:
In our project, we used the `CORSMiddleware` from FastAPI to configure CORS settings. Here's how it was done:

```python
from fastapi.middleware.cors import CORSMiddleware
import os

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
```

### Key Points:
- **`allow_origins`**: Specifies which domains are allowed to access the server. Using `"*"` allows all domains, but it's recommended to restrict this in production.
- **`allow_credentials`**: Enables cookies and authentication headers to be sent with requests.
- **`allow_methods`**: Restricts the HTTP methods (e.g., `GET`, `POST`) that are allowed.
- **`allow_headers`**: Restricts the headers that can be included in requests.

---

## Docker and Dockerfile
Docker is a platform that allows you to package applications and their dependencies into containers. Containers are lightweight, portable, and ensure consistency across different environments.

### Key Aspects of Docker and the Dockerfile
1. **Base Image**:
   - `FROM python:3.12-slim`: Specifies the base image for the container. In this case, it's a lightweight Python 3.12 image. Base images provide the foundation for your container, including the operating system and pre-installed software.

2. **Working Directory**:
   - `WORKDIR /app`: Sets the working directory inside the container to `/app`. All subsequent commands will be executed in this directory.

3. **Copying Files**:
   - `COPY . /app`: Copies the contents of the current directory (your project files) into the `/app` directory in the container.

4. **Installing Dependencies**:
   - `RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt`: Installs the Python dependencies listed in `requirements.txt`. The `--no-cache-dir` option prevents caching to reduce the image size.

5. **Exposing Ports**:
   - `EXPOSE 8000`: Exposes port 8000 to allow external access to the application running inside the container. This is the default port for FastAPI when using Uvicorn.

6. **Environment Variables**:
   - `ENV PYTHONUNBUFFERED=1`: Sets an environment variable to ensure Python output is sent directly to the terminal without buffering.

7. **Command to Run the Application**:
   - `CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]`: Specifies the command to run when the container starts. Here, it runs the FastAPI application using Uvicorn on port 8000, accessible from any network interface (`0.0.0.0`).

### Why Use Docker?
- **Consistency**: Ensures the application runs the same way in development, testing, and production environments.
- **Isolation**: Keeps the application and its dependencies isolated from the host system.
- **Portability**: Containers can run on any system with Docker installed, regardless of the underlying OS.
- **Scalability**: Makes it easier to scale applications by running multiple containers.

---

## Importance of YAML Files
YAML (YAML Ain't Markup Language) is a human-readable data serialization format often used for configuration files. It is widely used in various tools and platforms, including Docker Compose, Kubernetes, and deployment services like Railway and Render.

### Key Points:
1. **Human-Readable**:
   - YAML is designed to be easy to read and write, making it ideal for configuration files.
   - It uses indentation to represent data hierarchy, similar to Python.

2. **Flexibility**:
   - YAML files can have any name, such as `render.yaml`, `ABC.yaml`, or `config.yaml`. The name does not matter as long as the platform or tool is configured to recognize it.

3. **Multiple YAML Files**:
   - If multiple YAML files are present, the behavior depends on the platform or tool being used. For example:
     - Some platforms may look for a specific file name (e.g., `render.yaml` for Render).
     - Others may allow you to specify which YAML file to use during deployment.
     - If no specific file is specified, the platform may throw an error or use the default file.

4. **Standardization**:
   - YAML is a standard format supported by many tools, making it a versatile choice for configuration management.

### YAML Expansion:
- YAML stands for **YAML Ain't Markup Language**. It emphasizes simplicity and readability over complex syntax.

### Example Usage in Deployment:
- In our project, the `render.yaml` file is used to configure the deployment of the backend application to Railway. It specifies the service name, type, environment, build commands, start commands, and environment variables.

---

These notes can be used for future reference or interview preparation. Let me know if you'd like to add more topics!