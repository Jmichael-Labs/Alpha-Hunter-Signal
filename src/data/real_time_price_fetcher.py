#!/usr/bin/env python3
"""
📊 REAL-TIME PRICE FETCHER
Sistema para obtener precios reales en tiempo real de acciones
"""

import requests
import json
import time
from datetime import datetime
import re

class RealTimePriceFetcher:
    """Fetcher de precios reales en tiempo real"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def get_yahoo_price(self, symbol):
        """Obtener precio de Yahoo Finance"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart']:
                    result = data['chart']['result'][0]
                    if 'meta' in result and 'regularMarketPrice' in result['meta']:
                        price = float(result['meta']['regularMarketPrice'])
                        return {
                            'price': price,
                            'source': 'yahoo_finance',
                            'timestamp': datetime.now().isoformat(),
                            'symbol': symbol
                        }
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
            return None
            
    def get_marketwatch_price(self, symbol):
        """Obtener precio de MarketWatch usando scraping simple"""
        try:
            url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                text = response.text
                # Look for price patterns in the HTML
                price_patterns = [
                    r'"lastPrice":"([0-9,]+\.?[0-9]*)"',
                    r'data-module="LastPrice">([0-9,]+\.?[0-9]*)',
                    r'class="value">([0-9,]+\.?[0-9]*)</span>'
                ]
                
                for pattern in price_patterns:
                    match = re.search(pattern, text)
                    if match:
                        price_str = match.group(1).replace(',', '')
                        price = float(price_str)
                        return {
                            'price': price,
                            'source': 'marketwatch',
                            'timestamp': datetime.now().isoformat(),
                            'symbol': symbol
                        }
        except Exception as e:
            print(f"MarketWatch error for {symbol}: {e}")
            return None
            
    def get_finnhub_price(self, symbol):
        """Obtener precio de Finnhub API (gratis)"""
        try:
            # Free API key (public tier)
            api_key = "sandbox_c7bj2g2ad3iccl4b05f0"
            url = f"https://finnhub.io/api/v1/quote"
            params = {
                'symbol': symbol,
                'token': api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'c' in data and data['c'] > 0:  # Current price
                    price = float(data['c'])
                    return {
                        'price': price,
                        'source': 'finnhub',
                        'timestamp': datetime.now().isoformat(),
                        'symbol': symbol
                    }
        except Exception as e:
            print(f"Finnhub error for {symbol}: {e}")
            return None
    
    def get_real_time_price(self, symbol):
        """Obtener precio real con fallback múltiple"""
        methods = [
            self.get_yahoo_price,
            self.get_finnhub_price,
            self.get_marketwatch_price
        ]
        
        for method in methods:
            try:
                result = method(symbol)
                if result and result['price'] > 0:
                    print(f"✅ {symbol}: ${result['price']:.2f} (from {result['source']})")
                    return result
            except Exception as e:
                print(f"Method failed for {symbol}: {e}")
                continue
                
        print(f"❌ Could not get real price for {symbol}")
        return None
    
    def get_multiple_prices(self, symbols):
        """Obtener precios múltiples en lote"""
        results = {}
        
        for symbol in symbols:
            print(f"📊 Fetching real-time price for {symbol}...")
            price_data = self.get_real_time_price(symbol)
            
            if price_data:
                results[symbol] = price_data
            else:
                results[symbol] = None
                
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        return results

# Test function
def test_real_time_fetcher():
    """Test the real-time price fetcher"""
    print("🧪 TESTING REAL-TIME PRICE FETCHER")
    print("=" * 50)
    
    fetcher = RealTimePriceFetcher()
    test_symbols = ['SPY', 'AAPL', 'MSFT', 'TSLA']
    
    print("Fetching real-time prices...")
    results = fetcher.get_multiple_prices(test_symbols)
    
    print(f"\n📊 RESULTS:")
    for symbol, data in results.items():
        if data:
            print(f"✅ {symbol}: ${data['price']:.2f} (source: {data['source']})")
        else:
            print(f"❌ {symbol}: Failed to fetch")
    
    return results

if __name__ == "__main__":
    test_real_time_fetcher()