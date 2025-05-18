import requests
import base64
import time

client_id = "c0173db999d54a1e9fbeae16cf1d1ad3"
client_secret = "d76ea4e136d8441995316097281f14a1"


# Cache token and expiry time globally
access_token = None
token_expiry = 0  # Unix timestamp

def get_access_token():
    global access_token, token_expiry

    # Check if token is still valid
    if access_token and time.time() < token_expiry:
        return access_token

    # Generate new token
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data.get('access_token')
        expires_in = response_data.get('expires_in')  # usually 3600 sec
        token_expiry = time.time() + expires_in - 10  # buffer of 10 sec

        print("✅ Access token retrieved successfully!")
        print("Access Token:", access_token)
        return access_token
    else:
        print("❌ Failed to get access token.")
        print(response.json())
        return None

# --- Optional: test this directly when running the file ---
if __name__ == '__main__':
    get_access_token()
