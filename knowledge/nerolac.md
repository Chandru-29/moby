# DOMAIN: 0. Global & Shared System Entities

TYPE: context
INTENT: Manage universal cross-cutting entities including user identity resolution, authentication credentials, system-wide audit trails, and real-time weighbridge hardware telemetry.
TARGET TABLES: user, log, gatewaylogs
DESCRIPTION: Core administrative and telemetry layer providing centralized access to user profiles, endpoint event logs, and automated weighbridge gateway metrics required for cross-domain operational tracking.

### TABLE: user

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
USAGE: Central user credentials used across picklists, inventory updates, and material movements.

### TABLE: log

COLUMNS:
id (PK)
email
role
endPoint
event
method
createdAt
USAGE: System audit trails and endpoint tracking.

### TABLE: gatewaylogs

COLUMNS:
id (PK)
topic
GrossWeight
NetWeight
TareWeight
cd
USAGE: Hardware weighbridge gateway logs.

---

# DOMAIN: 1. Picklist & Warehouse Picking Management

TYPE: schema_domain
INTENT: Manage warehouse order picking workflows, picklist lifecycles, line-item quantities, supervisors, and FEFO override exception rules.
TARGET TABLES: SS_PICKLIST, SS_PICKLISTVIEW, pickuplist, pickuplistmapping, SS_SUPERSEDEFEFOMAPPING
DESCRIPTION: Covers all operational tables, statuses, and query patterns associated with warehouse picking and fulfillment execution.

### TABLE: SS_PICKLIST

COLUMNS:
picklistId (PK, UNIQUE)
picklistCode (UNIQUE)
documentTypeId → SS_DOCUMENT.documentId
documentNumber
mvtId → SS_MVT.mvtId
status
picklistTypeStatus
assignedUser → user.userId
transactionId → SS_TRANSACTIONM.transactionId
pivHeaderId → pivHeaders.id
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

- If status = 5 (Completed) → completion date = ud (Updated Date)
- "completion date" ALWAYS maps to SS_PICKLIST.ud

DOCUMENT TYPE DEFINITIONS:
1 → GRN
21 → Work Order
16 → Transfer Order

DEFAULT OUTPUT:
picklistCode, status

### TABLE: SS_PICKLISTVIEW

COLUMNS:
picklistViewId (PK)
picklistId → SS_PICKLIST.picklistId
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

### TABLE: pickuplist

COLUMNS:
id (PK)
pickupListCode (UNIQUE)
documentNumber
materialCode
qty
status
assignedUser → user.userId
cd
ud
USAGE: Master pickup list header records.

### TABLE: pickuplistmapping

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

### TABLE: SS_SUPERSEDEFEFOMAPPING

COLUMNS:
supersedaFefoMapId (PK)
picklistId → SS_PICKLIST.picklistId
reason
userId → user.userId
isDeleted
cd
ud
cdBy
udBy

## DOMAIN CORE RELATIONSHIPS & JOINS (Picklist):

- `SS_PICKLIST.picklistId → SS_PICKLISTVIEW.picklistId`
- `SS_PICKLIST.picklistId → SS_SUPERSEDEFEFOMAPPING.picklistId`
- `pickuplist.pickupListCode → pickuplistmapping.pickupListCode`
- `SS_PICKLIST.assignedUser → user.userId`

## QUERY PATTERNS (PICKLIST):

OPEN PICKUP LISTS:

```sql
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
```

OPEN SS PICKLISTS:

```sql
SELECT
  picklistCode,
  documentNumber,
  status,
  cd
FROM SS_PICKLIST
WHERE status IN (0, 1, 2, 3, 4)
  AND isDeleted = 0
ORDER BY cd DESC
LIMIT 20;
```

COMPLETED PICKLISTS WITH COMPLETION DATE:

```sql
SELECT
  picklistCode,
  documentNumber,
  status,
  ud AS completionDate
FROM SS_PICKLIST
WHERE status = 5
  AND isDeleted = 0
ORDER BY ud DESC
LIMIT 20;
```

---

# DOMAIN: 2. Inventory, Store & Stock Management

TYPE: schema_domain
INTENT: Track raw material master data, warehouse inventory ledger balances, SUID storage units, and physical storage bin structures.
TARGET TABLES: item, store, SS_SULOCATION, location, SS_LOCATION, warehouse, SS_WAREHOUSE, SS_WHLOCCMAP, SS_WHTYPEMAP, SS_ITEMCATEGORY, SS_RELATIONALALLLTYPE, SS_ITEMLOCACNMAP, pivallocation
DESCRIPTION: Comprehensive inventory and storage management rules to handle stock availability, bin mappings, and plant layouts.

### TABLE: item

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
USAGE: Item and raw material master reference data

### TABLE: store

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
userId → user.userId
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
USAGE: Primary warehouse storage inventory and inbound SKU ledger

### TABLE: SS_SULOCATION

COLUMNS:
suidId (PK)
suid (UNIQUE)
skuId → store.id
qty
packSize
locationId → SS_LOCATION.locationId
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
RULE: Unit storage tracking for picklist fulfillment and bin location mapping

### TABLE: location

COLUMNS:
id (PK)
locationName
warehouseId → warehouse.id
zoneId
isEmpty
isDeleted
cd
ud
USAGE: Legacy physical warehouse storage bin definitions.

### TABLE: SS_LOCATION

COLUMNS:
locationId (PK)
locationCode (UNIQUE)
locationName
parentId
parentCode
isLocation
rltId → SS_RELATIONALALLLTYPE.rltId
status
isEmpty
isDeleted
cd
ud
USAGE: Smart storage location hierarchy entity.

### TABLE: warehouse

COLUMNS:
id (PK)
warehouseCode (UNIQUE)
warehouseName
plant
isDeleted
cd
ud
USAGE: Physical warehouse facility definitions.

### TABLE: SS_WAREHOUSE

COLUMNS:
warehouseId (PK)
warehouseCode (UNIQUE)
warehouseName
plantCode
status
isDeleted
cd
ud
USAGE: Smart storage warehouse definitions.

### TABLE: ss_whlocmap

COLUMNS:
id (PK)
warehouseId → SS_WAREHOUSE.warehouseId
locationId → SS_LOCATION.locationId
isDeleted
cd
ud
USAGE: Mapping table linking warehouses to location hierarchies.

### TABLE: SS_WHTYPEMAP

COLUMNS:
id (PK)
warehouseId → SS_WAREHOUSE.warehouseId
typeId
isDeleted
cd
ud
USAGE: Warehouse type classification mapping table.

### TABLE: SS_ITEMCATEGORY

COLUMNS:
categoryId (PK)
categoryCode (UNIQUE)
categoryName
description
cd
USAGE: Master item category definitions.

### TABLE: SS_RELATIONALALLLTYPE

COLUMNS:
rltId (PK)
rltCode (UNIQUE)
rltName
description
cd
USAGE: Relation allocation type master definitions.

### TABLE: SS_ITEMLOCACNMAP

COLUMNS:
id (PK)
itemId → item.id
locationId → SS_LOCATION.locationId
isDeleted
cd
USAGE: Item to location association mapping table.

## DOMAIN CORE RELATIONSHIPS & JOINS (Inventory):

- `item.materialCode → store.materialCode`
- `store.id → SS_SULOCATION.skuId`
- `warehouse.id → location.warehouseId`
- `SS_WAREHOUSE.warehouseId → SS_WHLOCCMAP.warehouseId → SS_LOCATION.locationId`
- `SS_LOCATION.rltId → SS_RELATIONALALLLTYPE.rltId`
- `SS_ITEMLOCACNMAP.itemId → item.id`
- `SS_ITEMLOCACNMAP.locationId → SS_LOCATION.locationId`

## QUERY PATTERNS (INVENTORY):

TOTAL STOCK BY MATERIAL:

```sql
SELECT
  i.materialCode,
  i.materialDescription,
  SUM(s.totalQty) AS totalStock,
  i.uom
FROM item i
JOIN store s ON i.materialCode = s.materialCode
WHERE s.isRejected = 0
GROUP BY i.materialCode, i.materialDescription, i.uom;
```

---

# DOMAIN: 3. Production Orders & PIV Management

TYPE: schema_domain
INTENT: Handle shop-floor manufacturing process orders, batch schedules, production phase definitions, and material issuance slips.
TARGET TABLES: pivHeaders, pivphases, pivmaterialissueslip, pivallocation
DESCRIPTION: Covers process order scheduling and allocation details linked via production order numbers (poNumber).

### TABLE: pivHeaders

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
USAGE: Production order headers and PIV batch schedules

### TABLE: pivphases

COLUMNS:
id (PK)
poNumber → pivHeaders.poNumber
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
USAGE: Step-by-step production process phase details and material thresholds

### TABLE: pivmaterialissueslip

COLUMNS:
id (PK)
poNumber → pivHeaders.poNumber
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
USAGE: Material issue slips for shop-floor batch consumption

### TABLE: pivallocation

COLUMNS:
id (PK)
documentType
documentNumber → pivHeaders.poNumber
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
assignedUser → user.userId
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
USAGE: Batch material allocations mapped to pickup lists and weighbridges

## DOMAIN CORE RELATIONSHIPS & JOINS (Production):

- `pivHeaders.poNumber → pivallocation.documentNumber`
- `pivHeaders.poNumber → pivphases.poNumber`
- `pivHeaders.poNumber → pivmaterialissueslip.poNumber`
- `pickuplist.documentNumber → pivHeaders.poNumber`

## QUERY PATTERNS (PRODUCTION / PIV):

PIV PO ALLOCATION DETAILS:

```sql
SELECT
  ph.poNumber,
  ph.finalMaterialCode,
  ph.batchNumber,
  pa.materialCode,
  pa.qty,
  pa.actualWeight,
  pa.status
FROM pivHeaders ph
JOIN pivallocation pa ON ph.poNumber = pa.documentNumber
WHERE ph.poNumber = '{poNumber}'
  AND pa.isDeleted = 0;
```

---

# DOMAIN: 4. Material Movement & Transfers

TYPE: schema_domain
INTENT: Track inter-location material transfers, movement document headers, line items, movement pickup lists, and SUID mappings.
TARGET TABLES: movementheaders, movementlineitems, movementpickuplist, movementsuidmapping, movementtypes, ss_mvt
DESCRIPTION: Manages material movement lifecycles and document-based transfers across warehouse locations.

### TABLE: movementheaders

COLUMNS:
id (PK)
documentNumber (UNIQUE)
movementType
tCode
plant
vendorName
vendorCode
cd
udCode
USAGE: Header information for material movement and transfer documents.

### TABLE: movementlineitems

COLUMNS:
id (PK)
plant
materialCode
documentNumber → movementheaders.documentNumber
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
USAGE: Line items specifying transfer quantities and locations.

### TABLE: movementpickuplist

COLUMNS:
id (PK)
plant
pickupListCode (UNIQUE)
movementType
tCode
documentNumber → movementheaders.documentNumber
lineNumber
materialCode
qty
uom
source
destination
status
assignedUser → user.userId
cd
movementStartTime
movementEndTime
expiryDate
USAGE: Pickup lists generated specifically for material transfers.

### TABLE: movementsuidmapping

COLUMNS:
id (PK)
documentNumber → movementheaders.documentNumber
pickupListCode → movementpickuplist.pickupListCode
materialCode
suId → ss_sulocation.suid
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
USAGE: SUID-level tracking for picked and moved stock units.

### TABLE: movementtypes

COLUMNS:
id (PK)
movementTypeCode (UNIQUE)
movementTypeName
description
cd
USAGE: Reference table defining movement type classifications.

### TABLE: ss_mvt

COLUMNS:
mvtId (PK)
mvtCode (UNIQUE)
mvtName
description
status
isDeleted
cd
ud
USAGE: Standard movement type definitions and codes referenced by picklists.

## DOMAIN CORE RELATIONSHIPS & JOINS (Movement):

- `movementheaders.documentNumber → movementlineitems.documentNumber`
- `movementlineitems.documentNumber → movementpickuplist.documentNumber`
- `movementpickuplist.pickupListCode → movementsuidmapping.pickupListCode`

---

# DOMAIN: 5. Roles, Permissions & Assets

TYPE: schema_domain
INTENT: Manage user roles, access control modules, physical pallets, asset records, network printers, and quality inspector credentials.
TARGET TABLES: accesses, action, submodules, department, qualityinspector, assetmaster, pallet, tempassetmapping, resource, printer, rejmaterialdetails, revalidation, updateqistatuslog, reqtypes
DESCRIPTION: Handles administrative security permissions, plant assets, and quality inspection logging tables.

### TABLE: accesses

COLUMNS:
id (PK)
roleId
subModuleId
actionId
cd
USAGE: Role-based access permissions mapping.

### TABLE: action

COLUMNS:
actionId (PK)
actionName
subModuleId → submodules.subModuleId
cd
USAGE: System action definitions linked to submodules.

### TABLE: submodules

COLUMNS:
subModuleId (PK)
subModuleName
moduleId
cd
USAGE: System feature sub-modules.

### TABLE: department

COLUMNS:
id (PK)
departmentName
cd
USAGE: Plant organizational department list.

### TABLE: qualityinspector

COLUMNS:
id (PK)
employeeId (UNIQUE)
Name
userName (UNIQUE)
email
role
cd
USAGE: Authorized quality inspector credentials and profiles.

### TABLE: rejmaterialdetails

COLUMNS:
id (PK)
materialCode
batchNumber
rejectedQty
reason
inspectorId → qualityinspector.employeeId
cd
USAGE: Logs of materials rejected during quality inspection.

### TABLE: revalidation

COLUMNS:
id (PK)
skuId → store.id
materialCode
batchNumber
status
revalidatedDate
inspectorId
cd
USAGE: Material shelf-life and quality revalidation logs.

### TABLE: updateqistatuslog

COLUMNS:
id (PK)
skuId → store.id
oldStatus
newStatus
updatedBy
cd
USAGE: Audit trail for quality inspector status updates.

### TABLE: reqtypes

COLUMNS:
id (PK)
typeCode (UNIQUE)
typeName
description
cd
USAGE: Request type classification definitions.

### TABLE: assetmaster

COLUMNS:
assetId (PK)
assetCode (UNIQUE)
assetType
locationId
status
isDeleted
cd
ud
USAGE: Master catalog of plant physical assets and containers.

### TABLE: pallet

COLUMNS:
palletId (PK)
palletCode (UNIQUE)
capacity
status
isDeleted
cd
ud
USAGE: Physical storage pallet inventory.

### TABLE: tempassetmapping

COLUMNS:
id (PK)
tempAssetId
realAssetId
suid
cd
USAGE: Temporary asset to permanent asset mapping ledger.

### TABLE: resource

COLUMNS:
id (PK)
resourceCode (UNIQUE)
resourceName
plant
status
cd
USAGE: Machine, equipment, and work-center resources.

### TABLE: printer

COLUMNS:
id (PK)
printerName
ipAddress
plant
isDefault
cd
USAGE: Network barcode and document printer configurations.

## DOMAIN CORE RELATIONSHIPS & JOINS (Assets):

- `store.palletId → assetmaster.assetId`
- `store.palletId → pallet.palletId`
- `action.subModuleId → submodules.subModuleId`

---

# DOMAIN: 6. Filling & Weight Operations

TYPE: schema_domain
INTENT: Record intermediate filling processes, production filling quantities, batch balances, and manual stainer scale logs.
TARGET TABLES: intermediatefilling, intermediatefillinggrn, productionfilling, stainersmanualweightlogs, gatewaylogs
DESCRIPTION: Manages shop-floor filling operations and weight verification logs.

### TABLE: intermediatefilling

COLUMNS:
id (PK)
poNumber
materialCode
materialDescription
batchNumber
tareWeight
grossWeight
netWeight
filledQty
status
cd
USAGE: Intermediate chemical filling logs.

### TABLE: intermediatefillinggrn

COLUMNS:
id (PK)
grnNumber
poNumber
materialCode
batchNumber
totalQty
cd
USAGE: GRN records for intermediate filled stock.

### TABLE: productionfilling

COLUMNS:
id (PK)
pickupListCode
poNumber
materialCode
batchNumber
targetQty
actualWeight
balanceBatchQty
status
cd
USAGE: Final paint production filling weight records.

### TABLE: stainersmanualweightlogs

COLUMNS:
id (PK)
uId
weight
userId → user.userId
scannedOfficer
cd
USAGE: Manual stainer scale weighing logs.

### TABLE: gatewaylogs

COLUMNS:
id (PK)
topic
GrossWeight
NetWeight
TareWeight
cd
USAGE: Hardware weighbridge MQTT/Gateway weight events.

## DOMAIN CORE RELATIONSHIPS & JOINS (Filling & Weights):

- `intermediatefilling.materialCode → item.materialCode`
- `productionfilling.pickupListCode → pickuplist.pickupListCode`
- `stainersmanualweightlogs.userId → user.userId`

---

# DOMAIN: 7. Global Rules, Constraints & Semantic Mappings (always on)

TYPE: global_rule
INTENT: Define global constraints, business term mappings, and natural language intent patterns to ensure precise query generation across all operations.
TARGET TABLES: none
DESCRIPTION: Universal rulebook outlining software generation standards, soft-delete rules, and semantic column mappings.

## BUSINESS TERM MAPPING:

- "material" / "item" → item.materialCode
- "sku" / "store inventory" → store.sku
- "stock" / "available inventory" → store.totalQty / store.actualQty
- "suid" → SS_SULOCATION.suid
- "location" / "bin" → location.locationName / SS_LOCATION.locationId
- "warehouse" → warehouse.warehouseCode / SS_WAREHOUSE.warehouseCode
- "picklist" → pickuplist.pickupListCode / SS_PICKLIST.picklistCode
- "piv order" / "process order" → pivHeaders.poNumber / pivallocation.pickupListCode
- "pallet" → assetmaster.assetId / store.palletId / pallet.palletId
- "movement" → movementheaders / movementpickuplist / movementlineitems
- "grn" → store.grnNumber

## INTENT MAPPING & LOGIC:

- "item stock in store" → item + store
- "open pickup lists" → pickuplist WHERE status IN (0, 1, 2) OR SS_PICKLIST WHERE status IN (0, 1, 2, 3, 4)
- "completed picklists" → SS_PICKLIST WHERE status = 5
- "po batch details" → pivHeaders
- "piv order allocation" → pivHeaders + pivallocation
- "piv production phases" → pivHeaders + pivphases
- "material movement by document" → movementheaders + movementlineitems

## SPECIAL RULES & CONSTRAINTS:

- **formatting**: Present non-empty SQL execution results in a clean Markdown table with business-friendly Title Case column headers (e.g., convert `cd` to `Created Date`). Include a brief introductory summary sentence. If 0 rows are returned, provide a clear message (e.g., "No matching records found") instead of rendering an empty table.
- **Soft Delete Rule**: Always filter `isDeleted = 0` (or `isDeleted = '0'`) for tables containing the soft-delete flag.
- **SQL Dialect**: Target MySQL syntax (Use `LIMIT` instead of `TOP`).
- **Join Integrity**: Follow defined joins strictly. Do NOT assume missing relationships.
- **Keywords**: Always wrap table names in backticks (e.g., `user`, `store`, `location`, `action`, `resource`) to avoid MySQL syntax errors.
- **Sorting (Latest/Recent)**: Always sort by `cd DESC` (unless filtering completed records where `ud DESC` applies for completion date).
- **Multi-Value Filters**: ALWAYS use `IN (...)` clause for multiple filter values (e.g., `WHERE materialCode IN ('MAT01', 'MAT02')`).
- **User Resolution**: `pickuplist.assignedUser` → `user.userId` or `user.userName`; Return `user.name`, `user.userName`.
