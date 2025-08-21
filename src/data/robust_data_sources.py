#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - ROBUST DATA SOURCES SYSTEM
Sistema robusto con múltiples fuentes de datos y failover inteligente
Based on free-for.dev APIs + AGI Nuclei recommendations
"""

import os
import sys
import time
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Import our credential manager
try:
    from api_credentials_manager import api_manager
except ImportError:
    print("⚠️ API Credentials Manager not found")
    api_manager = None

# Import yfinance as backup
try:
    import yfinance as yf
except ImportError:
    yf = None

class RobustDataSourceManager:
    """Gestor robusto con múltiples fuentes de datos financieros"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_manager = api_manager
        
        # Priority order for different data types
        self.data_source_priority = {
            'stock_price': ['iex', 'fmp', 'yahoo', 'alphavantage', 'finnhub', 'polygon'],
            'options': ['polygon', 'yahoo', 'alphavantage'],
            'crypto': ['finnhub', 'polygon', 'fmp'],
            'news': ['finnhub', 'alphavantage'],
            'fundamentals': ['fmp', 'alphavantage', 'iex']
        }
        
        # Health status for each API
        self.api_health = {}
        self.last_health_check = {}
        
    def get_stock_data(self, symbol: str, period: str = "5d", data_type: str = "stock_price") -> Tuple[Optional[pd.DataFrame], str]:
        """
        Get stock data with intelligent failover
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Time period ('5d', '1mo', '1y', '2y')
            data_type: Type of data ('stock_price', 'options', 'crypto')
            
        Returns:
            Tuple of (DataFrame, source_name) or (None, 'failed')
        """
        
        # Get priority list for this data type
        sources = self.data_source_priority.get(data_type, ['yahoo', 'alphavantage', 'polygon'])
        
        for source in sources:
            try:
                # Check if API is healthy and within rate limits
                if not self._check_api_availability(source):
                    continue
                
                # Try to get data from this source
                data = self._get_data_from_source(source, symbol, period)
                
                if data is not None and not data.empty:
                    self.logger.info(f"✅ Successfully got data for {symbol} from {source}")
                    if self.api_manager:
                        self.api_manager.record_api_call(source)
                    return data, source
                
            except Exception as e:
                self.logger.warning(f"⚠️ {source} failed for {symbol}: {e}")
                if self.api_manager:
                    self.api_manager.mark_api_failed(source, str(e))
                continue
        
        self.logger.error(f"❌ All data sources failed for {symbol}")
        return None, "failed"
    
    def _check_api_availability(self, source: str) -> bool:
        """Check if API is available and healthy"""
        
        # Check rate limits
        if self.api_manager and not self.api_manager.check_rate_limit(source):
            return False
        
        # Check health status
        if source in self.api_health:
            health = self.api_health[source]
            last_check = self.last_health_check.get(source, 0)
            
            # If last check was less than 5 minutes ago and failed, skip
            if time.time() - last_check < 300 and not health:
                return False
        
        return True
    
    def _get_data_from_source(self, source: str, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Get data from specific source"""
        
        if source == 'yahoo':
            return self._get_yahoo_data(symbol, period)
        elif source == 'iex':
            return self._get_iex_data(symbol, period)
        elif source == 'fmp':
            return self._get_fmp_data(symbol, period)
        elif source == 'alphavantage':
            return self._get_alphavantage_data(symbol, period)
        elif source == 'finnhub':
            return self._get_finnhub_data(symbol, period)
        elif source == 'polygon':
            return self._get_polygon_data(symbol, period)
        else:
            raise Exception(f"Unknown data source: {source}")
    
    def _get_yahoo_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Get data from Yahoo Finance"""
        if not yf:
            raise Exception("yfinance not available")
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, timeout=10)
        
        if data.empty:
            raise Exception("Yahoo returned empty data")
        
        # Add delay to respect rate limits
        time.sleep(0.5)
        return data
    
    def _get_iex_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Get data from IEX Cloud (free tier: 100 requests/day)"""
        if not self.api_manager:
            raise Exception("API manager not available")
        
        creds = self.api_manager.get_credentials('iex')
        if not creds or not creds.get('api_key'):
            raise Exception("IEX API key not configured")
        
        # Convert period to IEX format
        period_map = {'5d': '5d', '1mo': '1m', '1y': '1y', '2y': '2y'}
        iex_period = period_map.get(period, '5d')
        
        url = f"https://cloud.iexapis.com/stable/stock/{symbol}/chart/{iex_period}"
        params = {'token': creds['api_key']}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            raise Exception("IEX returned empty data")
        
        # Convert to pandas DataFrame
        df_data = []
        for item in data:
            df_data.append({
                'Date': pd.to_datetime(item['date']),
                'Open': float(item.get('open', item.get('close', 0))),
                'High': float(item.get('high', item.get('close', 0))),
                'Low': float(item.get('low', item.get('close', 0))),
                'Close': float(item['close']),
                'Volume': int(item.get('volume', 0))
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        time.sleep(1)  # Rate limiting
        return df
    
    def _get_fmp_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Get data from Financial Modeling Prep (free tier: 250 requests/day)"""
        if not self.api_manager:
            raise Exception("API manager not available")
        
        creds = self.api_manager.get_credentials('fmp')
        if not creds or not creds.get('api_key'):
            raise Exception("FMP API key not configured")
        
        # Convert period to days
        days_map = {'5d': 5, '1mo': 30, '1y': 365, '2y': 730}
        days = days_map.get(period, 5)
        
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}"
        params = {
            'apikey': creds['api_key'],
            'timeseries': days
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('historical'):
            raise Exception("FMP returned no historical data")
        
        # Convert to pandas DataFrame
        df_data = []
        for item in data['historical'][:days]:  # Limit to requested period
            df_data.append({
                'Date': pd.to_datetime(item['date']),
                'Open': float(item['open']),
                'High': float(item['high']),
                'Low': float(item['low']),
                'Close': float(item['close']),
                'Volume': int(item['volume'])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        time.sleep(2)  # Rate limiting
        return df
    
    def _get_alphavantage_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Get data from Alpha Vantage (enhanced version)"""
        if not self.api_manager:
            raise Exception("API manager not available")
        
        creds = self.api_manager.get_credentials('alphavantage')
        if not creds or not creds.get('api_key'):
            raise Exception("Alpha Vantage API key not configured")
        
        # Use different function based on period
        if period in ['5d', '1mo']:
            function = 'TIME_SERIES_DAILY'
            outputsize = 'compact'
        else:
            function = 'TIME_SERIES_DAILY'
            outputsize = 'full'
        
        url = "https://www.alphavantage.co/query"
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': creds['api_key'],
            'outputsize': outputsize
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if 'Error Message' in data:
            raise Exception(f"Alpha Vantage error: {data['Error Message']}")
        
        if 'Note' in data:
            raise Exception("Alpha Vantage rate limit exceeded")
        
        time_series_key = 'Time Series (Daily)'
        if time_series_key not in data:
            raise Exception(f"No time series data found. Keys: {list(data.keys())}")
        
        time_series = data[time_series_key]
        
        # Convert to pandas DataFrame
        df_data = []
        for date_str, values in time_series.items():
            df_data.append({
                'Date': pd.to_datetime(date_str),
                'Open': float(values['1. open']),
                'High': float(values['2. high']),
                'Low': float(values['3. low']),
                'Close': float(values['4. close']),
                'Volume': int(values['5. volume'])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        # Filter by period
        days_map = {'5d': 5, '1mo': 30, '1y': 365, '2y': 730}
        days = days_map.get(period, 5)
        df = df.tail(days)
        
        time.sleep(12)  # Alpha Vantage rate limiting
        return df
    
    def _get_finnhub_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Get data from Finnhub (free tier: 60 calls/minute)"""
        if not self.api_manager:
            raise Exception("API manager not available")
        
        creds = self.api_manager.get_credentials('finnhub')
        if not creds or not creds.get('api_key'):
            raise Exception("Finnhub API key not configured")
        
        # Calculate time range
        end_time = int(time.time())
        days_map = {'5d': 5, '1mo': 30, '1y': 365, '2y': 730}
        days = days_map.get(period, 5)
        start_time = end_time - (days * 24 * 60 * 60)
        
        url = "https://finnhub.io/api/v1/stock/candle"
        params = {
            'symbol': symbol,
            'resolution': 'D',  # Daily
            'from': start_time,
            'to': end_time,
            'token': creds['api_key']
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('s') != 'ok':
            raise Exception(f"Finnhub error: {data}")
        
        # Convert to pandas DataFrame
        df_data = []
        timestamps = data.get('t', [])
        opens = data.get('o', [])
        highs = data.get('h', [])
        lows = data.get('l', [])
        closes = data.get('c', [])
        volumes = data.get('v', [])
        
        for i in range(len(timestamps)):
            df_data.append({
                'Date': pd.to_datetime(timestamps[i], unit='s'),
                'Open': float(opens[i]),
                'High': float(highs[i]),
                'Low': float(lows[i]),
                'Close': float(closes[i]),
                'Volume': int(volumes[i])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        time.sleep(1)  # Rate limiting
        return df
    
    def _get_polygon_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Get data from Polygon.io (enhanced version)"""
        if not self.api_manager:
            raise Exception("API manager not available")
        
        creds = self.api_manager.get_credentials('polygon')
        if not creds or not creds.get('api_key'):
            raise Exception("Polygon API key not configured")
        
        # Calculate date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        days_map = {'5d': 5, '1mo': 30, '1y': 365, '2y': 730}
        days = days_map.get(period, 5)
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
        params = {'apikey': creds['api_key']}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') != 'OK' or not data.get('results'):
            raise Exception(f"Polygon API error: {data}")
        
        # Convert to pandas DataFrame
        df_data = []
        for item in data['results']:
            df_data.append({
                'Date': pd.to_datetime(item['t'], unit='ms'),
                'Open': float(item['o']),
                'High': float(item['h']),
                'Low': float(item['l']),
                'Close': float(item['c']),
                'Volume': int(item['v'])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        time.sleep(1)  # Rate limiting
        return df
    
    def get_multiple_stocks(self, symbols: List[str], period: str = "5d") -> Dict[str, pd.DataFrame]:
        """Get data for multiple stocks efficiently"""
        results = {}
        
        for symbol in symbols:
            try:
                data, source = self.get_stock_data(symbol, period)
                if data is not None:
                    results[symbol] = data
                    self.logger.info(f"✅ {symbol}: {len(data)} days from {source}")
                else:
                    self.logger.warning(f"❌ Failed to get data for {symbol}")
            except Exception as e:
                self.logger.error(f"❌ Error getting {symbol}: {e}")
        
        return results
    
    def health_check_all_apis(self) -> Dict[str, bool]:
        """Perform health check on all configured APIs"""
        results = {}
        
        for source in ['yahoo', 'iex', 'fmp', 'alphavantage', 'finnhub', 'polygon']:
            try:
                # Try to get a simple data request
                data, _ = self.get_stock_data('AAPL', '5d')
                results[source] = data is not None
                self.api_health[source] = results[source]
                self.last_health_check[source] = time.time()
            except Exception as e:
                results[source] = False
                self.api_health[source] = False
                self.last_health_check[source] = time.time()
                self.logger.warning(f"❌ {source} health check failed: {e}")
        
        return results
    
    def get_api_status_report(self) -> Dict:
        """Get comprehensive status report"""
        if self.api_manager:
            usage_report = self.api_manager.get_usage_report()
        else:
            usage_report = {}
        
        health_status = self.health_check_all_apis()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'health_status': health_status,
            'usage_report': usage_report,
            'available_sources': [k for k, v in health_status.items() if v],
            'failed_sources': [k for k, v in health_status.items() if not v]
        }
        
        return report

# Global instance
robust_data_manager = RobustDataSourceManager()

def test_all_sources():
    """Test all data sources"""
    print("🧪 TESTING ALL DATA SOURCES")
    print("=" * 40)
    
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        data, source = robust_data_manager.get_stock_data(symbol, '5d')
        
        if data is not None:
            print(f"✅ Success! Got {len(data)} days from {source}")
            print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
        else:
            print(f"❌ Failed to get data for {symbol}")
    
    # Status report
    print("\n📋 API STATUS REPORT:")
    status = robust_data_manager.get_api_status_report()
    
    print(f"✅ Available: {', '.join(status['available_sources'])}")
    print(f"❌ Failed: {', '.join(status['failed_sources'])}")

if __name__ == "__main__":
    test_all_sources()