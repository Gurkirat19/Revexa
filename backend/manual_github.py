import requests

from app.config import GITHUB_TOKEN


url = "https://api.github.com/user"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


response = requests.get(url, headers=headers)

print("Status code:", response.status_code)
print("Response:", response.text)