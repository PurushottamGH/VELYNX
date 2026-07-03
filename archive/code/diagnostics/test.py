import requests

url = "https://opengateway.gitlawb.com/v1/chat/completions"

headers = {
    "Authorization": "Bearer ogw_live_694b53d425d0a11c6bb83448e166129c",
    "Content-Type": "application/json",
    "Accept-Encoding": "identity"
}

payload = {
    "model": "mimo-v2.5-pro",
    "messages": [
        {
            "role": "user",
            "content": "hello"
        }
    ]
}

response = requests.post(
    url,
    headers=headers,
    json=payload
)

print(response.status_code)
print(response.text)