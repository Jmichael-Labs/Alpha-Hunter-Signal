#!/usr/bin/env python3
"""
🌐 WEB SCRAPER REAL DATA
Scraping directo de MarketWatch, FinViz, Yahoo Finance
Para obtener datos 100% actuales y precisos
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import random
from datetime import datetime
import json

class WebScraperRealData:
    """Web scraper para datos financieros en tiempo real"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Headers realistas para evitar bloqueos
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        self.session.headers.update(self.headers)
        
        print("🌐 Web Scraper Real Data initialized")
        print("├─ MarketWatch.com: Ready")
        print("├─ FinViz.com: Ready")
        print("└─ YahooFinance.com: Ready")
    
    def get_marketwatch_data(self, symbol):
        """Scraping de MarketWatch para precio actual y datos básicos"""
        try:
            print(f"🔍 Scraping MarketWatch for {symbol}...")
            
            # Rate limiting
            time.sleep(random.uniform(2.0, 4.0))
            
            url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            marketwatch_data = {
                'symbol': symbol,
                'source': 'marketwatch',
                'timestamp': datetime.now()
            }
            
            # Precio actual - múltiples selectores posibles
            price_selectors = [
                'bg-quote.value',
                '.intraday__price .value',
                '[data-module="Quote"] .value',
                '.quote-val'
            ]
            
            current_price = None
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text().strip()
                    current_price = self.parse_price(price_text)
                    if current_price:
                        break
            
            if current_price:
                marketwatch_data['current_price'] = current_price
                print(f"✅ MarketWatch: {symbol} price ${current_price:.2f}")
            else:
                print(f"❌ MarketWatch: Could not find price for {symbol}")
                return None
            
            # Volumen
            volume_element = soup.select_one('.kv__item .kv__primary:contains("Volume")')
            if volume_element:
                volume_text = volume_element.find_next_sibling().get_text().strip()
                marketwatch_data['volume'] = self.parse_volume(volume_text)
            
            # Market Cap
            market_cap_element = soup.select_one('.kv__item .kv__primary:contains("Market Cap")')
            if market_cap_element:
                market_cap_text = market_cap_element.find_next_sibling().get_text().strip()
                marketwatch_data['market_cap'] = self.parse_market_cap(market_cap_text)
            
            # P/E Ratio
            pe_element = soup.select_one('.kv__item .kv__primary:contains("P/E Ratio")')
            if pe_element:
                pe_text = pe_element.find_next_sibling().get_text().strip()
                marketwatch_data['pe_ratio'] = self.parse_number(pe_text)
            
            return marketwatch_data
            
        except Exception as e:
            print(f"❌ MarketWatch error for {symbol}: {e}")
            return None
    
    def get_finviz_data(self, symbol):
        """Scraping de FinViz para datos fundamentales detallados"""
        try:
            print(f"🔍 Scraping FinViz for {symbol}...")
            
            # Rate limiting más agresivo para FinViz
            time.sleep(random.uniform(3.0, 6.0))
            
            url = f"https://finviz.com/quote.ashx?t={symbol.upper()}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            finviz_data = {
                'symbol': symbol,
                'source': 'finviz',
                'timestamp': datetime.now()
            }
            
            # Encontrar tabla de fundamentales
            fundamental_table = soup.find('table', {'class': 'snapshot-table2'})
            
            if fundamental_table:
                rows = fundamental_table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    
                    for i in range(0, len(cells), 2):
                        if i + 1 < len(cells):
                            metric = cells[i].get_text().strip()
                            value = cells[i + 1].get_text().strip()
                            
                            # Mapear métricas clave
                            if 'Market Cap' in metric:
                                finviz_data['market_cap'] = self.parse_market_cap(value)
                            elif 'Income' in metric:
                                finviz_data['income'] = self.parse_market_cap(value)
                            elif 'Sales' in metric:
                                finviz_data['sales'] = self.parse_market_cap(value)
                            elif 'Book/sh' in metric:
                                finviz_data['book_value'] = self.parse_number(value)
                            elif 'Cash/sh' in metric:
                                finviz_data['cash_per_share'] = self.parse_number(value)
                            elif 'P/E' in metric and 'Forward' not in metric:
                                finviz_data['pe_ratio'] = self.parse_number(value)
                            elif 'Forward P/E' in metric:
                                finviz_data['forward_pe'] = self.parse_number(value)
                            elif 'PEG' in metric:
                                finviz_data['peg_ratio'] = self.parse_number(value)
                            elif 'P/S' in metric:
                                finviz_data['ps_ratio'] = self.parse_number(value)
                            elif 'P/B' in metric:
                                finviz_data['pb_ratio'] = self.parse_number(value)
                            elif 'P/C' in metric:
                                finviz_data['pc_ratio'] = self.parse_number(value)
                            elif 'P/FCF' in metric:
                                finviz_data['pfcf_ratio'] = self.parse_number(value)
                            elif 'Debt/Eq' in metric:
                                finviz_data['debt_equity'] = self.parse_number(value)
                            elif 'EPS (ttm)' in metric:
                                finviz_data['eps_ttm'] = self.parse_number(value)
                            elif 'EPS next Y' in metric:
                                finviz_data['eps_next_year'] = self.parse_number(value)
                            elif 'EPS next Q' in metric:
                                finviz_data['eps_next_quarter'] = self.parse_number(value)
                            elif 'EPS this Y' in metric:
                                finviz_data['eps_this_year'] = self.parse_percentage(value)
                            elif 'EPS next Y' in metric:
                                finviz_data['eps_growth_next_year'] = self.parse_percentage(value)
                            elif 'EPS past 5Y' in metric:
                                finviz_data['eps_growth_5y'] = self.parse_percentage(value)
                            elif 'Sales past 5Y' in metric:
                                finviz_data['sales_growth_5y'] = self.parse_percentage(value)
                            elif 'Sales Q/Q' in metric:
                                finviz_data['sales_growth_qq'] = self.parse_percentage(value)
                            elif 'EPS Q/Q' in metric:
                                finviz_data['eps_growth_qq'] = self.parse_percentage(value)
                            elif 'Insider Own' in metric:
                                finviz_data['insider_ownership'] = self.parse_percentage(value)
                            elif 'Insider Trans' in metric:
                                finviz_data['insider_transactions'] = self.parse_percentage(value)
                            elif 'Inst Own' in metric:
                                finviz_data['institutional_ownership'] = self.parse_percentage(value)
                            elif 'Inst Trans' in metric:
                                finviz_data['institutional_transactions'] = self.parse_percentage(value)
                            elif 'ROA' in metric:
                                finviz_data['roa'] = self.parse_percentage(value)
                            elif 'ROE' in metric:
                                finviz_data['roe'] = self.parse_percentage(value)
                            elif 'ROI' in metric:
                                finviz_data['roi'] = self.parse_percentage(value)
                            elif 'Gross M' in metric:
                                finviz_data['gross_margin'] = self.parse_percentage(value)
                            elif 'Oper M' in metric:
                                finviz_data['operating_margin'] = self.parse_percentage(value)
                            elif 'Profit M' in metric:
                                finviz_data['profit_margin'] = self.parse_percentage(value)
                            elif 'Payout' in metric:
                                finviz_data['payout_ratio'] = self.parse_percentage(value)
                            elif 'Shs Outstand' in metric:
                                finviz_data['shares_outstanding'] = self.parse_market_cap(value)
                            elif 'Shs Float' in metric:
                                finviz_data['shares_float'] = self.parse_market_cap(value)
                            elif 'Short Float' in metric:
                                finviz_data['short_float'] = self.parse_percentage(value)
                            elif 'Short Ratio' in metric:
                                finviz_data['short_ratio'] = self.parse_number(value)
                            elif 'Target Price' in metric:
                                finviz_data['target_price'] = self.parse_number(value)
                            elif '52W Range' in metric:
                                range_parts = value.split(' - ')
                                if len(range_parts) == 2:
                                    finviz_data['52w_low'] = self.parse_number(range_parts[0])
                                    finviz_data['52w_high'] = self.parse_number(range_parts[1])
                            elif 'Beta' in metric:
                                finviz_data['beta'] = self.parse_number(value)
                            elif 'ATR' in metric:
                                finviz_data['atr'] = self.parse_number(value)
                            elif 'Volatility' in metric:
                                volatility_parts = value.split()
                                if len(volatility_parts) >= 2:
                                    finviz_data['volatility_week'] = self.parse_percentage(volatility_parts[0])
                                    finviz_data['volatility_month'] = self.parse_percentage(volatility_parts[1])
                            elif 'RSI (14)' in metric:
                                finviz_data['rsi'] = self.parse_number(value)
                            elif 'Rel Volume' in metric:
                                finviz_data['relative_volume'] = self.parse_number(value)
                            elif 'Avg Volume' in metric:
                                finviz_data['avg_volume'] = self.parse_market_cap(value)
                            elif 'Volume' in metric:
                                finviz_data['volume'] = self.parse_market_cap(value)
                            elif 'Perf Week' in metric:
                                finviz_data['performance_week'] = self.parse_percentage(value)
                            elif 'Perf Month' in metric:
                                finviz_data['performance_month'] = self.parse_percentage(value)
                            elif 'Perf Quarter' in metric:
                                finviz_data['performance_quarter'] = self.parse_percentage(value)
                            elif 'Perf Half Y' in metric:
                                finviz_data['performance_half_year'] = self.parse_percentage(value)
                            elif 'Perf Year' in metric:
                                finviz_data['performance_year'] = self.parse_percentage(value)
                            elif 'Perf YTD' in metric:
                                finviz_data['performance_ytd'] = self.parse_percentage(value)
                            elif 'SMA20' in metric:
                                finviz_data['sma_20'] = self.parse_percentage(value)
                            elif 'SMA50' in metric:
                                finviz_data['sma_50'] = self.parse_percentage(value)
                            elif 'SMA200' in metric:
                                finviz_data['sma_200'] = self.parse_percentage(value)
                            elif '50-Day High' in metric:
                                finviz_data['high_50d'] = self.parse_percentage(value)
                            elif '50-Day Low' in metric:
                                finviz_data['low_50d'] = self.parse_percentage(value)
                            elif 'Earnings' in metric:
                                finviz_data['earnings_date'] = value
                            elif 'Dividend' in metric and '%' in value:
                                finviz_data['dividend_yield'] = self.parse_percentage(value.replace('%', ''))
                            elif 'Ex-Dividend' in metric:
                                finviz_data['ex_dividend_date'] = value
                
                print(f"✅ FinViz: Got {len(finviz_data)} metrics for {symbol}")
                return finviz_data
            else:
                print(f"❌ FinViz: Could not find fundamental table for {symbol}")
                return None
                
        except Exception as e:
            print(f"❌ FinViz error for {symbol}: {e}")
            return None
    
    def get_yahoo_finance_data(self, symbol):
        """Scraping de Yahoo Finance para datos complementarios"""
        try:
            print(f"🔍 Scraping Yahoo Finance for {symbol}...")
            
            # Rate limiting
            time.sleep(random.uniform(1.5, 3.0))
            
            url = f"https://finance.yahoo.com/quote/{symbol.upper()}"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            yahoo_data = {
                'symbol': symbol,
                'source': 'yahoo_finance',
                'timestamp': datetime.now()
            }
            
            # Precio actual
            price_element = soup.select_one('[data-symbol="{}"] [data-field="regularMarketPrice"]'.format(symbol.upper()))
            if not price_element:
                price_element = soup.select_one('[data-testid="qsp-price"]')
            if not price_element:
                price_element = soup.select_one('.Fw\(b\).Fz\(36px\).Mb\(-4px\).D\(ib\)')
            
            if price_element:
                price_text = price_element.get_text().strip()
                yahoo_data['current_price'] = self.parse_price(price_text)
            
            # Datos de la tabla de estadísticas
            stats_table = soup.find('table', {'data-test': 'left-summary-table'})
            if stats_table:
                rows = stats_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        metric = cells[0].get_text().strip()
                        value = cells[1].get_text().strip()
                        
                        if 'Market Cap' in metric:
                            yahoo_data['market_cap'] = self.parse_market_cap(value)
                        elif 'Trailing P/E' in metric:
                            yahoo_data['pe_ratio'] = self.parse_number(value)
                        elif 'Forward P/E' in metric:
                            yahoo_data['forward_pe'] = self.parse_number(value)
                        elif 'PEG Ratio' in metric:
                            yahoo_data['peg_ratio'] = self.parse_number(value)
                        elif 'Price/Sales' in metric:
                            yahoo_data['ps_ratio'] = self.parse_number(value)
                        elif 'Price/Book' in metric:
                            yahoo_data['pb_ratio'] = self.parse_number(value)
                        elif 'Enterprise Value' in metric:
                            yahoo_data['enterprise_value'] = self.parse_market_cap(value)
                        elif 'Beta' in metric:
                            yahoo_data['beta'] = self.parse_number(value)
                        elif 'EPS' in metric:
                            yahoo_data['eps'] = self.parse_number(value)
                        elif 'Dividend Yield' in metric:
                            yahoo_data['dividend_yield'] = self.parse_percentage(value)
                        elif 'Ex-Dividend' in metric:
                            yahoo_data['ex_dividend_date'] = value
                        elif '52 Week Range' in metric:
                            range_parts = value.split(' - ')
                            if len(range_parts) == 2:
                                yahoo_data['52w_low'] = self.parse_number(range_parts[0])
                                yahoo_data['52w_high'] = self.parse_number(range_parts[1])
                        elif 'Volume' in metric:
                            yahoo_data['volume'] = self.parse_volume(value)
                        elif 'Avg Volume' in metric:
                            yahoo_data['avg_volume'] = self.parse_volume(value)
            
            print(f"✅ Yahoo Finance: Got data for {symbol}")
            return yahoo_data
            
        except Exception as e:
            print(f"❌ Yahoo Finance error for {symbol}: {e}")
            return None
    
    def parse_price(self, price_text):
        """Parse precio de texto"""
        try:
            # Remover caracteres no numéricos excepto punto y comas
            clean_price = re.sub(r'[^\d.,]', '', price_text)
            # Reemplazar comas por nada (formato US)
            clean_price = clean_price.replace(',', '')
            return float(clean_price)
        except:
            return None
    
    def parse_number(self, value_text):
        """Parse número general"""
        try:
            if value_text in ['-', 'N/A', '', 'None']:
                return None
            
            # Remover caracteres especiales
            clean_value = re.sub(r'[^\d.,-]', '', value_text)
            clean_value = clean_value.replace(',', '')
            return float(clean_value)
        except:
            return None
    
    def parse_percentage(self, value_text):
        """Parse porcentaje"""
        try:
            if value_text in ['-', 'N/A', '', 'None']:
                return None
            
            # Remover % y convertir
            clean_value = value_text.replace('%', '').strip()
            clean_value = re.sub(r'[^\d.,-]', '', clean_value)
            return float(clean_value)
        except:
            return None
    
    def parse_volume(self, volume_text):
        """Parse volumen con K, M, B"""
        try:
            if volume_text in ['-', 'N/A', '', 'None']:
                return None
                
            volume_text = volume_text.upper().strip()
            
            # Extraer número base
            number_part = re.findall(r'[\d.,]+', volume_text)[0]
            number = float(number_part.replace(',', ''))
            
            # Aplicar multiplicador
            if 'K' in volume_text:
                return int(number * 1000)
            elif 'M' in volume_text:
                return int(number * 1000000)
            elif 'B' in volume_text:
                return int(number * 1000000000)
            else:
                return int(number)
        except:
            return None
    
    def parse_market_cap(self, market_cap_text):
        """Parse market cap con K, M, B, T"""
        try:
            if market_cap_text in ['-', 'N/A', '', 'None']:
                return None
                
            market_cap_text = market_cap_text.upper().strip()
            
            # Extraer número base
            number_match = re.search(r'[\d.,]+', market_cap_text)
            if not number_match:
                return None
                
            number = float(number_match.group().replace(',', ''))
            
            # Aplicar multiplicador
            if 'K' in market_cap_text:
                return number * 1000
            elif 'M' in market_cap_text:
                return number * 1000000
            elif 'B' in market_cap_text:
                return number * 1000000000
            elif 'T' in market_cap_text:
                return number * 1000000000000
            else:
                return number
        except:
            return None
    
    def get_comprehensive_data(self, symbol):
        """Obtener datos completos de todas las fuentes web"""
        
        print(f"🌐 Getting comprehensive web data for {symbol}")
        print("-" * 50)
        
        comprehensive_data = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'sources': []
        }
        
        # 1. MarketWatch (precio principal)
        marketwatch_data = self.get_marketwatch_data(symbol)
        if marketwatch_data:
            comprehensive_data.update(marketwatch_data)
            comprehensive_data['sources'].append('marketwatch')
            comprehensive_data['primary_price_source'] = 'marketwatch'
        
        # 2. FinViz (fundamentales detallados)
        finviz_data = self.get_finviz_data(symbol)
        if finviz_data:
            # Merge data, preservando precios de MarketWatch
            for key, value in finviz_data.items():
                if key not in comprehensive_data or key in ['book_value', 'pe_ratio', 'pb_ratio', 'beta', 'roe']:
                    comprehensive_data[key] = value
            comprehensive_data['sources'].append('finviz')
        
        # 3. Yahoo Finance (datos complementarios)
        yahoo_data = self.get_yahoo_finance_data(symbol)
        if yahoo_data:
            # Merge data como backup
            for key, value in yahoo_data.items():
                if key not in comprehensive_data or comprehensive_data[key] is None:
                    comprehensive_data[key] = value
            comprehensive_data['sources'].append('yahoo_finance')
        
        # 4. Calculate derived metrics
        comprehensive_data.update(self.calculate_quality_metrics(comprehensive_data))
        
        return comprehensive_data
    
    def calculate_quality_metrics(self, data):
        """Calcular métricas de calidad y derived values"""
        
        quality_metrics = {}
        
        try:
            # Data completeness score
            essential_fields = ['current_price', 'book_value', 'pe_ratio', 'beta', 'market_cap']
            available_fields = sum(1 for field in essential_fields if data.get(field) is not None)
            quality_metrics['data_completeness'] = (available_fields / len(essential_fields)) * 100
            
            # Source reliability score
            sources = data.get('sources', [])
            source_scores = {'marketwatch': 30, 'finviz': 35, 'yahoo_finance': 25}
            total_source_score = sum(source_scores.get(source, 0) for source in sources)
            quality_metrics['source_reliability'] = min(total_source_score, 100)
            
            # Calculate P/B if missing but have price and book value
            current_price = data.get('current_price')
            book_value = data.get('book_value')
            
            if current_price and book_value and not data.get('pb_ratio'):
                quality_metrics['pb_ratio_calculated'] = current_price / book_value
            
            # Value assessment
            pb_ratio = data.get('pb_ratio') or quality_metrics.get('pb_ratio_calculated')
            pe_ratio = data.get('pe_ratio')
            
            if pb_ratio and pb_ratio < 1.0:
                quality_metrics['value_assessment'] = "STRONG BUY - Below Book Value"
                quality_metrics['is_undervalued'] = True
            elif pb_ratio and pb_ratio < 1.5 and pe_ratio and pe_ratio < 15:
                quality_metrics['value_assessment'] = "BUY - Value Play"
                quality_metrics['is_undervalued'] = True
            elif pe_ratio and pe_ratio < 12:
                quality_metrics['value_assessment'] = "BUY - Low P/E"
                quality_metrics['is_undervalued'] = True
            else:
                quality_metrics['value_assessment'] = "HOLD - Monitor"
                quality_metrics['is_undervalued'] = False
            
            # Overall quality score
            quality_metrics['overall_quality_score'] = (
                quality_metrics['data_completeness'] * 0.6 +
                quality_metrics['source_reliability'] * 0.4
            )
            
        except Exception as e:
            print(f"❌ Error calculating quality metrics: {e}")
            quality_metrics['error'] = str(e)
        
        return quality_metrics

# Test the web scraper
if __name__ == "__main__":
    print("🌐 TESTING WEB SCRAPER REAL DATA")
    print("=" * 70)
    
    scraper = WebScraperRealData()
    
    # Test with WFC
    test_symbol = "WFC"
    print(f"\n🧪 Testing comprehensive scraping for {test_symbol}")
    print("Expected: Real price ~$77.99")
    print("-" * 50)
    
    data = scraper.get_comprehensive_data(test_symbol)
    
    if data:
        print(f"\n✅ COMPREHENSIVE WEB DATA FOR {test_symbol}:")
        print(f"├─ Sources: {', '.join(data.get('sources', []))}")
        print(f"├─ Current Price: ${data.get('current_price', 'N/A'):.2f}" if data.get('current_price') else "├─ Current Price: N/A")
        print(f"├─ Book Value: ${data.get('book_value', 'N/A')}" if data.get('book_value') else "├─ Book Value: N/A")
        print(f"├─ P/E Ratio: {data.get('pe_ratio', 'N/A')}")
        print(f"├─ P/B Ratio: {data.get('pb_ratio', 'N/A')}")
        print(f"├─ Beta: {data.get('beta', 'N/A')}")
        print(f"├─ ROE: {data.get('roe', 'N/A')}%")
        print(f"├─ Market Cap: ${data.get('market_cap', 'N/A'):,.0f}" if data.get('market_cap') else "├─ Market Cap: N/A")
        print(f"├─ Value Assessment: {data.get('value_assessment', 'N/A')}")
        print(f"├─ Data Quality: {data.get('overall_quality_score', 0):.1f}/100")
        print(f"└─ Completeness: {data.get('data_completeness', 0):.1f}%")
        
        # Check if WFC price is correct
        current_price = data.get('current_price')
        if current_price and 77 <= current_price <= 80:
            print(f"\n✅ PRICE VALIDATION PASSED!")
            print(f"Expected ~$77.99, Got ${current_price:.2f} ✅")
        else:
            print(f"\n⚠️ Price validation: Expected ~$77.99, Got ${current_price:.2f}")
            
    else:
        print(f"❌ Failed to get comprehensive data for {test_symbol}")
    
    print(f"\n✅ WEB SCRAPER REAL DATA READY!")
    print("Now getting 100% current data from live websites!")