import requests
from .config import ADK_RUN_URL, REQUEST_TIMEOUT_SECONDS

def call_adk_run(payload: dict, headers: dict = None) -> dict:
    headers = headers or {}

    print("➡ Calling ADK:", ADK_RUN_URL)
    print("➡ Payload:", payload)

    try:
        resp = requests.post(
            ADK_RUN_URL,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS
        )

        print("➡ ADK Status:", resp.status_code)
        print("➡ ADK Body:", resp.text)

        resp.raise_for_status()
        return resp.json()

    except Exception as e:
        print("❌ ERROR calling ADK:", e)
        raise
