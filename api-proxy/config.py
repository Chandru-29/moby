import os
from dotenv import load_dotenv

load_dotenv()

AI_PROXY_API_KEY = os.getenv("AI_PROXY_API_KEY") or "super_secret_key_123"

# BASE URL OF the HOSTED ADK
ADK_BASE_URL = os.getenv("ADK_BASE_URL", "https://ai-chatbot.mobillor.net")

# ADK RUN ENDPOINT
ADK_RUN_URL = os.getenv("ADK_RUN_URL") or f"{ADK_BASE_URL}/api/run"

REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS") or 15)

JWT_SECRET = os.getenv("JWT_SECRET", "my_jwt_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
