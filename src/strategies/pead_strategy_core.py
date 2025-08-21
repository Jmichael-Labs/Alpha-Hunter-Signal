#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - POST-EARNINGS-ANNOUNCEMENT DRIFT (PEAD) STRATEGY
Implementation of PEAD strategy targeting 17-19% annualized returns
Based on academic research and market anomaly exploitation
"""

import sys
import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import yfinance as yf

@dataclass
class EarningsSurprise:
    """Data structure for earnings surprise analysis"""
    symbol: str
    earnings_date: str
    actual_eps: float
    estimated_eps: float
    surprise_percent: float
    surprise_magnitude: str  # 'POSITIVE', 'NEGATIVE', 'NEUTRAL'
    revenue_actual: float
    revenue_estimate: float
    revenue_surprise: float
    
@dataclass
class ValueGlamourClassification:
    """Classification of stocks into Value vs Glamour"""
    symbol: str
    classification: str  # 'VALUE', 'GLAMOUR', 'NEUTRAL'
    pe_ratio: float
    pb_ratio: float
    ear_ratio: float  # Earnings-to-Price Ratio
    confidence_score: float
    
@dataclass
class PEADSignal:
    """Complete PEAD trading signal"""
    symbol: str
    signal_type: str  # 'LONG_VALUE', 'SHORT_GLAMOUR', 'SKIP'
    earnings_surprise: EarningsSurprise
    value_glamour: ValueGlamourClassification
    expected_return: float
    holding_period: int  # days
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float

class PEADStrategyCore:
    """Core implementation of Post-Earnings-Announcement Drift strategy"""
    
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_KEY')
        if not self.api_key:
            # Try to load from env file
            env_path = os.path.expanduser('~/.gemini_keys.env')
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        if line.strip().startswith('ALPHA_VANTAGE_KEY='):
                            self.api_key = line.strip().split('=')[1].strip('"')
                            break
        
        # PEAD Strategy Configuration
        self.surprise_threshold = 5.0  # Minimum 5% surprise to trigger
        self.holding_period_days = 45  # 45-day drift tracking
        self.max_positions = 10
        self.position_size = 0.1  # 10% per position
        
        # Value vs Glamour thresholds (based on academic research)
        self.value_thresholds = {
            'pe_max': 15.0,  # P/E < 15 = Value
            'pb_max': 1.5,   # P/B < 1.5 = Value  
            'ear_min': 0.08  # EAR > 8% = Value
        }
        
        self.glamour_thresholds = {
            'pe_min': 25.0,  # P/E > 25 = Glamour
            'pb_min': 3.0,   # P/B > 3 = Glamour
            'ear_max': 0.04  # EAR < 4% = Glamour
        }
        
        print("🎯 PEAD Strategy Core initialized")
        print(f"📊 Targeting 17-19% annualized returns")
        print(f"⏰ {self.holding_period_days}-day drift tracking")
    
    def detect_earnings_surprises(self, symbols: List[str], lookback_days: int = 7) -> List[EarningsSurprise]:
        """Detect significant earnings surprises in the last N days"""
        surprises = []
        
        for symbol in symbols:
            try:
                # Get recent earnings data
                ticker = yf.Ticker(symbol)
                earnings = ticker.earnings_dates
                
                if earnings is None or earnings.empty:
                    continue
                
                # Filter recent earnings (last 7 days)
                recent_date = datetime.now() - timedelta(days=lookback_days)
                recent_earnings = earnings[earnings.index >= recent_date]
                
                if recent_earnings.empty:
                    continue
                
                for date, row in recent_earnings.iterrows():
                    if pd.isna(row.get('EPS Estimate')) or pd.isna(row.get('Reported EPS')):
                        continue
                    
                    actual_eps = row['Reported EPS']
                    estimated_eps = row['EPS Estimate']
                    
                    if estimated_eps != 0:
                        surprise_percent = ((actual_eps - estimated_eps) / abs(estimated_eps)) * 100
                    else:
                        continue
                    
                    # Only process significant surprises
                    if abs(surprise_percent) >= self.surprise_threshold:
                        surprise_magnitude = 'POSITIVE' if surprise_percent > 0 else 'NEGATIVE'
                        
                        surprise = EarningsSurprise(
                            symbol=symbol,
                            earnings_date=date.strftime('%Y-%m-%d'),
                            actual_eps=actual_eps,
                            estimated_eps=estimated_eps,
                            surprise_percent=surprise_percent,
                            surprise_magnitude=surprise_magnitude,
                            revenue_actual=0,  # Would need additional API for revenue data
                            revenue_estimate=0,
                            revenue_surprise=0
                        )
                        surprises.append(surprise)
                        
                        print(f"🎯 {symbol}: {surprise_percent:+.1f}% earnings surprise detected")
                
            except Exception as e:
                print(f"⚠️ Error getting earnings for {symbol}: {e}")
                continue
        
        return surprises
    
    def classify_value_glamour(self, symbols: List[str]) -> Dict[str, ValueGlamourClassification]:
        """Classify stocks as Value, Glamour, or Neutral"""
        classifications = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Get financial ratios
                pe_ratio = info.get('forwardPE', info.get('trailingPE', 0))
                pb_ratio = info.get('priceToBook', 0)
                
                # Calculate EAR (Earnings-to-Price Ratio) = 1/PE
                ear_ratio = 1.0 / pe_ratio if pe_ratio and pe_ratio > 0 else 0
                
                # Classification logic based on academic research
                value_score = 0
                glamour_score = 0
                
                if pe_ratio and pe_ratio <= self.value_thresholds['pe_max']:
                    value_score += 1
                if pe_ratio and pe_ratio >= self.glamour_thresholds['pe_min']:
                    glamour_score += 1
                
                if pb_ratio and pb_ratio <= self.value_thresholds['pb_max']:
                    value_score += 1
                if pb_ratio and pb_ratio >= self.glamour_thresholds['pb_min']:
                    glamour_score += 1
                
                if ear_ratio >= self.value_thresholds['ear_min']:
                    value_score += 1
                if ear_ratio <= self.glamour_thresholds['ear_max']:
                    glamour_score += 1
                
                # Determine classification
                if value_score >= 2:
                    classification = 'VALUE'
                    confidence = value_score / 3.0
                elif glamour_score >= 2:
                    classification = 'GLAMOUR'
                    confidence = glamour_score / 3.0
                else:
                    classification = 'NEUTRAL'
                    confidence = 0.5
                
                classifications[symbol] = ValueGlamourClassification(
                    symbol=symbol,
                    classification=classification,
                    pe_ratio=pe_ratio or 0,
                    pb_ratio=pb_ratio or 0,
                    ear_ratio=ear_ratio,
                    confidence_score=confidence
                )
                
                print(f"📊 {symbol}: {classification} (P/E: {pe_ratio:.1f}, P/B: {pb_ratio:.1f})")
                
            except Exception as e:
                print(f"⚠️ Error classifying {symbol}: {e}")
                continue
        
        return classifications
    
    def generate_pead_signals(self, symbols: List[str]) -> List[PEADSignal]:
        """Generate PEAD trading signals based on earnings surprises and value/glamour classification"""
        print("🚀 Generating PEAD signals...")
        
        # Step 1: Detect earnings surprises
        surprises = self.detect_earnings_surprises(symbols)
        if not surprises:
            print("⚠️ No significant earnings surprises found")
            return []
        
        # Step 2: Classify value vs glamour
        surprise_symbols = [s.symbol for s in surprises]
        classifications = self.classify_value_glamour(surprise_symbols)
        
        # Step 3: Generate trading signals
        signals = []
        
        for surprise in surprises:
            symbol = surprise.symbol
            classification = classifications.get(symbol)
            
            if not classification:
                continue
            
            # PEAD Strategy Logic:
            # Long Value stocks with positive surprises
            # Short Glamour stocks with negative surprises
            signal_type = 'SKIP'
            expected_return = 0
            
            if (surprise.surprise_magnitude == 'POSITIVE' and 
                classification.classification == 'VALUE'):
                signal_type = 'LONG_VALUE'
                expected_return = 0.15 + (abs(surprise.surprise_percent) / 100 * 0.5)  # Base 15% + surprise boost
            
            elif (surprise.surprise_magnitude == 'NEGATIVE' and 
                  classification.classification == 'GLAMOUR'):
                signal_type = 'SHORT_GLAMOUR'  
                expected_return = 0.12 + (abs(surprise.surprise_percent) / 100 * 0.4)  # Base 12% + surprise boost
            
            if signal_type != 'SKIP':
                # Get current price for entry calculation
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='1d')
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        
                        # Calculate targets based on expected return
                        if signal_type == 'LONG_VALUE':
                            target_price = current_price * (1 + expected_return)
                            stop_loss = current_price * 0.90  # 10% stop loss
                        else:  # SHORT_GLAMOUR
                            target_price = current_price * (1 - expected_return)
                            stop_loss = current_price * 1.10  # 10% stop loss
                        
                        confidence = (abs(surprise.surprise_percent) / 20 + 
                                    classification.confidence_score) / 2
                        confidence = min(confidence, 0.95)
                        
                        signal = PEADSignal(
                            symbol=symbol,
                            signal_type=signal_type,
                            earnings_surprise=surprise,
                            value_glamour=classification,
                            expected_return=expected_return,
                            holding_period=self.holding_period_days,
                            entry_price=current_price,
                            target_price=target_price,
                            stop_loss=stop_loss,
                            confidence=confidence
                        )
                        
                        signals.append(signal)
                        print(f"✅ {symbol}: {signal_type} signal generated - {expected_return:.1%} expected")
                
                except Exception as e:
                    print(f"⚠️ Error generating signal for {symbol}: {e}")
                    continue
        
        return signals
    
    def format_pead_alert(self, signal: PEADSignal) -> str:
        """Format PEAD signal into professional alert"""
        surprise = signal.earnings_surprise
        classification = signal.value_glamour
        
        alert = f"""🎯 **PEAD STRATEGY SIGNAL DETECTED**
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}

**TICKER:** ${signal.symbol}
**STRATEGY:** {signal.signal_type.replace('_', ' ')}
**EXPECTED RETURN:** {signal.expected_return:.1%} ({signal.holding_period} days)

📊 **EARNINGS SURPRISE ANALYSIS:**
▪️ *Earnings Date:* {surprise.earnings_date}
▪️ *Surprise:* {surprise.surprise_percent:+.1f}% ({surprise.surprise_magnitude})
▪️ *Actual EPS:* ${surprise.actual_eps:.2f} vs ${surprise.estimated_eps:.2f} est.

📈 **VALUE/GLAMOUR CLASSIFICATION:**
▪️ *Type:* {classification.classification}
▪️ *P/E Ratio:* {classification.pe_ratio:.1f}
▪️ *P/B Ratio:* {classification.pb_ratio:.1f}  
▪️ *EAR Ratio:* {classification.ear_ratio:.1%}
▪️ *Confidence:* {classification.confidence_score:.0%}

💰 **TRADING PLAN:**
▪️ *Entry Price:* ${signal.entry_price:.2f}
▪️ *Target Price:* ${signal.target_price:.2f}
▪️ *Stop Loss:* ${signal.stop_loss:.2f}
▪️ *Holding Period:* {signal.holding_period} days
▪️ *Position Size:* {self.position_size:.0%} of portfolio

🎯 **PEAD LOGIC:**
Post-Earnings drift typically continues for 45-60 days after announcement.
Academic studies show 17-19% annualized returns using this strategy.

⚡ **CONFIDENCE:** {signal.confidence:.0%}
"""
        return alert

if __name__ == "__main__":
    # Test PEAD strategy
    pead = PEADStrategyCore()
    
    # Test symbols (mix of potential value and glamour stocks)
    test_symbols = ['AAPL', 'NVDA', 'BRK-B', 'JNJ', 'XOM', 'TSLA', 'META', 'PFE']
    
    signals = pead.generate_pead_signals(test_symbols)
    
    if signals:
        print(f"\n🚀 Generated {len(signals)} PEAD signals:")
        for signal in signals:
            alert = pead.format_pead_alert(signal)
            print("\n" + "="*80)
            print(alert)
    else:
        print("\n⚠️ No PEAD signals generated - no recent earnings surprises found")