from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import asyncio
import json
from db import upsert_token_usage
import os
from dotenv import load_dotenv
from fastapi import APIRouter

router = APIRouter()
load_dotenv()

# ADK_BASE_URL = os.getenv("ADK_BASE_URL")
ADK_BASE_URL = "https://ai-chatbot.mobillor.net/dev_api/run"

# HTTP client
client = httpx.AsyncClient(timeout=60.0)

# In-memory store (Node-RED global equivalent)
token_store = {}

# ---------------------------------------------------
#  TOKEN TRACKING 
# ---------------------------------------------------   



async def track_tokens(raw_payload, userId, sessionId):
    try:
        print(" track_tokens called:", userId, sessionId)

        try:
            events = json.loads(raw_payload)
        except Exception:
            print(" Invalid JSON → skipping")
            return

      
        if isinstance(events, dict):
            events = [events]
        elif not isinstance(events, list):
            print(" Unexpected format:", type(events))
            return

        totalTokens = 0
        promptTokens = 0
        completionTokens = 0

        for event in events:
            usage = event.get("usageMetadata")
            if not usage:
                continue

            totalTokens += usage.get("totalTokenCount", 0)
            promptTokens += usage.get("promptTokenCount", 0)
            completionTokens += usage.get("candidatesTokenCount", 0)

        print(" Tokens:", totalTokens)

        # STORE IN DB
        upsert_token_usage(
            userId,
            sessionId,
            totalTokens,
            promptTokens,
            completionTokens
        )

        print(" Stored in DB:", userId, sessionId)

    except Exception as e:
        print(" Token tracking error:", str(e))

# ---------------------------------------------------
#  PROXY RUN API
# ---------------------------------------------------
@router.post("/dev/proxy/run")
async def proxy_run(request: Request):
    try:
        payload = await request.json()

        userId = payload.get("userId", "unknown_user")
        sessionId = payload.get("sessionId", "default_session")

        # Step 1: Call ADK
        response = await client.post(
            ADK_BASE_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        raw_text = response.text  # IMPORTANT: Node-RED used raw payload

        # Step 2: Background token tracking (like parallel wire)
        asyncio.create_task(
            track_tokens(raw_text, userId, sessionId)
        )

        # Step 3: Return response (same as Node-RED)
        try:
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
        except Exception:
            return JSONResponse(
                content={"raw": raw_text},
                status_code=response.status_code
            )

    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )










# from fastapi import Request
# from fastapi.responses import JSONResponse
# import httpx
# import os
# from dotenv import load_dotenv
# from fastapi import APIRouter

# router = APIRouter()
# load_dotenv()

# ADK_BASE_URL = "https://ai-chatbot.mobillor.net/dev_api"

# # HTTP client
# client = httpx.AsyncClient(timeout=60.0)


# # ---------------------------------------------------
# #  PROXY RUN API
# # ---------------------------------------------------
# @router.post("/dev/proxy/run")
# async def proxy_run(request: Request):
#     try:
#         payload = await request.json()

#         # Step 1: Call ADK
#         response = await client.post(
#             ADK_BASE_URL,
#             json=payload,
#             headers={"Content-Type": "application/json"}
#         )

#         raw_text = response.text

#         # Step 2: Return response
#         try:
#             return JSONResponse(
#                 content=response.json(),
#                 status_code=response.status_code
#             )
#         except Exception:
#             return JSONResponse(
#                 content={"raw": raw_text},
#                 status_code=response.status_code
#             )

#     except Exception as e:
#         return JSONResponse(
#             content={"error": str(e)},
#             status_code=500
#         )