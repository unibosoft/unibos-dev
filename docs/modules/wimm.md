# 🎯 wimm (where is my money)

## 📋 overview
comprehensive financial management system for tracking income, expenses, invoices, and cash flow. supports multi-currency transactions, credit card management, subscription tracking, and detailed financial reporting with double-entry bookkeeping principles.

## 🔧 current capabilities
### ✅ fully functional
- **multi-currency accounts** - manage accounts in TRY, USD, EUR with real-time conversion
- **transaction tracking** - income, expense, and transfer recording with categories
- **invoice management** - create, track, and manage sales/purchase invoices
- **credit card tracking** - link transactions to specific cards with statements
- **subscription management** - track recurring payments and renewals
- **budget monitoring** - set and track budgets by category with alerts
- **financial reports** - P&L, cash flow, balance sheet generation
- **expense categorization** - hierarchical categories with custom tags
- **document linking** - attach receipts and documents to transactions

### 🚧 in development
- bank account synchronization via API
- automated transaction categorization using ML
- tax calculation and reporting
- financial forecasting models

### 📅 planned features
- cryptocurrency wallet integration
- investment portfolio tracking
- automated bill payment
- financial goal planning

## 💻 technical implementation
### core functions
- `Transaction` model - financial transaction records
- `Invoice` model - invoice generation and tracking
- `TransactionCategory` model - hierarchical categorization
- `Budget` model - budget planning and monitoring
- `CreditCard` model - card management and statements
- `Subscription` model - recurring payment tracking
- `save()` override - automatic account balance updates

### database models
- `Transaction` - income/expense/transfer records
- `Invoice` - sales and purchase invoices
- `InvoiceItem` - line items in invoices
- `TransactionCategory` - expense/income categories
- `Account` - bank/cash/credit accounts (from core)
- `Budget` - budget allocations and tracking
- `RecurringTransaction` - templates for repeated transactions

### api integrations
- **currencies module** - real-time exchange rates
- **documents module** - receipt attachment and OCR
- **restopos module** - restaurant financial integration
- **PDF generation** - invoice and report exports
- **Excel export** - data export functionality

## 🎮 how to use
1. navigate to main menu
2. select "modules" (m)
3. choose "💸 wimm" (w)
4. main dashboard options:
   - press '1' for accounts overview
   - press '2' for add transaction
   - press '3' for invoices
   - press '4' for reports
   - press '5' for budgets
   - press '6' for credit cards
   - press '7' for subscriptions
5. transaction workflow:
   - select transaction type (income/expense/transfer)
   - choose account(s)
   - enter amount and currency
   - select category
   - add description and tags
   - attach document if available
6. invoice creation:
   - choose invoice type (sales/purchase)
   - add customer/vendor details
   - add line items
   - set payment terms
   - generate PDF

## 📊 data flow
- **input sources**:
  - manual transaction entry
  - document OCR (via documents module)
  - restopos sales data
  - CSV/Excel imports
  - API integrations (planned)
- **processing steps**:
  1. validate transaction data
  2. apply currency conversion if needed
  3. update account balances
  4. categorize and tag
  5. check budget limits
  6. trigger alerts if needed
- **output destinations**:
  - PostgreSQL database
  - PDF reports
  - Excel exports
  - dashboard analytics
  - email notifications

## 🔌 integrations
- **documents** - automatic transaction creation from receipts
- **currencies** - real-time exchange rate conversion
- **restopos** - restaurant revenue and expense tracking
- **kişisel enflasyon** - expense data for inflation tracking
- **WIMS** - inventory purchase transactions

## ⚡ performance metrics
- transaction processing: <50ms
- invoice generation: <2 seconds
- report generation: <5 seconds for 10,000 transactions
- supports 1M+ transactions
- real-time balance updates
- concurrent user support: 100+

## 🐛 known limitations
- bank API integration not yet complete
- tax calculations limited to Turkish tax system
- report customization requires technical knowledge
- bulk import limited to 10,000 records at once
- some complex financial instruments not supported

## 📈 version history
- v0.5 - basic transaction tracking
- v0.7 - multi-currency support added
- v0.8 - invoice system implemented
- v0.9 - budget and reporting features
- v1.0 - credit cards and subscriptions
- v1.1 - document integration completed

## 🛠️ development status
**completion: 75%**
- transaction management: ✅ complete
- invoice system: ✅ complete
- reporting: ✅ complete
- budget tracking: ✅ complete
- credit cards: ✅ complete
- bank integration: 🚧 in progress (30%)
- tax reporting: 🚧 in progress (20%)
- crypto wallets: 📅 planned