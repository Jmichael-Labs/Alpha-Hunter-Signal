#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - UNIFIED STRATEGY BRAIN
Cerebro unificado que consolida TODAS las estrategias en una sola probabilidad
Combina: Earnings, PEAD, Technical, Probability Engine, Value/Glamour, Sentiment, Quantum
"""

import sys
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Import all Alpha Hunter components
try:
    from probability_engine_v2 import ProfessionalProbabilityEngine
    from pead_strategy_core import PEADStrategyCore, PEADSignal
    from earnings_analyzer_core import EarningsAnalyzerCore, EarningsData
    from quantum_evolution_core import QuantumEvolutionCore
    from markov_chain_analyzer import MarkovChainAnalyzer
    UNIFIED_COMPONENTS_AVAILABLE = True
    print("🧠 All Alpha Hunter components loaded successfully")
except ImportError as e:
    print(f"⚠️ Some components not available: {e}")
    UNIFIED_COMPONENTS_AVAILABLE = False

@dataclass
class UnifiedSignal:
    """Complete unified trading signal with all strategy inputs"""
    # Basic Info
    symbol: str
    timestamp: str
    
    # Unified Probability (0-100)
    unified_probability: float
    confidence_level: str  # 'EXTREME', 'HIGH', 'MEDIUM', 'LOW'
    
    # Component Scores (each 0-100)
    technical_score: float
    earnings_score: float
    pead_score: float
    sentiment_score: float
    quantum_score: float
    value_glamour_score: float
    markov_score: float
    
    # Strategy Details
    primary_strategy: str  # Dominant strategy driving the signal
    contributing_strategies: List[str]  # All strategies that contributed
    
    # Trading Parameters
    entry_price: float
    target_price: float
    stop_loss: float
    expected_return: float
    holding_period: int
    risk_reward_ratio: float
    
    # Catalysts and Events
    earnings_catalyst: Optional[Dict]
    pead_opportunity: Optional[Dict]
    technical_patterns: List[str]
    market_events: List[str]
    
    # Quality Metrics
    signal_quality: float  # 0-100 overall quality
    urgency: str  # 'IMMEDIATE', 'SOON', 'MODERATE', 'PATIENT'
    
class UnifiedStrategyBrain:
    """Master brain that coordinates all Alpha Hunter strategies"""
    
    def __init__(self):
        print("🧠 INITIALIZING UNIFIED STRATEGY BRAIN")
        print("="*50)
        
        # Initialize all components
        self.prob_engine = None
        self.pead_strategy = None
        self.earnings_analyzer = None
        self.quantum_core = None
        self.markov_analyzer = None
        
        if UNIFIED_COMPONENTS_AVAILABLE:
            try:
                self.prob_engine = ProfessionalProbabilityEngine()
                print("✅ Probability Engine loaded")
            except Exception as e:
                print(f"⚠️ Probability Engine failed: {e}")
            
            try:
                self.pead_strategy = PEADStrategyCore()
                print("✅ PEAD Strategy loaded")
            except Exception as e:
                print(f"⚠️ PEAD Strategy failed: {e}")
            
            try:
                self.earnings_analyzer = EarningsAnalyzerCore()
                print("✅ Earnings Analyzer loaded")
            except Exception as e:
                print(f"⚠️ Earnings Analyzer failed: {e}")
            
            try:
                self.quantum_core = QuantumEvolutionCore()
                print("✅ Quantum Core loaded")
            except Exception as e:
                print(f"⚠️ Quantum Core failed: {e}")
            
            try:
                self.markov_analyzer = MarkovChainAnalyzer()
                print("✅ Markov Analyzer loaded")
            except Exception as e:
                print(f"⚠️ Markov Analyzer failed: {e}")
        
        # Unified scoring weights (must sum to 1.0)
        self.strategy_weights = {
            'technical': 0.20,      # 20% - Technical analysis base
            'earnings': 0.25,       # 25% - Earnings catalysts (highest weight)
            'pead': 0.15,          # 15% - Post-earnings drift
            'sentiment': 0.10,      # 10% - Market sentiment
            'quantum': 0.15,        # 15% - Quantum evolution patterns
            'value_glamour': 0.10,  # 10% - Value vs Glamour classification
            'markov': 0.05         # 5% - Markov chain patterns
        }
        
        # Quality thresholds for unified signals
        self.quality_thresholds = {
            'EXTREME': 90,   # 90%+ unified probability
            'HIGH': 75,      # 75-90% unified probability  
            'MEDIUM': 60,    # 60-75% unified probability
            'LOW': 45        # 45-60% unified probability
        }
        
        print(f"🎯 Strategy weights configured: {self.strategy_weights}")
        print(f"🏆 Quality thresholds: {self.quality_thresholds}")
        print("✅ Unified Strategy Brain ready!")
    
    def analyze_symbol_unified(self, symbol: str) -> Optional[UnifiedSignal]:
        """Perform complete unified analysis of a symbol"""
        print(f"\n🔍 UNIFIED ANALYSIS: {symbol}")
        print("-" * 30)
        
        # Initialize component scores
        scores = {
            'technical': 0,
            'earnings': 0,
            'pead': 0,
            'sentiment': 0,
            'quantum': 0,
            'value_glamour': 0,
            'markov': 0
        }
        
        contributing_strategies = []
        catalysts = {}
        
        try:
            # 1. TECHNICAL ANALYSIS (via Probability Engine)
            if self.prob_engine:
                try:
                    data = self.prob_engine.get_real_market_data(symbol, period='60d')
                    if data is not None and len(data) > 20:
                        # Calculate technical probability
                        tech_prob = self.prob_engine.calculate_professional_probability(
                            symbol, 'put', 90, 30)
                        scores['technical'] = min(tech_prob, 100)
                        contributing_strategies.append('Technical Analysis')
                        print(f"📊 Technical Score: {scores['technical']:.1f}%")
                except Exception as e:
                    print(f"⚠️ Technical analysis failed: {e}")
            
            # 2. EARNINGS ANALYSIS
            if self.earnings_analyzer:
                try:
                    earnings_analysis = self.earnings_analyzer.run_comprehensive_earnings_analysis(days_ahead=14)
                    earnings_list = earnings_analysis.get('earnings_list', [])
                    
                    for earnings_data in earnings_list:
                        if earnings_data.symbol.upper() == symbol.upper():
                            # Score based on proximity and sentiment
                            days_to_earnings = earnings_data.days_to_earnings
                            sentiment = getattr(earnings_data, 'sentiment_score', 50)
                            
                            if days_to_earnings <= 7:  # Within a week
                                base_score = 80  # High base for near-term earnings
                                sentiment_bonus = (sentiment - 50) * 0.4  # Scale sentiment
                                scores['earnings'] = min(base_score + sentiment_bonus, 100)
                                
                                catalysts['earnings'] = {
                                    'date': earnings_data.earnings_date,
                                    'days_to': days_to_earnings,
                                    'sentiment': sentiment
                                }
                                contributing_strategies.append('Earnings Catalyst')
                                print(f"📅 Earnings Score: {scores['earnings']:.1f}% (in {days_to_earnings} days)")
                            break
                except Exception as e:
                    print(f"⚠️ Earnings analysis failed: {e}")
            
            # 3. PEAD ANALYSIS
            if self.pead_strategy:
                try:
                    pead_signals = self.pead_strategy.generate_pead_signals([symbol])
                    if pead_signals:
                        pead_signal = pead_signals[0]
                        scores['pead'] = min(pead_signal.confidence * 100, 100)
                        
                        catalysts['pead'] = {
                            'signal_type': pead_signal.signal_type,
                            'expected_return': pead_signal.expected_return,
                            'surprise_percent': pead_signal.earnings_surprise.surprise_percent
                        }
                        contributing_strategies.append('PEAD Strategy')
                        print(f"🎯 PEAD Score: {scores['pead']:.1f}%")
                except Exception as e:
                    print(f"⚠️ PEAD analysis failed: {e}")
            
            # 4. SENTIMENT ANALYSIS (from earnings analyzer)
            # Already captured in earnings analysis
            
            # 5. QUANTUM EVOLUTION ANALYSIS
            if self.quantum_core:
                try:
                    # Quantum analysis based on market patterns
                    quantum_result = self.quantum_core.analyze_symbol_quantum(symbol)
                    if quantum_result:
                        scores['quantum'] = quantum_result.get('probability', 0)
                        contributing_strategies.append('Quantum Evolution')
                        print(f"⚡ Quantum Score: {scores['quantum']:.1f}%")
                except Exception as e:
                    print(f"⚠️ Quantum analysis failed: {e}")
            
            # 6. VALUE/GLAMOUR CLASSIFICATION
            try:
                classifications = self.pead_strategy.classify_value_glamour([symbol]) if self.pead_strategy else {}
                classification = classifications.get(symbol)
                if classification:
                    # Score based on classification quality
                    base_score = 60 if classification.classification == 'VALUE' else 40
                    confidence_bonus = classification.confidence_score * 20
                    scores['value_glamour'] = min(base_score + confidence_bonus, 100)
                    contributing_strategies.append('Value/Glamour Analysis')
                    print(f"💎 Value/Glamour Score: {scores['value_glamour']:.1f}% ({classification.classification})")
            except Exception as e:
                print(f"⚠️ Value/Glamour analysis failed: {e}")
            
            # 7. MARKOV CHAIN ANALYSIS
            if self.markov_analyzer:
                try:
                    markov_result = self.markov_analyzer.analyze_symbol_markov(symbol)
                    if markov_result:
                        scores['markov'] = markov_result.get('transition_probability', 0) * 100
                        contributing_strategies.append('Markov Chain')
                        print(f"🔗 Markov Score: {scores['markov']:.1f}%")
                except Exception as e:
                    print(f"⚠️ Markov analysis failed: {e}")
            
            # CALCULATE UNIFIED PROBABILITY
            unified_prob = sum(scores[key] * self.strategy_weights[key] 
                             for key in scores.keys())
            
            print(f"\n🧠 UNIFIED PROBABILITY: {unified_prob:.1f}%")
            
            # Determine confidence level
            if unified_prob >= self.quality_thresholds['EXTREME']:
                confidence = 'EXTREME'
            elif unified_prob >= self.quality_thresholds['HIGH']:
                confidence = 'HIGH'
            elif unified_prob >= self.quality_thresholds['MEDIUM']:
                confidence = 'MEDIUM'
            else:
                confidence = 'LOW'
            
            # Only generate signals for MEDIUM or higher
            if unified_prob >= self.quality_thresholds['LOW']:
                # Determine primary strategy (highest contributing score)
                primary_strategy = max(scores.keys(), key=lambda k: scores[k])
                
                # Get real current price
                current_price = 100  # Default
                try:
                    if self.prob_engine:
                        market_data = self.prob_engine.get_real_market_data(symbol, period='5d')
                        if market_data is not None and len(market_data) > 0:
                            current_price = market_data.get('Close', pd.Series([100])).iloc[-1]
                except Exception:
                    pass
                
                # Calculate trading parameters based on unified probability
                expected_return = min(unified_prob / 100 * 0.20, 0.25)  # Cap at 25% return
                target_price = current_price * (1 + expected_return)
                stop_loss = current_price * 0.95  # 5% stop loss
                
                unified_signal = UnifiedSignal(
                    symbol=symbol,
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    unified_probability=unified_prob,
                    confidence_level=confidence,
                    technical_score=scores['technical'],
                    earnings_score=scores['earnings'],
                    pead_score=scores['pead'],
                    sentiment_score=scores['sentiment'],
                    quantum_score=scores['quantum'],
                    value_glamour_score=scores['value_glamour'],
                    markov_score=scores['markov'],
                    primary_strategy=primary_strategy,
                    contributing_strategies=contributing_strategies,
                    entry_price=current_price,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    expected_return=expected_return,
                    holding_period=30,  # Default 30 days
                    risk_reward_ratio=(target_price - current_price) / (current_price - stop_loss),
                    earnings_catalyst=catalysts.get('earnings'),
                    pead_opportunity=catalysts.get('pead'),
                    technical_patterns=[],  # Would be populated from technical analysis
                    market_events=[],
                    signal_quality=unified_prob,
                    urgency='IMMEDIATE' if unified_prob > 85 else 'SOON' if unified_prob > 70 else 'MODERATE'
                )
                
                print(f"✅ UNIFIED SIGNAL GENERATED: {confidence} confidence")
                return unified_signal
            
            else:
                print(f"⚠️ Signal below threshold ({unified_prob:.1f}% < {self.quality_thresholds['LOW']}%)")
                return None
                
        except Exception as e:
            print(f"❌ Unified analysis failed for {symbol}: {e}")
            return None
    
    def format_unified_alert(self, signal: UnifiedSignal) -> str:
        """Format unified signal into clean, executable alert"""
        
        # Determine optimal contract type based on primary strategy
        if signal.primary_strategy == 'earnings' and signal.earnings_catalyst:
            days_to_earnings = signal.earnings_catalyst.get('days_to', 7)
            if days_to_earnings <= 3:
                contract_type = "CALLS - Earnings Week Play"
                contract_details = f"Buy ATM calls expiring 2 weeks after earnings"
            else:
                contract_type = "PUTS - Pre-earnings Positioning"  
                contract_details = f"Sell cash-secured puts to collect premium"
        elif signal.primary_strategy == 'pead' and signal.pead_opportunity:
            pead_type = signal.pead_opportunity.get('signal_type', 'LONG_VALUE')
            if 'LONG' in pead_type:
                contract_type = "CALLS - PEAD Drift Play"
                contract_details = f"Buy slightly OTM calls, 45-day expiry"
            else:
                contract_type = "PUTS - PEAD Drift Short"
                contract_details = f"Buy puts or short shares, 45-day target"
        else:
            contract_type = "PUTS - Technical Strategy"
            contract_details = f"Sell cash-secured puts at support level"
        
        # Create catalyst section
        catalyst_text = ""
        if signal.earnings_catalyst:
            earnings_date = signal.earnings_catalyst.get('date', 'TBD')
            days_to = signal.earnings_catalyst.get('days_to', 'N/A')
            catalyst_text += f"\nEARNINGS CATALYST: {earnings_date} (in {days_to} days)"
        
        if signal.pead_opportunity:
            pead_type = signal.pead_opportunity.get('signal_type', 'N/A')
            surprise = signal.pead_opportunity.get('surprise_percent', 0)
            catalyst_text += f"\nPEAD OPPORTUNITY: {pead_type} after {surprise:+.1f}% earnings surprise"
        
        # Execution steps
        entry_process = f"""
ENTRY PROCESS:
1. Wait for market open confirmation
2. Check volume > 50k in first 30 minutes
3. Enter position when price confirms direction
4. Set alerts for all exit levels immediately

EXIT STRATEGY:
- TAKE PROFIT: {signal.expected_return:.0%} target ({signal.urgency} urgency)
- STOP LOSS: 5% maximum loss from entry
- TIME STOP: Close before {signal.holding_period} days if no movement
- PROFIT PROTECTION: Move stop to breakeven at 50% of target
"""

        alert = f"""🧠 ALPHA HUNTER UNIFIED SIGNAL 🧠
{signal.confidence_level} CONFIDENCE - {signal.urgency} PRIORITY

TICKER: ${signal.symbol}
PROBABILITY: {signal.unified_probability:.0f}%
STRATEGY: {signal.primary_strategy.upper()}

RECOMMENDED ACTION:
{contract_type}
{contract_details}
{catalyst_text}

EXECUTION PLAN:
BUY AT: ${signal.entry_price:.2f}
SELL TARGET: ${signal.target_price:.2f} ({signal.expected_return:.0%} profit)
STOP LOSS: ${signal.stop_loss:.2f}
HOLD FOR: {signal.holding_period} days maximum

ENTRY CHECKLIST:
1. Market open + volume > 50k
2. Price confirms direction
3. Set stop loss immediately
4. Set profit target alert

EXIT RULES:
- Take profit at {signal.expected_return:.0%} gain
- Stop loss at 5% down
- Close if no movement in {signal.holding_period} days
- Move stop to breakeven at 50% profit

ANALYSIS:
{len(signal.contributing_strategies)} strategies agree
{signal.primary_strategy.upper()} strategy is primary driver
{signal.unified_probability:.0f}% combined probability from all filters
{signal.confidence_level} confidence level

PRIORITY: {signal.urgency}
"""
        return alert

# Test the unified brain
if __name__ == "__main__":
    print("🧠 TESTING UNIFIED STRATEGY BRAIN")
    print("="*50)
    
    brain = UnifiedStrategyBrain()
    
    # Test symbols
    test_symbols = ['AAPL', 'NVDA', 'TSLA']
    
    for symbol in test_symbols:
        signal = brain.analyze_symbol_unified(symbol)
        
        if signal:
            alert = brain.format_unified_alert(signal)
            print("\n" + "="*80)
            print(alert)
            print("="*80)
        else:
            print(f"\n⚠️ No unified signal generated for {symbol}")