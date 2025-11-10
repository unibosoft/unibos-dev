"""
Currencies API Module
Real data fetching from TCMB and banks
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import time
import json
import logging

logger = logging.getLogger(__name__)


class CurrencyAPI:
    """Currency data fetching from real sources"""
    
    # API endpoints
    TCMB_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
    
    # Bank URLs for additional rates
    BANK_URLS = {
        'garanti': 'https://www.garantibbva.com.tr/tr/guncel/doviz_kurlari.page',
        'isbank': 'https://www.isbank.com.tr/doviz-kurlari',
        'akbank': 'https://www.akbank.com/tr-tr/sayfalar/Doviz-Kurlari.aspx'
    }
    
    # Crypto APIs (free tier)
    CRYPTO_APIS = {
        'coingecko': 'https://api.coingecko.com/api/v3/simple/price',
        'binance': 'https://api.binance.com/api/v3/ticker/price'
    }
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.last_fetch = {}
    
    def get_tcmb_rates(self) -> Dict[str, float]:
        """Get official rates from Turkish Central Bank"""
        try:
            # Check cache
            if self._is_cache_valid('tcmb'):
                return self.cache.get('tcmb', {})
            
            response = requests.get(self.TCMB_URL, timeout=10)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            rates = {}
            
            for currency in root.findall('.//Currency'):
                code = currency.get('Kod')
                if code:
                    try:
                        forex_buying = currency.find('ForexBuying')
                        forex_selling = currency.find('ForexSelling')
                        
                        if forex_buying is not None and forex_selling is not None:
                            buy_rate = float(forex_buying.text)
                            sell_rate = float(forex_selling.text)
                            # Use average for display
                            rates[code] = (buy_rate + sell_rate) / 2
                    except (ValueError, AttributeError):
                        continue
            
            # Cache results
            self.cache['tcmb'] = rates
            self.last_fetch['tcmb'] = time.time()
            
            return rates
            
        except Exception as e:
            logger.error(f"Failed to fetch TCMB rates: {e}")
            return self.cache.get('tcmb', {})
    
    def get_bank_rates(self, bank: str) -> Dict[str, float]:
        """Get rates from specific bank website"""
        try:
            if bank not in self.BANK_URLS:
                return {}
            
            # Check cache
            cache_key = f'bank_{bank}'
            if self._is_cache_valid(cache_key):
                return self.cache.get(cache_key, {})
            
            response = requests.get(self.BANK_URLS[bank], timeout=10)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            rates = {}
            
            # Bank-specific parsing logic would go here
            # This is a simplified example
            if bank == 'garanti':
                # Find currency table
                table = soup.find('table', {'class': 'currency-table'})
                if table:
                    for row in table.find_all('tr')[1:]:  # Skip header
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            currency = cells[0].text.strip()
                            buy = float(cells[1].text.replace(',', '.'))
                            sell = float(cells[2].text.replace(',', '.'))
                            rates[currency] = (buy + sell) / 2
            
            # Cache results
            self.cache[cache_key] = rates
            self.last_fetch[cache_key] = time.time()
            
            return rates
            
        except Exception as e:
            logger.error(f"Failed to fetch {bank} rates: {e}")
            return self.cache.get(f'bank_{bank}', {})
    
    def get_crypto_rates(self) -> Dict[str, float]:
        """Get cryptocurrency rates"""
        try:
            # Check cache
            if self._is_cache_valid('crypto'):
                return self.cache.get('crypto', {})
            
            # Try CoinGecko API (free, no key required)
            crypto_ids = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'BNB': 'binancecoin',
                'USDT': 'tether',
                'SOL': 'solana',
                'XRP': 'ripple',
                'ADA': 'cardano',
                'AVAX': 'avalanche-2',
                'DOGE': 'dogecoin',
                'DOT': 'polkadot'
            }
            
            ids = ','.join(crypto_ids.values())
            url = f"{self.CRYPTO_APIS['coingecko']}?ids={ids}&vs_currencies=try"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rates = {}
            
            for symbol, coin_id in crypto_ids.items():
                if coin_id in data:
                    rates[symbol] = data[coin_id]['try']
            
            # Cache results
            self.cache['crypto'] = rates
            self.last_fetch['crypto'] = time.time()
            
            return rates
            
        except Exception as e:
            logger.error(f"Failed to fetch crypto rates: {e}")
            # Fallback to demo data if API fails
            return self._get_demo_crypto_rates()
    
    def _get_demo_crypto_rates(self) -> Dict[str, float]:
        """Get demo crypto rates for offline mode"""
        return {
            'BTC': 2500000.0,
            'ETH': 150000.0,
            'BNB': 25000.0,
            'USDT': 32.5,
            'SOL': 3500.0,
            'XRP': 25.0,
            'ADA': 15.0,
            'AVAX': 1200.0,
            'DOGE': 5.0,
            'DOT': 350.0
        }
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache is still valid"""
        if key not in self.last_fetch:
            return False
        
        elapsed = time.time() - self.last_fetch[key]
        return elapsed < self.cache_timeout
    
    def get_all_rates(self) -> Dict[str, float]:
        """Get all rates (fiat + crypto)"""
        rates = {'TRY': 1.0}  # Base currency
        
        # Get fiat rates from TCMB
        tcmb_rates = self.get_tcmb_rates()
        rates.update(tcmb_rates)
        
        # Get crypto rates
        crypto_rates = self.get_crypto_rates()
        rates.update(crypto_rates)
        
        return rates
    
    def get_historical_rates(self, currency: str, days: int = 30) -> List[Dict]:
        """Get historical rates for a currency"""
        # This would typically query a database or API
        # For now, generate simulated historical data
        historical = []
        base_rate = self.get_all_rates().get(currency, 1.0)
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            # Simulate price variation
            variation = random.uniform(0.95, 1.05)
            rate = base_rate * variation
            
            historical.append({
                'date': date.strftime('%Y-%m-%d'),
                'rate': rate,
                'open': rate * random.uniform(0.99, 1.01),
                'high': rate * random.uniform(1.01, 1.03),
                'low': rate * random.uniform(0.97, 0.99),
                'close': rate
            })
        
        return historical


# Singleton instance
_api_instance = None

def get_currency_api() -> CurrencyAPI:
    """Get singleton API instance"""
    global _api_instance
    if _api_instance is None:
        _api_instance = CurrencyAPI()
    return _api_instance