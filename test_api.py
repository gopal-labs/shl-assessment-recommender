import requests

url = "http://127.0.0.1:8000/chat"
data = {
    "messages": [
        {"role": "user", "content": "We need a personality test for a retail customer service entry-level role."}
    ]
}

print("Sending request to the API...")
response = requests.post(url, json=data)

try:
    print(response.json())
except Exception:
    print(f"Error! Status Code: {response.status_code}")
    print(response.text)
