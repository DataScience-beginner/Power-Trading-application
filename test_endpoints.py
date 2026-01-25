import requests

def test_register():
    url = "http://0.0.0.0:8000/register"
    payload = {"username": "testuser", "password": "testpass"}
    response = requests.post(url, json=payload)
    print("Testing /register endpoint")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

def test_login():
    url = "http://0.0.0.0:8000/login"
    payload = {"username": "testuser", "password": "testpass"}
    response = requests.post(url, json=payload)
    print("\nTesting /login endpoint")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

def test_profile():
    url = "http://0.0.0.0:8000/profile"
    params = {"username": "testuser"}
    response = requests.get(url, params=params)
    print("\nTesting /profile endpoint")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

if __name__ == "__main__":
    test_register()
    test_login()
    test_profile()