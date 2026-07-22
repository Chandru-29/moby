from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
import re

app = FastAPI()

BASE_ADK_URL = "https://ai-chatbot.mobillor.net/dev_api"

# Reusable HTTP client (better performance)
client = httpx.AsyncClient(timeout=60.0)


@app.post("/dev/proxy/create_session")
async def create_session(
    userId: str = Query(...),
    appName: str = Query(...)
):
    try:
        #  Validation
        if not userId or not appName:
            return JSONResponse(
                content={"error": "Missing userId or appName"},
                status_code=400
            )

        #  Prevent malformed values
        if not re.match(r"^[a-zA-Z0-9_-]+$", appName):
            return JSONResponse(
                content={"error": "Invalid appName"},
                status_code=400
            )

        if not re.match(r"^[a-zA-Z0-9_-]+$", userId):
            return JSONResponse(
                content={"error": "Invalid userId"},
                status_code=400
            )

    #  ADK URL  
        adk_url = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions"

    #  Call ADK API (POST with empty body)
        response = await client.post(
            adk_url,
            json={},  # Important: empty JSON body
            headers={"Content-Type": "application/json"}
        )

        # Return response
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )

    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )