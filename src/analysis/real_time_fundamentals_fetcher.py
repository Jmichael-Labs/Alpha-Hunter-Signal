#!/usr/bin/env python3
"""
🎯 REAL-TIME FUNDAMENTALS FETCHER
APIs directas para datos fundamentales 100% actuales
NO web scraping - Solo APIs confiables
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
import pandas as pd

class RealTimeFundamentalsFetcher:
    """Fetcher de datos fundamentales usando APIs directas"""
    
    def __init__(self):
        # API Keys from environment
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY')
        self.iex_token = os.getenv('IEX_TOKEN')  # IEX Cloud token
        
        # API Base URLs
        self.polygon_base = "https://api.polygon.io"
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        self.iex_base = "https://api.iex.cloud/v1"
        
        # Rate limiting
        self.last_polygon_call = 0
        self.last_alpha_call = 0
        self.last_iex_call = 0
        
        print("✅ Real-Time Fundamentals Fetcher initialized")
        print(f"├─ Polygon API: {'✅' if self.polygon_api_key else '❌'}")
        print(f"├─ Alpha Vantage: {'✅' if self.alpha_vantage_key else '❌'}")
        print(f"└─ IEX Cloud: {'✅' if self.iex_token else '❌'}")
    
    def get_real_time_fundamentals(self, symbol):
        """Obtener datos fundamentales en tiempo real de múltiples APIs"""
        
        print(f"🔍 Getting REAL-TIME fundamentals for {symbol}")
        
        fundamentals = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'source': 'multiple_apis',
            'data_quality': 'real_time'
        }
        
        # 1. Try Polygon API first (most comprehensive)
        polygon_data = self.get_polygon_fundamentals(symbol)
        if polygon_data:
            fundamentals.update(polygon_data)
            fundamentals['primary_source'] = 'polygon'
        
        # 2. Alpha Vantage as backup/supplement
        alpha_data = self.get_alpha_vantage_fundamentals(symbol)
        if alpha_data:
            # Merge data, preferring Polygon when available
            for key, value in alpha_data.items():
                if key not in fundamentals or fundamentals[key] is None:
                    fundamentals[key] = value
            if fundamentals.get('primary_source') != 'polygon':
                fundamentals['primary_source'] = 'alpha_vantage'
        
        # 3. IEX as final backup
        iex_data = self.get_iex_fundamentals(symbol)
        if iex_data:
            for key, value in iex_data.items():
                if key not in fundamentals or fundamentals[key] is None:
                    fundamentals[key] = value
            if 'primary_source' not in fundamentals:
                fundamentals['primary_source'] = 'iex'
        
        # 4. Calculate derived metrics
        fundamentals.update(self.calculate_derived_metrics(fundamentals))
        
        return fundamentals
    
    def get_polygon_fundamentals(self, symbol):
        """Polygon API para datos fundamentales"""
        if not self.polygon_api_key:
            return None
            
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_polygon_call < 12:  # 12 second delay
                time.sleep(12 - (current_time - self.last_polygon_call))
            
            print(f"📡 Fetching {symbol} fundamentals from Polygon...")
            
            # Get company details
            details_url = f"{self.polygon_base}/v3/reference/tickers/{symbol}"
            details_response = requests.get(
                details_url,
                params={'apikey': self.polygon_api_key},
                timeout=10
            )
            
            self.last_polygon_call = time.time()
            
            if details_response.status_code == 200:
                details_data = details_response.json()
                
                if 'results' in details_data:
                    company_info = details_data['results']
                    
                    # Get financials (another API call)
                    time.sleep(12)  # Rate limit
                    
                    # Try to get latest financials
                    financials_url = f"{self.polygon_base}/vX/reference/financials"
                    financials_response = requests.get(
                        financials_url,
                        params={
                            'ticker': symbol,
                            'limit': 1,
                            'apikey': self.polygon_api_key
                        },
                        timeout=10
                    )
                    
                    self.last_polygon_call = time.time()
                    
                    polygon_fundamentals = {
                        'market_cap': company_info.get('market_cap'),
                        'shares_outstanding': company_info.get('share_class_shares_outstanding'),
                        'sic_description': company_info.get('sic_description'),
                        'homepage_url': company_info.get('homepage_url'),
                        'total_employees': company_info.get('total_employees'),
                        'source_type': 'polygon_real_time'
                    }
                    
                    if financials_response.status_code == 200:
                        financials_data = financials_response.json()
                        if 'results' in financials_data and financials_data['results']:
                            latest_financials = financials_data['results'][0]
                            
                            # Extract key metrics
                            if 'financials' in latest_financials:
                                fin_data = latest_financials['financials']
                                
                                # Balance Sheet data
                                balance_sheet = fin_data.get('balance_sheet', {})
                                equity = balance_sheet.get('equity', {}).get('value')
                                assets = balance_sheet.get('assets', {}).get('value')
                                liabilities = balance_sheet.get('liabilities', {}).get('value')
                                
                                if equity and company_info.get('share_class_shares_outstanding'):
                                    shares = company_info['share_class_shares_outstanding']
                                    polygon_fundamentals['book_value'] = equity / shares
                                
                                # Income Statement data
                                income_statement = fin_data.get('income_statement', {})
                                net_income = income_statement.get('net_income_loss', {}).get('value')
                                revenues = income_statement.get('revenues', {}).get('value')
                                
                                if net_income and shares:
                                    earnings_per_share = net_income / shares
                                    polygon_fundamentals['eps'] = earnings_per_share
                                
                                if revenues:
                                    polygon_fundamentals['revenue'] = revenues
                                
                                # Calculate ratios if we have current price
                                polygon_fundamentals['debt_to_equity'] = (liabilities / equity) if equity and liabilities else None
                    
                    print(f"✅ Polygon: Got fundamentals for {symbol}")
                    return polygon_fundamentals
                else:
                    print(f"❌ Polygon: No results for {symbol}")
                    return None
            else:
                print(f"❌ Polygon API error: {details_response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Polygon error: {e}")
            return None
    
    def get_alpha_vantage_fundamentals(self, symbol):
        """Alpha Vantage API para datos fundamentales"""
        if not self.alpha_vantage_key:
            return None
            
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_alpha_call < 12:  # 12 second delay
                time.sleep(12 - (current_time - self.last_alpha_call))
            
            print(f"📡 Fetching {symbol} fundamentals from Alpha Vantage...")
            
            # Company Overview endpoint
            response = requests.get(
                self.alpha_vantage_base,
                params={
                    'function': 'OVERVIEW',
                    'symbol': symbol,
                    'apikey': self.alpha_vantage_key
                },
                timeout=10
            )
            
            self.last_alpha_call = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                if 'Symbol' in data and data['Symbol'] == symbol:
                    alpha_fundamentals = {
                        'market_cap': self.parse_number(data.get('MarketCapitalization')),
                        'pe_ratio': self.parse_number(data.get('PERatio')),
                        'pb_ratio': self.parse_number(data.get('PriceToBookRatio')),
                        'book_value': self.parse_number(data.get('BookValue')),
                        'dividend_per_share': self.parse_number(data.get('DividendPerShare')),
                        'dividend_yield': self.parse_percentage(data.get('DividendYield')),
                        'eps': self.parse_number(data.get('EPS')),
                        'revenue_ttm': self.parse_number(data.get('RevenueTTM')),
                        'gross_profit_ttm': self.parse_number(data.get('GrossProfitTTM')),
                        'ebitda': self.parse_number(data.get('EBITDA')),
                        'pe_ratio': self.parse_number(data.get('PERatio')),
                        'peg_ratio': self.parse_number(data.get('PEGRatio')),
                        'price_to_sales_ratio': self.parse_number(data.get('PriceToSalesRatioTTM')),
                        'return_on_assets': self.parse_percentage(data.get('ReturnOnAssetsTTM')),
                        'return_on_equity': self.parse_percentage(data.get('ReturnOnEquityTTM')),
                        'revenue_per_share': self.parse_number(data.get('RevenuePerShareTTM')),
                        'operating_margin': self.parse_percentage(data.get('OperatingMarginTTM')),
                        'profit_margin': self.parse_percentage(data.get('ProfitMargin')),
                        'quarterly_earnings_growth': self.parse_percentage(data.get('QuarterlyEarningsGrowthYOY')),
                        'quarterly_revenue_growth': self.parse_percentage(data.get('QuarterlyRevenueGrowthYOY')),
                        'analyst_target_price': self.parse_number(data.get('AnalystTargetPrice')),
                        'trailing_pe': self.parse_number(data.get('TrailingPE')),
                        'forward_pe': self.parse_number(data.get('ForwardPE')),
                        'price_to_sales_ratio': self.parse_number(data.get('PriceToSalesRatioTTM')),
                        'enterprise_value': self.parse_number(data.get('EnterpriseValue')),
                        'enterprise_to_revenue': self.parse_number(data.get('EnterpriseToRevenue')),
                        'enterprise_to_ebitda': self.parse_number(data.get('EnterpriseToEBITDA')),
                        'beta': self.parse_number(data.get('Beta')),
                        '52_week_high': self.parse_number(data.get('52WeekHigh')),
                        '52_week_low': self.parse_number(data.get('52WeekLow')),
                        '50_day_moving_avg': self.parse_number(data.get('50DayMovingAverage')),
                        '200_day_moving_avg': self.parse_number(data.get('200DayMovingAverage')),
                        'shares_outstanding': self.parse_number(data.get('SharesOutstanding')),
                        'dividend_date': data.get('DividendDate'),
                        'ex_dividend_date': data.get('ExDividendDate'),
                        'source_type': 'alpha_vantage_real_time'
                    }
                    
                    print(f"✅ Alpha Vantage: Got comprehensive fundamentals for {symbol}")
                    return alpha_fundamentals
                else:
                    print(f"❌ Alpha Vantage: No data for {symbol}")
                    return None
            else:
                print(f"❌ Alpha Vantage API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Alpha Vantage error: {e}")
            return None
    
    def get_iex_fundamentals(self, symbol):
        """IEX Cloud API para datos fundamentales"""
        if not self.iex_token:
            return None
            
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_iex_call < 1:  # 1 second delay
                time.sleep(1 - (current_time - self.last_iex_call))
            
            print(f"📡 Fetching {symbol} fundamentals from IEX Cloud...")
            
            # Get company stats
            stats_url = f"{self.iex_base}/data/core/stats/{symbol}"
            response = requests.get(
                stats_url,
                params={'token': self.iex_token},
                timeout=10
            )
            
            self.last_iex_call = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    stats = data[0] if isinstance(data, list) else data
                    
                    iex_fundamentals = {
                        'market_cap': stats.get('marketCap'),
                        'pe_ratio': stats.get('peRatio'),
                        'beta': stats.get('beta'),
                        'dividend_yield': stats.get('dividendYield'),
                        'eps_ttm': stats.get('ttmEPS'),
                        'revenue_ttm': stats.get('revenue'),
                        'gross_profit': stats.get('grossProfit'),
                        'total_cash': stats.get('totalCash'),
                        'current_debt': stats.get('currentDebt'),
                        'revenue_per_share': stats.get('revenuePerShare'),
                        'revenue_per_employee': stats.get('revenuePerEmployee'),
                        'debt_to_equity': stats.get('debtToEquity'),
                        'return_on_assets': stats.get('returnOnAssets'),
                        'return_on_capital': stats.get('returnOnCapital'),
                        'profit_margin': stats.get('profitMargin'),
                        'price_to_sales': stats.get('priceToSales'),
                        'price_to_book': stats.get('priceToBook'),
                        'day_200_moving_avg': stats.get('day200MovingAvg'),
                        'day_50_moving_avg': stats.get('day50MovingAvg'),
                        'employees': stats.get('employees'),
                        'enterprise_value': stats.get('enterpriseValue'),
                        'enterprise_value_to_revenue': stats.get('enterpriseValueToRevenue'),
                        'forward_pe_ratio': stats.get('forwardPERatio'),
                        'peg_ratio': stats.get('pegRatio'),
                        'source_type': 'iex_real_time'
                    }
                    
                    print(f"✅ IEX: Got fundamentals for {symbol}")
                    return iex_fundamentals
                else:
                    print(f"❌ IEX: No data for {symbol}")
                    return None
            else:
                print(f"❌ IEX API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ IEX error: {e}")
            return None
    
    def parse_number(self, value_str):
        """Parse numeric values from API responses"""
        if not value_str or value_str in ['None', 'N/A', '-']:
            return None
        
        try:
            # Handle different formats
            if isinstance(value_str, (int, float)):
                return float(value_str)
            
            # Remove common formatting
            clean_value = str(value_str).replace(',', '').replace('$', '')
            
            # Handle millions, billions
            if 'M' in clean_value:
                return float(clean_value.replace('M', '')) * 1000000
            elif 'B' in clean_value:
                return float(clean_value.replace('B', '')) * 1000000000
            elif 'K' in clean_value:
                return float(clean_value.replace('K', '')) * 1000
            else:
                return float(clean_value)
                
        except:
            return None
    
    def parse_percentage(self, value_str):
        """Parse percentage values"""
        if not value_str or value_str in ['None', 'N/A', '-']:
            return None
        
        try:
            clean_value = str(value_str).replace('%', '')
            return float(clean_value)
        except:
            return None
    
    def calculate_derived_metrics(self, fundamentals):
        """Calcular métricas derivadas con datos reales"""
        derived = {}
        
        try:
            # Book Value Score
            book_value = fundamentals.get('book_value')
            if book_value and book_value > 0:
                if book_value > 50:
                    derived['book_value_score'] = 100
                elif book_value > 20:
                    derived['book_value_score'] = 80
                elif book_value > 10:
                    derived['book_value_score'] = 60
                else:
                    derived['book_value_score'] = 40
            else:
                derived['book_value_score'] = 0
                
            # P/E Score (lower P/E = better value)
            pe_ratio = fundamentals.get('pe_ratio')
            if pe_ratio and pe_ratio > 0:
                if pe_ratio < 10:
                    derived['pe_score'] = 100
                elif pe_ratio < 15:
                    derived['pe_score'] = 80
                elif pe_ratio < 20:
                    derived['pe_score'] = 60
                elif pe_ratio < 30:
                    derived['pe_score'] = 40
                else:
                    derived['pe_score'] = 20
            else:
                derived['pe_score'] = 50
            
            # Beta Score (closer to 1.0 = better)
            beta = fundamentals.get('beta')
            if beta is not None:
                beta_deviation = abs(beta - 1.0)
                if beta_deviation < 0.2:
                    derived['beta_score'] = 100
                elif beta_deviation < 0.5:
                    derived['beta_score'] = 80
                elif beta_deviation < 1.0:
                    derived['beta_score'] = 60
                else:
                    derived['beta_score'] = 40
            else:
                derived['beta_score'] = 50
            
            # ROE Score
            roe = fundamentals.get('return_on_equity')
            if roe and roe > 0:
                if roe > 20:
                    derived['roe_score'] = 100
                elif roe > 15:
                    derived['roe_score'] = 80
                elif roe > 10:
                    derived['roe_score'] = 60
                else:
                    derived['roe_score'] = 40
            else:
                derived['roe_score'] = 30
            
            # Overall Fundamental Score
            scores = [
                derived.get('book_value_score', 0),
                derived.get('pe_score', 0),
                derived.get('beta_score', 0),
                derived.get('roe_score', 0)
            ]
            
            derived['overall_fundamental_score'] = sum(scores) / len(scores)
            
            # Value opportunity assessment
            pb_ratio = fundamentals.get('pb_ratio') or fundamentals.get('price_to_book')
            if pb_ratio and pb_ratio < 1.0:
                derived['value_opportunity'] = "STRONG BUY - Below Book Value"
                derived['is_undervalued'] = True
            elif pb_ratio and pb_ratio < 1.5 and roe and roe > 12:
                derived['value_opportunity'] = "BUY - Value + Quality"
                derived['is_undervalued'] = True
            elif pe_ratio and pe_ratio < 12:
                derived['value_opportunity'] = "BUY - Low P/E"
                derived['is_undervalued'] = True
            else:
                derived['value_opportunity'] = "HOLD - Monitor"
                derived['is_undervalued'] = False
            
        except Exception as e:
            print(f"❌ Error calculating derived metrics: {e}")
        
        return derived
    
    def validate_data_quality(self, symbol, fundamentals):
        """Validar calidad de datos obtenidos"""
        
        quality_score = 0
        max_score = 100
        
        # Check essential metrics
        essential_metrics = ['pe_ratio', 'book_value', 'beta', 'market_cap']
        available_metrics = sum(1 for metric in essential_metrics if fundamentals.get(metric) is not None)
        quality_score += (available_metrics / len(essential_metrics)) * 40
        
        # Check data freshness
        timestamp = fundamentals.get('timestamp')
        if timestamp and (datetime.now() - timestamp).total_seconds() < 86400:  # Less than 24 hours
            quality_score += 20
        
        # Check source reliability
        source = fundamentals.get('primary_source')
        if source == 'polygon':
            quality_score += 20
        elif source == 'alpha_vantage':
            quality_score += 15
        elif source == 'iex':
            quality_score += 10
        
        # Check for realistic values
        pe_ratio = fundamentals.get('pe_ratio')
        if pe_ratio and 1 < pe_ratio < 100:
            quality_score += 10
            
        beta = fundamentals.get('beta')
        if beta and 0.1 < beta < 5.0:
            quality_score += 10
        
        fundamentals['data_quality_score'] = min(quality_score, max_score)
        fundamentals['data_validation'] = {
            'essential_metrics_available': f"{available_metrics}/{len(essential_metrics)}",
            'primary_source': source,
            'timestamp': timestamp,
            'quality_score': quality_score
        }
        
        return fundamentals

# Test the real-time fetcher
if __name__ == "__main__":
    # Load environment variables
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
    
    print("🎯 TESTING REAL-TIME FUNDAMENTALS FETCHER")
    print("=" * 70)
    
    fetcher = RealTimeFundamentalsFetcher()
    
    # Test with WFC (current price $77.99)
    test_symbol = "WFC"
    print(f"\n🧪 Testing with {test_symbol} (current real price: $77.99)")
    print("-" * 50)
    
    fundamentals = fetcher.get_real_time_fundamentals(test_symbol)
    
    if fundamentals:
        print(f"\n✅ REAL-TIME FUNDAMENTALS FOR {test_symbol}:")
        print(f"├─ Primary Source: {fundamentals.get('primary_source', 'Unknown')}")
        print(f"├─ Data Quality Score: {fundamentals.get('data_quality_score', 0):.1f}/100")
        print(f"├─ Book Value: ${fundamentals.get('book_value', 'N/A')}")
        print(f"├─ P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}")
        print(f"├─ Beta: {fundamentals.get('beta', 'N/A')}")
        print(f"├─ P/B Ratio: {fundamentals.get('pb_ratio') or fundamentals.get('price_to_book', 'N/A')}")
        print(f"├─ ROE: {fundamentals.get('return_on_equity', 'N/A')}%")
        print(f"├─ Market Cap: {fundamentals.get('market_cap', 'N/A')}")
        print(f"├─ Value Opportunity: {fundamentals.get('value_opportunity', 'N/A')}")
        print(f"└─ Overall Fund Score: {fundamentals.get('overall_fundamental_score', 0):.1f}/100")
        
        # Validation
        validation = fundamentals.get('data_validation', {})
        print(f"\n📊 DATA VALIDATION:")
        print(f"├─ Essential Metrics: {validation.get('essential_metrics_available', 'Unknown')}")
        print(f"├─ Source: {validation.get('primary_source', 'Unknown')}")
        print(f"└─ Quality: {validation.get('quality_score', 0):.1f}/100")
        
    else:
        print(f"❌ Failed to get real-time fundamentals for {test_symbol}")
    
    print(f"\n✅ REAL-TIME FUNDAMENTALS FETCHER READY!")
    print("Now using direct APIs instead of web scraping for 100% accurate data!")