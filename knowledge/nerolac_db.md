# SYSTEM: Nerolac Paint Manufacturing & Warehouse Management System

TYPE: context

DESCRIPTION:
Nerolac WMS and batch production database schema, entity relationships, and SQL generation rules (MySQL / Standard SQL).

RULE:

- Do NOT invent tables or columns
- Only use defined schema
- Table names and column names are case-sensitive where indicated

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

- Always filter `isDeleted = 0` (or `isDeleted = '0'`) for tables containing the soft-delete flag
- Target MySQL syntax (Use `LIMIT` instead of `TOP`)
- Follow defined joins strictly
- Do NOT assume missing relationships
- Use backticks for reserved keywords if necessary (e.g., `user`)

---

# USER RESOLUTION

TYPE: constraint

RULES:

- `pickuplist.assignedUser` → `user.userId` or `user.userName`
- `store.userId` → `user.userId`
- `operator.employeeId` maps to manual operation & charging logs

RETURN:

- user.name
- user.userName

---

# BUSINESS TERM MAPPING

TYPE: semantic

"material" / "item" → item.materialCode
"sku" / "store inventory" → store.sku
"stock" / "available inventory" → store.totalQty / store.actualQty
"suid" → ss_sulocation.suid
"location" / "bin" → location.locationName / ss_sulocation.locationId
"warehouse" → warehouse.warehouseCode / ss_warehouse.warehouseCode
"picklist" → pickuplist.pickupListCode / ss_picklist.picklistCode
"piv order" / "process order" → pivheaders.poNumber / pivallocation.pickupListCode
"pallet" → assetmaster.assetId / store.palletId / pallet.palletId
"movement" → movementheaders / movementpickuplist / movementlineitems
"grn" → store.grnNumber

---

# TABLE: item

TYPE: schema

COLUMNS:
id (PK)
plant
materialCode (UNIQUE)
materialDescription
materialType
materialTypeDesc
materialGroup
uom
issueType
sloc
sloc2
procurementType
shelfLife
batchIndicator
isFEFO
partialCharging
storLoc
isXBT
cd

USAGE:

- Item and raw material master reference data

---

# TABLE: store

TYPE: schema

COLUMNS:
id (PK)
sku (UNIQUE)
grnNumber
grnDate
grnLineNumber
asnNumber
invoiceNumber
vendorCode
vendorName
materialCode
materialDescription
mfgDate
shelfLife
uom
batchNumber
plant
sourceLocation
storingLocation
locationId
invoiceQty
actualQty
holdQty
packSize
totalPacks
totalQty
printedDate
palletId
isPutaway
isPartFull
putawayStartTime
putawayEndTime
stockType
isRejected
rejectedQty
isBatch
userName
movementRestrictedQty
userId
reValidation
isRestricted
storageCon
isPiv
refDocType
refDoc
poNumber
reprintCount
isMaterialReturned
parentSkuId

USAGE:

- Primary warehouse storage inventory and inbound SKU ledger

---

# TABLE: ss_sulocation

TYPE: schema

COLUMNS:
suidId (PK)
suid (UNIQUE)
skuId → store.id
qty
packSize
locationId → ss_location.locationId
isGrouped
grnLineNumber
serialNumber
status
palletId
binId
tempAssetId
inTransit
onHold
picklistId
isAllocated
rejectionReason
documentId
kittingType
isDeleted
cd
ud
cdBy
udBy

RULE:

- Unit storage tracking for picklist fulfillment and bin location mapping

---

# TABLE: location

TYPE: schema

COLUMNS:
id (PK)
locationName
warehouseId
zoneId
isEmpty
isDeleted
cd
ud

USAGE:

- Physical warehouse locations and storage bin tracking

---

# TABLE: ss_location

TYPE: schema

COLUMNS:
locationId (PK)
locationCode (UNIQUE)
locationName
parentId
parentCode
isLocation
rltId
status
isEmpty
isDeleted
cd
ud
cdBy
udBy

---

# TABLE: warehouse

TYPE: schema

COLUMNS:
id (PK)
plant
warehouseName
warehouseCode
type
isDeleted
isActive
cd
ud
storeType

---

# TABLE: ss_warehouse

TYPE: schema

COLUMNS:
warehouseId (PK)
warehouseName
warehouseCode
warehouseTypeId
acnId
plantId
isActive
isDeleted
cd
ud
cdBy
udBy

---

# TABLE: ss_whlocmap

TYPE: schema

COLUMNS:
whLocMapId (PK)
warehouseId → ss_warehouse.warehouseId
locationId → ss_location.locationId
isDeleted
cd
ud
cdBy
udBy

---

# TABLE: ss_whtypemap

TYPE: schema

COLUMNS:
WHTypeMapId (PK)
warehouseId
warehouseTypeId
isDeleted
cd
ud
cdBy
udBy

---

# TABLE: pivheaders

TYPE: schema

COLUMNS:
id (PK)
plant
date
poNumber (UNIQUE)
orderType
mrpType
prodVer
createdDate
releaseDate
plannedStartDate
plannedEndDate
basicStartDate
basicFinishDate
tecoDate
batchNumber
batchSize
batchUom
batchPercQty
finalMaterialCode
finalMaterialDescription
cd
plantDesc
isPoClosed
poClosedTime

USAGE:

- Production order headers and PIV batch schedules

---

# TABLE: pivphases

TYPE: schema

COLUMNS:
id (PK)
poNumber
phaseNumber
phaseDescription
srNo
itemNo
batchNumber
resources
materialCode
materialDescription
materialPercQty
materialQty
upperLimit
lowerLimit
materialUom
phaseProInstruction
gi
sign
status
ctaStatus
ctaTime
officerId
sapRes
isSapPosted
postedDate
cd
matIssuanceDate
proReleaseTime
storeIssuanceDate
releasePickuplistDate

---

# TABLE: pivmaterialissueslip

TYPE: schema

COLUMNS:
id (PK)
poNumber
pBatchNumber
finalMaterialCode
finalMaterialDescription
orderStartDate
orderQty
phaseDescription
materialCode
materialDescription
formQty
uom
batchNumber
batchQty
storageLoc
cd

---

# TABLE: pivallocation

TYPE: schema

COLUMNS:
id (PK)
documentType
documentNumber
lineNumber
srNo
materialCode
materialDescription
finalMaterialCode
finalMaterialDescription
qty
pickupListCode (UNIQUE)
destination
grossWeight
tareWeight
actualWeight
balanceBatchQty
assetId
assignedUser
resource
startTime
endTime
status
cd
isDeleted
ud
weightSaved
checker
charged
source

---

# TABLE: pickuplist

TYPE: schema

COLUMNS:
id (PK)
plant
pickupListCode (UNIQUE)
documentType
documentNumber
lineNumber
srNo
materialCode
qty
uom
source
destination
status
cd
assignedUser
pickupStartTime
pickupEndTime
resourceId
ud
prdKittingStatus
officer
storeUserAllocationTime
materialReturnUser
forceClosed
forceClosedTime

---

# TABLE: ss_picklist

TYPE: schema

COLUMNS:
picklistId (PK, UNIQUE)
picklistCode (UNIQUE)
documentTypeId → ss_document.documentId
documentNumber
mvtId → ss_mvt.mvtId
status
picklistTypeStatus
assignedUser
transactionId → ss_transactionm.transactionId
pivHeaderId → pivheaders.id
pivPhaseId → pivphases.id
supersedeFEFO
isDeleted
cd
ud
cdBy
udBy

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
- "completion date" ALWAYS maps to ss_picklist.ud (or PICKLIST.ud)

DOCUMENT TYPE DEFINITIONS:
1 → GRN
21 → Work Order
16 → Transfer Order

DEFAULT OUTPUT:
picklistCode, status

---

# TABLE: ss_picklistview

TYPE: schema

COLUMNS:
picklistViewId (PK)
picklistId → ss_picklist.picklistId
itemId → item.id
suidId
suid
pickedQty
allocatedQty
sourceLocId
sourcePalletId
sourceBinId
sourceAssetId
status
isDeleted
cd
ud
cdBy
udBy

---

# TABLE: pickuplistmapping

TYPE: schema

COLUMNS:
id (PK)
pickupListCode
materialCode
sku
qty
pickedQty
allocatedQty
uom
locationId
palletId
virtualBinId
isPicked
isPutaway
cd
pickupStartTime
pickupEndTime
chargedStatus
chargedTime
resource
operator
chargedQty
ispartial
kittingTime
putawayTime
releaseToShopFloorTime
isMaterialReturned

---

# TABLE: ss_supersedefefomapping

TYPE: schema

COLUMNS:
supersedaFefoMapId (PK)
picklistId → ss_picklist.picklistId
reason
userId
isDeleted
cd
ud
cdBy
udBy

---

# TABLE: movementheaders

TYPE: schema

COLUMNS:
id (PK)
documentNumber
movementType
tCode
plant
vendorName
vendorCode
cd
udCode

---

# TABLE: movementlineitems

TYPE: schema

COLUMNS:
id (PK)
plant
materialCode
documentNumber
movementType
tCode
lineNumber
qty
uom
source
destination
inspectionLotId
batchNumber
grnNumber
grnLineNumber
recvMaterial
recvPlant
recvPlantDescription
recvBatch
status
cd
expiryDate

---

# TABLE: movementpickuplist

TYPE: schema

COLUMNS:
id (PK)
plant
pickupListCode (UNIQUE)
movementType
tCode
documentNumber
lineNumber
materialCode
qty
uom
source
destination
status
assignedUser
cd
movementStartTime
movementEndTime
expiryDate

---

# TABLE: movementsuidmapping

TYPE: schema

COLUMNS:
id (PK)
documentNumber
pickupListCode
materialCode
suId
qty
pickedQty
allocatedQty
uom
locationId
palletId
virtualBinId
grnNumber
isPicked
isPutaway
cd
documentType
movedQty

---

# TABLE: movementtypes

TYPE: schema

COLUMNS:
id (PK)
movementType
description
type
cd

---

# TABLE: ss_mvt

TYPE: schema

COLUMNS:
mvtId (PK)
mvtCode (UNIQUE)
mvtName
mvtDescription
sAcnId
dAcnId
isDeleted
cd
ud
cdBy
udBy

---

# TABLE: user

TYPE: schema

COLUMNS:
id (PK)
name
userName (UNIQUE)
userId (UNIQUE)
email (UNIQUE)
password
roleId
firstlogin
isMobileLoggedIn
isDashboardLoggedIn
printerId
isDefaultPrinterSet
isDeleted
cd
ud

---

# TABLE: accesses

TYPE: schema

COLUMNS:
id (PK)
roleId
actionId
departmentId
isDeleted
cd
ud

---

# TABLE: action

TYPE: schema

COLUMNS:
id (PK)
actionId (UNIQUE)
actionName
subModuleId
isDeleted
cd
ud

---

# TABLE: submodules

TYPE: schema

COLUMNS:
id (PK)
subModuleId (UNIQUE)
subModuleName
moduleId
isDeleted
cd
ud

---

# TABLE: department

TYPE: schema

COLUMNS:
id (PK)
departmentName
departmentId
isDeleted
cd
ud

---

# TABLE: qualityinspector

TYPE: schema

COLUMNS:
id (PK)
employeeId (UNIQUE)
Name
userName
isDeleted
cd
ud

---

# TABLE: assetmaster

TYPE: schema

COLUMNS:
id (PK)
assetId (UNIQUE)
assetType
assetName
isMapped
isEmpty
isDeleted
cd
cdBy
ud
udBy

---

# TABLE: pallet

TYPE: schema

COLUMNS:
id (PK)
palletId (UNIQUE)
palletStatus
isActive
isDeleted
isEmpty
cd
ud

---

# TABLE: tempassetmapping

TYPE: schema

COLUMNS:
id (PK)
assetId (UNIQUE)
documentNumber
cd
isDeleted
ud

---

# TABLE: resource

TYPE: schema

COLUMNS:
id (PK)
location
whLocation
floor
resourceId
resourceName (UNIQUE)
resourceCapacity
stream
product
sapName
isOccupied
cd
isActive

---

# TABLE: intermediatefilling

TYPE: schema

COLUMNS:
id (PK)
uId (UNIQUE)
documentType
documentNumber
materialCode
materialDescription
qty
uom
tareWeight
beforeGrossWeight
afterGrossWeight
grossWeight
actualWeight
balanceBatchQty
isTempAsset
assetId
palletId
source
destination
status
isPrinted
weightSaved
isFilled
isDeleted
releasedDate
startTime
endTime
cd
ud

---

# TABLE: intermediatefillinggrn

TYPE: schema

COLUMNS:
id (PK)
plant
grnNumber
grnLineNumber
processOrder
materialCode
movType
storageLoc
qty
batch
uom
tintingStrength
stockType
cd

---

# TABLE: productionfilling

TYPE: schema

COLUMNS:
id (PK)
uId (UNIQUE)
documentType
documentNumber
materialCode
materialDescription
pickupListCode
grossWeight
tareWeight
actualWeight
balanceBatchQty
afterGrossWeight
beforeGrossWeight
assetId
status
cd
isDeleted
ud

---

# TABLE: stainersmanualweightlogs

TYPE: schema

COLUMNS:
id (PK)
uId
weight
userId
scannedOfficer
cd

---

# TABLE: gatewaylogs

TYPE: schema

COLUMNS:
id (PK)
topic
GrossWeight
NetWeight
TareWeight
cd

---

# TABLE: printer

TYPE: schema

COLUMNS:
id (PK)
printerId
name
location
ip (UNIQUE)
port
isDeleted
cd
ud
isActive

---

# TABLE: ss_itemcategory

TYPE: schema

COLUMNS:
categoryId (PK)
categoryCode (UNIQUE)
categoryName
isDeleted
cd
ud
cdBy
udBy

---

# TABLE: ss_relationalloctype

TYPE: schema

COLUMNS:
rltId (PK)
rltName
rltLevel (UNIQUE)
isActive
isDeleted
cd
ud
cdBy
udBy

---

# TABLE: ss_itemlocacnmap

TYPE: schema

COLUMNS:
itemLocAcnMapId (PK)
categoryId
itemId
warehouseId
locationId
acnId
zoneId
sectionId
rackId
isDeleted
cd
ud
cdBy
udBy
isActive

---

# TABLE: rejmaterialdetails

TYPE: schema

COLUMNS:
id (PK)
sku
materialCode
grnNumber
batchNumber
userId
qty
uom
palletId
cd

---

# TABLE: revalidation

TYPE: schema

COLUMNS:
id (PK)
sku
materialCode
grnNumber
grnLineNumber
batchNumber
userId
qty
uom
noOfDays
url
shelfLife
palletId
cd

---

# TABLE: updateqistatuslog

TYPE: schema

COLUMNS:
id (PK)
grnNumber
grnLineNumber
materialCode
previousStatus
userId
cd
updatedStatus

---

# TABLE: reqtypes

TYPE: schema

COLUMNS:
reqTypeId (PK)
reqTitle
reqDescription
attachment
isDeleted
cd
cdBy
ud
udBy

---

# TABLE: log

TYPE: schema

COLUMNS:
id (PK)
email
role
endPoint
event
method
createdAt

---

# CORE RELATIONSHIPS

TYPE: relationship

item.materialCode → store.materialCode
item.id → ss_itemcategorymap.itemId
item.id → ss_documenttr.itemId
item.id → sapstockstatus.itemId
item.id → ss_picklistview.itemId

store.id → ss_sulocation.skuId
store.palletId → assetmaster.assetId
store.palletId → pallet.palletId

pickuplist.pickupListCode → pickuplistmapping.pickupListCode
pickuplist.documentNumber → pivheaders.poNumber

ss_picklist.picklistId → ss_picklistview.picklistId
ss_picklist.picklistId → ss_supersedefefomapping.picklistId
ss_picklist.pivHeaderId → pivheaders.id
ss_picklist.pivPhaseId → pivphases.id
ss_picklist.mvtId → ss_mvt.mvtId

movementheaders.documentNumber → movementlineitems.documentNumber
movementlineitems.documentNumber → movementpickuplist.documentNumber
movementpickuplist.pickupListCode → movementsuidmapping.pickupListCode

pivheaders.poNumber → pivallocation.documentNumber
pivheaders.poNumber → pivphases.poNumber
pivheaders.poNumber → pivmaterialissueslip.poNumber
pivheaders.poNumber → phasespecification.poNumber

palletbinmapping.binPalletId → assetmaster.id
palletbinmapping.binAId → assetmaster.id

ss_whlocmap.warehouseId → ss_warehouse.warehouseId
ss_whlocmap.locationId → ss_location.locationId
ss_location.rltId → ss_relationalloctype.rltId
action.subModuleId → submodules.subModuleId

---

# JOIN PATHS (CRITICAL)

TYPE: guidance

ITEM → STORE INVENTORY:
item → store (ON item.materialCode = store.materialCode)

STORE → SU LOCATION:
store → ss_sulocation (ON store.id = ss_sulocation.skuId)

PICKUP LIST → ALLOCATED SKUS:
pickuplist → pickuplistmapping (ON pickuplist.pickupListCode = pickuplistmapping.pickupListCode)

SS PICKLIST → VIEW DETAILS:
ss_picklist → ss_picklistview (ON ss_picklist.picklistId = ss_picklistview.picklistId)

PIV ORDER → PRODUCTION ALLOCATION:
pivheaders → pivallocation (ON pivheaders.poNumber = pivallocation.documentNumber)

PIV ORDER → PRODUCTION PHASES:
pivheaders → pivphases (ON pivheaders.poNumber = pivphases.poNumber)

MOVEMENT HEADER → LINE ITEMS → PICKLIST:
movementheaders → movementlineitems → movementpickuplist

WAREHOUSE MAPPING:
warehouse → location (ON warehouse.id = location.warehouseId)

SS WAREHOUSE MAPPING:
ss_warehouse → ss_whlocmap → ss_location

---

# INTENT MAPPING

TYPE: logic

"item stock in store"
→ item + store

"open pickup lists"
→ pickuplist WHERE status IN (0, 1, 2)
→ ss_picklist WHERE status IN (0, 1, 2, 3, 4)

"completed picklists"
→ ss_picklist WHERE status = 5

"po batch details"
→ pivheaders

"piv order allocation"
→ pivheaders + pivallocation

"piv production phases"
→ pivheaders + pivphases

"material movement by document"
→ movementheaders + movementlineitems

"tank material allocation"
→ tankmaterialmapping

"filling weight logs"
→ productionfilling / intermediatefilling / stainersmanualweightlogs

"quality inspection logs"
→ updateqistatuslog / qualityinspector

---

# QUERY PATTERNS

TYPE: query

TOTAL STOCK BY MATERIAL:

SELECT
i.materialCode,
i.materialDescription,
SUM(s.totalQty) AS totalStock,
i.uom
FROM item i
JOIN store s ON i.materialCode = s.materialCode
WHERE s.isRejected = 0
GROUP BY i.materialCode, i.materialDescription, i.uom;

OPEN PICKUP LISTS:

SELECT
p.pickupListCode,
p.documentNumber,
p.materialCode,
p.qty,
p.status,
u.name AS assignedUserName
FROM pickuplist p
LEFT JOIN user u ON p.assignedUser = u.userId
WHERE p.status IN (0, 1, 2)
ORDER BY p.cd DESC
LIMIT 50;

OPEN SS PICKLISTS:

SELECT
picklistCode,
documentNumber,
status,
cd
FROM ss_picklist
WHERE status IN (0, 1, 2, 3, 4)
AND isDeleted = 0
ORDER BY cd DESC
LIMIT 20;

COMPLETED PICKLISTS WITH COMPLETION DATE:

SELECT
picklistCode,
documentNumber,
status,
ud AS completionDate
FROM ss_picklist
WHERE status = 5
AND isDeleted = 0
ORDER BY ud DESC
LIMIT 20;

PIV PO ALLOCATION DETAILS:

SELECT
ph.poNumber,
ph.finalMaterialCode,
ph.batchNumber,
pa.materialCode,
pa.qty,
pa.actualWeight,
pa.status
FROM pivheaders ph
JOIN pivallocation pa ON ph.poNumber = pa.documentNumber
WHERE ph.poNumber = '{poNumber}'
AND pa.isDeleted = 0;

---

# SPECIAL RULES

TYPE: constraint

DISTINCT:

- Use only when explicitly asked

LATEST / RECENT:

- Always sort by `cd DESC` (unless filtering completed records where `ud DESC` applies for completion date)

MULTI-VALUE FILTERS:

- ALWAYS use `IN (...)` clause for multiple filter values
- Example: `WHERE materialCode IN ('MAT01', 'MAT02')`
