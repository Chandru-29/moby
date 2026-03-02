# import requests
# import json
# from typing import Optional, Dict, Any

# # =====================================
# # CONFIG
# # =====================================

# ITEM_API_BASE_URL = "https://swms.mobillor.net/api/api/acp/api/swms/item_with_pagination"
# REQUEST_TIMEOUT = 10
# MAX_ROWS_PER_PAGE = 20   # hard safety cap


# # =====================================
# # ITEM API TOOL
# # =====================================

# def get_items(
#     page_number: int = 1,
#     rows_per_page: int = 5,
#     search: Optional[Dict[str, Any]] = None
# ) -> Dict[str, Any]:
#     """
#     Fetch item data from Item API (PAGINATED).

#     - Fetches ONLY ONE PAGE at a time
#     - No auto-pagination
#     - Safe for LLM usage

#     Args:
#         page_number (int): Page number (starts from 1)
#         rows_per_page (int): Rows per page
#         search (dict): Optional search payload (e.g. {"itemCode": "PACK01"})

#     Returns:
#         dict: Normalized API response
#     """

#     # -------------------------------
#     # SAFETY GUARDS
#     # -------------------------------
#     if page_number < 1:
#         page_number = 1

#     if rows_per_page > MAX_ROWS_PER_PAGE:
#         rows_per_page = MAX_ROWS_PER_PAGE

#     # -------------------------------
#     # QUERY PARAMS
#     # -------------------------------
#     params = {
#         "page_number": page_number,
#         "rows_per_page": rows_per_page
#     }

#     if search and isinstance(search, dict):
#         # API expects search as JSON string
#         params["search"] = json.dumps(search)

#     # -------------------------------
#     # API CALL
#     # -------------------------------
#     try:
#         response = requests.get(
#             ITEM_API_BASE_URL,
#             params=params,
#             timeout=REQUEST_TIMEOUT
#         )
#         response.raise_for_status()
#         api_response = response.json()

#     except requests.exceptions.RequestException as exc:
#         return {
#             "success": False,
#             "error": "Failed to fetch item data from Item API",
#             "details": str(exc)
#         }

#     # -------------------------------
#     # VALIDATION
#     # -------------------------------
#     if not api_response.get("status"):
#         return {
#             "success": False,
#             "error": api_response.get("msg", "Item API returned failure")
#         }

#     # -------------------------------
#     # NORMALIZATION LAYER (IMPORTANT)
#     # -------------------------------
#     items = api_response.get("data", [])
#     pagination = api_response.get("pagination", {})

#     normalized_metadata = {
#         "currentPage": pagination.get("currentPage", page_number),
#         "rowsPerPage": pagination.get("rowsPerPage", rows_per_page),
#         "totalRecords": pagination.get("totalRecords"),
#         "lastPage": pagination.get("lastPage"),
#         "recordCount": len(items),
#         "isPaginated": True
#     }

#     return {
#         "success": True,
#         "entity": "item",
#         "records": items,
#         "metadata": normalized_metadata
#     }
