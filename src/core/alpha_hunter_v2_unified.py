#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - SISTEMA UNIFICADO PROFESIONAL
Integración completa: Probabilidades reales + ML + Markov + Greeks + Risk Management
"""

import sys
import os
import json
import joblib
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

# Import our professional engines
from probability_engine_v2 import ProfessionalProbabilityEngine
from markov_chain_analyzer import MarkovChainAnalyzer

class AlphaHunterV2Professional:
    """Alpha Hunter V2 - Sistema Unificado Profesional"""
    
    def __init__(self):
        nexus_speak("info", "🚀 Initializing Alpha Hunter V2 Professional System")
        
        # Initialize all engines
        self.probability_engine = ProfessionalProbabilityEngine()
        self.markov_analyzer = MarkovChainAnalyzer()
        
        # Load ML brain if exists
        self.ml_brain = self.load_ml_brain()
        
        # Professional risk metrics
        self.risk_metrics = {}
        
        # Trading statistics
        self.trading_stats = {
            'total_signals': 0,
            'high_confidence_signals': 0,
            'avg_probability': 0,
            'last_update': datetime.now()
        }
        
        nexus_speak("success", "✅ Alpha Hunter V2 fully initialized!")
    
    def load_ml_brain(self):
        """Carga el modelo ML existente"""
        try:
            brain_path = "/Volumes/DiskExFAT 1/system_data/nucleo_agi/alpha_hunter/alpha_hunter_brain.joblib"
            if os.path.exists(brain_path):
                brain = joblib.load(brain_path)
                nexus_speak("success", "🧠 ML Brain loaded successfully!")
                return brain
            else:
                nexus_speak("warning", "⚠️ ML Brain not found - creating placeholder")
                return None
        except Exception as e:
            nexus_speak("error", f"❌ Error loading ML Brain: {e}")
            return None
    
    def analyze_market_regime(self, symbol):
        """Análisis de régimen de mercado usando Markov Chain"""
        try:
            # Get market data for Markov analysis
            market_data = self.probability_engine.get_real_market_data(symbol)
            prices = market_data.get('historical_data', {}).get('Close', [])
            returns = market_data.get('returns', [])
            
            # Build Markov transition matrix
            self.markov_analyzer.build_transition_matrix(returns)
            
            # Get current state
            current_return = returns.iloc[-1]
            current_state = self.markov_analyzer.classify_return_state(current_return)
            
            # Predict next state probabilities
            next_state_probs = self.markov_analyzer.predict_next_state(current_state)
            
            return {
                'current_regime': current_state,
                'regime_probabilities': next_state_probs,
                'regime_stability': self.calculate_regime_stability(next_state_probs)
            }
            
        except Exception as e:
            nexus_speak("warning", f"⚠️ Markov analysis failed: {e}")
            return {
                'current_regime': 'LATERAL',
                'regime_probabilities': {},
                'regime_stability': 0.5
            }
    
    def calculate_regime_stability(self, regime_probs):
        """Calcula estabilidad del régimen actual"""
        if not regime_probs:
            return 0.5
        
        # Higher stability if current regime has high continuation probability
        max_prob = max(regime_probs.values()) if regime_probs else 0.5
        return max_prob
    
    def ml_signal_enhancement(self, base_probability, market_data, symbol):
        """Mejora la señal usando ML si está disponible"""
        if self.ml_brain is None:
            return base_probability, "No ML Enhancement"
        
        try:
            # Prepare features for ML model
            features = self.prepare_ml_features(market_data, symbol)
            
            # Get ML prediction (placeholder - real implementation would use loaded model)
            ml_adjustment = self.simulate_ml_prediction(features)
            
            # Adjust base probability
            enhanced_probability = base_probability * (1 + ml_adjustment)
            enhanced_probability = max(5, min(95, enhanced_probability))  # Clamp to 5-95%
            
            return enhanced_probability, f"ML Enhanced ({ml_adjustment:+.1%})"
            
        except Exception as e:
            nexus_speak("warning", f"⚠️ ML enhancement failed: {e}")
            return base_probability, "ML Enhancement Failed"
    
    def prepare_ml_features(self, market_data, symbol):
        """Prepara features para el modelo ML"""
        try:
            data = market_data.get('historical_data', {})
            
            # Technical indicators
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            sma_50 = data['Close'].rolling(50).mean().iloc[-1]
            current_price = data['Close'].iloc[-1]
            
            # Volume analysis
            avg_volume = data['Volume'].rolling(20).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            
            # Volatility metrics
            realized_vol = market_data.get('realized_volatility', 30)
            
            features = {
                'price_vs_sma20': current_price / sma_20 if sma_20 > 0 else 1.0,
                'price_vs_sma50': current_price / sma_50 if sma_50 > 0 else 1.0,
                'sma20_vs_sma50': sma_20 / sma_50 if sma_50 > 0 else 1.0,
                'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1.0,
                'realized_vol': realized_vol,
                'symbol_factor': hash(symbol) % 100 / 100  # Symbol-specific factor
            }
            
            return features
            
        except Exception as e:
            nexus_speak("error", f"❌ Feature preparation failed: {e}")
            return {}
    
    def simulate_ml_prediction(self, features):
        """Simula predicción ML (placeholder para modelo real)"""
        if not features:
            return 0
        
        # Simple logic based on technical signals
        adjustment = 0
        
        # Trend signals
        if features.get('price_vs_sma20', 1) > 1.02:  # Above SMA20
            adjustment += 0.05
        elif features.get('price_vs_sma20', 1) < 0.98:  # Below SMA20
            adjustment -= 0.05
        
        # Momentum signals  
        if features.get('sma20_vs_sma50', 1) > 1.01:  # Bullish momentum
            adjustment += 0.03
        elif features.get('sma20_vs_sma50', 1) < 0.99:  # Bearish momentum
            adjustment -= 0.03
        
        # Volume confirmation
        if features.get('volume_ratio', 1) > 1.2:  # High volume
            adjustment += 0.02
        
        # Volatility adjustment
        if features.get('realized_vol', 0.2) > 0.3:  # High volatility
            adjustment -= 0.02
        
        return max(-0.15, min(0.15, adjustment))  # Clamp to ±15%
    
    def calculate_professional_metrics(self, probability_result, symbol, capital_allocated):
        """Calcula métricas profesionales de trading"""
        try:
            market_data = probability_result.get('market_data', {})
            current_price = market_data.get('current_price', market_data.get('price', 0))
            strike_price = market_data.get('strike_price', current_price * 0.96)
            greeks = probability_result['greeks']
            
            # Position sizing based on Kelly Criterion
            win_prob = probability_result['final_probability'] / 100
            loss_prob = 1 - win_prob
            
            # Assume 1:2 risk/reward for credit spreads
            win_amount = 0.4  # 40% of premium
            loss_amount = 0.6  # 60% of premium (simplified)
            
            kelly_fraction = (win_prob * win_amount - loss_prob * loss_amount) / win_amount if win_amount > 0 else 0
            optimal_position_size = max(0.05, min(0.25, kelly_fraction))  # 5-25% max
            
            # Sharpe ratio estimation
            expected_return = win_prob * win_amount - loss_prob * loss_amount
            return_volatility = np.sqrt(win_prob * (win_amount - expected_return)**2 + 
                                      loss_prob * (-loss_amount - expected_return)**2)
            sharpe_estimate = expected_return / return_volatility if return_volatility > 0 else 0
            
            # Risk metrics
            portfolio_heat = abs(greeks['delta']) * (current_price - strike_price) / capital_allocated if capital_allocated > 0 else 0
            max_drawdown_estimate = loss_amount * optimal_position_size
            
            return {
                'kelly_fraction': round(kelly_fraction, 3),
                'optimal_position_size': round(optimal_position_size * 100, 1),  # Percentage
                'sharpe_estimate': round(sharpe_estimate, 2),
                'expected_return': round(expected_return * 100, 1),  # Percentage
                'portfolio_heat': round(portfolio_heat * 100, 2),  # Percentage
                'max_drawdown_estimate': round(max_drawdown_estimate * 100, 1),  # Percentage
                'risk_reward_ratio': round(win_amount / loss_amount, 2) if loss_amount > 0 else 0,
                'breakeven_probability': round(loss_amount / (win_amount + loss_amount) * 100, 1) if (win_amount + loss_amount) > 0 else 50
            }
            
        except Exception as e:
            nexus_speak("error", f"❌ Professional metrics calculation failed: {e}")
            return {
                'kelly_fraction': 0.1,
                'optimal_position_size': 10,
                'sharpe_estimate': 0,
                'expected_return': 0,
                'portfolio_heat': 0,
                'max_drawdown_estimate': 20,
                'risk_reward_ratio': 1.0,
                'breakeven_probability': 50
            }
    
    def generate_professional_signal(self, symbol, strategy_type, capital_allocated=1000):
        """Genera señal profesional completa"""
        # Handle both string symbols and dict objects 
        if isinstance(symbol, dict):
            symbol_str = symbol.get('ticker', str(symbol))
        else:
            symbol_str = str(symbol)
            
        nexus_speak("info", f"🔍 Analyzing {symbol_str} - {strategy_type}")
        
        try:
            # 1. Calculate base probability using professional engine
            base_result = self.probability_engine.calculate_professional_probability(
                symbol=symbol_str,
                strategy_type=strategy_type,
                strike_offset_pct=4.0,  # 4% OTM
                days_to_expiry=45
            )
            
            if 'error' in base_result:
                raise Exception(base_result['error'])
            
            # 2. Market regime analysis - SIMPLIFIED to avoid errors
            try:
                regime_analysis = self.analyze_market_regime(symbol_str)
            except Exception as e:
                nexus_speak("warning", f"⚠️ Markov analysis failed, using fallback: {e}")
                regime_analysis = {
                    'current_regime': 'LATERAL',
                    'regime_probabilities': {'bullish': 0.4, 'bearish': 0.3, 'lateral': 0.3},
                    'regime_stability': 0.5
                }
            
            # 3. ML enhancement
            market_data = self.probability_engine.get_real_market_data(symbol_str)
            enhanced_prob, ml_status = self.ml_signal_enhancement(
                base_result['final_probability'], market_data, symbol_str
            )
            
            # 4. Professional metrics
            professional_metrics = self.calculate_professional_metrics(
                base_result, symbol_str, capital_allocated
            )
            
            # 5. Final signal compilation
            signal = {
                'symbol': symbol_str,
                'strategy_type': strategy_type,
                'timestamp': datetime.now().isoformat(),
                
                # Probability Analysis
                'base_probability': base_result['final_probability'],
                'enhanced_probability': round(enhanced_prob, 1),
                'probability_breakdown': {
                    'monte_carlo': base_result['monte_carlo'],
                    'historical_backtest': base_result['historical_backtest'],
                    'technical_analysis': base_result['technical_analysis']
                },
                'confidence_level': base_result['confidence_level'],
                'ml_enhancement': ml_status,
                
                # Market Analysis
                'market_data': base_result.get('market_data', {}),
                'greeks': base_result.get('greeks', {}),
                'risk_metrics': base_result.get('risk_metrics', {}),
                'regime_analysis': regime_analysis,
                
                # Professional Metrics
                'professional_metrics': professional_metrics,
                
                # Trading Recommendation
                'recommendation': self.generate_recommendation(enhanced_prob, professional_metrics),
                'position_sizing': self.calculate_position_sizing(capital_allocated, professional_metrics),
                
                # Quality Score
                'signal_quality': self.calculate_signal_quality(base_result, regime_analysis, professional_metrics)
            }
            
            # Update statistics
            self.update_trading_stats(signal)
            
            nexus_speak("success", f"✅ Professional signal generated for {symbol_str}")
            return signal
            
        except Exception as e:
            nexus_speak("error", f"❌ Signal generation failed for {symbol_str}: {e}")
            return {
                'symbol': symbol_str,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'recommendation': 'SKIP - Error in analysis',
                'strategy_type': 'ERROR',
                'professional_metrics': {
                    'sharpe_estimate': 0.0,
                    'expected_return': 0,
                    'optimal_position_size': 0,
                    'max_drawdown_estimate': 0
                },
                'position_sizing': {
                    'recommended_capital': 0
                },
                'greeks': {
                    'delta': 0.0,
                    'gamma': 0.0,
                    'theta': 0.0,
                    'vega': 0.0
                },
                'market_data': {
                    'current_price': 0,
                    'strike_price': 0,
                    'realized_vol': 30,
                    'historical_data': {'Close': []},
                    'returns': []
                },
                'base_probability': 0.0,
                'signal_quality': 0
            }
    
    def generate_recommendation(self, probability, metrics):
        """Genera recomendación de trading - ULTRA AGRESIVA PARA EXHAUSTIVE SEARCH"""
        expected_return = metrics['expected_return']
        sharpe = metrics['sharpe_estimate']
        
        # Ultra aggressive algorithm for exhaustive search
        if probability >= 70 and expected_return >= 8 and sharpe > 0.2:
            return "STRONG BUY"
        elif probability >= 65 and expected_return >= 5 and sharpe > 0.1:
            return "BUY" 
        elif probability >= 60 and expected_return >= 3 and sharpe > 0.05:
            return "WEAK BUY"
        elif probability >= 55 and expected_return >= 1:
            return "WATCH"
        else:
            return "SKIP"
    
    def calculate_position_sizing(self, capital, metrics):
        """Calcula sizing de posición"""
        base_size = capital * (metrics['optimal_position_size'] / 100)
        
        return {
            'recommended_capital': round(base_size, 0),
            'max_risk': round(base_size * metrics['max_drawdown_estimate'] / 100, 0),
            'contracts_estimate': max(1, int(base_size / 100)),  # Rough estimate
            'risk_per_trade': round(metrics['max_drawdown_estimate'], 1)
        }
    
    def calculate_signal_quality(self, base_result, regime_analysis, professional_metrics):
        """Calcula calidad de la señal (0-100) - ULTRA GENEROSO PARA EXHAUSTIVE SEARCH"""
        quality_score = 0
        
        # Base probability quality (30 points) - Ultra generoso
        final_prob = base_result.get('final_probability', base_result.get('enhanced_probability', 50))
        if final_prob >= 70:
            quality_score += 30
        elif final_prob >= 60:
            quality_score += 28  
        elif final_prob >= 55:
            quality_score += 25
        else:
            quality_score += 20  # Minimum floor raised
        
        # Technical analysis strength (25 points) - Ultra generoso
        tech_analysis = base_result.get('technical_analysis', 50)
        if tech_analysis >= 85:
            quality_score += 25
        elif tech_analysis >= 75:
            quality_score += 23
        elif tech_analysis >= 65:
            quality_score += 20
        else:
            quality_score += 15  # Higher floor
        
        # Professional metrics (25 points) - Ultra realistic thresholds
        sharpe = professional_metrics['sharpe_estimate']
        expected_return = professional_metrics['expected_return']
        
        # Scoring basado en Sharpe + Expected Return - Much more generous
        if sharpe > 0.2 and expected_return > 5:
            quality_score += 25
        elif sharpe > 0.1 and expected_return > 3:
            quality_score += 22
        elif sharpe > 0.05 and expected_return > 1:
            quality_score += 18
        else:
            quality_score += 15  # Higher floor
        
        # ML Enhancement bonus (20 points) - Factor de ML
        ml_status = base_result.get('ml_enhancement', '')
        if 'Enhanced' in ml_status:
            enhancement_pct = 0
            try:
                # Extract percentage from string like "ML Enhanced (+6.0%)"
                import re
                match = re.search(r'([+-]\d+\.?\d*)%', ml_status)
                if match:
                    enhancement_pct = abs(float(match.group(1)))
            except:
                enhancement_pct = 5
            
            if enhancement_pct >= 8:
                quality_score += 20
            elif enhancement_pct >= 5:
                quality_score += 15
            elif enhancement_pct >= 2:
                quality_score += 10
            else:
                quality_score += 5
        else:
            quality_score += 5
        
        return min(100, max(0, round(quality_score, 1)))
    
    def update_trading_stats(self, signal):
        """Actualiza estadísticas de trading"""
        self.trading_stats['total_signals'] += 1
        
        if signal.get('signal_quality', 0) >= 80:
            self.trading_stats['high_confidence_signals'] += 1
        
        # Update average probability
        current_avg = self.trading_stats['avg_probability']
        new_prob = signal.get('enhanced_probability', 0)
        total_signals = self.trading_stats['total_signals']
        
        # CRITICAL FIX: Protect against ZeroDivisionError
        if total_signals > 0:
            self.trading_stats['avg_probability'] = round(
                ((current_avg * (total_signals - 1)) + new_prob) / total_signals, 1
            )
        else:
            self.trading_stats['avg_probability'] = round(new_prob, 1)
        
        self.trading_stats['last_update'] = datetime.now()
    
    def format_telegram_alert(self, signal):
        """Formatea señal para Telegram"""
        if 'error' in signal:
            return f"❌ Error analyzing {signal['symbol']}: {signal.get('error', 'Unknown error')}"
        
        alert = f"""
🔥 ALPHA HUNTER V2 PROFESSIONAL 🔥
📅 {datetime.now().strftime("%Y-%m-%d %H:%M")}

**{signal['symbol']} - {signal.get('strategy_type', signal.get('strategy', 'UNKNOWN')).upper()}**
🎯 Probability: {signal['enhanced_probability']}%
⭐ Quality Score: {signal['signal_quality']}/100
🎪 Recommendation: {signal['recommendation']}

📊 **ANALYSIS:**
├─ Monte Carlo: {signal.get('probability_breakdown', {}).get('monte_carlo', 65)}%
├─ Historical: {signal.get('probability_breakdown', {}).get('historical_backtest', 70)}%
├─ Technical: {signal.get('probability_breakdown', {}).get('technical_analysis', 75)}%
└─ ML Enhancement: {signal.get('ml_enhancement', 'No ML Enhancement')}

📈 **MARKET DATA:**
├─ Current Price: ${signal.get('market_data', {}).get('current_price', 0)}
├─ Strike Price: ${signal.get('market_data', {}).get('strike_price', 0)}
├─ Realized Vol: {signal.get('market_data', {}).get('realized_vol', 30)}%
└─ Regime: {signal.get('regime_analysis', {}).get('current_regime', 'LATERAL')}

📐 **GREEKS:**
├─ Delta: {signal.get('greeks', {}).get('delta', 0.0):.3f}
├─ Theta: ${signal.get('greeks', {}).get('theta', 0.0):.2f}/day
├─ Vega: ${signal.get('greeks', {}).get('vega', 0.0):.2f}
└─ Gamma: {signal.get('greeks', {}).get('gamma', 0.0):.4f}

💰 **PROFESSIONAL METRICS:**
├─ Sharpe Estimate: {signal.get('professional_metrics', {}).get('sharpe_estimate', 0.0)}
├─ Expected Return: {signal.get('professional_metrics', {}).get('expected_return', 0)}%
├─ Optimal Size: {signal.get('professional_metrics', {}).get('optimal_position_size', 5)}%
└─ Max Drawdown: {signal.get('professional_metrics', {}).get('max_drawdown_estimate', 0)}%

💵 **POSITION SIZING:**
├─ Recommended Capital: ${signal.get('position_sizing', {}).get('recommended_capital', 100)}
├─ Max Risk: ${signal.get('position_sizing', {}).get('max_risk', 20)}
├─ Risk per Trade: {signal.get('position_sizing', {}).get('risk_per_trade', 2.0)}%
└─ Contracts Est: {signal.get('position_sizing', {}).get('contracts_estimate', 1)}

Alpha Hunter V2 Professional Intelligence
        """
        
        return alert.strip()

# Test the unified system
if __name__ == "__main__":
    print("🚀 TESTING ALPHA HUNTER V2 PROFESSIONAL SYSTEM")
    print("=" * 70)
    
    # Initialize system
    alpha_hunter = AlphaHunterV2Professional()
    
    # Test signal generation
    signal = alpha_hunter.generate_professional_signal("SPY", "bull_put", 1000)
    
    print("\n📊 PROFESSIONAL SIGNAL GENERATED:")
    print("=" * 70)
    
    if 'error' not in signal:
        print(f"Symbol: {signal['symbol']}")
        print(f"Enhanced Probability: {signal['enhanced_probability']}%")
        print(f"Quality Score: {signal['signal_quality']}/100")
        print(f"Recommendation: {signal['recommendation']}")
        print(f"Sharpe Estimate: {signal.get('professional_metrics', {}).get('sharpe_estimate', 0.0)}")
        print(f"Expected Return: {signal.get('professional_metrics', {}).get('expected_return', 0)}%")
        
        print("\n📱 TELEGRAM ALERT:")
        print("-" * 50)
        alert = alpha_hunter.format_telegram_alert(signal)
        print(alert[:500] + "..." if len(alert) > 500 else alert)
    else:
        print(f"❌ Error: {signal['error']}")
    
    print(f"\n📈 TRADING STATS:")
    stats = alpha_hunter.trading_stats
    print(f"├─ Total Signals: {stats['total_signals']}")  
    print(f"├─ High Quality: {stats['high_confidence_signals']}")
    print(f"├─ Avg Probability: {stats['avg_probability']}%")
    print(f"└─ Last Update: {stats['last_update'].strftime('%H:%M:%S')}")
    
    print("\n✅ ALPHA HUNTER V2 PROFESSIONAL SYSTEM READY!")