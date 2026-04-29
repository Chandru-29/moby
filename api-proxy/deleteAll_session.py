from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
import asyncio
import re

app = FastAPI()

BASE_ADK_URL = "https://ai-chatbot.mobillor.net/dev_api"

# Reusable HTTP client
client = httpx.AsyncClient(timeout=60.0)


@app.delete("/dev/proxy/deleteAll_session")
async def delete_all_sessions(
    userId: str = Query(...),
    appName: str = Query(...)
):
    try:
        # Validation
        if not userId or not appName:
            return JSONResponse(
                content={"error": "Missing userId or appName"},
                status_code=400
            )

        pattern = r"^[a-zA-Z0-9_-]+$"
        if not re.match(pattern, userId):
            return JSONResponse({"error": "Invalid userId"}, status_code=400)

        if not re.match(pattern, appName):
            return JSONResponse({"error": "Invalid appName"}, status_code=400)

        # --------------------------------------------------
        # GETTING all sessions
        # --------------------------------------------------
        list_url = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions"

        list_response = await client.get(
            list_url,
            headers={"Content-Type": "application/json"}
        )

        if list_response.status_code != 200:
            return JSONResponse(
                content={
                    "success": False,
                    "error": "Failed to fetch sessions",
                    "details": list_response.text
                },
                status_code=list_response.status_code
            )

        sessions = list_response.json()

        
        if not isinstance(sessions, list):
            return JSONResponse(
                content={"error": "Sessions response is not an array"},
                status_code=500
            )

        # --------------------------------------------------
        # Preparing to delete tasks 
        # --------------------------------------------------
        async def delete_single_session(session):
            session_id = session.get("id")

            delete_url = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions/{session_id}"

            try:
                response = await client.delete(
                    delete_url,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in [200, 204]:
                    return {
                        "sessionId": session_id,
                        "success": True
                    }
                else:
                    return {
                        "sessionId": session_id,
                        "success": False,
                        "error": response.text
                    }

            except Exception as e:
                return {
                    "sessionId": session_id,
                    "success": False,
                    "error": str(e)
                }

        # --------------------------------------------------
        #  Run deletes in parallel 
        # --------------------------------------------------
        results = await asyncio.gather(
            *[delete_single_session(s) for s in sessions]
        )

        # --------------------------------------------------
        #  Final response
        # --------------------------------------------------
        return JSONResponse(
            content={
                "success": True,
                "userId": userId,
                "totalSessions": len(sessions),
                "deleted": results
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )