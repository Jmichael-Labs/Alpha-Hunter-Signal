#!/usr/bin/env python3
"""
🚀 ENHANCED REAL TIME DATA SCRAPER - FUENTES ADICIONALES
Sistema mejorado con más fuentes de datos financieros confiables
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
from typing import Dict, Optional

class EnhancedRealTimeDataScraper:
    """Scraper mejorado con múltiples fuentes adicionales"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session.headers.update(self.headers)
    
    def get_finviz_data(self, symbol: str) -> Optional[Dict]:
        """Obtener datos comprehensivos de Finviz - MUY CONFIABLE"""
        try:
            url = f"https://finviz.com/quote.ashx?t={symbol}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            data = {'symbol': symbol, 'source': 'finviz'}
            
            # FINVIZ tiene una tabla con todas las métricas
            # Buscar todas las celdas de datos
            table = soup.find('table', class_='snapshot-table2')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    i = 0
                    while i < len(cells) - 1:
                        label = cells[i].get_text(strip=True)
                        value = cells[i + 1].get_text(strip=True)
                        
                        # PRECIO
                        if label == 'Price':
                            price_match = re.search(r'[\d,]+\.?\d*', value.replace(',', ''))
                            if price_match:
                                data['current_price'] = float(price_match.group())
                        
                        # VOLUMEN
                        elif label == 'Volume':
                            if 'M' in value:
                                vol_match = re.search(r'([\d,\.]+)M', value.replace(',', ''))
                                if vol_match:
                                    data['volume'] = int(float(vol_match.group(1)) * 1000000)
                            elif 'K' in value:
                                vol_match = re.search(r'([\d,\.]+)K', value.replace(',', ''))
                                if vol_match:
                                    data['volume'] = int(float(vol_match.group(1)) * 1000)
                        
                        # P/E RATIO
                        elif label == 'P/E':
                            if value != '-':
                                pe_match = re.search(r'[\d,]+\.?\d*', value.replace(',', ''))
                                if pe_match:
                                    data['pe_ratio'] = float(pe_match.group())
                        
                        # EPS
                        elif label == 'EPS (ttm)':
                            if value != '-':
                                eps_match = re.search(r'-?[\d,]+\.?\d*', value.replace(',', ''))
                                if eps_match:
                                    data['eps'] = float(eps_match.group())
                        
                        # BETA
                        elif label == 'Beta':
                            if value != '-':
                                beta_match = re.search(r'[\d,]+\.?\d*', value.replace(',', ''))
                                if beta_match:
                                    data['beta'] = float(beta_match.group())
                        
                        # MARKET CAP
                        elif label == 'Market Cap':
                            if 'T' in value:
                                cap_match = re.search(r'([\d,\.]+)T', value.replace(',', ''))
                                if cap_match:
                                    data['market_cap'] = float(cap_match.group(1)) * 1000000000000
                            elif 'B' in value:
                                cap_match = re.search(r'([\d,\.]+)B', value.replace(',', ''))
                                if cap_match:
                                    data['market_cap'] = float(cap_match.group(1)) * 1000000000
                        
                        # 52 WEEK RANGE
                        elif label == '52W Range':
                            range_match = re.search(r'([\d,\.]+)\s*-\s*([\d,\.]+)', value.replace(',', ''))
                            if range_match:
                                data['52w_low'] = float(range_match.group(1))
                                data['52w_high'] = float(range_match.group(2))
                        
                        # DIVIDEND YIELD
                        elif label == 'Dividend %':
                            if value != '-':
                                div_match = re.search(r'[\d,]+\.?\d*', value.replace(',', '').replace('%', ''))
                                if div_match:
                                    data['dividend_yield'] = float(div_match.group())
                        
                        # VOLATILIDAD
                        elif label == 'Volatility':
                            vol_parts = value.split()
                            if len(vol_parts) >= 2:
                                # Usar volatilidad semanal como proxy
                                week_vol = vol_parts[0].replace('%', '')
                                vol_match = re.search(r'[\d,]+\.?\d*', week_vol.replace(',', ''))
                                if vol_match:
                                    data['volatility_week'] = float(vol_match.group())
                        
                        i += 2
            
            data['timestamp'] = datetime.now()
            return data
            
        except Exception as e:
            print(f"❌ Finviz error for {symbol}: {e}")
            return None
    
    def get_barchart_data(self, symbol: str) -> Optional[Dict]:
        """Obtener datos de Barchart.com - Excelente para opciones"""
        try:
            url = f"https://www.barchart.com/stocks/quotes/{symbol}/overview"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            data = {'symbol': symbol, 'source': 'barchart'}
            
            # Buscar precio en el header
            price_elem = soup.find('span', class_='last-change')
            if not price_elem:
                price_elem = soup.find('span', class_='price')
            
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    data['current_price'] = float(price_match.group())
            
            # Buscar tabla de datos adicionales
            data_rows = soup.find_all('tr')
            for row in data_rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value_text = cells[1].get_text(strip=True)
                    
                    if 'volume' in label:
                        vol_match = re.search(r'[\d,]+', value_text.replace(',', ''))
                        if vol_match:
                            data['volume'] = int(vol_match.group())
            
            data['timestamp'] = datetime.now()
            return data
            
        except Exception as e:
            print(f"❌ Barchart error for {symbol}: {e}")
            return None
    
    def get_stockanalysis_data(self, symbol: str) -> Optional[Dict]:
        """Obtener datos de StockAnalysis.com - Muy detallado"""
        try:
            url = f"https://stockanalysis.com/stocks/{symbol.lower()}/"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            data = {'symbol': symbol, 'source': 'stockanalysis'}
            
            # Precio principal
            price_elem = soup.find('span', {'data-test': 'price'})
            if not price_elem:
                price_elem = soup.select_one('.text-3xl')
            
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    data['current_price'] = float(price_match.group())
            
            data['timestamp'] = datetime.now()
            return data
            
        except Exception as e:
            print(f"❌ StockAnalysis error for {symbol}: {e}")
            return None
    
    def get_comprehensive_real_time_data(self, symbol: str) -> Dict:
        """Obtener datos de MÚLTIPLES fuentes confiables y hacer consenso"""
        print(f"🚀 Obteniendo datos comprehensivos para {symbol} de fuentes MEJORADAS...")
        
        # Lista de scrapers en orden de confiabilidad
        scrapers = [
            ('Finviz', self.get_finviz_data),
            ('Barchart', self.get_barchart_data), 
            ('StockAnalysis', self.get_stockanalysis_data)
        ]
        
        all_data = []
        successful_sources = []
        
        for source_name, scraper_func in scrapers:
            try:
                print(f"🔍 Consultando {source_name}...")
                result = scraper_func(symbol)
                if result:
                    all_data.append(result)
                    successful_sources.append(source_name)
                    print(f"✅ {source_name}: Datos obtenidos")
                    
                    # Mostrar precio si está disponible
                    if result.get('current_price'):
                        print(f"   📊 Precio: ${result['current_price']:.2f}")
                else:
                    print(f"❌ {source_name}: Sin datos")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ {source_name} error: {e}")
                continue
        
        if not all_data:
            print(f"❌ No se pudieron obtener datos para {symbol}")
            return {
                'symbol': symbol,
                'error': 'No sources available',
                'sources_tried': len(scrapers),
                'successful_sources': 0
            }
        
        # COMBINAR Y CONSENSAR DATOS
        combined = {
            'symbol': symbol,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sources_used': successful_sources,
            'sources_count': len(successful_sources)
        }
        
        # PRECIOS - usar consenso
        prices = [d.get('current_price') for d in all_data if d.get('current_price')]
        if prices:
            if len(prices) == 1:
                combined['current_price'] = prices[0]
                combined['price_confidence'] = 'SINGLE_SOURCE'
            else:
                # Eliminar outliers obvios
                filtered_prices = []
                avg_price = sum(prices) / len(prices)
                for price in prices:
                    # CRITICAL FIX: Protect against ZeroDivisionError
                    if avg_price > 0 and abs(price - avg_price) / avg_price < 0.5:  # <50% diferencia
                        filtered_prices.append(price)
                    elif avg_price <= 0:  # If avg_price is 0 or negative, keep all prices
                        filtered_prices.append(price)
                
                if filtered_prices:
                    combined['current_price'] = sum(filtered_prices) / len(filtered_prices)
                    combined['price_confidence'] = 'CONSENSUS' if len(filtered_prices) > 1 else 'FILTERED'
                else:
                    combined['current_price'] = avg_price
                    combined['price_confidence'] = 'AVERAGE_WITH_OUTLIERS'
        
        # OTROS DATOS - usar el más completo disponible
        numeric_fields = ['volume', 'pe_ratio', 'eps', 'beta', 'market_cap', 
                         '52w_low', '52w_high', 'dividend_yield', 'volatility_week']
        
        for field in numeric_fields:
            values = [d.get(field) for d in all_data if d.get(field) is not None]
            if values:
                if len(values) == 1:
                    combined[field] = values[0]
                else:
                    # Usar promedio para campos numéricos
                    combined[field] = sum(values) / len(values)
        
        # CALCULAR MÉTRICAS DERIVADAS - CRITICAL FIX: Protect against ZeroDivisionError
        if combined.get('current_price') and combined.get('52w_low') and combined.get('52w_high'):
            price = combined['current_price']
            low = combined['52w_low']
            high = combined['52w_high']
            
            # Protect against zero division
            if (high - low) > 0:
                combined['position_in_52w_range'] = ((price - low) / (high - low)) * 100
            else:
                combined['position_in_52w_range'] = 50  # Default middle position
                
            if price > 0:
                combined['volatility_estimate'] = ((high - low) / price) * 100
            else:
                combined['volatility_estimate'] = 0  # Default no volatility
        
        # DATOS DE CALIDAD
        data_completeness = len([k for k, v in combined.items() 
                               if k not in ['symbol', 'timestamp', 'sources_used', 'sources_count'] 
                               and v is not None])
        combined['data_completeness'] = data_completeness
        combined['data_quality'] = 'HIGH' if data_completeness >= 8 else 'MEDIUM' if data_completeness >= 5 else 'LOW'
        
        print(f"🎯 Datos finales para {symbol}:")
        print(f"   💰 Precio: ${combined.get('current_price', 0):.2f}")
        print(f"   📊 Campos: {data_completeness}")
        print(f"   🎯 Calidad: {combined.get('data_quality', 'UNKNOWN')}")
        print(f"   🔗 Fuentes: {', '.join(successful_sources)}")
        
        return combined

def test_enhanced_scraper():
    """Test del scraper mejorado"""
    scraper = EnhancedRealTimeDataScraper()
    
    print("🚀 TESTING ENHANCED REAL-TIME DATA SCRAPER")
    print("=" * 70)
    
    # Test símbolos críticos
    test_symbols = ['SPY', 'AAPL', 'MSFT']
    
    for symbol in test_symbols:
        print(f"\n🔍 TESTING {symbol}")
        print("-" * 50)
        
        result = scraper.get_comprehensive_real_time_data(symbol)
        
        # Verificar precio
        price = result.get('current_price')
        if price:
            if symbol == 'SPY' and 600 <= price <= 650:
                print(f"✅ {symbol} precio CORRECTO: ${price:.2f}")
            elif symbol == 'AAPL' and 200 <= price <= 250:
                print(f"✅ {symbol} precio CORRECTO: ${price:.2f}")
            elif symbol == 'MSFT' and 400 <= price <= 600:
                print(f"✅ {symbol} precio CORRECTO: ${price:.2f}")
            else:
                print(f"📊 {symbol} precio: ${price:.2f}")
        
        # Mostrar calidad de datos
        print(f"📈 Completitud: {result.get('data_completeness', 0)} campos")
        print(f"🎯 Calidad: {result.get('data_quality', 'UNKNOWN')}")
        print(f"🔗 Fuentes: {result.get('sources_count', 0)}")

if __name__ == "__main__":
    test_enhanced_scraper()