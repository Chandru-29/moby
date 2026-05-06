from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
import httpx
import asyncio
import json
from run_api import router as run_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run_router)

# URLs
BASE_ADK_URL = "https://ai-chatbot.mobillor.net/dev_api"
ADK_RUN_URL = f"{BASE_ADK_URL}/run"

# HTTP client
client = httpx.AsyncClient(timeout=60.0)


# ---------------------------------------------------
# HOME
# ---------------------------------------------------
@app.get("/")
def home():
    return {"status": "API is running"}



# ---------------------------------------------------
# CREATE SESSION
# ---------------------------------------------------
@app.post("/dev/proxy/create_session")
async def create_session(userId: str = Query(...), appName: str = Query(...)):
    url = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions"
    res = await client.post(url, json={})
    return JSONResponse(content=res.json(), status_code=res.status_code)


# ---------------------------------------------------
# LIST SESSION
# ---------------------------------------------------
@app.get("/dev/proxy/list_session")
async def list_session(userId: str = Query(...), appName: str = Query(...)):
    url = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions"
    res = await client.get(url)
    return JSONResponse(content=res.json(), status_code=res.status_code)


# ---------------------------------------------------
# GET SESSION
# ---------------------------------------------------
@app.get("/dev/proxy/get_session")
async def get_session(userId: str = Query(...), sessionId: str = Query(...), appName: str = Query(...)):
    url = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions/{sessionId}"
    res = await client.get(url)
    return JSONResponse(content=res.json(), status_code=res.status_code)


# ---------------------------------------------------
# DELETE SESSION
# ---------------------------------------------------
@app.delete("/dev/proxy/delete_session")
async def delete_session(userId: str = Query(...), sessionId: str = Query(...), appName: str = Query(...)):
    url = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions/{sessionId}"
    res = await client.delete(url)

    if res.status_code not in [200, 204]:
        return JSONResponse(
            content={"success": False, "error": res.text},
            status_code=res.status_code
        )

    return {"success": True, "sessionId": sessionId}


# ---------------------------------------------------
# DELETE ALL
# ---------------------------------------------------
@app.delete("/dev/proxy/deleteAll_session")
async def delete_all(userId: str = Query(...), appName: str = Query(...)):
    url = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions"

    res = await client.get(url)
    sessions = res.json()

    async def delete_one(s):
        sid = s.get("id")
        durl = f"{BASE_ADK_URL}/apps/{appName}/users/{userId}/sessions/{sid}"
        r = await client.delete(durl)
        return {"sessionId": sid, "success": r.status_code in [200, 204]}

    results = await asyncio.gather(*[delete_one(s) for s in sessions])

    return {"success": True, "deleted": results}


