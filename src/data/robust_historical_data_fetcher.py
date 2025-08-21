#!/usr/bin/env python3
"""
📈 ROBUST HISTORICAL DATA FETCHER
Sistema robusto para obtener datos históricos reales usando múltiples fuentes
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import json

class RobustHistoricalDataFetcher:
    """Fetcher robusto para datos históricos con múltiples fuentes"""
    
    def __init__(self):
        self.polygon_key = os.getenv('POLYGON_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY', 'demo')
        
    def get_polygon_historical_data(self, symbol, period_days=252):
        """Obtener datos históricos de Polygon.io"""
        if not self.polygon_key:
            return None
            
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days + 100)  # Extra buffer for weekends
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            params = {
                'apikey': self.polygon_key,
                'adjusted': 'true',
                'sort': 'asc',
                'limit': 50000
            }
            
            print(f"📡 Fetching {symbol} historical data from Polygon...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' in data and data['results']:
                    results = data['results']
                    
                    # Convert to DataFrame
                    df_data = []
                    for result in results:
                        df_data.append({
                            'Date': pd.to_datetime(result['t'], unit='ms'),
                            'Open': result['o'],
                            'High': result['h'],
                            'Low': result['l'],
                            'Close': result['c'],
                            'Volume': result['v']
                        })
                    
                    df = pd.DataFrame(df_data)
                    df.set_index('Date', inplace=True)
                    df = df.sort_index()
                    
                    print(f"✅ Polygon: {len(df)} días de datos históricos para {symbol}")
                    print(f"✅ Rango: {df.index[0].date()} a {df.index[-1].date()}")
                    print(f"✅ Último precio: ${df['Close'].iloc[-1]:.2f}")
                    
                    return df
                else:
                    print(f"❌ Polygon: No results for {symbol}")
                    return None
            else:
                print(f"❌ Polygon API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Polygon error for {symbol}: {e}")
            return None
    
    def get_alpha_vantage_historical_data(self, symbol):
        """Obtener datos históricos de Alpha Vantage"""
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY_ADJUSTED',
                'symbol': symbol,
                'outputsize': 'full',
                'apikey': self.alpha_vantage_key
            }
            
            print(f"📡 Fetching {symbol} from Alpha Vantage (historical)...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'Time Series (Daily)' in data:
                    time_series = data['Time Series (Daily)']
                    
                    # Convert to DataFrame
                    df_data = []
                    for date_str, values in time_series.items():
                        df_data.append({
                            'Date': pd.to_datetime(date_str),
                            'Open': float(values['1. open']),
                            'High': float(values['2. high']),
                            'Low': float(values['3. low']),
                            'Close': float(values['4. close']),
                            'Volume': int(values['6. volume'])
                        })
                    
                    df = pd.DataFrame(df_data)
                    df.set_index('Date', inplace=True)
                    df = df.sort_index()
                    
                    print(f"✅ Alpha Vantage: {len(df)} días para {symbol}")
                    return df
                else:
                    print(f"❌ Alpha Vantage: {data}")
                    return None
            else:
                print(f"❌ Alpha Vantage HTTP error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Alpha Vantage error: {e}")
            return None
    
    def generate_realistic_mock_data(self, symbol, days=252):
        """Generate realistic mock data as last resort"""
        print(f"⚠️ Generating realistic mock data for {symbol} ({days} days)")
        
        # Base prices for different symbols
        base_prices = {
            'SPY': 637.18, 'AAPL': 229.35, 'MSFT': 522.04, 'TSLA': 329.65,
            'GOOGL': 167.0, 'AMZN': 182.0, 'NVDA': 137.0, 'META': 510.0
        }
        
        base_price = base_prices.get(symbol, 200.0)
        
        # Generate realistic price movement
        np.random.seed(hash(symbol) % 10000)  # Deterministic but symbol-specific
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate realistic returns (0.8% daily volatility)
        returns = np.random.normal(0.0001, 0.008, days)  # Slight upward bias, realistic vol
        
        # Generate price series
        prices = [base_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # Generate volumes (realistic for each symbol)
        base_volumes = {
            'SPY': 50000000, 'AAPL': 40000000, 'MSFT': 20000000, 'TSLA': 30000000,
            'GOOGL': 15000000, 'AMZN': 25000000, 'NVDA': 35000000, 'META': 18000000
        }
        base_volume = base_volumes.get(symbol, 10000000)
        
        volumes = []
        for i in range(days):
            vol_multiplier = np.random.uniform(0.5, 2.0)  # ±50-100% variation
            volumes.append(int(base_volume * vol_multiplier))
        
        # Create DataFrame
        df_data = []
        for i, date in enumerate(dates):
            price = prices[i]
            # Generate OHLC from close price
            daily_range = price * 0.02  # 2% daily range
            high = price + np.random.uniform(0, daily_range/2)
            low = price - np.random.uniform(0, daily_range/2)
            open_price = low + np.random.uniform(0, high - low)
            
            df_data.append({
                'Date': date,
                'Open': round(open_price, 2),
                'High': round(high, 2),
                'Low': round(low, 2),
                'Close': round(price, 2),
                'Volume': volumes[i]
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        
        print(f"✅ Mock data: {len(df)} días, precio final ${df['Close'].iloc[-1]:.2f}")
        return df
    
    def get_robust_historical_data(self, symbol, period_days=252):
        """Obtener datos históricos con sistema robusto de fallbacks"""
        print(f"📊 FETCHING ROBUST HISTORICAL DATA FOR {symbol}")
        print(f"📅 Período solicitado: {period_days} días")
        print("-" * 50)
        
        # Method 1: Polygon.io (primary)
        if self.polygon_key:
            data = self.get_polygon_historical_data(symbol, period_days)
            if data is not None and len(data) >= 30:  # At least 30 days
                print(f"✅ SUCCESS: Using Polygon data for {symbol}")
                return data
        else:
            print("⚠️ No Polygon API key available")
        
        # Method 2: Alpha Vantage (backup)
        print("🔄 Trying Alpha Vantage as backup...")
        data = self.get_alpha_vantage_historical_data(symbol)
        if data is not None and len(data) >= 30:
            print(f"✅ SUCCESS: Using Alpha Vantage data for {symbol}")
            # Trim to requested period
            return data.tail(period_days)
        
        # Method 3: Realistic mock data (last resort)
        print("🔄 Using realistic mock data as last resort...")
        data = self.generate_realistic_mock_data(symbol, period_days)
        print(f"⚠️ FALLBACK: Using mock data for {symbol}")
        return data
    
    def calculate_technical_indicators(self, df):
        """Calcular indicadores técnicos reales"""
        if df is None or len(df) < 20:
            return None
            
        # RSI
        def calculate_rsi(prices, period=14):
            deltas = prices.diff()
            gains = deltas.where(deltas > 0, 0)
            losses = -deltas.where(deltas < 0, 0)
            
            avg_gain = gains.rolling(window=period).mean()
            avg_loss = losses.rolling(window=period).mean()
            
            # Prevent division by zero in RSI calculation
            avg_loss_safe = avg_loss.where(avg_loss > 0, 0.01)  # Replace zeros with small value
            rs = avg_gain / avg_loss_safe
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        # Calculate indicators
        df['RSI'] = calculate_rsi(df['Close'])
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        
        # Calculate volatility
        df['Returns'] = df['Close'].pct_change()
        df['Volatility'] = df['Returns'].rolling(window=20).std() * np.sqrt(252) * 100
        
        return df

def test_robust_fetcher():
    """Test the robust historical data fetcher"""
    print("🧪 TESTING ROBUST HISTORICAL DATA FETCHER")
    print("=" * 60)
    
    # Load environment
    env_file = "/Users/suxtan/.gemini_keys.env"
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value.strip('"').strip("'")
                    except:
                        continue
    
    fetcher = RobustHistoricalDataFetcher()
    test_symbols = ['SPY', 'AAPL']
    
    for symbol in test_symbols:
        print(f"\n📈 TESTING {symbol}")
        print("=" * 40)
        
        # Get historical data
        data = fetcher.get_robust_historical_data(symbol, 60)
        
        if data is not None:
            # Calculate technical indicators
            data_with_indicators = fetcher.calculate_technical_indicators(data)
            
            if data_with_indicators is not None:
                latest = data_with_indicators.iloc[-1]
                
                print(f"📊 RESULTADOS PARA {symbol}:")
                print(f"├─ Datos disponibles: {len(data_with_indicators)} días")
                print(f"├─ Precio actual: ${latest['Close']:.2f}")
                print(f"├─ RSI (14): {latest['RSI']:.1f}")
                print(f"├─ SMA (20): ${latest['SMA_20']:.2f}")
                print(f"├─ EMA (12): ${latest['EMA_12']:.2f}")
                print(f"├─ Volumen promedio: {latest['Volume_SMA']:,.0f}")
                print(f"└─ Volatilidad anualizada: {latest['Volatility']:.1f}%")
                
                # Validate indicators
                checks = [
                    (0 <= latest['RSI'] <= 100, "RSI en rango válido"),
                    (latest['SMA_20'] > 0, "SMA positivo"),
                    (5 <= latest['Volatility'] <= 50, "Volatilidad realista")
                ]
                
                print(f"\n🔍 VALIDACIÓN:")
                for check, desc in checks:
                    status = "✅" if check else "❌"
                    print(f"{status} {desc}")
            else:
                print(f"❌ No se pudieron calcular indicadores para {symbol}")
        else:
            print(f"❌ No se pudieron obtener datos para {symbol}")

if __name__ == "__main__":
    test_robust_fetcher()