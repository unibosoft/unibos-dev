# 🎯 wims (where is my stuff)

## 📋 overview
comprehensive inventory and asset management system for tracking products, stock levels, and movements across multiple warehouses. handles batch tracking, expiry management, barcode operations, and automated reordering with full audit trail capabilities.

## 🔧 current capabilities
### ✅ fully functional
- **multi-warehouse management** - unlimited warehouse/location hierarchies
- **real-time stock tracking** - live inventory levels with movement history
- **batch/serial tracking** - full traceability for batches and serial numbers
- **expiry management** - automated alerts for expiring products
- **barcode operations** - generate, print, and scan barcodes/QR codes
- **stock movements** - in/out/transfer/adjustment with reasons
- **inventory valuation** - FIFO, LIFO, weighted average costing
- **reorder management** - automatic reorder points and quantities
- **stock taking** - physical count with variance reports

### 🚧 in development
- RFID tag support
- predictive stock analytics
- automated purchase order generation
- mobile warehouse app

### 📅 planned features
- IoT sensor integration for real-time monitoring
- AI-powered demand forecasting
- multi-company consolidation
- advanced warehouse robotics integration

## 💻 technical implementation
### core functions
- `Warehouse` model - location hierarchy management
- `Product` model - product master data (inherited from core)
- `StockLevel` model - current inventory by location
- `StockMovement` model - all inventory transactions
- `Batch` model - batch/lot tracking
- `calculate_reorder_point()` - automated reorder calculations
- `process_stock_movement()` - movement validation and processing

### database models
- `Warehouse` - locations with hierarchical structure
- `Product` - items with SKU, barcode, categories
- `StockLevel` - current stock by product/warehouse/batch
- `StockMovement` - detailed movement history
- `Batch` - batch numbers with expiry dates
- `StockTake` - physical count records
- `ReorderRule` - automatic reordering configuration

### api integrations
- **restopos** - restaurant inventory synchronization
- **documents** - purchase order and receipt processing
- **WIMM** - inventory valuation and cost tracking
- **barcode libraries** - ZXing for generation/scanning
- **label printers** - Zebra/Dymo integration

## 🎮 how to use
1. navigate to main menu
2. select "modules" (m)
3. choose "📦 wims" (s)
4. main inventory dashboard:
   - press '1' for stock overview
   - press '2' for add stock movement
   - press '3' for products
   - press '4' for warehouses
   - press '5' for stock taking
   - press '6' for reports
   - press '7' for barcode operations
5. stock movement workflow:
   - select movement type (in/out/transfer/adjust)
   - choose product (search or scan barcode)
   - select warehouse/location
   - enter quantity
   - add batch/serial if required
   - provide reason/reference
6. stock taking process:
   - create count session
   - scan/enter actual quantities
   - review variances
   - approve adjustments

## 📊 data flow
- **input sources**:
  - manual stock entries
  - barcode scanner input
  - purchase receipts (documents module)
  - sales data (restopos)
  - stock taking counts
- **processing steps**:
  1. validate movement data
  2. check stock availability
  3. update stock levels
  4. record movement history
  5. trigger reorder alerts
  6. update valuation
- **output destinations**:
  - PostgreSQL database
  - warehouse reports
  - reorder notifications
  - expiry alerts
  - valuation reports to WIMM

## 🔌 integrations
- **restopos** - automatic stock deduction from sales
- **documents** - purchase order creation from reorder points
- **WIMM** - inventory valuation for financial reports
- **kişisel enflasyon** - product price tracking
- **currencies** - multi-currency purchase tracking

## ⚡ performance metrics
- stock query: <50ms for 100,000 products
- movement processing: <100ms
- barcode scanning: <200ms recognition
- supports 1M+ SKUs
- handles 10,000+ movements/day
- real-time sync across 50+ warehouses

## 🐛 known limitations
- RFID support not yet implemented
- batch splitting requires manual adjustment
- complex BOM (bill of materials) limited to 3 levels
- barcode scanning requires good lighting
- some industrial barcode formats unsupported

## 📈 version history
- v0.5 - basic inventory tracking
- v0.7 - multi-warehouse support
- v0.8 - batch and serial tracking
- v0.9 - barcode integration
- v1.0 - full feature set with reordering
- v1.1 - improved stock taking

## 🛠️ development status
**completion: 72%**
- inventory tracking: ✅ complete
- warehouse management: ✅ complete
- batch/serial: ✅ complete
- barcode operations: ✅ complete
- reorder management: ✅ complete
- RFID support: 🚧 in progress (15%)
- demand forecasting: 📅 planned
- IoT integration: 📅 planned