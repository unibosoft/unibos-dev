# 🎯 kişisel enflasyon

## 📋 overview
personal inflation tracking system that calculates your real cost of living by monitoring actual purchase prices. tracks product prices across stores, creates personalized consumption baskets, and compares your inflation rate with official statistics.

## 🔧 current capabilities
### ✅ fully functional
- **product price tracking** - monitors prices across multiple stores with barcode scanning
- **consumption basket** - personalized basket based on actual purchases
- **inflation calculation** - weighted average based on purchase frequency
- **price alerts** - notifications when prices change >10%
- **category analysis** - inflation breakdown by product categories
- **receipt integration** - automatic price updates from OCR receipts
- **store comparison** - price comparison across different chains
- **historical trends** - price history graphs for each product
- **budget impact** - calculates monthly/yearly cost increases

### 🚧 in development
- predictive price modeling
- substitute product suggestions
- bulk price data import
- social price sharing

### 📅 planned features
- machine learning price predictions
- crowdsourced price database
- shopping list optimization
- inflation-adjusted budgeting

## 💻 technical implementation
### core functions
- `PersonalInflationCalculator` class - main calculation engine
- `Product` model - product definitions with barcodes
- `PriceEntry` model - price records with timestamps
- `InflationStats` dataclass - statistical calculations
- `calculate_inflation()` - weighted inflation computation
- `import_from_receipt()` - OCR data processing
- `generate_basket()` - personalized basket creation

### database models
- `Product` - items with name, category, barcode, unit
- `PriceEntry` - price records with store, date, quantity
- `Store` - store chains and locations
- `ConsumptionBasket` - user's regular purchases
- `Category` - product categories for analysis
- `PriceAlert` - configured price alerts
- `InflationReport` - calculated inflation metrics

### api integrations
- **documents module** - receipt OCR data import
- **SQLite/PostgreSQL** - local data storage
- **store APIs** - Migros, CarrefourSA price data (when available)
- **TCMB API** - official inflation comparison
- **barcode database** - product identification

## 🎮 how to use
1. navigate to main menu
2. select "modules" (m)
3. choose "📈 kişisel enflasyon" (k)
4. main inflation tracker:
   - press '1' for add product
   - press '2' for record price
   - press '3' for view inflation
   - press '4' for price alerts
   - press '5' for category analysis
   - press '6' for import receipt
   - press '7' for reports
5. product management:
   - scan barcode or search by name
   - set category and unit
   - mark as regular purchase
6. price recording:
   - select product
   - enter price and quantity
   - choose store
   - auto-calculates unit price
7. inflation view:
   - personal rate vs official
   - 30/90/365 day periods
   - category breakdown
   - biggest price increases

## 📊 data flow
- **input sources**:
  - manual price entry
  - OCR receipts (documents module)
  - barcode scanner
  - store API imports
  - CSV bulk imports
- **processing steps**:
  1. validate price data
  2. match products by barcode/name
  3. calculate unit prices
  4. update price history
  5. recalculate inflation
  6. trigger price alerts
  7. generate reports
- **output destinations**:
  - local database
  - inflation dashboard
  - price alert notifications
  - export to Excel/CSV
  - monthly reports

## 🔌 integrations
- **documents** - automatic price import from receipts
- **WIMM** - expense tracking synchronization
- **currencies** - foreign product price conversion
- **restopos** - restaurant price tracking

## ⚡ performance metrics
- price lookup: <50ms
- inflation calculation: <200ms for 1000 products
- receipt import: 5-10 seconds per receipt
- supports 100,000+ price records
- handles 500+ products per basket
- real-time alert processing

## 🐛 known limitations
- barcode database incomplete for some local products
- store API access limited (manual entry required)
- historical data limited to user's entry period
- some product matching requires manual verification
- bulk imports limited to CSV format

## 📈 version history
- v0.5 - basic price tracking
- v0.7 - inflation calculation added
- v0.8 - receipt integration
- v0.9 - category analysis
- v1.0 - full feature set with alerts
- v1.1 - improved product matching

## 🛠️ development status
**completion: 82%**
- price tracking: ✅ complete
- inflation calculation: ✅ complete
- receipt integration: ✅ complete
- alerts: ✅ complete
- category analysis: ✅ complete
- price prediction: 🚧 in progress (25%)
- social sharing: 📅 planned
- ML optimization: 📅 planned