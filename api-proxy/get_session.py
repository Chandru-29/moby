from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
import re

app = FastAPI()

BASE_ADK_URL = "https://ai-chatbot.mobillor.net/dev_api"

# Reuse client (better performance)
client = httpx.AsyncClient(timeout=60.0)


@app.get("/dev/proxy/get_session")
async def get_session(
    userId: str = Query(...),
    sessionId: str = Query(...),
    appName: str = Query(...)
):
    try:
        # Basic validation
        if not userId or not sessionId or not appName:
            return JSONResponse(
                content={"error": "Missing required parameters"},
                status_code=400
            )

        #  Prevent injection 
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

        #  Build ADK URL
        adk_url = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions/{sessionId}"

        # Call ADK API
        response = await client.get(
            adk_url,
            headers={"Content-Type": "application/json"}
        )

        #  Return response
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )

    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )