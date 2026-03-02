import requests
import json
from typing import Optional, Dict, Any

# ===============================
# CONFIG
# ===============================

PICKLIST_API_URL = "https://swms.mobillor.net/api/api/acp/api/swms/picklist/v2w2/picklist_with_pagination"
REQUEST_TIMEOUT = 10
MAX_ROWS_PER_PAGE = 20


# ===============================
# PICKLIST API TOOL
# ===============================

def get_picklists(
    page_number: int = 1,
    rows_per_page: int = 10,
    search: Optional[Dict[str, Any]] = None,
    status: Optional[int] = None
) -> Dict[str, Any]:
    """
    Fetch picklists from Picklist API (PAGINATED).

    Supported filters:
    - search (e.g. {"itemCode": "IC-027"})
    - status (integer)

    Fetches ONLY one page at a time.
    """

    # ---------------------------
    # SAFETY GUARDS
    # ---------------------------
    if page_number < 1:
        page_number = 1

    if rows_per_page > MAX_ROWS_PER_PAGE:
        rows_per_page = MAX_ROWS_PER_PAGE

    # ---------------------------
    # QUERY PARAMS
    # ---------------------------
    params = {
        "page_number": page_number,
        "rows_per_page": rows_per_page
    }

    if search and isinstance(search, dict):
        params["search"] = json.dumps(search)

    if status is not None:
        params["status"] = status

    # ---------------------------
    # API CALL
    # ---------------------------
    try:
        response = requests.get(
            PICKLIST_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        api_response = response.json()

    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error": "Failed to fetch picklists",
            "details": str(exc)
        }

    # ---------------------------
    # VALIDATION
    # ---------------------------
    if not api_response.get("status"):
        return {
            "success": False,
            "error": api_response.get("msg", "Picklist API returned failure")
        }

    # ---------------------------
    # NORMALIZATION
    # ---------------------------
    records = api_response.get("data", [])
    pagination = api_response.get("pagination", {})

    return {
        "success": True,
        "entity": "picklist",
        "records": records,
        "metadata": {
            "currentPage": pagination.get("currentPage", page_number),
            "rowsPerPage": pagination.get("rowsPerPage", rows_per_page),
            "lastPage": pagination.get("lastPage"),
            "totalRecords": pagination.get("totalRecords"),
            "recordCount": len(records),
            "isPaginated": True
        }
    }
