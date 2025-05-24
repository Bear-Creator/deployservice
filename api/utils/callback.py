import requests

def send_callback(url: str, data: dict):
    try:
        requests.post(url, json=data)
    except Exception as e:
        print(f"Failed to send callback: {e}")