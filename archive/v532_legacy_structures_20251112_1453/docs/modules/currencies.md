# 🎯 currencies

## 📋 overview
comprehensive real-time exchange rate tracking system for fiat currencies, cryptocurrencies, and commodities. manages portfolio tracking, price alerts, and historical data analysis with multi-source API integration for accurate market data.

## 🔧 current capabilities
### ✅ fully functional
- **real-time exchange rates** - tracks USD, EUR, GBP, CHF, JPY, CAD, AUD, SEK, NOK, DKK against TRY
- **cryptocurrency tracking** - monitors BTC, ETH, AVAX, SOL, ADA, DOT, MATIC, LINK prices
- **portfolio management** - tracks holdings with real-time P&L calculations
- **price alerts** - configurable alerts for rate thresholds (above/below/percentage change)
- **data caching** - offline viewing with automatic cache management
- **websocket updates** - real-time price updates via WebSocket connections
- **multi-source data** - aggregates from TCMB, Binance, CoinGecko, BTCTurk

### 🚧 in development
- advanced technical indicators (RSI, MACD, moving averages)
- automated trading signals
- portfolio rebalancing recommendations

### 📅 planned features
- DeFi protocol integration
- NFT portfolio tracking
- tax reporting for crypto transactions
- multi-wallet synchronization

## 💻 technical implementation
### core functions
- `CurrenciesModule` - main module class in currencies_enhanced.py
- `ExchangeRate` model - stores rate history with bid/ask spreads
- `CurrencyAlert` model - manages user price alerts
- `CurrencyPortfolio` model - tracks user holdings and transactions
- `fetch_real_crypto` - retrieves live crypto prices
- `update_rates` - updates all exchange rates from sources

### database models
- `Currency` - currency definitions (code, name, symbol, type)
- `ExchangeRate` - historical rates with timestamps
- `CurrencyAlert` - user alert configurations
- `PortfolioHolding` - user asset holdings
- `PortfolioTransaction` - buy/sell transaction history

### api integrations
- **TCMB API** - Turkish Central Bank official rates (XML format)
- **Binance API** - cryptocurrency spot prices and market data
- **CoinGecko API** - comprehensive crypto market data
- **BTCTurk API** - Turkish crypto exchange rates
- **fallback mode** - demo data when APIs unavailable

## 🎮 how to use
1. navigate to main menu
2. select "modules" (m)
3. choose "💰 currencies" (c)
4. view exchange rates dashboard:
   - press 'r' to refresh rates
   - press 'p' to manage portfolio
   - press 'a' to set alerts
   - press 'h' for historical charts
   - press 'arrow keys' to navigate
   - press 'enter' to view details
5. portfolio management:
   - add holdings with quantity and purchase price
   - view real-time P&L calculations
   - track performance across time periods

## 📊 data flow
- **input sources**:
  - TCMB XML feed (every 15 minutes)
  - Binance WebSocket (real-time)
  - CoinGecko REST API (every 30 seconds)
  - BTCTurk REST API (every minute)
- **processing steps**:
  1. fetch data from multiple sources
  2. normalize currency pairs
  3. calculate weighted averages
  4. store in database with timestamps
  5. trigger alerts if thresholds met
  6. update WebSocket clients
- **output destinations**:
  - PostgreSQL database (primary storage)
  - Redis cache (fast access)
  - WebSocket to frontend
  - email/push notifications

## 🔌 integrations
- **WIMM module** - exports transaction data for financial tracking
- **documents module** - links receipts to currency conversions
- **personal inflation** - uses exchange rates for international comparisons
- **restopos** - multi-currency payment support

## ⚡ performance metrics
- API response time: <100ms average
- WebSocket latency: <50ms
- database query time: <10ms for cached data
- supports 1000+ concurrent WebSocket connections
- processes 10,000+ rate updates per minute

## 🐛 known limitations
- API rate limits: CoinGecko (50 calls/minute free tier)
- historical data limited to 1 year in free storage
- some exotic currency pairs require premium APIs
- WebSocket reconnection issues on unstable networks

## 📈 version history
- v1.0 - initial release with basic exchange rates
- v2.0 - added cryptocurrency support
- v2.5 - portfolio management features
- v3.0 - WebSocket real-time updates, alert system
- v3.1 - multi-source aggregation, improved caching

## 🛠️ development status
**completion: 85%**
- core functionality: ✅ complete
- real-time updates: ✅ complete
- portfolio management: ✅ complete
- alert system: ✅ complete
- technical indicators: 🚧 in progress (60%)
- automated trading: 📅 planned
- DeFi integration: 📅 planned