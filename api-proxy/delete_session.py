from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
import re

app = FastAPI()

BASE_ADK_URL = "https://ai-chatbot.mobillor.net/dev_api"

# Reusable HTTP client
client = httpx.AsyncClient(timeout=60.0)


@app.delete("/dev/proxy/delete_session")
async def delete_session(
    userId: str = Query(...),
    sessionId: str = Query(...),
    appName: str = Query(...)
):
    try:
        # Validation
        if not userId or not sessionId or not appName:
            return JSONResponse(
                content={"error": "Missing required parameters"},
                status_code=400
            )

        # Sanitization
        pattern = r"^[a-zA-Z0-9_-]+$"

        if not re.match(pattern, userId):
            return JSONResponse({"error": "Invalid userId"}, status_code=400)

        if not re.match(pattern, appName):
            return JSONResponse({"error": "Invalid appName"}, status_code=400)

        #  Build ADK URL
        adk_url = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions/{sessionId}"

        #  Call ADK DELETE
        response = await client.delete(
            adk_url,
            headers={"Content-Type": "application/json"}
        )

        #  Handling failure 
        if response.status_code not in [200, 204]:
            return JSONResponse(
                content={
                    "success": False,
                    "error": "Failed to delete session",
                    "details": response.text
                },
                status_code=response.status_code
            )

        # Success response
        return JSONResponse(
            content={
                "success": True,
                "userId": userId,
                "sessionId": sessionId,
                "message": f"Session {sessionId} deleted successfully"
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )