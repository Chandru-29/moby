# SYSTEM: Warehouse Management System

TYPE: context

DESCRIPTION:
Warehouse Management System (WMS) schema, relationships, and SQL generation rules.

RULE:
- Do NOT invent tables or columns
- Only use defined schema

PRIORITY RULE:

If a QUERY pattern is present in retrieved knowledge:
→ USE IT as base
→ DO NOT rewrite structure
→ ONLY adjust filters if needed

COLUMN RULE:
Use EXACT column names from schema (case-sensitive)

---

# GLOBAL RULES
TYPE: constraint

RULES:

- Always filter isDeleted = 0
- Use TOP instead of LIMIT (SQL Server)
- Follow defined joins strictly
- Do NOT assume missing relationships
- Use [user] for reserved keyword table

---

# USER RESOLUTION
TYPE: constraint

RULES:

- PICKLIST.assignedUser → [user].userId
- NEVER return assignedUser directly
- ALWAYS join [user]

RETURN:
- user.name
- user.userName

---

# BUSINESS TERM MAPPING
TYPE: semantic

"location" → LOCATION.locationCode
"bin location" → LOCATION.locationCode
"put away location" → LOCATION.locationCode
GRN = entry point (inbound flow)
ITEM = master reference

Bridge = itemCode (NOT itemId)

Stock is NOT directly in GRN
→ must go through SKUITEM → SULOCATION

# JOIN REQUIREMENT:
To get put away location:

PICKLIST 
→ PICKLISTVIEW 
→ SULOCATION 
→ LOCATION

"inventory" → SULOCATION.qty
"stock" → SULOCATION.qty

"picklist" → PICKLIST
"picklist items" → PICKLISTITEM
"item" → ITEM

---

# TABLE: ITEM
TYPE: schema

COLUMNS:
itemId (PK)
itemCode (UNIQUE)
itemDescription
itemGroup
uom
status
isDeleted
cd
ud

USAGE:
- Item master data
- Use for item details and counts

---

# TABLE: SKUITEM
TYPE: schema

COLUMNS:
skuId (PK)
sku
itemId → ITEM.itemId
qty
grnNumber
vendorCode
vendorName
isDeleted

JOIN:
SKUITEM.itemId → ITEM.itemId

---

# TABLE: SULOCATION
TYPE: schema

COLUMNS:
suidId (PK)
skuId → SKUITEM.skuId
qty
locationId → LOCATION.locationId
picklistId
status
isDeleted

RULE:
- Source of truth for stock

JOIN:
SULOCATION.skuId → SKUITEM.skuId

---

# TABLE: LOCATION
TYPE: schema

COLUMNS:
locationId (PK)
locationCode (UNIQUE)
locationName
parentId
status
isDeleted

USAGE:
- Always use locationCode for filtering

---

# TABLE: PICKLIST
TYPE: schema

COLUMNS:
picklistId (PK)
picklistCode
documentTypeId
documentNumber
status
assignedUser
isDeleted
cd
ud

STATUS:
0 = Created
1 = Released
2 = Picking Started
3 = Picked
4 = Putaway Started
5 = Completed

COMPLETION LOGIC:

- If status = 5 (Completed)
  → completion date = ud (Updated Date)

- "completion date" ALWAYS maps to PICKLIST.ud

DOCUMENT TYPE DEFINITIONS:

1 → GRN
21 → Work Order
16 → Transfer Order

DEFAULT OUTPUT:
picklistCode, status

---

# TABLE: PICKLISTITEM
TYPE: schema

COLUMNS:
picklistItemId (PK)
picklistId → PICKLIST.picklistId
itemId → ITEM.itemId
qty
pickedQty
status
isDeleted

---

# TABLE: PICKLISTVIEW
TYPE: schema

COLUMNS:
picklistViewId (PK)
picklistId → PICKLIST.picklistId
itemId → ITEM.itemId
suidId → SULOCATION.suidId
sourceLocId → LOCATION.locationId
status
isDeleted

---

# TABLE: GRN
TYPE: schema

COLUMNS:
grnId (PK)
grnNumber
grnLineNumber
itemCode
qty
grnDate
cd
isDeleted

RULE:
Latest → ORDER BY cd DESC

---

# TABLE: FGMODEL
TYPE: schema

COLUMNS:
fgModelId (PK)
fgModelCode
itemId → ITEM.itemId
isDeleted

---

# TABLE: ITEMLOCACNMAP
TYPE: schema

COLUMNS:
itemLocAcnMapId (PK)
itemId → ITEM.itemId
locationId → LOCATION.locationId
warehouseId
zoneId
rackId
isDeleted

---

# TABLE: FGTRANSACTION
TYPE: schema

COLUMNS:
fgTransactionId (PK)
fgCode
vin
sNo
putawayTime
isSFG
isVinHold
suidId → SULOCATION.suidId
locationId → LOCATION.locationId
isPutaway
isDelivered
isDeleted
isAccepted
isAccessed
cd
ud
cdBy
udBy
isEol

---

# TABLE: SUIDACTIVITYLOG
TYPE: schema

COLUMNS:
suidActivityLogId (PK)
suidId → SULOCATION.suidId
picklistId
status
remark
isDeleted

---

# TABLE: [user]
TYPE: schema

COLUMNS:
id
name
userName
userId
isDeleted

RULE:
- Always use [user]
- Always filter isDeleted = 0

---

# TABLE: WAREHOUSE
type: schema

COLUMNS:
warehouseId (PK)
warehouseName
warehouseCode
plantId
isActive
isDeleted
cd
ud
cdBy
udBy
warehouseTypeId
acnId
layoutJson

---

# CORE RELATIONSHIPS
TYPE: relationship

ITEM → SKUITEM → SULOCATION

SULOCATION.locationId → LOCATION.locationId

PICKLIST → PICKLISTITEM
PICKLIST → PICKLISTVIEW

PICKLISTVIEW.suidId → SULOCATION.suidId

PICKLIST.assignedUser → [user].userId

FGTRANSACTION.suidId → SULOCATION.suidId
FGTRANSACTION.locationId → LOCATION.locationId

SUIDACTIVITYLOG.suidId → SULOCATION.suidId

SULOCATION.skuId → SKUITEM.skuId
SKUITEM.itemId → ITEM.itemId

WAREHOUSE.warehouseId → ITEMLOCACNMAP.warehouseId

ITEMLOCACNMAP.itemId → ITEM.itemId

ITEMLOCACNMAP.locationId → LOCATION.locationId


GRN.itemCode → ITEM.itemCode

ITEM.itemId → SKUITEM.itemId

SKUITEM.skuId → SULOCATION.skuId

SULOCATION.locationId → LOCATION.locationId



---

# JOIN PATHS (CRITICAL)
TYPE: guidance

ITEM → STOCK:
ITEM → SKUITEM → SULOCATION

PICKLIST → LOCATION:
PICKLIST → PICKLISTVIEW → SULOCATION → LOCATION

PICKLIST → USER:
PICKLIST → [user]

STOCK BY LOCATION:
SULOCATION → LOCATION

WAREHOUSE → ITEMLOCACNMAP → ITEM
WAREHOUSE → ITEMLOCACNMAP → LOCATION
WAREHOUSE → ITEMLOCACNMAP → ITEM → SKUITEM → SULOCATION
WAREHOUSE → ITEMLOCACNMAP → ITEM → SKUITEM → SULOCATION → LOCATION
WAREHOUSE → ITEMLOCACNMAP → ITEM → SKUITEM → SULOCATION → FGTRANSACTION

GRN → ITEM (via itemCode)
GRN → ITEM → SKUITEM → SULOCATION
GRN → ITEM → SKUITEM → SULOCATION → LOCATION
ITEM → GRN (via itemCode)
ITEM → GRN → SKUITEM → SULOCATION

---

# INTENT MAPPING
TYPE: logic

"latest grn"
→ GRN ORDER BY cd DESC

"open picklists"
→ PICKLIST.status IN (1,2,3,4)

"picklist items"
→ PICKLISTITEM

"items with stock"
→ ITEM + SKUITEM + SULOCATION

"inventory"
→ SULOCATION

"inventory by location"
→ SULOCATION + LOCATION

"item details"
→ ITEM

"total items"
→ COUNT(ITEM.itemId)


"warehouse items"
→ WAREHOUSE + ITEMLOCACNMAP + ITEM

"warehouse locations"
→ WAREHOUSE + ITEMLOCACNMAP + LOCATION

"warehouse stock"
→ WAREHOUSE + ITEMLOCACNMAP + ITEM + SKUITEM + SULOCATION

"warehouse inventory by location"
→ WAREHOUSE + ITEMLOCACNMAP + ITEM + SKUITEM + SULOCATION + LOCATION

"warehouse fg tracking"
→ WAREHOUSE + ITEMLOCACNMAP + ITEM + SKUITEM + SULOCATION + FGTRANSACTION

"warehouse item mapping"
→ ITEMLOCACNMAP

"item grn details"
→ ITEM + GRN

"grn item stock"
→ GRN + ITEM + SKUITEM + SULOCATION

"grn inventory by location"
→ GRN + ITEM + SKUITEM + SULOCATION + LOCATION

"items received via grn"
→ GRN + ITEM

"latest grn for item"
→ GRN + ITEM ORDER BY GRN.cd DESC

"grn item movement"
→ GRN + ITEM + SKUITEM + SULOCATION

---

# QUERY PATTERNS
TYPE: query

OPEN PICKLISTS:

SELECT TOP 20 picklistCode, status
FROM PICKLIST
WHERE status IN (1,2,3,4)
AND isDeleted = 0


ITEMS WITH STOCK:

SELECT i.itemCode, SUM(s.qty) AS stock
FROM ITEM i
JOIN SKUITEM sk ON i.itemId = sk.itemId
JOIN SULOCATION s ON sk.skuId = s.skuId
WHERE i.isDeleted = 0
AND sk.isDeleted = 0
AND s.isDeleted = 0
GROUP BY i.itemCode
HAVING SUM(s.qty) > 0


PICKLIST PUTAWAY LOCATION:

SELECT DISTINCT 
    p.picklistCode,
    l.locationCode
FROM PICKLIST p
JOIN PICKLISTVIEW pv ON p.picklistId = pv.picklistId
JOIN SULOCATION s ON pv.suidId = s.suidId
JOIN LOCATION l ON s.locationId = l.locationId
WHERE p.picklistCode = '{picklistCode}'
AND p.isDeleted = 0
AND pv.isDeleted = 0
AND s.isDeleted = 0
AND l.isDeleted = 0


PICKLIST BY MULTIPLE USERS:

SELECT DISTINCT TOP 20
    p.picklistCode,
    u.name
FROM PICKLIST p
JOIN [user] u ON p.assignedUser = u.userId
WHERE u.name IN ({user_names})
AND p.isDeleted = 0
AND u.isDeleted = 0
---

# SPECIAL RULES
TYPE: constraint

DISTINCT:
- Use only when explicitly asked
- Syntax: SELECT DISTINCT TOP N

LATEST:
- Always use cd column
- Never use business date


MULTI VALUE FILTER (CRITICAL):

If user provides multiple values (e.g., multiple user names, item codes, picklist codes):

→ ALWAYS use IN clause

Example:
WHERE u.name IN ('Admin', 'User02', 'User04')

DO NOT:
- use multiple OR conditions
- use separate queries
- use = for multiple values

This rule MUST be followed whenever multiple values are present.