# 🎯 restopos

## 📋 overview
professional restaurant point-of-sale system with comprehensive table management, real-time order tracking, kitchen display system, and multi-payment processing. designed for restaurants, cafes, and food service businesses with full integration to inventory and financial modules.

## 🔧 current capabilities
### ✅ fully functional
- **table management** - visual floor plan with drag-drop table arrangement
- **QR code ordering** - customer self-service via QR codes
- **order processing** - create, modify, split, merge orders
- **kitchen display system** - real-time order routing to stations
- **menu management** - categories, modifiers, combos, time-based availability
- **payment processing** - cash, card, split bills, tips
- **staff management** - roles, permissions, shift tracking
- **receipt printing** - thermal printer support with customization
- **reporting** - sales, inventory, staff performance

### 🚧 in development
- mobile waiter app
- online ordering integration
- loyalty program management
- table reservation system

### 📅 planned features
- delivery management
- franchise multi-location support
- AI-powered sales forecasting
- voice ordering system

## 💻 technical implementation
### core functions
- `Restaurant` model - restaurant configuration and settings
- `Table` model - table layouts and status
- `Order` model - order management with items
- `MenuItem` model - menu items with modifiers
- `Kitchen` model - kitchen stations and routing
- `process_order()` - order workflow management
- `calculate_bill()` - pricing and tax calculations

### database models
- `Restaurant` - branch info, settings, tax rates
- `MenuCategory` - menu organization
- `MenuItem` - dishes with pricing and options
- `Table` - physical tables with QR codes
- `Order` - active and historical orders
- `OrderItem` - individual items in orders
- `Kitchen` - kitchen stations
- `Staff` - employees with roles
- `Payment` - payment records

### api integrations
- **WIMM** - financial transaction recording
- **WIMS** - real-time inventory deduction
- **documents** - receipt archival and OCR
- **WebSocket** - real-time order updates
- **thermal printers** - ESC/POS protocol
- **payment gateways** - card processing

## 🎮 how to use
1. navigate to main menu
2. select "modules" (m)
3. choose "🍽️ restopos" (r)
4. main POS interface:
   - press '1' for table view
   - press '2' for new order
   - press '3' for kitchen display
   - press '4' for payments
   - press '5' for reports
   - press '6' for menu setup
   - press '7' for staff management
5. order workflow:
   - select or scan table QR
   - add menu items
   - apply modifiers (size, extras)
   - send to kitchen
   - monitor preparation status
   - process payment
   - print receipt
6. kitchen display:
   - view incoming orders
   - mark items as preparing/ready
   - communicate with waitstaff
   - track preparation times

## 📊 data flow
- **input sources**:
  - waiter POS terminals
  - customer QR code scanning
  - kitchen touch screens
  - payment terminals
  - online ordering (planned)
- **processing steps**:
  1. validate order items
  2. calculate pricing with tax
  3. route to kitchen stations
  4. update inventory levels
  5. track preparation status
  6. process payment
  7. record financial data
- **output destinations**:
  - kitchen displays
  - receipt printers
  - WIMM (financials)
  - WIMS (inventory)
  - customer notifications
  - management reports

## 🔌 integrations
- **WIMM** - automatic revenue and expense tracking
- **WIMS** - real-time ingredient inventory updates
- **documents** - digital receipt storage
- **currencies** - multi-currency payment support
- **kişisel enflasyon** - menu price optimization data

## ⚡ performance metrics
- order processing: <100ms
- kitchen display update: <500ms real-time
- supports 100+ concurrent tables
- handles 1000+ orders/day
- receipt printing: <2 seconds
- payment processing: <3 seconds

## 🐛 known limitations
- online ordering integration incomplete
- limited to single restaurant (no chain support yet)
- some payment gateways not integrated
- kitchen display requires stable network
- complex modifier combinations limited to 5 levels

## 📈 version history
- v0.5 - basic POS functionality
- v0.7 - table management and QR codes
- v0.8 - kitchen display system
- v0.9 - payment processing
- v1.0 - full integration with WIMM/WIMS
- v1.1 - enhanced reporting and analytics

## 🛠️ development status
**completion: 80%**
- POS core: ✅ complete
- table management: ✅ complete
- kitchen display: ✅ complete
- payment processing: ✅ complete
- reporting: ✅ complete
- mobile app: 🚧 in progress (40%)
- online ordering: 🚧 in progress (25%)
- delivery management: 📅 planned