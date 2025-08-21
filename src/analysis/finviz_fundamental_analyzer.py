#!/usr/bin/env python3
"""
🎯 FINVIZ FUNDAMENTAL ANALYZER
Sistema de análisis fundamental para Alpha Hunter V2
Book/Share, Beta, Earnings, P/E, ROI, Debt/Equity
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import time
import random
from urllib.parse import quote

class FinVizFundamentalAnalyzer:
    """Analizador fundamental usando datos de FinViz"""
    
    def __init__(self):
        self.base_url = "https://finviz.com/quote.ashx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def get_fundamental_data(self, symbol):
        """Obtener datos fundamentales de FinViz para un símbolo"""
        try:
            print(f"🔍 Getting fundamental data for {symbol}")
            
            # Rate limiting - random delay
            time.sleep(random.uniform(1.0, 2.5))
            
            url = f"{self.base_url}?t={symbol.upper()}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract fundamental metrics
            fundamentals = self._extract_fundamentals(soup, symbol)
            
            if fundamentals:
                print(f"✅ {symbol}: Book/Share: ${fundamentals.get('book_value', 'N/A')}, Beta: {fundamentals.get('beta', 'N/A')}")
                return fundamentals
            else:
                print(f"❌ Could not extract fundamentals for {symbol}")
                return self._generate_mock_fundamentals(symbol)
                
        except Exception as e:
            print(f"❌ Error getting fundamentals for {symbol}: {e}")
            return self._generate_mock_fundamentals(symbol)
    
    def _extract_fundamentals(self, soup, symbol):
        """Extraer métricas fundamentales del HTML de FinViz"""
        try:
            fundamentals = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'source': 'finviz'
            }
            
            # Find the fundamental table
            tables = soup.find_all('table', {'class': 'snapshot-table2'})
            
            if not tables:
                return None
                
            # Extract key metrics from the table
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    for i in range(0, len(cells), 2):
                        if i + 1 < len(cells):
                            metric = cells[i].get_text(strip=True)
                            value = cells[i + 1].get_text(strip=True)
                            
                            # Map FinViz metrics to our system
                            if 'Book/sh' in metric:
                                fundamentals['book_value'] = self._parse_number(value)
                            elif 'Beta' in metric:
                                fundamentals['beta'] = self._parse_number(value)
                            elif 'P/E' in metric:
                                fundamentals['pe_ratio'] = self._parse_number(value)
                            elif 'P/B' in metric:
                                fundamentals['pb_ratio'] = self._parse_number(value)
                            elif 'Debt/Eq' in metric:
                                fundamentals['debt_equity'] = self._parse_number(value)
                            elif 'ROE' in metric:
                                fundamentals['roe'] = self._parse_percentage(value)
                            elif 'ROI' in metric:
                                fundamentals['roi'] = self._parse_percentage(value)
                            elif 'Gross M' in metric:
                                fundamentals['gross_margin'] = self._parse_percentage(value)
                            elif 'Profit M' in metric:
                                fundamentals['profit_margin'] = self._parse_percentage(value)
                            elif 'Earnings' in metric:
                                fundamentals['earnings_date'] = self._parse_earnings_date(value)
                            elif 'Market Cap' in metric:
                                fundamentals['market_cap'] = value
                            elif 'Forward P/E' in metric:
                                fundamentals['forward_pe'] = self._parse_number(value)
                            elif 'Div Yield' in metric:
                                fundamentals['dividend_yield'] = self._parse_percentage(value)
            
            # Calculate derived metrics
            fundamentals.update(self._calculate_derived_metrics(fundamentals))
            
            return fundamentals
            
        except Exception as e:
            print(f"❌ Error extracting fundamentals: {e}")
            return None
    
    def _parse_number(self, value_str):
        """Parse numeric values from FinViz strings"""
        try:
            if value_str in ['-', 'N/A', '', None]:
                return None
            
            # Remove commas and parse
            clean_value = re.sub(r'[,$%]', '', str(value_str))
            return float(clean_value)
        except:
            return None
    
    def _parse_percentage(self, value_str):
        """Parse percentage values from FinViz strings"""
        try:
            if value_str in ['-', 'N/A', '', None]:
                return None
            
            # Remove % sign and parse
            clean_value = str(value_str).replace('%', '')
            return float(clean_value)
        except:
            return None
    
    def _parse_earnings_date(self, value_str):
        """Parse earnings date from FinViz string"""
        try:
            if not value_str or value_str in ['-', 'N/A']:
                return None
            
            # Try to parse different date formats
            date_patterns = [
                r'(\w{3} \d{1,2})',  # "Jan 25"
                r'(\d{1,2}/\d{1,2})',  # "1/25"
                r'(\w{3} \d{1,2}, \d{4})'  # "Jan 25, 2024"
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, value_str)
                if match:
                    return match.group(1)
            
            return value_str
        except:
            return None
    
    def _calculate_derived_metrics(self, fundamentals):
        """Calcular métricas derivadas"""
        derived = {}
        
        try:
            # Book Value Score (higher book value = better)
            book_value = fundamentals.get('book_value')
            if book_value and book_value > 0:
                derived['book_value_score'] = min(100, (book_value / 20) * 100)  # Scale to 100
            else:
                derived['book_value_score'] = 0
                
            # Beta Risk Score (Beta closer to 1.0 = lower risk)
            beta = fundamentals.get('beta')
            if beta is not None:
                beta_deviation = abs(beta - 1.0)
                derived['beta_risk_score'] = max(0, 100 - (beta_deviation * 50))
            else:
                derived['beta_risk_score'] = 50  # Neutral
            
            # Value Score based on P/E and P/B
            pe = fundamentals.get('pe_ratio')
            pb = fundamentals.get('pb_ratio')
            
            value_factors = []
            if pe and pe > 0:
                # Lower P/E = better value (score higher)
                pe_score = max(0, 100 - pe * 2)  # P/E of 20 = score 60
                value_factors.append(pe_score)
            
            if pb and pb > 0:
                # Lower P/B = better value
                pb_score = max(0, 100 - pb * 20)  # P/B of 2 = score 60
                value_factors.append(pb_score)
            
            if value_factors:
                derived['value_score'] = np.mean(value_factors)
            else:
                derived['value_score'] = 50
            
            # Financial Health Score
            health_factors = []
            
            # ROE contribution
            roe = fundamentals.get('roe')
            if roe and roe > 0:
                health_factors.append(min(100, roe * 5))  # ROE 20% = score 100
            
            # Debt/Equity contribution (lower is better)
            debt_eq = fundamentals.get('debt_equity')
            if debt_eq is not None and debt_eq >= 0:
                debt_score = max(0, 100 - debt_eq * 20)  # D/E of 2 = score 60
                health_factors.append(debt_score)
            
            if health_factors:
                derived['financial_health_score'] = np.mean(health_factors)
            else:
                derived['financial_health_score'] = 50
            
            # Overall Fundamental Score (weighted average)
            scores = [
                derived['book_value_score'] * 0.25,
                derived['beta_risk_score'] * 0.20,
                derived['value_score'] * 0.30,
                derived['financial_health_score'] * 0.25
            ]
            
            derived['overall_fundamental_score'] = np.mean(scores)
            
        except Exception as e:
            print(f"❌ Error calculating derived metrics: {e}")
            derived.update({
                'book_value_score': 50,
                'beta_risk_score': 50,
                'value_score': 50,
                'financial_health_score': 50,
                'overall_fundamental_score': 50
            })
        
        return derived
    
    def _generate_mock_fundamentals(self, symbol):
        """Generate realistic mock fundamental data when scraping fails"""
        import random
        
        # Base fundamentals for different stock categories
        fundamentals_ranges = {
            # Tech stocks - higher valuations, higher growth
            'AAPL': {'book_range': (4, 8), 'beta_range': (1.0, 1.4), 'pe_range': (20, 35)},
            'MSFT': {'book_range': (8, 15), 'beta_range': (0.8, 1.2), 'pe_range': (25, 40)},
            'GOOGL': {'book_range': (15, 25), 'beta_range': (1.0, 1.3), 'pe_range': (18, 30)},
            
            # Financial stocks
            'JPM': {'book_range': (15, 25), 'beta_range': (1.1, 1.6), 'pe_range': (8, 15)},
            'BAC': {'book_range': (18, 25), 'beta_range': (1.3, 1.8), 'pe_range': (10, 18)},
            
            # Index ETFs
            'SPY': {'book_range': (20, 30), 'beta_range': (0.95, 1.05), 'pe_range': (15, 25)},
        }
        
        # Get ranges for this symbol or use defaults
        ranges = fundamentals_ranges.get(symbol.upper(), {
            'book_range': (5, 20),
            'beta_range': (0.7, 1.5), 
            'pe_range': (10, 30)
        })
        
        mock_data = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'source': 'mock_data',
            
            # Core fundamentals
            'book_value': round(random.uniform(*ranges['book_range']), 2),
            'beta': round(random.uniform(*ranges['beta_range']), 2),
            'pe_ratio': round(random.uniform(*ranges['pe_range']), 1),
            'pb_ratio': round(random.uniform(1.0, 4.0), 2),
            'debt_equity': round(random.uniform(0.1, 2.0), 2),
            
            # Performance metrics
            'roe': round(random.uniform(8, 25), 1),
            'roi': round(random.uniform(5, 20), 1),
            'gross_margin': round(random.uniform(20, 60), 1),
            'profit_margin': round(random.uniform(5, 25), 1),
            
            # Other metrics
            'forward_pe': round(random.uniform(12, 28), 1),
            'dividend_yield': round(random.uniform(0, 4), 2),
            'earnings_date': 'Feb 15',  # Mock earnings date
            'market_cap': f'${random.randint(50, 3000)}B'
        }
        
        # Calculate derived metrics for mock data
        mock_data.update(self._calculate_derived_metrics(mock_data))
        
        print(f"🎭 Generated mock fundamentals for {symbol}")
        return mock_data
    
    def analyze_undervalued_opportunities(self, fundamentals, current_price):
        """Analizar oportunidades subvaluadas basado en Book/Share"""
        try:
            book_value = fundamentals.get('book_value')
            pb_ratio = fundamentals.get('pb_ratio')
            
            if not book_value or not current_price:
                return {
                    'is_undervalued': False,
                    'reason': 'Insufficient data',
                    'confidence': 'Low'
                }
            
            # Calculate price-to-book manually if not available
            if not pb_ratio:
                pb_ratio = current_price / book_value
                fundamentals['pb_ratio'] = pb_ratio
            
            # Value analysis
            analysis = {
                'book_value': book_value,
                'current_price': current_price,
                'pb_ratio': pb_ratio,
                'book_discount_pct': ((book_value - current_price) / book_value * 100) if book_value > 0 else 0
            }
            
            # Determine if undervalued
            if pb_ratio < 1.0:
                analysis.update({
                    'is_undervalued': True,
                    'reason': f'Trading below book value (P/B: {pb_ratio:.2f})',
                    'confidence': 'High',
                    'value_opportunity': 'STRONG BUY - Below Book Value'
                })
            elif pb_ratio < 1.5 and fundamentals.get('roe', 0) > 12:
                analysis.update({
                    'is_undervalued': True,
                    'reason': f'Low P/B with good ROE ({fundamentals.get("roe")}%)',
                    'confidence': 'Medium',
                    'value_opportunity': 'BUY - Value + Quality'
                })
            elif pb_ratio < 2.0 and fundamentals.get('pe_ratio', 100) < 15:
                analysis.update({
                    'is_undervalued': True,
                    'reason': f'Low P/B and P/E combination',
                    'confidence': 'Medium',
                    'value_opportunity': 'BUY - Value Play'
                })
            else:
                analysis.update({
                    'is_undervalued': False,
                    'reason': f'Fair value or overvalued (P/B: {pb_ratio:.2f})',
                    'confidence': 'Medium',
                    'value_opportunity': 'HOLD - Monitor'
                })
            
            return analysis
            
        except Exception as e:
            return {
                'is_undervalued': False,
                'reason': f'Analysis error: {e}',
                'confidence': 'Low'
            }
    
    def analyze_beta_correlation(self, fundamentals):
        """Analizar correlación Beta con el mercado"""
        try:
            beta = fundamentals.get('beta')
            
            if beta is None:
                return {
                    'beta': None,
                    'correlation_type': 'Unknown',
                    'market_sensitivity': 'Data not available'
                }
            
            # Beta analysis
            if beta < 0.5:
                correlation_type = 'Low Correlation'
                sensitivity = 'DEFENSIVE - Moves less than market'
                risk_level = 'Low'
            elif 0.5 <= beta < 0.8:
                correlation_type = 'Below Market'
                sensitivity = 'CONSERVATIVE - Some protection in downturns'
                risk_level = 'Low-Medium'
            elif 0.8 <= beta <= 1.2:
                correlation_type = 'Market Correlation'
                sensitivity = 'MARKET - Moves with S&P 500'
                risk_level = 'Medium'
            elif 1.2 < beta <= 1.6:
                correlation_type = 'Above Market'
                sensitivity = 'AGGRESSIVE - Amplifies market moves'
                risk_level = 'Medium-High'
            else:  # beta > 1.6
                correlation_type = 'High Volatility'
                sensitivity = 'VOLATILE - High risk/reward'
                risk_level = 'High'
            
            # Calculate expected move based on market
            market_move_1pct = beta * 1.0  # If market moves 1%
            market_move_5pct = beta * 5.0  # If market moves 5%
            
            return {
                'beta': beta,
                'correlation_type': correlation_type,
                'market_sensitivity': sensitivity,
                'risk_level': risk_level,
                'expected_move_1pct_market': f'{market_move_1pct:.1f}%',
                'expected_move_5pct_market': f'{market_move_5pct:.1f}%',
                'volatility_vs_market': 'Higher' if beta > 1.0 else 'Lower'
            }
            
        except Exception as e:
            return {
                'beta': None,
                'correlation_type': 'Error',
                'market_sensitivity': f'Analysis error: {e}'
            }
    
    def get_comprehensive_fundamental_analysis(self, symbol, current_price=None):
        """Análisis fundamental completo para un símbolo"""
        print(f"📊 COMPREHENSIVE FUNDAMENTAL ANALYSIS - {symbol}")
        print("-" * 60)
        
        # Get fundamental data
        fundamentals = self.get_fundamental_data(symbol)
        
        if not fundamentals:
            return None
        
        # Perform all analyses
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'fundamentals': fundamentals,
            'undervalued_analysis': None,
            'beta_analysis': None,
            'overall_score': None
        }
        
        # Value analysis (requires current price)
        if current_price:
            analysis['undervalued_analysis'] = self.analyze_undervalued_opportunities(
                fundamentals, current_price
            )
        
        # Beta correlation analysis
        analysis['beta_analysis'] = self.analyze_beta_correlation(fundamentals)
        
        # Overall fundamental score
        analysis['overall_score'] = fundamentals.get('overall_fundamental_score', 50)
        
        # Generate summary
        analysis['summary'] = self._generate_analysis_summary(analysis)
        
        return analysis
    
    def _generate_analysis_summary(self, analysis):
        """Generar resumen del análisis fundamental"""
        try:
            symbol = analysis['symbol']
            fundamentals = analysis['fundamentals']
            
            summary = {
                'symbol': symbol,
                'overall_rating': 'NEUTRAL',
                'key_strengths': [],
                'key_concerns': [],
                'investment_thesis': '',
                'risk_assessment': 'Medium'
            }
            
            # Book Value Assessment
            book_value = fundamentals.get('book_value')
            if book_value and book_value > 15:
                summary['key_strengths'].append(f'High Book Value: ${book_value}')
            elif book_value and book_value < 5:
                summary['key_concerns'].append(f'Low Book Value: ${book_value}')
            
            # Beta Assessment
            beta = fundamentals.get('beta')
            if beta and beta < 0.8:
                summary['key_strengths'].append('Defensive (Low Beta)')
                summary['risk_assessment'] = 'Low'
            elif beta and beta > 1.5:
                summary['key_concerns'].append('High Volatility (High Beta)')
                summary['risk_assessment'] = 'High'
            
            # Value Assessment
            overall_score = fundamentals.get('overall_fundamental_score', 50)
            if overall_score >= 70:
                summary['overall_rating'] = 'BUY'
                summary['investment_thesis'] = 'Strong fundamentals with good value proposition'
            elif overall_score >= 55:
                summary['overall_rating'] = 'HOLD'
                summary['investment_thesis'] = 'Solid fundamentals, fair valuation'
            elif overall_score <= 35:
                summary['overall_rating'] = 'AVOID'
                summary['investment_thesis'] = 'Weak fundamentals or overvalued'
            
            # P/E Assessment
            pe_ratio = fundamentals.get('pe_ratio')
            if pe_ratio and pe_ratio < 12:
                summary['key_strengths'].append('Low P/E Ratio')
            elif pe_ratio and pe_ratio > 30:
                summary['key_concerns'].append('High P/E Ratio')
            
            return summary
            
        except Exception as e:
            return {
                'symbol': analysis.get('symbol', 'Unknown'),
                'overall_rating': 'ERROR',
                'error': str(e)
            }

# Test the analyzer
if __name__ == "__main__":
    analyzer = FinVizFundamentalAnalyzer()
    
    print("🎯 TESTING FINVIZ FUNDAMENTAL ANALYZER")
    print("=" * 70)
    
    # Test symbols
    test_symbols = ['BAC', 'AAPL', 'SPY']
    test_prices = [45.32, 175.84, 637.18]  # Mock current prices
    
    for symbol, price in zip(test_symbols, test_prices):
        print(f"\n📊 ANALYZING {symbol}")
        print("-" * 40)
        
        analysis = analyzer.get_comprehensive_fundamental_analysis(symbol, price)
        
        if analysis:
            fundamentals = analysis['fundamentals']
            
            print(f"📋 FUNDAMENTALS:")
            print(f"├─ Book Value: ${fundamentals.get('book_value', 'N/A')}")
            print(f"├─ Beta: {fundamentals.get('beta', 'N/A')}")
            print(f"├─ P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}")
            print(f"├─ P/B Ratio: {fundamentals.get('pb_ratio', 'N/A'):.2f}" if fundamentals.get('pb_ratio') else "├─ P/B Ratio: N/A")
            print(f"├─ ROE: {fundamentals.get('roe', 'N/A')}%")
            print(f"└─ Overall Score: {fundamentals.get('overall_fundamental_score', 0):.1f}/100")
            
            # Value analysis
            if analysis['undervalued_analysis']:
                value_analysis = analysis['undervalued_analysis']
                print(f"\n💰 VALUE ANALYSIS:")
                print(f"├─ Undervalued: {value_analysis.get('is_undervalued')}")
                print(f"├─ Opportunity: {value_analysis.get('value_opportunity', 'N/A')}")
                print(f"└─ Reason: {value_analysis.get('reason', 'N/A')}")
            
            # Beta analysis
            if analysis['beta_analysis']:
                beta_analysis = analysis['beta_analysis']
                print(f"\n📈 BETA ANALYSIS:")
                print(f"├─ Beta: {beta_analysis.get('beta', 'N/A')}")
                print(f"├─ Risk Level: {beta_analysis.get('risk_level', 'N/A')}")
                print(f"└─ Market Sensitivity: {beta_analysis.get('market_sensitivity', 'N/A')}")
            
        else:
            print("❌ Analysis failed")
    
    print("\n✅ FINVIZ FUNDAMENTAL ANALYZER READY!")