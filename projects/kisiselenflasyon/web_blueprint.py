"""
Kişisel Enflasyon Web Blueprint
Flask blueprint for personal inflation tracking web interface
"""

from flask import Blueprint, jsonify, render_template_string, request, session
from datetime import datetime, timedelta
import secrets
from typing import Dict, List, Optional
import statistics

from core.database.database import get_db

# Create blueprint
inflation_bp = Blueprint('inflation', __name__)

# Global database instance
db = get_db()


@inflation_bp.route('/')
def index():
    """Main web interface"""
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>unibosoft - Kişisel Enflasyon</title>
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
            color: #ffcc00;
            margin-bottom: 30px;
        }
        .back-link {
            display: inline-block;
            color: #ffcc00;
            text-decoration: none;
            margin-bottom: 20px;
            padding: 5px 10px;
            border: 1px solid #ffcc00;
            border-radius: 4px;
            transition: background 0.2s;
        }
        .back-link:hover {
            background: rgba(255, 204, 0, 0.1);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        .stat-label {
            color: #888;
            font-size: 14px;
        }
        .add-product {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 40px;
        }
        .form-row {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .form-group {
            flex: 1;
            min-width: 200px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #ffcc00;
        }
        input, select {
            width: 100%;
            padding: 10px;
            background: #222;
            border: 1px solid #444;
            color: #fff;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background: #ffcc00;
            color: #000;
            border: none;
            padding: 12px 30px;
            border-radius: 4px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #ffd633;
        }
        .products-table {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 40px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: #222;
            padding: 15px;
            text-align: left;
            color: #ffcc00;
        }
        td {
            padding: 15px;
            border-top: 1px solid #333;
        }
        .price-up {
            color: #ff4444;
        }
        .price-down {
            color: #00ff88;
        }
        .price-same {
            color: #888;
        }
        .category-chart {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 40px;
        }
        .category-bar {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .category-name {
            width: 150px;
        }
        .category-progress {
            flex: 1;
            height: 30px;
            background: #222;
            border-radius: 4px;
            overflow: hidden;
            margin: 0 10px;
        }
        .category-fill {
            height: 100%;
            background: #ffcc00;
            transition: width 0.3s;
        }
        .category-percent {
            width: 60px;
            text-align: right;
        }
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .alert-success {
            background: #1a4d1a;
            border: 1px solid #00ff88;
            color: #00ff88;
        }
        .alert-error {
            background: #4d1a1a;
            border: 1px solid #ff4444;
            color: #ff4444;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Ana Sayfa</a>
        <h1>💰 Kişisel Enflasyon Hesaplayıcı</h1>
        
        <div id="alerts"></div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Aylık Enflasyon</div>
                <div class="stat-value" id="monthlyInflation">-%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">3 Aylık Enflasyon</div>
                <div class="stat-value" id="quarterlyInflation">-%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Yıllık Enflasyon</div>
                <div class="stat-value" id="yearlyInflation">-%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Sepet Büyüklüğü</div>
                <div class="stat-value" id="basketSize">0</div>
            </div>
        </div>
        
        <div class="add-product">
            <h2>🛒 Ürün Ekle</h2>
            <form id="addProductForm">
                <div class="form-row">
                    <div class="form-group">
                        <label>Barkod</label>
                        <input type="text" id="barcode" placeholder="8690000000000">
                    </div>
                    <div class="form-group">
                        <label>Ürün Adı</label>
                        <input type="text" id="productName" placeholder="Ürün adı" required>
                    </div>
                    <div class="form-group">
                        <label>Kategori</label>
                        <select id="category" required>
                            <option value="">Seçin</option>
                            <option value="Gıda">Gıda</option>
                            <option value="Temizlik">Temizlik</option>
                            <option value="Kişisel Bakım">Kişisel Bakım</option>
                            <option value="Elektronik">Elektronik</option>
                            <option value="Giyim">Giyim</option>
                            <option value="Diğer">Diğer</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Marka</label>
                        <input type="text" id="brand" placeholder="Marka">
                    </div>
                    <div class="form-group">
                        <label>Fiyat (₺)</label>
                        <input type="number" id="price" step="0.01" placeholder="0.00" required>
                    </div>
                    <div class="form-group">
                        <label>Miktar</label>
                        <input type="number" id="quantity" value="1" min="1" required>
                    </div>
                </div>
                <button type="submit">Ekle</button>
            </form>
        </div>
        
        <div class="category-chart">
            <h2>📊 Kategori Dağılımı</h2>
            <div id="categoryChart"></div>
        </div>
        
        <div class="products-table">
            <h2 style="padding: 20px 20px 0;">📋 Son Eklenen Ürünler</h2>
            <table>
                <thead>
                    <tr>
                        <th>Ürün</th>
                        <th>Kategori</th>
                        <th>Marka</th>
                        <th>Fiyat</th>
                        <th>Değişim</th>
                        <th>Tarih</th>
                    </tr>
                </thead>
                <tbody id="productsTable">
                    <tr>
                        <td colspan="6" style="text-align: center; color: #888;">Henüz ürün eklenmedi</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        async function loadDashboard() {
            try {
                // Load inflation stats
                const statsResponse = await fetch('/inflation/api/stats');
                const stats = await statsResponse.json();
                
                document.getElementById('monthlyInflation').textContent = 
                    stats.monthly ? `${stats.monthly.toFixed(1)}%` : '-%';
                document.getElementById('quarterlyInflation').textContent = 
                    stats.quarterly ? `${stats.quarterly.toFixed(1)}%` : '-%';
                document.getElementById('yearlyInflation').textContent = 
                    stats.yearly ? `${stats.yearly.toFixed(1)}%` : '-%';
                document.getElementById('basketSize').textContent = stats.basket_size || 0;
                
                // Load category distribution
                loadCategoryChart(stats.categories || {});
                
                // Load recent products
                const productsResponse = await fetch('/inflation/api/products?limit=10');
                const products = await productsResponse.json();
                displayProducts(products.products || []);
                
            } catch (error) {
                console.error('Error loading dashboard:', error);
                showAlert('Veriler yüklenirken hata oluştu', 'error');
            }
        }
        
        function loadCategoryChart(categories) {
            const container = document.getElementById('categoryChart');
            container.innerHTML = '';
            
            const total = Object.values(categories).reduce((a, b) => a + b, 0);
            
            Object.entries(categories).forEach(([name, value]) => {
                const percent = total > 0 ? (value / total * 100) : 0;
                
                const bar = document.createElement('div');
                bar.className = 'category-bar';
                bar.innerHTML = `
                    <div class="category-name">${name}</div>
                    <div class="category-progress">
                        <div class="category-fill" style="width: ${percent}%"></div>
                    </div>
                    <div class="category-percent">${percent.toFixed(1)}%</div>
                `;
                container.appendChild(bar);
            });
        }
        
        function displayProducts(products) {
            const tbody = document.getElementById('productsTable');
            
            if (products.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #888;">Henüz ürün eklenmedi</td></tr>';
                return;
            }
            
            tbody.innerHTML = products.map(product => {
                const changeClass = product.price_change > 0 ? 'price-up' : 
                                  product.price_change < 0 ? 'price-down' : 'price-same';
                const arrow = product.price_change > 0 ? '↑' : 
                            product.price_change < 0 ? '↓' : '→';
                
                return `
                    <tr>
                        <td>${product.name}</td>
                        <td>${product.category || '-'}</td>
                        <td>${product.brand || '-'}</td>
                        <td>₺${product.price.toFixed(2)}</td>
                        <td class="${changeClass}">
                            ${arrow} ${Math.abs(product.price_change || 0).toFixed(1)}%
                        </td>
                        <td>${new Date(product.recorded_at).toLocaleDateString('tr-TR')}</td>
                    </tr>
                `;
            }).join('');
        }
        
        function showAlert(message, type = 'success') {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type}`;
            alertDiv.textContent = message;
            
            const container = document.getElementById('alerts');
            container.appendChild(alertDiv);
            
            setTimeout(() => {
                alertDiv.remove();
            }, 3000);
        }
        
        // Handle form submission
        document.getElementById('addProductForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                barcode: document.getElementById('barcode').value,
                name: document.getElementById('productName').value,
                category: document.getElementById('category').value,
                brand: document.getElementById('brand').value,
                price: parseFloat(document.getElementById('price').value),
                quantity: parseInt(document.getElementById('quantity').value)
            };
            
            try {
                const response = await fetch('/inflation/api/add-product', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAlert('Ürün başarıyla eklendi');
                    document.getElementById('addProductForm').reset();
                    loadDashboard();
                } else {
                    showAlert(result.message || 'Ürün eklenirken hata oluştu', 'error');
                }
            } catch (error) {
                console.error('Error adding product:', error);
                showAlert('Ürün eklenirken hata oluştu', 'error');
            }
        });
        
        // Load dashboard on page load
        loadDashboard();
        
        // Refresh every 30 seconds
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
    """)


@inflation_bp.route('/api/stats')
def api_inflation_stats():
    """Get inflation statistics"""
    user_id = session.get('user_id', 1)  # Default user for demo
    
    # Get inflation rates for different periods
    stats = {
        'monthly': calculate_inflation(30),
        'quarterly': calculate_inflation(90),
        'yearly': calculate_inflation(365),
        'basket_size': get_basket_size(user_id),
        'categories': get_category_distribution(user_id)
    }
    
    return jsonify(stats)


@inflation_bp.route('/api/products')
def api_get_products():
    """Get recent products with price history"""
    limit = int(request.args.get('limit', 20))
    
    products = db.select(
        'price_history',
        order_by='recorded_at DESC',
        limit=limit
    )
    
    # Calculate price changes
    for product in products:
        product_id = product['product_id']
        
        # Get product details
        product_info = db.select('products', where={'id': product_id})
        if product_info:
            product.update(product_info[0])
        
        # Get previous price
        prev_price = db.execute("""
            SELECT price FROM price_history
            WHERE product_id = ? AND recorded_at < ?
            ORDER BY recorded_at DESC
            LIMIT 1
        """, (product_id, product['recorded_at']))
        
        if prev_price and len(prev_price) > 0:
            old_price = prev_price[0]['price']
            product['price_change'] = ((product['price'] - old_price) / old_price) * 100
        else:
            product['price_change'] = 0
    
    return jsonify({'products': products})


@inflation_bp.route('/api/add-product', methods=['POST'])
def api_add_product():
    """Add a new product or price record"""
    data = request.json
    
    try:
        # Check if product exists
        existing = db.select('products', where={'barcode': data.get('barcode')}) if data.get('barcode') else None
        
        if existing:
            product_id = existing[0]['id']
        else:
            # Create new product
            product_id = db.insert('products', {
                'name': data['name'],
                'category': data.get('category'),
                'brand': data.get('brand'),
                'barcode': data.get('barcode')
            })
        
        # Add price record
        db.insert('price_history', {
            'product_id': product_id,
            'price': data['price'],
            'store': data.get('store', 'Genel')
        })
        
        return jsonify({'success': True, 'product_id': product_id})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@inflation_bp.route('/api/search')
def api_search_products():
    """Search products by name or barcode"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'products': []})
    
    products = db.execute("""
        SELECT DISTINCT p.*, 
               (SELECT price FROM price_history WHERE product_id = p.id ORDER BY recorded_at DESC LIMIT 1) as current_price
        FROM products p
        WHERE p.name LIKE ? OR p.barcode LIKE ?
        LIMIT 20
    """, (f'%{query}%', f'%{query}%'))
    
    return jsonify({'products': [dict(row) for row in products]})


def calculate_inflation(days: int) -> float:
    """Calculate inflation rate for given period"""
    try:
        # Get current basket total
        current_total = db.execute("""
            SELECT SUM(ph.price * COALESCE(b.quantity, 1)) as total
            FROM (
                SELECT product_id, MAX(recorded_at) as latest_date
                FROM price_history
                WHERE recorded_at >= datetime('now', '-' || ? || ' days')
                GROUP BY product_id
            ) latest
            JOIN price_history ph ON ph.product_id = latest.product_id 
                AND ph.recorded_at = latest.latest_date
            LEFT JOIN basket b ON b.product_id = ph.product_id
        """, (days,))
        
        # Get past basket total
        past_total = db.execute("""
            SELECT SUM(ph.price * COALESCE(b.quantity, 1)) as total
            FROM (
                SELECT product_id, MIN(recorded_at) as earliest_date
                FROM price_history
                WHERE recorded_at >= datetime('now', '-' || ? || ' days')
                GROUP BY product_id
            ) earliest
            JOIN price_history ph ON ph.product_id = earliest.product_id 
                AND ph.recorded_at = earliest.earliest_date
            LEFT JOIN basket b ON b.product_id = ph.product_id
        """, (days,))
        
        if current_total and past_total and current_total[0]['total'] and past_total[0]['total']:
            current = current_total[0]['total']
            past = past_total[0]['total']
            return ((current - past) / past) * 100
        
        return 0
        
    except Exception as e:
        print(f"Error calculating inflation: {e}")
        return 0


def get_basket_size(user_id: int) -> int:
    """Get number of products in user's basket"""
    # For now, count unique products with recent prices
    result = db.execute("""
        SELECT COUNT(DISTINCT product_id) as count
        FROM price_history
        WHERE recorded_at >= datetime('now', '-30 days')
    """)
    
    return result[0]['count'] if result else 0


def get_category_distribution(user_id: int) -> Dict[str, float]:
    """Get spending distribution by category"""
    results = db.execute("""
        SELECT p.category, SUM(ph.price) as total
        FROM price_history ph
        JOIN products p ON p.id = ph.product_id
        WHERE ph.recorded_at >= datetime('now', '-30 days')
        AND p.category IS NOT NULL
        GROUP BY p.category
    """)
    
    distribution = {}
    for row in results:
        distribution[row['category']] = float(row['total'])
    
    return distribution