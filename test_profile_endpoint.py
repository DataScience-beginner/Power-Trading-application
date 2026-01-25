import requests

url = "http://0.0.0.0:8000/profile"
params = {"username": "testuser"}

try:
    response = requests.get(url, params=params)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error:", e)