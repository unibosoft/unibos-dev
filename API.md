# UNIBOS API Documentation

## 🔗 Quick Navigation
- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [FEATURES.md](FEATURES.md) - Feature documentation
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
  - [Authentication](#authentication-endpoints)
  - [Users](#user-endpoints)
  - [Currencies](#currencies-endpoints)
  - [Documents](#documents-endpoints)
  - [WIMM](#wimm-endpoints)
  - [WIMS](#wims-endpoints)
  - [Personal Inflation](#personal-inflation-endpoints)
  - [CCTV](#cctv-endpoints)
- [WebSocket APIs](#websocket-apis)
- [Examples](#examples)

## Overview

The UNIBOS API provides programmatic access to all system modules through a RESTful interface. The API uses JSON for request and response payloads and follows REST conventions.

### API Version
Current API version: `v1`  
Base path: `/api/v1/`

### Content Type
All requests must include:
```
Content-Type: application/json
Accept: application/json
```

## Authentication

UNIBOS uses JWT (JSON Web Token) based authentication with refresh tokens.

### Login
```http
POST /api/v1/auth/login/
```

Request:
```json
{
  "username": "user@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "roles": ["user"],
    "permissions": ["view_own_data", "edit_own_data"]
  }
}
```

### Using Tokens
Include the access token in the Authorization header:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Refresh Token
```http
POST /api/v1/auth/refresh/
```

Request:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Logout
```http
POST /api/v1/auth/logout/
```

Request:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Base URL

### Development
```
http://localhost:8000/api/v1/
```

### Production
```
https://api.unibos.com/api/v1/
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": ["Field specific error"]
    }
  }
}
```

### HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

Default rate limits:
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Premium: 10000 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1628764800
```

## Endpoints

### Authentication Endpoints

#### Register
```http
POST /api/v1/auth/register/
```

Request:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "secure_password",
  "password_confirm": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Password Reset Request
```http
POST /api/v1/auth/password-reset/
```

Request:
```json
{
  "email": "user@example.com"
}
```

#### Password Reset Confirm
```http
POST /api/v1/auth/password-reset-confirm/
```

Request:
```json
{
  "token": "reset_token",
  "password": "new_secure_password",
  "password_confirm": "new_secure_password"
}
```

#### Enable 2FA
```http
POST /api/v1/auth/2fa/enable/
```

Response:
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,..."
}
```

#### Verify 2FA
```http
POST /api/v1/auth/2fa/verify/
```

Request:
```json
{
  "code": "123456"
}
```

### User Endpoints

#### Get Current User
```http
GET /api/v1/users/me/
```

Response:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "avatar": "https://api.unibos.com/media/avatars/user1.jpg",
    "bio": "Software developer",
    "location": "Bodrum, Turkey",
    "language": "en",
    "timezone": "Europe/Istanbul"
  },
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-08-09T12:00:00Z"
}
```

#### Update Profile
```http
PATCH /api/v1/users/me/
```

Request:
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "profile": {
    "bio": "Updated bio",
    "language": "tr"
  }
}
```

#### List Users (Admin)
```http
GET /api/v1/users/
```

Query Parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `search`: Search query
- `role`: Filter by role
- `is_active`: Filter by active status

### Currencies Endpoints

#### Get Exchange Rates
```http
GET /api/v1/currencies/rates/
```

Response:
```json
{
  "base": "USD",
  "date": "2025-08-09",
  "rates": {
    "EUR": 0.85,
    "GBP": 0.73,
    "TRY": 27.5,
    "JPY": 110.5
  }
}
```

#### Get Cryptocurrency Prices
```http
GET /api/v1/currencies/crypto/
```

Response:
```json
{
  "prices": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "price_usd": 45000,
      "price_try": 1237500,
      "change_24h": 2.5,
      "market_cap": 850000000000
    },
    {
      "symbol": "ETH",
      "name": "Ethereum",
      "price_usd": 3000,
      "price_try": 82500,
      "change_24h": 1.8,
      "market_cap": 350000000000
    }
  ]
}
```

#### Portfolio Management
```http
GET /api/v1/currencies/portfolio/
```

```http
POST /api/v1/currencies/portfolio/
```

Request:
```json
{
  "name": "My Portfolio",
  "holdings": [
    {
      "currency": "BTC",
      "amount": 0.5,
      "purchase_price": 40000
    }
  ]
}
```

#### Price Alerts
```http
POST /api/v1/currencies/alerts/
```

Request:
```json
{
  "currency": "BTC",
  "condition": "above",
  "price": 50000,
  "notification_method": "email"
}
```

### Documents Endpoints

#### Upload Document
```http
POST /api/v1/documents/upload/
```

Request (multipart/form-data):
```
file: [binary]
type: receipt
perform_ocr: true
```

Response:
```json
{
  "id": 123,
  "filename": "receipt_2025_08_09.pdf",
  "type": "receipt",
  "size": 245632,
  "ocr_status": "processing",
  "created_at": "2025-08-09T12:00:00Z"
}
```

#### Get Document
```http
GET /api/v1/documents/{id}/
```

Response:
```json
{
  "id": 123,
  "filename": "receipt_2025_08_09.pdf",
  "type": "receipt",
  "size": 245632,
  "ocr_status": "completed",
  "ocr_text": "MARKET RECEIPT\nDate: 09/08/2025\n...",
  "ocr_confidence": 0.95,
  "parsed_data": {
    "store": "SuperMarket",
    "date": "2025-08-09",
    "total": 150.50,
    "items": [
      {
        "name": "Milk",
        "quantity": 2,
        "price": 25.00
      }
    ]
  },
  "thumbnail": "https://api.unibos.com/media/thumbnails/doc123.jpg",
  "created_at": "2025-08-09T12:00:00Z"
}
```

#### List Documents
```http
GET /api/v1/documents/
```

Query Parameters:
- `type`: Document type filter
- `ocr_status`: OCR status filter
- `date_from`: Start date
- `date_to`: End date
- `search`: Full-text search

#### Batch OCR Processing
```http
POST /api/v1/documents/batch-ocr/
```

Request:
```json
{
  "document_ids": [123, 124, 125]
}
```

### WIMM Endpoints

#### Accounts
```http
GET /api/v1/wimm/accounts/
POST /api/v1/wimm/accounts/
```

Account Structure:
```json
{
  "id": 1,
  "name": "Main Account",
  "currency": "USD",
  "balance": 5000.00,
  "type": "checking",
  "is_active": true
}
```

#### Transactions
```http
GET /api/v1/wimm/transactions/
POST /api/v1/wimm/transactions/
```

Transaction Structure:
```json
{
  "id": 1,
  "account_id": 1,
  "type": "expense",
  "amount": 50.00,
  "category": "groceries",
  "description": "Weekly shopping",
  "date": "2025-08-09",
  "tags": ["food", "essential"]
}
```

#### Invoices
```http
GET /api/v1/wimm/invoices/
POST /api/v1/wimm/invoices/
```

Invoice Structure:
```json
{
  "id": 1,
  "invoice_number": "INV-2025-001",
  "client": "Client Name",
  "amount": 1000.00,
  "currency": "USD",
  "status": "pending",
  "due_date": "2025-09-09",
  "items": [
    {
      "description": "Service",
      "quantity": 1,
      "price": 1000.00
    }
  ]
}
```

#### Financial Reports
```http
GET /api/v1/wimm/reports/summary/
GET /api/v1/wimm/reports/cashflow/
GET /api/v1/wimm/reports/profit-loss/
```

### WIMS Endpoints

#### Warehouses
```http
GET /api/v1/wims/warehouses/
POST /api/v1/wims/warehouses/
```

#### Products
```http
GET /api/v1/wims/products/
POST /api/v1/wims/products/
```

Product Structure:
```json
{
  "id": 1,
  "sku": "PROD-001",
  "name": "Product Name",
  "category": "electronics",
  "current_stock": 100,
  "minimum_stock": 10,
  "unit": "piece",
  "barcode": "1234567890123"
}
```

#### Stock Movements
```http
GET /api/v1/wims/movements/
POST /api/v1/wims/movements/
```

Movement Structure:
```json
{
  "id": 1,
  "product_id": 1,
  "warehouse_id": 1,
  "type": "inbound",
  "quantity": 50,
  "reference": "PO-2025-001",
  "date": "2025-08-09"
}
```

#### Stock Reports
```http
GET /api/v1/wims/reports/stock-levels/
GET /api/v1/wims/reports/expiring-products/
GET /api/v1/wims/reports/low-stock/
```

### Personal Inflation Endpoints

#### Products
```http
GET /api/v1/inflation/products/
POST /api/v1/inflation/products/
```

Product Structure:
```json
{
  "id": 1,
  "name": "Milk 1L",
  "category": "dairy",
  "unit": "liter",
  "barcode": "8690123456789"
}
```

#### Price Records
```http
GET /api/v1/inflation/prices/
POST /api/v1/inflation/prices/
```

Price Record:
```json
{
  "id": 1,
  "product_id": 1,
  "store_id": 1,
  "price": 25.50,
  "date": "2025-08-09"
}
```

#### Stores
```http
GET /api/v1/inflation/stores/
POST /api/v1/inflation/stores/
```

#### Personal Baskets
```http
GET /api/v1/inflation/baskets/
POST /api/v1/inflation/baskets/
```

Basket Structure:
```json
{
  "id": 1,
  "name": "Monthly Shopping",
  "items": [
    {
      "product_id": 1,
      "quantity": 4
    }
  ]
}
```

#### Inflation Calculation
```http
GET /api/v1/inflation/calculate/
```

Query Parameters:
- `basket_id`: Basket to calculate
- `date_from`: Start date
- `date_to`: End date

Response:
```json
{
  "personal_inflation": 12.5,
  "official_inflation": 8.2,
  "difference": 4.3,
  "categories": {
    "food": 15.2,
    "transportation": 8.1,
    "utilities": 10.5
  }
}
```

### CCTV Endpoints

#### Cameras
```http
GET /api/v1/cctv/cameras/
POST /api/v1/cctv/cameras/
```

Camera Structure:
```json
{
  "id": 1,
  "name": "Front Door",
  "model": "TP-Link Tapo C200",
  "ip_address": "192.168.1.100",
  "rtsp_url": "rtsp://192.168.1.100:554/stream1",
  "status": "online",
  "ptz_capable": true
}
```

#### Live Stream
```http
GET /api/v1/cctv/cameras/{id}/stream/
```

#### PTZ Control
```http
POST /api/v1/cctv/cameras/{id}/ptz/
```

Request:
```json
{
  "action": "move",
  "direction": "left",
  "speed": 5
}
```

#### Recordings
```http
GET /api/v1/cctv/recordings/
GET /api/v1/cctv/recordings/{id}/download/
```

#### Alerts
```http
GET /api/v1/cctv/alerts/
POST /api/v1/cctv/alerts/acknowledge/{id}/
```

## WebSocket APIs

### Connection
```javascript
const ws = new WebSocket('wss://api.unibos.com/ws/');
ws.send(JSON.stringify({
  'type': 'auth',
  'token': 'your_jwt_token'
}));
```

### Currency Updates
```javascript
// Subscribe to currency updates
ws.send(JSON.stringify({
  'type': 'subscribe',
  'channel': 'currencies',
  'symbols': ['USD', 'EUR', 'BTC']
}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // {
  //   'type': 'currency_update',
  //   'symbol': 'BTC',
  //   'price': 45000,
  //   'change': 2.5
  // }
};
```

### CCTV Events
```javascript
// Subscribe to camera events
ws.send(JSON.stringify({
  'type': 'subscribe',
  'channel': 'cctv',
  'camera_ids': [1, 2, 3]
}));

// Receive alerts
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // {
  //   'type': 'motion_detected',
  //   'camera_id': 1,
  //   'timestamp': '2025-08-09T12:00:00Z'
  // }
};
```

## Examples

### Python Example
```python
import requests

# Login
response = requests.post('https://api.unibos.com/api/v1/auth/login/', json={
    'username': 'user@example.com',
    'password': 'password'
})
tokens = response.json()

# Use API with token
headers = {
    'Authorization': f'Bearer {tokens["access"]}'
}

# Get exchange rates
rates = requests.get(
    'https://api.unibos.com/api/v1/currencies/rates/',
    headers=headers
).json()

print(f"1 USD = {rates['rates']['TRY']} TRY")
```

### JavaScript Example
```javascript
// Login
const loginResponse = await fetch('https://api.unibos.com/api/v1/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'password'
  })
});

const tokens = await loginResponse.json();

// Use API with token
const ratesResponse = await fetch('https://api.unibos.com/api/v1/currencies/rates/', {
  headers: {
    'Authorization': `Bearer ${tokens.access}`
  }
});

const rates = await ratesResponse.json();
console.log(`1 USD = ${rates.rates.TRY} TRY`);
```

### cURL Example
```bash
# Login
curl -X POST https://api.unibos.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"password"}'

# Get rates with token
curl https://api.unibos.com/api/v1/currencies/rates/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## API Clients

### Official SDKs
- Python: `pip install unibos-sdk`
- JavaScript/Node.js: `npm install unibos-sdk`
- Go: `go get github.com/unibos/unibos-go`

### OpenAPI/Swagger
- Specification: `https://api.unibos.com/api/v1/openapi.json`
- Swagger UI: `https://api.unibos.com/api/v1/docs/`
- ReDoc: `https://api.unibos.com/api/v1/redoc/`

## Testing

### Sandbox Environment
- Base URL: `https://sandbox.api.unibos.com/api/v1/`
- Test credentials available upon request
- Data resets daily

### Postman Collection
Download our Postman collection for easy API testing:
`https://api.unibos.com/postman/unibos-api.json`

## Support

### API Status
Check API status and uptime: `https://status.unibos.com`

### Rate Limit Issues
Contact support for increased limits: `api-support@unibos.com`

### Bug Reports
Report API issues on GitHub: `https://github.com/unibos/unibos/issues`

---

## Related Resources
- [Postman Collection](https://api.unibos.com/postman/unibos-api.json)
- [OpenAPI Specification](https://api.unibos.com/api/v1/openapi.json)
- [API Status Page](https://status.unibos.com)
- [GitHub Issues](https://github.com/unibos/unibos/issues)

---

*Last Updated: 2025-08-12*  
*API Documentation Version: 2.0*  
*API Version: v1*
*Compatible with UNIBOS v446+*