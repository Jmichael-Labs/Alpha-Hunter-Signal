#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - PRESENT CONTINUOUS OPTIONS ENGINE
Sistema de trading de opciones enfocado en presente continuo (7-14 días máximo)
Estrategias permitidas: long_call, long_put (ONLY SIMPLE OPTIONS)
Lógica: ITM para consistencia, predicción direccional inmediata
"""

import sys
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.nexus_utils import nexus_speak
except ImportError:
    def nexus_speak(level, message):
        print(f"[{level.upper()}] {message}")

class PresentContinuousOptionsEngine:
    """Motor de opciones para presente continuo - Trades direccionales 7-14 días"""
    
    def __init__(self):
        nexus_speak("info", "🎯 Initializing Present Continuous Options Engine")
        
        # Configuración de estrategias permitidas
        self.allowed_strategies = ["long_call", "long_put"]  # ONLY SIMPLE OPTIONS
        
        # Reglas de expiración (7-14 días máximo)
        self.min_days_to_expiry = 7
        self.max_days_to_expiry = 14
        
        # Configuración ATM (At The Money)
        self.atm_tolerance = 0.02  # 2% de tolerancia para considerar ATM
        
        # Configuración de predicción direccional
        self.momentum_threshold = 0.55  # 55% mínimo para señal direccional
        
        nexus_speak("success", "✅ Present Continuous Engine initialized - 7-14 day trades only")
    
    def analyze_market_direction(self, symbol, market_data):
        """Predice dirección del mercado a corto plazo (7-14 días)"""
        try:
            current_price = market_data.get('current_price', 0)
            historical_data = market_data.get('historical_data', {})
            
            if not historical_data or current_price <= 0:
                return {'direction': 'neutral', 'confidence': 0.5, 'reasoning': 'Insufficient data'}
            
            # Análisis de momentum a corto plazo
            closes = historical_data.get('Close', [])
            if len(closes) < 10:
                return {'direction': 'neutral', 'confidence': 0.5, 'reasoning': 'Insufficient history'}
            
            # Momentum 5 días vs 10 días
            sma_5 = np.mean(closes[-5:])
            sma_10 = np.mean(closes[-10:])
            
            # RSI a 7 días para presente continuo
            rsi_7 = self.calculate_rsi(closes[-14:], period=7)
            
            # Volatilidad reciente (último 7 días)
            recent_volatility = np.std(closes[-7:]) / np.mean(closes[-7:])
            
            # Análisis direccional
            momentum_score = 0.5  # Base neutral
            
            # Factor 1: SMA momentum (peso 40%)
            if sma_5 > sma_10 * 1.005:  # 0.5% por encima
                momentum_score += 0.2
            elif sma_5 < sma_10 * 0.995:  # 0.5% por debajo
                momentum_score -= 0.2
            
            # Factor 2: RSI presente continuo (peso 30%)
            if rsi_7 < 35:  # Oversold, probable rebote
                momentum_score += 0.15
            elif rsi_7 > 65:  # Overbought, probable corrección
                momentum_score -= 0.15
            
            # Factor 3: Volatilidad reciente (peso 20%)
            if recent_volatility > 0.03:  # Alta volatilidad = más movimiento
                momentum_score += 0.1 if sma_5 > sma_10 else -0.1
            
            # Factor 4: Precio vs SMA (peso 10%)
            price_vs_sma = current_price / sma_10
            if price_vs_sma > 1.02:
                momentum_score += 0.05
            elif price_vs_sma < 0.98:
                momentum_score -= 0.05
            
            # Determinar dirección y confianza
            if momentum_score >= 0.55:
                direction = 'bullish'
                confidence = min(momentum_score, 0.85)
            elif momentum_score <= 0.45:
                direction = 'bearish'
                confidence = min(1 - momentum_score, 0.85)
            else:
                direction = 'neutral'
                confidence = 0.5
            
            reasoning = f"SMA5/10: {sma_5/sma_10:.3f}, RSI7: {rsi_7:.1f}, Vol: {recent_volatility:.3f}"
            
            return {
                'direction': direction,
                'confidence': confidence,
                'momentum_score': momentum_score,
                'reasoning': reasoning,
                'rsi_7': rsi_7,
                'recent_volatility': recent_volatility * 100
            }
            
        except Exception as e:
            nexus_speak("error", f"❌ Market direction analysis failed: {e}")
            return {'direction': 'neutral', 'confidence': 0.5, 'reasoning': f'Error: {e}'}
    
    def calculate_rsi(self, prices, period=7):
        """Calcula RSI optimizado para presente continuo"""
        if len(prices) < period + 1:
            return 50  # Neutral si no hay suficientes datos
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def select_optimal_strategy(self, direction_analysis, market_data):
        """Selecciona estrategia óptima basada en análisis direccional"""
        direction = direction_analysis['direction']
        confidence = direction_analysis['confidence']
        current_price = market_data.get('current_price', 0)
        
        strategy_selection = {
            'strategy': None,
            'reasoning': '',
            'entry_params': {},
            'risk_level': 'medium'
        }
        
        # Lógica de selección de estrategia
        if direction == 'bullish' and confidence >= self.momentum_threshold:
            strategy_selection['strategy'] = 'long_call'
            strategy_selection['reasoning'] = f"Bullish momentum {confidence:.1%} - Long Call ATM"
            strategy_selection['entry_params'] = {
                'strike_target': current_price,  # ATM
                'strike_tolerance': self.atm_tolerance,
                'direction': 'CALL',
                'bullish_confidence': confidence
            }
            strategy_selection['risk_level'] = 'medium' if confidence < 0.7 else 'low'
            
        elif direction == 'bearish' and confidence >= self.momentum_threshold:
            strategy_selection['strategy'] = 'long_put'
            strategy_selection['reasoning'] = f"Bearish momentum {confidence:.1%} - Long Put ATM"
            strategy_selection['entry_params'] = {
                'strike_target': current_price,  # ATM
                'strike_tolerance': self.atm_tolerance,
                'direction': 'PUT',
                'bearish_confidence': confidence
            }
            strategy_selection['risk_level'] = 'medium' if confidence < 0.7 else 'low'
            
        elif direction == 'neutral' or confidence < self.momentum_threshold:
            # Neutral = use most probable direction with ITM option
            strategy_selection['strategy'] = 'long_call'  # Default to long_call for neutral
            strategy_selection['reasoning'] = f"Neutral/low confidence {confidence:.1%} - Long Call ITM for consistency"
            strategy_selection['entry_params'] = {
                'strike_target': current_price * 0.97,  # 3% ITM for consistency
                'strike_tolerance': 0.01,
                'direction': 'LONG_CALL_ITM',
                'consistency_strategy': True
            }
            strategy_selection['risk_level'] = 'low'
        
        return strategy_selection
    
    def calculate_expiration_targets(self):
        """Calcula fechas de expiración objetivo (7-14 días)"""
        today = datetime.now()
        
        # Buscar próximos viernes (opciones expiran viernes)
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:  # Si hoy es viernes
            days_until_friday = 7
        
        expiration_targets = []
        
        # Primera expiración (próximo viernes o siguiente)
        first_friday = today + timedelta(days=days_until_friday)
        if (first_friday - today).days >= self.min_days_to_expiry:
            expiration_targets.append(first_friday)
        
        # Segunda expiración (viernes siguiente)
        second_friday = first_friday + timedelta(days=7)
        if (second_friday - today).days <= self.max_days_to_expiry:
            expiration_targets.append(second_friday)
        
        return expiration_targets
    
    def generate_present_continuous_signal(self, symbol, market_data):
        """Genera señal completa para presente continuo"""
        try:
            nexus_speak("info", f"🎯 Analyzing {symbol} for present continuous options trading")
            
            # 1. Analizar dirección del mercado
            direction_analysis = self.analyze_market_direction(symbol, market_data)
            
            # 2. Seleccionar estrategia óptima
            strategy_selection = self.select_optimal_strategy(direction_analysis, market_data)
            
            # 3. Calcular expiraciones objetivo
            expiration_targets = self.calculate_expiration_targets()
            
            # 4. Compilar señal completa
            signal = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'trading_mode': 'PRESENT_CONTINUOUS',
                
                # Análisis direccional
                'market_direction': direction_analysis,
                
                # Estrategia seleccionada
                'selected_strategy': strategy_selection,
                
                # Configuración de entrada
                'entry_configuration': {
                    'max_days_to_expiry': self.max_days_to_expiry,
                    'min_days_to_expiry': self.min_days_to_expiry,
                    'atm_tolerance': self.atm_tolerance,
                    'expiration_targets': [exp.strftime('%Y-%m-%d') for exp in expiration_targets]
                },
                
                # Métricas de calidad
                'signal_quality': self.calculate_signal_quality(direction_analysis, strategy_selection),
                
                # Recomendación final
                'recommendation': self.generate_recommendation(direction_analysis, strategy_selection)
            }
            
            nexus_speak("success", f"✅ Present continuous signal generated for {symbol}")
            return signal
            
        except Exception as e:
            nexus_speak("error", f"❌ Present continuous signal generation failed: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'trading_mode': 'ERROR'
            }
    
    def calculate_signal_quality(self, direction_analysis, strategy_selection):
        """Calcula calidad de la señal para presente continuo"""
        base_quality = 50
        
        # Factor dirección (40 puntos)
        confidence = direction_analysis['confidence']
        if confidence >= 0.7:
            base_quality += 40
        elif confidence >= 0.6:
            base_quality += 30
        elif confidence >= 0.55:
            base_quality += 20
        else:
            base_quality += 10
        
        # Factor estrategia (30 puntos)
        if strategy_selection['strategy'] in ['long_call', 'long_put']:
            base_quality += 30  # Estrategias direccionales
        else:
            base_quality += 20  # Covered call
        
        # Factor riesgo (20 puntos)
        if strategy_selection['risk_level'] == 'low':
            base_quality += 20
        elif strategy_selection['risk_level'] == 'medium':
            base_quality += 15
        else:
            base_quality += 5
        
        # Factor RSI (10 puntos)
        rsi = direction_analysis.get('rsi_7', 50)
        if 35 <= rsi <= 65:  # RSI neutral = mejor para opciones cortas
            base_quality += 10
        else:
            base_quality += 5
        
        return min(100, max(0, base_quality))
    
    def generate_recommendation(self, direction_analysis, strategy_selection):
        """Genera recomendación final"""
        confidence = direction_analysis['confidence']
        strategy = strategy_selection['strategy']
        
        if strategy in ['long_call', 'long_put'] and confidence >= 0.7:
            return "STRONG_TRADE"
        elif strategy in ['long_call', 'long_put'] and confidence >= 0.6:
            return "MODERATE_TRADE"
        elif strategy in ['long_call', 'long_put'] and confidence >= 0.55:
            return "WEAK_TRADE"
        # Only long_call and long_put strategies allowed
        else:
            return "SKIP_TRADE"

# Test the present continuous engine
if __name__ == "__main__":
    print("🎯 TESTING PRESENT CONTINUOUS OPTIONS ENGINE")
    print("=" * 70)
    
    # Initialize engine
    engine = PresentContinuousOptionsEngine()
    
    # Mock market data for testing
    test_market_data = {
        'current_price': 637.50,
        'historical_data': {
            'Close': [620, 625, 630, 635, 640, 638, 636, 635, 637, 639, 641, 639, 637, 635, 637.50]
        }
    }
    
    # Generate signal
    signal = engine.generate_present_continuous_signal("SPY", test_market_data)
    
    print(f"\n📊 PRESENT CONTINUOUS SIGNAL FOR SPY:")
    print("=" * 50)
    
    if 'error' not in signal:
        print(f"Direction: {signal['market_direction']['direction'].upper()}")
        print(f"Confidence: {signal['market_direction']['confidence']:.1%}")
        print(f"Strategy: {signal['selected_strategy']['strategy'].upper()}")
        print(f"Reasoning: {signal['selected_strategy']['reasoning']}")
        print(f"Quality: {signal['signal_quality']}/100")
        print(f"Recommendation: {signal['recommendation']}")
        print(f"Days to expiry: {signal['entry_configuration']['min_days_to_expiry']}-{signal['entry_configuration']['max_days_to_expiry']}")
    else:
        print(f"❌ Error: {signal['error']}")
    
    print(f"\n✅ PRESENT CONTINUOUS ENGINE READY!")
    print("🎯 Focused on 7-14 day directional trades only!")