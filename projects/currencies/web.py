"""
Currencies Web Interface
Flask-based web API and UI for currency tracking
"""

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
from datetime import datetime, timedelta
import threading
import time
from typing import Dict, List, Optional

from .api import get_currency_api
from core.database.database import get_db

app = Flask(__name__)
CORS(app)

# Global variables
api = get_currency_api()
db = get_db()
last_update = None
update_thread = None


def update_rates_background():
    """Background thread to update rates periodically"""
    global last_update
    while True:
        try:
            rates = api.get_all_rates()
            last_update = datetime.now()
            
            # Save to database
            for currency, rate in rates.items():
                db.execute("""
                    INSERT INTO currency_history (from_currency, to_currency, rate, recorded_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (currency, 'TRY', rate))
            
            time.sleep(300)  # Update every 5 minutes
        except Exception as e:
            print(f"Error updating rates: {e}")
            time.sleep(60)  # Retry after 1 minute


@app.route('/')
def index():
    """Main web interface"""
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>unibosoft - Döviz Kurları</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0a0a0a;
            color: #fff;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #00ff88;
            margin-bottom: 30px;
        }
        .currency-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .currency-card {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .currency-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
        }
        .currency-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .currency-code {
            font-size: 24px;
            font-weight: bold;
        }
        .currency-flag {
            font-size: 32px;
        }
        .currency-rate {
            font-size: 28px;
            margin: 10px 0;
        }
        .change-positive {
            color: #00ff88;
        }
        .change-negative {
            color: #ff4444;
        }
        .change-neutral {
            color: #888;
        }
        .converter {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 40px;
        }
        .converter h2 {
            color: #00ff88;
            margin-bottom: 20px;
        }
        .converter-row {
            display: flex;
            gap: 20px;
            align-items: center;
            margin-bottom: 20px;
        }
        input, select {
            padding: 10px;
            background: #222;
            border: 1px solid #444;
            color: #fff;
            border-radius: 4px;
            font-size: 16px;
        }
        input[type="number"] {
            width: 200px;
        }
        select {
            width: 150px;
        }
        .update-info {
            text-align: center;
            color: #888;
            margin-top: 40px;
        }
        .chart-container {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 40px;
            height: 400px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💱 unibosoft - Döviz Kurları</h1>
        
        <div class="converter">
            <h2>Döviz Çevirici</h2>
            <div class="converter-row">
                <input type="number" id="amount" value="100" step="0.01">
                <select id="from">
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="TRY" selected>TRY</option>
                </select>
                <span>→</span>
                <select id="to">
                    <option value="USD" selected>USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="TRY">TRY</option>
                </select>
                <span id="result" style="font-size: 24px; font-weight: bold; color: #00ff88;">= 0.00</span>
            </div>
        </div>
        
        <div id="rates" class="currency-grid">
            <div style="text-align: center; grid-column: 1/-1;">Yükleniyor...</div>
        </div>
        
        <div class="update-info" id="updateInfo">
            Son güncelleme: -
        </div>
    </div>
    
    <script>
        const FLAGS = {
            'USD': '🇺🇸', 'EUR': '🇪🇺', 'GBP': '🇬🇧', 'JPY': '🇯🇵',
            'CHF': '🇨🇭', 'CAD': '🇨🇦', 'AUD': '🇦🇺', 'RUB': '🇷🇺',
            'CNY': '🇨🇳', 'SAR': '🇸🇦', 'TRY': '🇹🇷'
        };
        
        const CRYPTO_ICONS = {
            'BTC': '🟠', 'ETH': '🔷', 'BNB': '🟡', 'USDT': '🟢',
            'SOL': '🟣', 'XRP': '⚪', 'ADA': '🔵', 'AVAX': '🔺',
            'DOGE': '🐕', 'DOT': '⚫'
        };
        
        let rates = {};
        
        async function loadRates() {
            try {
                const response = await fetch('/api/rates');
                const data = await response.json();
                rates = data.rates;
                displayRates(data);
                updateConverter();
            } catch (error) {
                console.error('Error loading rates:', error);
            }
        }
        
        function displayRates(data) {
            const container = document.getElementById('rates');
            container.innerHTML = '';
            
            // Display currencies
            Object.entries(data.rates).forEach(([code, rate]) => {
                if (code === 'TRY') return;
                
                const change = data.changes[code] || 0;
                const changeClass = change > 0 ? 'change-positive' : 
                                  change < 0 ? 'change-negative' : 'change-neutral';
                const arrow = change > 0 ? '↑' : change < 0 ? '↓' : '→';
                
                const card = document.createElement('div');
                card.className = 'currency-card';
                card.innerHTML = `
                    <div class="currency-header">
                        <span class="currency-code">${code}</span>
                        <span class="currency-flag">${FLAGS[code] || CRYPTO_ICONS[code] || ''}</span>
                    </div>
                    <div class="currency-rate">₺${rate.toFixed(2)}</div>
                    <div class="${changeClass}">
                        ${arrow} ${Math.abs(change).toFixed(2)}%
                    </div>
                `;
                container.appendChild(card);
            });
            
            // Update time
            document.getElementById('updateInfo').textContent = 
                `Son güncelleme: ${new Date(data.last_update).toLocaleString('tr-TR')}`;
        }
        
        function updateConverter() {
            const amount = parseFloat(document.getElementById('amount').value) || 0;
            const from = document.getElementById('from').value;
            const to = document.getElementById('to').value;
            
            let result = 0;
            if (from === 'TRY') {
                result = amount / (rates[to] || 1);
            } else if (to === 'TRY') {
                result = amount * (rates[from] || 1);
            } else {
                const tryAmount = amount * (rates[from] || 1);
                result = tryAmount / (rates[to] || 1);
            }
            
            document.getElementById('result').textContent = `= ${result.toFixed(2)}`;
        }
        
        // Event listeners
        document.getElementById('amount').addEventListener('input', updateConverter);
        document.getElementById('from').addEventListener('change', updateConverter);
        document.getElementById('to').addEventListener('change', updateConverter);
        
        // Load rates initially and every 30 seconds
        loadRates();
        setInterval(loadRates, 30000);
    </script>
</body>
</html>
    """)


@app.route('/api/rates')
def api_rates():
    """Get current exchange rates"""
    rates = api.get_all_rates()
    
    # Calculate changes
    changes = {}
    for currency in rates:
        # Get previous rate from database
        prev_rate = db.execute("""
            SELECT rate FROM currency_history 
            WHERE from_currency = ? AND to_currency = 'TRY'
            AND recorded_at >= datetime('now', '-1 day')
            ORDER BY recorded_at ASC
            LIMIT 1
        """, (currency,))
        
        if prev_rate and len(prev_rate) > 0:
            old_rate = prev_rate[0]['rate']
            change = ((rates[currency] - old_rate) / old_rate) * 100
            changes[currency] = change
        else:
            changes[currency] = 0
    
    return jsonify({
        'rates': rates,
        'changes': changes,
        'last_update': last_update.isoformat() if last_update else None
    })


@app.route('/api/history/<currency>')
def api_history(currency):
    """Get historical rates for a currency"""
    days = int(request.args.get('days', 30))
    
    history = db.execute("""
        SELECT date(recorded_at) as date, 
               AVG(rate) as avg_rate,
               MIN(rate) as min_rate,
               MAX(rate) as max_rate
        FROM currency_history
        WHERE from_currency = ? AND to_currency = 'TRY'
        AND recorded_at >= datetime('now', '-' || ? || ' days')
        GROUP BY date(recorded_at)
        ORDER BY date ASC
    """, (currency, days))
    
    return jsonify({
        'currency': currency,
        'history': [dict(row) for row in history]
    })


@app.route('/api/alerts', methods=['GET', 'POST'])
def api_alerts():
    """Manage price alerts"""
    if request.method == 'POST':
        data = request.json
        # Save alert to database
        db.execute("""
            INSERT INTO currency_alerts (currency, target_rate, direction, user_id)
            VALUES (?, ?, ?, ?)
        """, (data['currency'], data['target_rate'], data['direction'], data.get('user_id', 1)))
        
        return jsonify({'success': True})
    
    # Get alerts
    alerts = db.execute("""
        SELECT * FROM currency_alerts
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (request.args.get('user_id', 1),))
    
    return jsonify({'alerts': [dict(row) for row in alerts]})


def start_web_server(host='0.0.0.0', port=5001):
    """Start the web server"""
    global update_thread
    
    # Start background update thread
    update_thread = threading.Thread(target=update_rates_background, daemon=True)
    update_thread.start()
    
    # Run Flask app
    app.run(host=host, port=port, debug=False)