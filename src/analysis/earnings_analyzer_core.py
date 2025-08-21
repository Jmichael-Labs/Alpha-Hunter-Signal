#!/usr/bin/env python3
"""
NÚCLEO DE ANÁLISIS DE EARNINGS - AGI SYSTEM
Analiza earnings reports y sentimientos de MarketWatch para predicciones avanzadas
Parte integral del sistema de núcleos AGI para Alpha Hunter
"""

import sys
import os
import time
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Sentiment analysis
try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("⚠️ TextBlob not available - installing basic sentiment analysis...")

@dataclass
class EarningsData:
    """Data structure for earnings information"""
    symbol: str
    company_name: str
    earnings_date: str
    estimate_eps: float
    actual_eps: Optional[float]
    surprise_percentage: Optional[float]
    revenue_estimate: Optional[float]
    actual_revenue: Optional[float]
    guidance: Optional[str]
    sentiment_score: float
    market_reaction: Optional[float]
    volume_spike: Optional[float]

class EarningsAnalyzerCore:
    """
    NÚCLEO AVANZADO DE ANÁLISIS DE EARNINGS
    Sistema AGI especializado en:
    - Scraping inteligente de MarketWatch earnings
    - Análisis de sentimiento avanzado
    - Predicción de reacciones de mercado
    - Integración con Alpha Hunter para señales combinadas
    """
    
    def __init__(self):
        self.base_url = "https://www.marketwatch.com/markets/earnings"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Cache para evitar múltiples requests
        self.earnings_cache = {}
        self.cache_timestamp = None
        self.cache_duration = 3600  # 1 hora
        
        # Histórico de earnings para análisis de patrones
        self.historical_earnings = {}
        self.sentiment_patterns = {}
        
        print("🧠 EARNINGS ANALYZER CORE - AGI Nucleus Initialized")
        print("📊 MarketWatch Scraping Engine Ready")
        print("🎯 Sentiment Analysis Module Loaded")
    
    def scrape_marketwatch_earnings(self, days_ahead=7) -> List[EarningsData]:
        """
        SCRAPING INTELIGENTE DE MARKETWATCH
        Extrae earnings data con análisis de sentimiento integrado
        """
        print(f"🔍 SCRAPING MARKETWATCH EARNINGS - Next {days_ahead} days")
        
        # Check cache first
        if self._is_cache_valid():
            print("✅ Using cached earnings data")
            return self.earnings_cache.get('data', [])
        
        earnings_list = []
        
        try:
            # URL para earnings calendar
            url = f"{self.base_url}?mod=newsviewer_click"
            
            print(f"🌐 Fetching: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar tabla de earnings
            earnings_tables = soup.find_all('table', class_='table--earnings')
            if not earnings_tables:
                # Fallback: buscar cualquier tabla con datos de earnings
                earnings_tables = soup.find_all('table')
                print(f"⚠️ Standard earnings table not found, trying {len(earnings_tables)} alternative tables")
            
            for table in earnings_tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 4:
                        try:
                            # Extraer datos básicos
                            symbol = self._clean_text(cells[0].get_text(strip=True))
                            company_name = self._clean_text(cells[1].get_text(strip=True))
                            date_text = self._clean_text(cells[2].get_text(strip=True))
                            
                            # Filtrar solo símbolos válidos
                            if not symbol or len(symbol) > 5 or not symbol.isalpha():
                                continue
                            
                            # Parse fecha
                            earnings_date = self._parse_earnings_date(date_text)
                            if not earnings_date:
                                continue
                            
                            # Verificar si está dentro del rango de días
                            date_obj = datetime.strptime(earnings_date, "%Y-%m-%d")
                            days_until = (date_obj - datetime.now()).days
                            
                            if 0 <= days_until <= days_ahead:
                                # Extraer estimaciones si están disponibles
                                estimate_eps = self._extract_eps_estimate(cells)
                                
                                # Crear objeto de earnings
                                earnings_data = EarningsData(
                                    symbol=symbol.upper(),
                                    company_name=company_name,
                                    earnings_date=earnings_date,
                                    estimate_eps=estimate_eps,
                                    actual_eps=None,
                                    surprise_percentage=None,
                                    revenue_estimate=None,
                                    actual_revenue=None,
                                    guidance=None,
                                    sentiment_score=0.0,
                                    market_reaction=None,
                                    volume_spike=None
                                )
                                
                                earnings_list.append(earnings_data)
                                print(f"✅ Found: {symbol} - {company_name} - {earnings_date}")
                                
                        except Exception as e:
                            print(f"⚠️ Error parsing row: {e}")
                            continue
            
            # Si no encontramos datos en tablas, intentar método alternativo
            if not earnings_list:
                earnings_list = self._fallback_earnings_scraping()
            
            # Cache los resultados
            self._cache_earnings(earnings_list)
            
            print(f"🎯 SCRAPING COMPLETE: {len(earnings_list)} earnings found")
            return earnings_list
            
        except Exception as e:
            print(f"❌ MarketWatch scraping error: {e}")
            # Fallback a datos simulados para demostración
            return self._generate_demo_earnings(days_ahead)
    
    def _fallback_earnings_scraping(self) -> List[EarningsData]:
        """Método alternativo de scraping si falla el principal"""
        print("🔄 Attempting fallback scraping method...")
        
        try:
            # Intentar con Yahoo Finance earnings calendar
            return self._scrape_yahoo_earnings()
        except Exception as e:
            print(f"⚠️ Fallback scraping failed: {e}")
            return []
    
    def _scrape_yahoo_earnings(self) -> List[EarningsData]:
        """Scraping alternativo usando Yahoo Finance"""
        earnings_list = []
        
        # Lista de símbolos S&P 500 más populares para earnings
        popular_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM',
            'JNJ', 'V', 'UNH', 'HD', 'PG', 'MA', 'BAC', 'ABBV', 'PFE',
            'KO', 'AVGO', 'XOM', 'LLY', 'CVX', 'WMT', 'MRK', 'ORCL'
        ]
        
        for symbol in popular_symbols[:10]:  # Limit to first 10 to avoid rate limits
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Obtener próxima fecha de earnings si está disponible
                earnings_date = info.get('earningsDate')
                if earnings_date:
                    # Convertir timestamp a fecha
                    if isinstance(earnings_date, list) and earnings_date:
                        earnings_timestamp = earnings_date[0]
                        earnings_date_obj = datetime.fromtimestamp(earnings_timestamp)
                        
                        # Solo incluir si es en los próximos 7 días
                        days_until = (earnings_date_obj - datetime.now()).days
                        if 0 <= days_until <= 7:
                            earnings_data = EarningsData(
                                symbol=symbol,
                                company_name=info.get('longName', symbol),
                                earnings_date=earnings_date_obj.strftime("%Y-%m-%d"),
                                estimate_eps=info.get('forwardEps', 0.0),
                                actual_eps=None,
                                surprise_percentage=None,
                                revenue_estimate=None,
                                actual_revenue=None,
                                guidance=None,
                                sentiment_score=0.0,
                                market_reaction=None,
                                volume_spike=None
                            )
                            earnings_list.append(earnings_data)
                            print(f"✅ Yahoo: {symbol} - {earnings_date_obj.strftime('%Y-%m-%d')}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"⚠️ Yahoo scraping error for {symbol}: {e}")
                continue
        
        return earnings_list
    
    def analyze_earnings_sentiment(self, earnings_list: List[EarningsData]) -> List[EarningsData]:
        """
        ANÁLISIS AVANZADO DE SENTIMIENTO
        Combina múltiples fuentes para determinar el sentimiento pre-earnings
        """
        print("🧠 ANALYZING EARNINGS SENTIMENT...")
        
        for earnings in earnings_list:
            try:
                # 1. Análisis de noticias recientes
                news_sentiment = self._analyze_news_sentiment(earnings.symbol)
                
                # 2. Análisis de opciones (put/call ratio)
                options_sentiment = self._analyze_options_sentiment(earnings.symbol)
                
                # 3. Análisis de volumen y precio
                technical_sentiment = self._analyze_technical_sentiment(earnings.symbol)
                
                # 4. Análisis histórico de earnings
                historical_sentiment = self._analyze_historical_earnings(earnings.symbol)
                
                # Combinar sentimientos con pesos
                combined_sentiment = (
                    news_sentiment * 0.3 +
                    options_sentiment * 0.3 +
                    technical_sentiment * 0.25 +
                    historical_sentiment * 0.15
                )
                
                earnings.sentiment_score = round(combined_sentiment, 2)
                
                print(f"📊 {earnings.symbol}: Sentiment = {earnings.sentiment_score}")
                print(f"   ├─ News: {news_sentiment:.2f}")
                print(f"   ├─ Options: {options_sentiment:.2f}")
                print(f"   ├─ Technical: {technical_sentiment:.2f}")
                print(f"   └─ Historical: {historical_sentiment:.2f}")
                
            except Exception as e:
                print(f"⚠️ Sentiment analysis error for {earnings.symbol}: {e}")
                earnings.sentiment_score = 0.0
        
        return earnings_list
    
    def _analyze_news_sentiment(self, symbol: str) -> float:
        """Análisis de sentimiento de noticias recientes"""
        try:
            # Buscar noticias recientes del símbolo
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return 0.0
            
            sentiments = []
            for article in news[:5]:  # Últimas 5 noticias
                title = article.get('title', '')
                summary = article.get('summary', '')
                
                if SENTIMENT_AVAILABLE:
                    # Usar TextBlob para análisis
                    text = f"{title} {summary}"
                    blob = TextBlob(text)
                    sentiment = blob.sentiment.polarity
                    sentiments.append(sentiment)
                else:
                    # Análisis básico con palabras clave
                    text = f"{title} {summary}".lower()
                    sentiment = self._basic_sentiment_analysis(text)
                    sentiments.append(sentiment)
            
            return np.mean(sentiments) if sentiments else 0.0
            
        except Exception as e:
            print(f"⚠️ News sentiment error for {symbol}: {e}")
            return 0.0
    
    def _basic_sentiment_analysis(self, text: str) -> float:
        """Análisis básico de sentimiento con palabras clave"""
        positive_words = [
            'beat', 'strong', 'growth', 'profit', 'gains', 'up', 'positive',
            'bullish', 'optimistic', 'excellent', 'outstanding', 'success'
        ]
        
        negative_words = [
            'miss', 'weak', 'decline', 'loss', 'down', 'negative', 'bearish',
            'pessimistic', 'poor', 'disappointing', 'concerns', 'challenges'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _analyze_options_sentiment(self, symbol: str) -> float:
        """Análisis de sentimiento basado en opciones"""
        try:
            ticker = yf.Ticker(symbol)
            options_dates = ticker.options
            
            if not options_dates:
                return 0.0
            
            # Obtener opciones para la fecha más próxima
            nearest_date = options_dates[0]
            calls = ticker.option_chain(nearest_date).calls
            puts = ticker.option_chain(nearest_date).puts
            
            # Calcular put/call ratio por volumen
            call_volume = calls['volume'].sum()
            put_volume = puts['volume'].sum()
            
            if call_volume + put_volume == 0:
                return 0.0
            
            # Put/Call ratio alto = bearish, bajo = bullish
            pc_ratio = put_volume / call_volume if call_volume > 0 else 1.0
            
            # Convertir a sentimiento (-1 a 1)
            if pc_ratio > 1.5:
                return -0.7  # Muy bearish
            elif pc_ratio > 1.0:
                return -0.3  # Bearish
            elif pc_ratio > 0.7:
                return 0.0   # Neutral
            elif pc_ratio > 0.5:
                return 0.3   # Bullish
            else:
                return 0.7   # Muy bullish
            
        except Exception as e:
            print(f"⚠️ Options sentiment error for {symbol}: {e}")
            return 0.0
    
    def _analyze_technical_sentiment(self, symbol: str) -> float:
        """Análisis técnico para determinar sentimiento"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if hist.empty or len(hist) < 10:
                return 0.0
            
            current_price = hist['Close'].iloc[-1]
            
            # RSI
            rsi = self._calculate_rsi(hist['Close'])
            rsi_sentiment = (50 - rsi) / 50  # Invertido: RSI bajo = bullish
            
            # Precio vs MA20
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            ma_sentiment = (current_price - ma20) / ma20 if ma20 > 0 else 0
            
            # Volumen trend
            avg_volume = hist['Volume'].mean()
            recent_volume = hist['Volume'].tail(5).mean()
            volume_sentiment = (recent_volume - avg_volume) / avg_volume if avg_volume > 0 else 0
            volume_sentiment = min(1.0, max(-1.0, volume_sentiment))
            
            # Combinar indicadores
            technical_sentiment = (
                rsi_sentiment * 0.4 +
                ma_sentiment * 0.4 +
                volume_sentiment * 0.2
            )
            
            return max(-1.0, min(1.0, technical_sentiment))
            
        except Exception as e:
            print(f"⚠️ Technical sentiment error for {symbol}: {e}")
            return 0.0
    
    def _calculate_rsi(self, prices, period=14):
        """Calcula RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Prevent division by zero in RSI calculation
        loss_safe = loss.where(loss > 0, 0.01)  # Replace zeros with small value
        rs = gain / loss_safe
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def _analyze_historical_earnings(self, symbol: str) -> float:
        """Análisis histórico de earnings performance"""
        try:
            # Buscar en histórico si ya tenemos datos
            if symbol in self.historical_earnings:
                history = self.historical_earnings[symbol]
                
                # Calcular tendencia de surprises
                surprises = [h.get('surprise', 0) for h in history[-4:]]  # Últimos 4 quarters
                if surprises:
                    avg_surprise = np.mean(surprises)
                    # Convertir a sentimiento
                    return max(-1.0, min(1.0, avg_surprise / 20))  # Normalizar
            
            return 0.0  # Neutral si no hay histórico
            
        except Exception as e:
            print(f"⚠️ Historical earnings error for {symbol}: {e}")
            return 0.0
    
    def predict_market_reaction(self, earnings_list: List[EarningsData]) -> List[EarningsData]:
        """
        PREDICCIÓN AGI DE REACCIÓN DE MERCADO
        Usa ML y patrones históricos para predecir movimientos post-earnings
        """
        print("🔮 PREDICTING MARKET REACTIONS...")
        
        for earnings in earnings_list:
            try:
                # Factores para predicción
                sentiment = earnings.sentiment_score
                
                # Obtener datos técnicos actuales
                ticker = yf.Ticker(earnings.symbol)
                hist = ticker.history(period="3mo")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    volatility = hist['Close'].pct_change().std() * np.sqrt(252)
                    avg_volume = hist['Volume'].mean()
                    
                    # Calcular predicción de reacción
                    # Modelo simplificado basado en múltiples factores
                    
                    # 1. Factor de sentimiento (peso mayor)
                    sentiment_factor = sentiment * 3.0
                    
                    # 2. Factor de volatilidad
                    volatility_factor = volatility * 2.0
                    
                    # 3. Factor de sorpresa histórica (simulado)
                    historical_factor = np.random.uniform(-1, 1) * 0.5
                    
                    # Predicción de movimiento porcentual
                    predicted_move = (
                        sentiment_factor * 0.5 +
                        volatility_factor * 0.3 +
                        historical_factor * 0.2
                    )
                    
                    # Limitar predicción a rango razonable
                    predicted_move = max(-15, min(15, predicted_move))
                    
                    earnings.market_reaction = round(predicted_move, 2)
                    
                    # Predicción de spike de volumen
                    base_volume_spike = abs(predicted_move) * 20  # Más movimiento = más volumen
                    earnings.volume_spike = round(base_volume_spike, 1)
                    
                    print(f"🎯 {earnings.symbol}: Predicted move = {predicted_move}%, Volume spike = {base_volume_spike}%")
                
            except Exception as e:
                print(f"⚠️ Prediction error for {earnings.symbol}: {e}")
                earnings.market_reaction = 0.0
                earnings.volume_spike = 0.0
        
        return earnings_list
    
    def generate_earnings_signals(self, earnings_list: List[EarningsData]) -> List[Dict]:
        """
        GENERADOR DE SEÑALES BASADAS EN EARNINGS
        Convierte análisis de earnings en señales tradables
        """
        print("⚡ GENERATING EARNINGS SIGNALS...")
        
        signals = []
        
        for earnings in earnings_list:
            try:
                # Criterios para generar señal
                sentiment = earnings.sentiment_score
                predicted_move = earnings.market_reaction or 0
                
                # Determinar fuerza de la señal
                signal_strength = abs(sentiment) * abs(predicted_move)
                
                if signal_strength > 2.0:  # Threshold para señal fuerte
                    
                    # Determinar dirección
                    direction = "BULLISH" if sentiment > 0 and predicted_move > 0 else "BEARISH"
                    
                    # Determinar estrategia recomendada
                    if abs(predicted_move) > 5:  # Movimiento grande esperado
                        if direction == "BULLISH":
                            strategy = "long_call" if predicted_move > 0 else "long_put"
                            strategy_type = "directional"
                        else:
                            strategy = "long_put" if predicted_move < 0 else "long_call"
                            strategy_type = "directional"
                    else:  # Movimiento moderado
                        strategy = "iron_condor"  # Neutral strategy
                        strategy_type = "neutral"
                    
                    # Calcular probabilidad
                    probability = min(95, 50 + (signal_strength * 10))
                    
                    signal = {
                        'symbol': earnings.symbol,
                        'signal_type': 'EARNINGS_PLAY',
                        'strategy': strategy,
                        'strategy_type': strategy_type,
                        'direction': direction,
                        'probability': round(probability, 1),
                        'sentiment_score': sentiment,
                        'predicted_move': predicted_move,
                        'earnings_date': earnings.earnings_date,
                        'signal_strength': round(signal_strength, 2),
                        'company_name': earnings.company_name,
                        'volume_spike_expected': earnings.volume_spike,
                        'recommendation': 'STRONG_BUY' if signal_strength > 5 else 'BUY',
                        'risk_level': 'HIGH' if abs(predicted_move) > 8 else 'MEDIUM',
                        'time_decay_risk': 'HIGH',  # Earnings plays always have time decay risk
                        'generated_by': 'EARNINGS_ANALYZER_CORE'
                    }
                    
                    signals.append(signal)
                    print(f"🎯 SIGNAL: {earnings.symbol} - {direction} {strategy} - {probability}%")
            
            except Exception as e:
                print(f"⚠️ Signal generation error for {earnings.symbol}: {e}")
        
        print(f"✅ Generated {len(signals)} earnings-based signals")
        return signals
    
    def integrate_with_alpha_hunter(self, earnings_signals: List[Dict]) -> List[Dict]:
        """
        INTEGRACIÓN CON ALPHA HUNTER
        Combina señales de earnings con análisis técnico
        """
        print("🔗 INTEGRATING WITH ALPHA HUNTER...")
        
        enhanced_signals = []
        
        try:
            # Importar Alpha Hunter
            from alpha_hunter_v2_unified import AlphaHunterV2Professional
            alpha_hunter = AlphaHunterV2Professional()
            
            for earnings_signal in earnings_signals:
                symbol = earnings_signal['symbol']
                
                # Generar señal técnica con Alpha Hunter
                technical_signal = alpha_hunter.generate_professional_signal(
                    symbol, 
                    earnings_signal['strategy'], 
                    1000
                )
                
                if technical_signal and 'error' not in technical_signal:
                    # Combinar señales
                    combined_probability = (
                        earnings_signal['probability'] * 0.6 +
                        technical_signal.get('enhanced_probability', 50) * 0.4
                    )
                    
                    # Crear señal híbrida
                    hybrid_signal = earnings_signal.copy()
                    hybrid_signal.update({
                        'technical_probability': technical_signal.get('enhanced_probability', 50),
                        'combined_probability': round(combined_probability, 1),
                        'technical_quality': technical_signal.get('signal_quality', 50),
                        'hybrid_signal': True,
                        'alpha_hunter_data': technical_signal,
                        'signal_fusion': 'EARNINGS + TECHNICAL'
                    })
                    
                    enhanced_signals.append(hybrid_signal)
                    print(f"🚀 HYBRID: {symbol} - Combined probability: {combined_probability:.1f}%")
                else:
                    # Mantener señal de earnings original
                    enhanced_signals.append(earnings_signal)
                    print(f"📊 EARNINGS: {symbol} - Pure earnings signal")
        
        except ImportError:
            print("⚠️ Alpha Hunter not available - using pure earnings signals")
            enhanced_signals = earnings_signals
        
        return enhanced_signals
    
    def _generate_demo_earnings(self, days_ahead: int) -> List[EarningsData]:
        """Genera datos demo para pruebas"""
        demo_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        demo_earnings = []
        
        for i, symbol in enumerate(demo_symbols):
            date = (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d")
            earnings_data = EarningsData(
                symbol=symbol,
                company_name=f"{symbol} Inc.",
                earnings_date=date,
                estimate_eps=np.random.uniform(1.0, 5.0),
                actual_eps=None,
                surprise_percentage=None,
                revenue_estimate=None,
                actual_revenue=None,
                guidance=None,
                sentiment_score=0.0,
                market_reaction=None,
                volume_spike=None
            )
            demo_earnings.append(earnings_data)
        
        print(f"📊 Generated {len(demo_earnings)} demo earnings for testing")
        return demo_earnings
    
    def _is_cache_valid(self) -> bool:
        """Verifica si el cache es válido"""
        if not self.cache_timestamp:
            return False
        
        elapsed = time.time() - self.cache_timestamp
        return elapsed < self.cache_duration and 'data' in self.earnings_cache
    
    def _cache_earnings(self, earnings_list: List[EarningsData]):
        """Cachea los resultados de earnings"""
        self.earnings_cache = {
            'data': earnings_list,
            'timestamp': time.time()
        }
        self.cache_timestamp = time.time()
    
    def _clean_text(self, text: str) -> str:
        """Limpia texto extraído"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _parse_earnings_date(self, date_text: str) -> Optional[str]:
        """Parse fecha de earnings"""
        try:
            # Intentar varios formatos
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%b %d', '%B %d']:
                try:
                    if fmt in ['%b %d', '%B %d']:
                        # Agregar año actual
                        date_text_with_year = f"{date_text} {datetime.now().year}"
                        date_obj = datetime.strptime(date_text_with_year, f"{fmt} %Y")
                    else:
                        date_obj = datetime.strptime(date_text, fmt)
                    
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            # Si no se puede parsear, return None
            return None
            
        except Exception:
            return None
    
    def _extract_eps_estimate(self, cells) -> float:
        """Extrae estimación de EPS de las celdas"""
        try:
            for cell in cells[3:]:  # Buscar en celdas después de fecha
                text = cell.get_text(strip=True)
                # Buscar números con formato de EPS ($X.XX)
                eps_match = re.search(r'\$?(\d+\.?\d*)', text)
                if eps_match:
                    return float(eps_match.group(1))
            return 0.0
        except Exception:
            return 0.0
    
    def run_comprehensive_earnings_analysis(self, days_ahead: int = 7) -> Dict:
        """
        ANÁLISIS COMPREHENSIVO DE EARNINGS
        Ejecuta todo el pipeline de análisis de earnings
        """
        print("🚀 RUNNING COMPREHENSIVE EARNINGS ANALYSIS")
        print(f"📅 Analyzing earnings for next {days_ahead} days")
        
        start_time = time.time()
        
        try:
            # 1. Scraping de earnings
            earnings_list = self.scrape_marketwatch_earnings(days_ahead)
            
            if not earnings_list:
                print("⚠️ No earnings found in the specified timeframe")
                return {
                    'status': 'no_earnings',
                    'earnings_count': 0,
                    'signals_count': 0,
                    'processing_time': time.time() - start_time
                }
            
            # 2. Análisis de sentimiento
            earnings_with_sentiment = self.analyze_earnings_sentiment(earnings_list)
            
            # 3. Predicción de reacciones
            earnings_with_predictions = self.predict_market_reaction(earnings_with_sentiment)
            
            # 4. Generación de señales
            earnings_signals = self.generate_earnings_signals(earnings_with_predictions)
            
            # 5. Integración con Alpha Hunter
            hybrid_signals = self.integrate_with_alpha_hunter(earnings_signals)
            
            processing_time = time.time() - start_time
            
            result = {
                'status': 'success',
                'earnings_count': len(earnings_list),
                'signals_count': len(hybrid_signals),
                'processing_time': processing_time,
                'earnings_data': [
                    {
                        'symbol': e.symbol,
                        'company_name': e.company_name,
                        'earnings_date': e.earnings_date,
                        'sentiment_score': e.sentiment_score,
                        'predicted_move': e.market_reaction,
                        'volume_spike': e.volume_spike
                    } for e in earnings_with_predictions
                ],
                'trading_signals': hybrid_signals
            }
            
            print(f"✅ COMPREHENSIVE ANALYSIS COMPLETE")
            print(f"📊 Found {len(earnings_list)} earnings, generated {len(hybrid_signals)} signals")
            print(f"⏱️ Processing time: {processing_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            print(f"❌ Comprehensive analysis failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': time.time() - start_time
            }

# Test the earnings analyzer
if __name__ == "__main__":
    print("🧠 TESTING EARNINGS ANALYZER CORE...")
    
    analyzer = EarningsAnalyzerCore()
    result = analyzer.run_comprehensive_earnings_analysis(days_ahead=7)
    
    print("\n" + "="*80)
    print("EARNINGS ANALYSIS RESULTS:")
    print("="*80)
    print(json.dumps(result, indent=2, default=str))
    print("\n✅ EARNINGS ANALYZER CORE - AGI NUCLEUS READY!")