import httpx

API_URL = "https://dlzfnf88-8010.inc1.devtunnels.ms/execute-query" 

try:
  response = httpx.post(API_URL, json={"query": "SELECT picklistCode, documentNumber, status FROM SS_PICKLIST WHERE status IN (0, 1, 2) AND isDeleted = 0 ORDER BY cd DESC LIMIT 4"}, timeout=5.0)
  print(f"Status Code: {response.status_code}")
  print(f"Response: {response.text}")
  if response.status_code == 200:
    print("🚀 API is up and running successfully!")
  else:
    print("⚠️ API responded with an error.")
except Exception as e:
  print(f"❌ Connection failed: {e}")