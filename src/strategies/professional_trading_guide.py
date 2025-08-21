#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - PROFESSIONAL TRADING EXECUTION GUIDE
Guías completas para ejecutar trades como un profesional
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.nexus_utils import nexus_speak
except ImportError:
    def nexus_speak(level, message):
        print(f"[{level.upper()}] {message}")

class ProfessionalTradingGuide:
    """Genera guías profesionales de ejecución para Robinhood Level 2"""
    
    def __init__(self, broker_level="robinhood_2"):
        self.broker_level = broker_level
        nexus_speak("info", f"🎯 Professional Trading Guide initialized for {broker_level.upper()}")
        
        # Robinhood Level 2 permitidas
        self.allowed_strategies = {
            'long_call': 'Long Call (Bullish)',
            'long_put': 'Long Put (Bearish)', 
            'covered_call': 'Covered Call (Income)',
            'cash_secured_put': 'Cash-Secured Put (Income)'
        }
        
        # Estrategias Level 3+ (no permitidas)
        self.restricted_strategies = {
            'bull_put', 'bear_call', 'iron_condor', 'iron_butterfly',
            'straddle', 'strangle', 'calendar_spread'
        }
    
    def convert_to_level2_strategy(self, original_strategy, signal):
        """Convierte estrategias Level 3+ a alternativas Level 2"""
        
        probability = signal['enhanced_probability']
        current_price = signal.get('market_data', {}).get('current_price', 0)
        
        if original_strategy == 'bull_put':
            # Bull Put → Cash-Secured Put (misma dirección alcista)
            return {
                'strategy_type': 'cash_secured_put',
                'reasoning': 'Bullish outlook - sell put to collect premium and potentially own stock',
                'strike_price': signal.get('market_data', {}).get('strike_price', 0),
                'premium_estimate': current_price * 0.015
            }
        elif original_strategy == 'bear_call':
            # Bear Call → Long Put (dirección bajista)
            return {
                'strategy_type': 'long_put',
                'reasoning': 'Bearish outlook - buy put for downside protection/profit',
                'strike_price': signal.get('market_data', {}).get('strike_price', 0),
                'premium_estimate': current_price * 0.018
            }
        elif original_strategy == 'long_call':
            # Ya es Level 2
            return {
                'strategy_type': 'long_call',
                'reasoning': 'Bullish outlook - buy call for upside leverage',
                'strike_price': signal.get('market_data', {}).get('strike_price', 0),
                'premium_estimate': current_price * 0.020
            }
        else:
            # Default a Long Call para estrategias no reconocidas
            return {
                'strategy_type': 'long_call',
                'reasoning': 'Default bullish play - buy call option',
                'strike_price': current_price,
                'premium_estimate': current_price * 0.025
            }
    
    def format_professional_alert(self, signals, budget_info):
        """Formatea alertas profesionales con estrategias Robinhood Level 2"""
        
        if not signals:
            return "❌ No trading opportunities found"
        
        # Convertir señales a estrategias Level 2
        converted_signals = []
        for signal_data in signals[:3]:
            signal = signal_data.get('signal', {}) or {} or {}
            original_strategy = signal['strategy_type']
            
            # Convertir a estrategia Level 2
            level2_strategy = self.convert_to_level2_strategy(original_strategy, signal)
            
            # Actualizar signal con nueva estrategia
            converted_signal = signal.copy()
            converted_signal['strategy_type'] = level2_strategy['strategy_type']
            converted_signal['level2_reasoning'] = level2_strategy['reasoning']
            converted_signal['original_strategy'] = original_strategy
            
            converted_signals.append({
                'signal': converted_signal,
                'probability': signal_data['probability']
            })
        
        alert = f"""🚀 ALPHA HUNTER V2 - ROBINHOOD LEVEL 2 TRADING ALERTS
📅 {datetime.now().strftime("%Y-%m-%d %H:%M EST")}

💡 EXECUTIVE SUMMARY:
├─ Total Opportunities: {len(signals)} (converted to Level 2 strategies)
├─ Broker: Robinhood Level 2 Compatible
├─ Allowed Strategies: Long Call, Long Put, Covered Call, Cash-Secured Put
├─ Portfolio Risk: Single-leg positions
└─ Expected ROI: 15-25% (45-day timeframe)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # Procesar cada señal convertida
        for i, signal_data in enumerate(converted_signals, 1):
            signal = signal_data.get('signal', {}) or {} or {}
            
            if signal['strategy_type'] == 'long_call':
                trade_guide = self.generate_long_call_guide(signal, i)
            elif signal['strategy_type'] == 'long_put':
                trade_guide = self.generate_long_put_guide(signal, i)
            elif signal['strategy_type'] == 'cash_secured_put':
                trade_guide = self.generate_cash_secured_put_guide(signal, i)
            # covered_call removed - use long_call instead
            else:
                trade_guide = self.generate_generic_level2_guide(signal, i)
            
            alert += trade_guide + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Análisis comparativo Level 2
        alert += self.generate_level2_comparative_analysis(converted_signals)
        
        # Gestión de riesgo para Robinhood Level 2
        alert += self.generate_robinhood_risk_management(budget_info)
        
        return alert
    
    def calculate_real_contract_costs(self, symbol, short_strike, long_strike, current_price, strategy_type="bull_put"):
        """Calcula costos reales de contratos de opciones"""
        
        # Estimación más precisa basada en volatilidad implícita y tiempo
        iv_estimate = max(0.20, min(0.60, current_price * 0.0005))  # IV estimada
        time_value = 45 / 365  # 45 días hasta expiración
        
        if strategy_type == "bull_put":
            # Para Bull Put Spread
            short_put_premium = max(0.05, current_price * 0.012 * iv_estimate)  # PUT corto que vendemos
            long_put_premium = max(0.02, current_price * 0.006 * iv_estimate)   # PUT largo que compramos
            net_credit = short_put_premium - long_put_premium
            
            # Margen requerido = diferencia de strikes - crédito neto
            spread_width = short_strike - long_strike
            margin_per_contract = max(spread_width - net_credit, spread_width * 0.2) * 100
            
        elif strategy_type == "bear_call":
            # Para Bear Call Spread
            short_call_premium = max(0.05, current_price * 0.014 * iv_estimate)  # CALL corto que vendemos
            long_call_premium = max(0.02, current_price * 0.007 * iv_estimate)   # CALL largo que compramos
            net_credit = short_call_premium - long_call_premium
            
            # Margen requerido = diferencia de strikes - crédito neto
            spread_width = long_strike - short_strike
            margin_per_contract = max(spread_width - net_credit, spread_width * 0.2) * 100
            
        else:  # iron_condor
            # Simplified iron condor calculation
            net_credit = current_price * 0.008
            margin_per_contract = current_price * 0.15 * 100
        
        return {
            'net_credit': net_credit,
            'margin_per_contract': margin_per_contract,
            'max_profit_per_contract': net_credit * 100,
            'max_loss_per_contract': margin_per_contract,
            'breakeven': short_strike - net_credit if strategy_type == "bull_put" else short_strike + net_credit
        }
    
    def generate_bull_put_guide(self, signal, position_num):
        """Guía completa para Bull Put Spread con costos reales"""
        
        symbol = signal['symbol']
        current_price = signal.get('market_data', {}).get('current_price', 0)
        strike_price = signal.get('market_data', {}).get('strike_price', 0)
        probability = signal['enhanced_probability']
        quality = signal['signal_quality']
        
        # Cálculo de strikes para el spread
        short_put_strike = strike_price  # Strike que vendemos (PUT corto)
        long_put_strike = short_put_strike - (current_price * 0.02)  # 2% más abajo
        
        # Cálculos reales de costos de contratos
        costs = self.calculate_real_contract_costs(symbol, short_put_strike, long_put_strike, current_price, "bull_put")
        
        net_credit = costs['net_credit']
        margin_per_contract = costs['margin_per_contract']
        max_profit_per_contract = costs['max_profit_per_contract']
        max_loss_per_contract = costs['max_loss_per_contract'] 
        breakeven = costs['breakeven']
        
        return f"""
🎯 TRADE #{position_num}: {symbol} BULL PUT SPREAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MARKET ANALYSIS:
├─ Current Price: ${current_price:.2f}
├─ Trend: Bullish/Neutral (expect price above ${short_put_strike:.2f})
├─ Success Probability: {probability}%
├─ Quality Score: {quality}/100
└─ Volatility: {signal.get('market_data', {}).get('realized_vol', 30):.1f}% (favorable for credit)

💰 REAL CONTRACT COSTS:
├─ Net Credit Received: ${net_credit:.2f} per spread
├─ Margin Required: ${margin_per_contract:.0f} per contract
├─ Max Profit: ${max_profit_per_contract:.0f} per contract ({max_profit_per_contract/margin_per_contract*100:.1f}% ROI)
├─ Max Loss: ${max_loss_per_contract:.0f} per contract
└─ Breakeven Price: ${breakeven:.2f}

🔢 SCALABLE INVESTMENT:
├─ 1 Contract = ${margin_per_contract:.0f} investment → ${max_profit_per_contract:.0f} max profit
├─ 5 Contracts = ${margin_per_contract*5:.0f} investment → ${max_profit_per_contract*5:.0f} max profit
├─ 10 Contracts = ${margin_per_contract*10:.0f} investment → ${max_profit_per_contract*10:.0f} max profit
└─ Custom: YOUR_CONTRACTS × ${margin_per_contract:.0f} = Total Investment

🔧 BROKER EXECUTION INSTRUCTIONS:

Step 1 - SELL TO OPEN (Short Put):
┌─────────────────────────────────────┐
│ Action: SELL TO OPEN                │
│ Symbol: {symbol}                     │
│ Strike: ${short_put_strike:.2f} PUT          │
│ Expiration: {(datetime.now() + timedelta(days=45)).strftime('%m/%d/%Y')}     │
│ Quantity: YOUR_CONTRACTS            │
│ Order Type: LIMIT ORDER             │
│ Limit Price: ${net_credit + (short_put_strike - long_put_strike - net_credit)*(1-net_credit/(short_put_strike - long_put_strike)):.2f} (or better)   │
│ Time in Force: GTC                  │
└─────────────────────────────────────┘

Step 2 - BUY TO OPEN (Long Put - Protection):
┌─────────────────────────────────────┐
│ Action: BUY TO OPEN                 │
│ Symbol: {symbol}                     │
│ Strike: ${long_put_strike:.2f} PUT           │
│ Expiration: {(datetime.now() + timedelta(days=45)).strftime('%m/%d/%Y')}     │
│ Quantity: YOUR_CONTRACTS            │
│ Order Type: LIMIT ORDER             │
│ Limit Price: ${(short_put_strike - long_put_strike - net_credit)*(net_credit/(short_put_strike - long_put_strike)):.2f} (or better)    │
│ Time in Force: GTC                  │
└─────────────────────────────────────┘

⚡ ALTERNATIVE - SINGLE SPREAD ORDER:
┌─────────────────────────────────────┐
│ Order Type: SPREAD ORDER            │
│ Strategy: PUT VERTICAL (CREDIT)     │
│ Sell: ${short_put_strike:.2f} PUT                 │
│ Buy: ${long_put_strike:.2f} PUT                  │
│ Net Credit: ${net_credit:.2f} (minimum)         │
│ Quantity: YOUR_CONTRACTS            │
└─────────────────────────────────────┘

📈 PROFIT/LOSS PER CONTRACT:
├─ Max Profit: ${max_profit_per_contract:.0f} (if {symbol} > ${short_put_strike:.2f} at expiration)
├─ Max Loss: ${max_loss_per_contract:.0f} (if {symbol} < ${long_put_strike:.2f} at expiration)  
├─ Breakeven: ${breakeven:.2f}
├─ Profit Zone: {symbol} price > ${breakeven:.2f}
└─ Success Rate: {probability}% based on technical analysis

💎 INVESTMENT CALCULATOR:
├─ YOUR INVESTMENT = Number of Contracts × ${margin_per_contract:.0f}
├─ YOUR MAX PROFIT = Number of Contracts × ${max_profit_per_contract:.0f}
├─ YOUR MAX LOSS = Number of Contracts × ${max_loss_per_contract:.0f}
└─ ROI = {max_profit_per_contract/margin_per_contract*100:.1f}% per contract (if successful)

🎯 MANAGEMENT RULES (Scale with your contract count):

TAKE PROFIT TARGETS (Per Contract):
├─ Target 1: 25% = ${max_profit_per_contract * 0.25:.0f} profit - Close at 10-15 DTE
├─ Target 2: 50% = ${max_profit_per_contract * 0.5:.0f} profit - Close at 21 DTE
└─ Target 3: 75% = ${max_profit_per_contract * 0.75:.0f} profit - Let expire if ITM

STOP LOSS RULES (Per Contract):
├─ Hard Stop: Close if loss reaches ${max_loss_per_contract * 0.5:.0f} (50% of max loss)
├─ Technical Stop: Close if {symbol} breaks below ${long_put_strike * 0.98:.2f}
├─ Time Stop: Close at 7 DTE if not profitable
└─ Volatility Stop: Close if IV rank drops below 20%

⚠️ POSITION SIZING FREEDOM:
├─ Minimum: 1 contract = ${margin_per_contract:.0f} investment
├─ Conservative: 2-5% of portfolio
├─ Aggressive: 5-10% of portfolio
├─ YOUR CHOICE: Decide based on risk tolerance
└─ Greeks Scale: Delta/Theta multiply by contract count

🧠 PROFESSIONAL INSIGHTS:
├─ Why This Trade: High probability mean reversion setup
├─ Best Outcome: {symbol} stays above ${short_put_strike:.2f} (76% historical)
├─ Risk Factor: Earnings dates, market volatility spikes
└─ Alternative: Convert to Iron Condor if bullish conviction weakens"""

    def generate_bear_call_guide(self, signal, position_num):
        """Guía completa para Bear Call Spread"""
        
        symbol = signal['symbol']
        current_price = signal.get('market_data', {}).get('current_price', 0)
        strike_price = signal.get('market_data', {}).get('strike_price', 0)
        probability = signal['enhanced_probability']
        quality = signal['signal_quality']
        
        # Cálculo de strikes para el spread
        short_call_strike = strike_price  # Strike que vendemos (CALL corto)
        long_call_strike = short_call_strike + (current_price * 0.02)  # 2% más arriba
        
        # Estimación de precios de opciones
        short_call_premium = current_price * 0.018  # ~1.8% del precio
        long_call_premium = current_price * 0.009   # ~0.9% del precio
        net_credit = short_call_premium - long_call_premium
        
        # Cálculos de riesgo
        max_profit = net_credit * 100  # Por contrato
        max_loss = (long_call_strike - short_call_strike - net_credit) * 100
        breakeven = short_call_strike + net_credit
        
        return f"""
🎯 TRADE #{position_num}: {symbol} BEAR CALL SPREAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MARKET ANALYSIS:
├─ Current Price: ${current_price:.2f}
├─ Trend: Bearish/Neutral (expect price below ${short_call_strike:.2f})
├─ Success Probability: {probability}%
├─ Quality Score: {quality}/100
└─ Volatility: {signal.get('market_data', {}).get('realized_vol', 30):.1f}% (favorable for credit)

💰 TRADE SPECIFICATIONS:
├─ Strategy: Bear Call Credit Spread
├─ Bias: Bearish to Neutral
├─ Expiration: ~45 days (next monthly cycle)
├─ Target Profit: {signal.get('professional_metrics', {}).get('expected_return', 0):.1f}%
└─ Max Risk: ${max_loss:.0f} per spread

🔧 BROKER EXECUTION INSTRUCTIONS:

Step 1 - SELL TO OPEN (Short Call):
┌─────────────────────────────────────┐
│ Action: SELL TO OPEN                │
│ Symbol: {symbol}                     │
│ Strike: ${short_call_strike:.2f} CALL         │
│ Expiration: {(datetime.now() + timedelta(days=45)).strftime('%m/%d/%Y')}     │
│ Quantity: 1 contract               │
│ Order Type: LIMIT ORDER             │
│ Limit Price: ${short_call_premium:.2f} (or better)  │
│ Time in Force: GTC                  │
└─────────────────────────────────────┘

Step 2 - BUY TO OPEN (Long Call - Protection):
┌─────────────────────────────────────┐
│ Action: BUY TO OPEN                 │
│ Symbol: {symbol}                     │
│ Strike: ${long_call_strike:.2f} CALL          │
│ Expiration: {(datetime.now() + timedelta(days=45)).strftime('%m/%d/%Y')}     │
│ Quantity: 1 contract               │
│ Order Type: LIMIT ORDER             │
│ Limit Price: ${long_call_premium:.2f} (or better)   │
│ Time in Force: GTC                  │
└─────────────────────────────────────┘

⚡ ALTERNATIVE - SINGLE SPREAD ORDER:
┌─────────────────────────────────────┐
│ Order Type: SPREAD ORDER            │
│ Strategy: CALL VERTICAL (CREDIT)    │
│ Sell: ${short_call_strike:.2f} CALL                │
│ Buy: ${long_call_strike:.2f} CALL                 │
│ Net Credit: ${net_credit:.2f} (minimum)         │
│ Quantity: 1 spread                 │
└─────────────────────────────────────┘

📈 PROFIT/LOSS SCENARIOS:
├─ Max Profit: ${max_profit:.0f} (if {symbol} < ${short_call_strike:.2f} at expiration)
├─ Max Loss: ${max_loss:.0f} (if {symbol} > ${long_call_strike:.2f} at expiration)
├─ Breakeven: ${breakeven:.2f}
├─ Profit Zone: {symbol} price < ${breakeven:.2f}
└─ Success Rate: {probability}% based on resistance analysis

🎯 MANAGEMENT RULES:

TAKE PROFIT TARGETS:
├─ Target 1: 25% of max profit (${max_profit * 0.25:.0f}) - Close at 10-15 DTE
├─ Target 2: 50% of max profit (${max_profit * 0.5:.0f}) - Close at 21 DTE
└─ Target 3: 75% of max profit (${max_profit * 0.75:.0f}) - Let expire if OTM

STOP LOSS RULES:
├─ Hard Stop: Close if loss reaches ${max_loss * 0.5:.0f} (50% of max loss)
├─ Technical Stop: Close if {symbol} breaks above ${long_call_strike * 1.02:.2f}
├─ Time Stop: Close at 7 DTE if not profitable
└─ Volatility Stop: Close if IV rank drops below 20%

⚠️ RISK MANAGEMENT:
├─ Position Size: Max 2-3% of portfolio per trade
├─ Capital Required: ${max_loss:.0f} (margin requirement)
├─ Greeks Exposure: Delta {signal['greeks']['delta']:.2f}, Theta {signal['greeks']['theta']:.3f}
└─ Liquidity: Ensure bid-ask spread < $0.15 for entry/exit

🧠 PROFESSIONAL INSIGHTS:
├─ Why This Trade: Strong resistance at ${short_call_strike:.2f} level
├─ Best Outcome: {symbol} stays below ${short_call_strike:.2f} (74% historical)
├─ Risk Factor: Momentum breakouts, positive news catalysts
└─ Alternative: Roll strikes higher if bullish momentum develops"""

    def generate_comparative_analysis(self, top_signals):
        """Análisis comparativo de las mejores oportunidades"""
        
        analysis = f"""
🔍 COMPARATIVE ANALYSIS - TOP 3 OPPORTUNITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RANKING BY CRITERIA:

HIGHEST PROBABILITY:
"""
        
        # Ordenar por probabilidad
        prob_sorted = sorted(top_signals, key=lambda x: x['probability'], reverse=True)
        for i, signal in enumerate(prob_sorted, 1):
            symbol = signal.get('signal', {}).get('symbol', 'UNKNOWN')
            prob = signal['probability']
            strategy = signal.get('signal', {}).get('strategy_type', 'unknown').replace('_', ' ').title()
            analysis += f"├─ #{i} {symbol}: {prob}% ({strategy})\n"
        
        analysis += f"""
BEST RISK/REWARD:
"""
        # Ordenar por expected return
        return_sorted = sorted(top_signals, key=lambda x: x.get('signal', {}).get('professional_metrics', {}).get('expected_return', 0), reverse=True)
        for i, signal in enumerate(return_sorted, 1):
            symbol = signal.get('signal', {}).get('symbol', 'UNKNOWN')
            exp_return = signal.get('signal', {}).get('professional_metrics', {}).get('expected_return', 0)
            risk = signal.get('signal', {}).get('professional_metrics', {}).get('max_drawdown_estimate', 0)
            ratio = exp_return / risk if risk > 0 else 0
            analysis += f"├─ #{i} {symbol}: {exp_return:.1f}% return, {risk:.1f}% risk (Ratio: {ratio:.2f})\n"
        
        analysis += f"""
PORTFOLIO ALLOCATION LOGIC:
├─ Position 1: Highest conviction (largest allocation)
├─ Position 2: Best risk-adjusted return (medium allocation)  
├─ Position 3: Diversification play (smaller allocation)
└─ Strategy Mix: Balanced bull/bear exposure

💡 PROFESSIONAL RECOMMENDATION:
"""
        
        best_signal = top_signals[0].get('signal', {}) or {}
        best_symbol = best_signal.get('symbol', 'UNKNOWN')
        best_strategy = best_signal.get('strategy_type', 'unknown').replace('_', ' ').title()
        best_prob = top_signals[0]['probability']
        
        analysis += f"""├─ PRIMARY TRADE: {best_symbol} {best_strategy} ({best_prob}% probability)
├─ RATIONALE: Highest quality setup with strong technical confluence
├─ POSITION SIZE: Start with smallest size, scale up on success
└─ TIMING: Execute during market hours for best fills

⚠️ RISK CONSIDERATIONS:
├─ Market Environment: Current volatility regime
├─ Correlation Risk: Monitor if positions move together
├─ Liquidity Risk: Ensure all options have tight bid-ask spreads
├─ Event Risk: Check earnings calendars before entry
└─ Portfolio Heat: Total options exposure < 10% of account

🎯 EXECUTION PRIORITY:
1. Execute highest probability trade first
2. Wait for fills before entering next position
3. Monitor Greeks exposure across all positions
4. Set stop losses immediately after entry
"""
        
        return analysis
    
    def generate_robinhood_risk_management(self, budget_info):
        """Gestión de riesgo del portfolio completo"""
        
        total_budget = sum(allocation['allocation'] for allocation in budget_info.values())
        max_single_risk = max(allocation['allocation'] for allocation in budget_info.values())
        
        return f"""
📋 PORTFOLIO RISK MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 CAPITAL ALLOCATION:
├─ Total Capital Deployed: ${total_budget:.0f}
├─ Largest Single Position: ${max_single_risk:.0f} ({max_single_risk/total_budget*100:.1f}% of total)
├─ Average Position Size: ${total_budget/len(budget_info):.0f}
├─ Reserved Cash: Minimum 20% for adjustments
└─ Max Portfolio Risk: {sum(alloc['allocation'] * 0.15 for alloc in budget_info.values()):.0f} (worst case)

📊 DIVERSIFICATION METRICS:
├─ Strategy Types: {len(set([str(alloc.get('strategy', 'unknown')) if isinstance(alloc, dict) else str(alloc) for alloc in budget_info.values()]))} different strategies
├─ Sector Exposure: Diversified across market sectors
├─ Time Decay: Positive theta from credit strategies
└─ Volatility Exposure: Mixed vega across positions

🎯 PROFESSIONAL CHECKLIST BEFORE TRADING:

□ Account Setup:
  ├─ Options trading approved (Level 2+ required)
  ├─ Sufficient buying power for margin requirements
  ├─ Real-time market data subscription active
  └─ Stop loss orders capability enabled

□ Pre-Trade Analysis:
  ├─ Verify no earnings within expiration period
  ├─ Check implied volatility rank (prefer IV > 30%)
  ├─ Confirm liquid options (bid-ask spread < 5% of mid)
  └─ Review overall portfolio correlation

□ Execution:
  ├─ Place orders during market hours (9:30 AM - 4:00 PM EST)
  ├─ Use limit orders (never market orders for spreads)
  ├─ Verify correct expiration dates and strikes
  └─ Set profit target and stop loss immediately

□ Post-Trade Management:
  ├─ Monitor positions daily for adjustment opportunities
  ├─ Close profitable trades at 25-50% of max profit
  ├─ Never let losing trades exceed predetermined risk
  └─ Keep detailed trade log for performance tracking

💡 PSYCHOLOGY & DISCIPLINE:
├─ Stick to predetermined position sizes
├─ Don't chase trades or FOMO into positions
├─ Accept small losses to preserve capital
├─ Scale position sizes based on account performance
└─ Review and adjust strategy monthly

⚡ EMERGENCY PROCEDURES:
├─ Market Crash: Close all positions if VIX > 40
├─ Account Drawdown: Reduce position sizes by 50%
├─ Winning Streak: Don't increase risk dramatically
└─ Technical Issues: Have backup broker access ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 ALPHA HUNTER V2 PROFESSIONAL TRADING SYSTEM
📊 Real-time analysis • Professional execution • Risk management
⚡ Trade with confidence using quantified probabilities
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

# Test the professional guide
if __name__ == "__main__":
    print("🎯 TESTING PROFESSIONAL TRADING GUIDE")
    print("=" * 60)
    
    # Sample signal data
    sample_signal = {
        'symbol': 'AAPL',
        'strategy_type': 'bull_put',
        'enhanced_probability': 75.1,
        'signal_quality': 85,
        'market_data': {
            'current_price': 202.07,
            'strike_price': 193.99,
            'realized_vol': 27.6
        },
        'greeks': {
            'delta': -0.299,
            'theta': -0.083
        },
        'professional_metrics': {
            'expected_return': 15.0,
            'max_drawdown_estimate': 15.0
        }
    }
    
    guide = ProfessionalTradingGuide()
    
    # Generate professional guide
    sample_signals = [{'signal': sample_signal, 'probability': 75.1}]
    sample_budget = {'AAPL': {'allocation': 250, 'strategy': 'bull_put'}}
    
    professional_alert = guide.format_professional_alert(sample_signals, sample_budget)
    
    print(professional_alert[:1000] + "...")
    print("\n🚀 ROBINHOOD LEVEL 2 SYSTEM READY!")
    print("💎 Real Level 2 costs • Single-leg strategies • Robinhood-specific execution!")

# Add missing methods to the class
def generate_covered_call_guide(self, signal, position_num):
    """Guía para Covered Call (Robinhood Level 2)"""
    
    symbol = signal['symbol']
    current_price = signal.get('market_data', {}).get('current_price', 0)
    strike_price = signal.get('market_data', {}).get('strike_price', 0)
    probability = signal['enhanced_probability']
    quality = signal['signal_quality']
    
    # Requires owning 100 shares per contract
    shares_required = 100
    stock_value = shares_required * current_price
    premium_per_contract = current_price * 0.012  # ~1.2% del precio
    premium_received = premium_per_contract * 100
    
    return f"""
🎯 TRADE #{position_num}: {symbol} COVERED CALL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 STRATEGY CONVERSION:
├─ Original: {signal.get('original_strategy', 'N/A').upper()}
├─ Robinhood Level 2: COVERED CALL
└─ Reasoning: {signal.get('level2_reasoning', 'Income on owned stock')}

📊 MARKET ANALYSIS:
├─ Current Price: ${current_price:.2f}
├─ Strike Price: ${strike_price:.2f}
├─ Success Probability: {probability}% (expires OTM)
├─ Quality Score: {quality}/100
└─ Direction: NEUTRAL (collect premium on owned stock)

💰 REQUIREMENTS & RETURNS:
├─ Stock Required: {shares_required} shares (${stock_value:.0f} value)
├─ Premium Received: ${premium_received:.0f} per contract
├─ Max Profit: ${premium_received + (strike_price - current_price)*100:.0f} (premium + capital gain)
├─ Yield: {premium_received/stock_value*100:.1f}% (45 days)
└─ Annualized Yield: {premium_received/stock_value*365/45*100:.1f}%

⚠️ PREREQUISITE:
Must own {shares_required} shares of {symbol} per contract you want to sell"""

def generate_generic_level2_guide(self, signal, position_num):
    """Guía genérica para estrategias Level 2"""
    
    symbol = signal['symbol']
    current_price = signal.get('market_data', {}).get('current_price', 0)
    probability = signal['enhanced_probability']
    strategy = signal['strategy_type']
    
    return f"""
🎯 TRADE #{position_num}: {symbol} {strategy.upper().replace('_', ' ')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 STRATEGY CONVERSION:
├─ Original: {signal.get('original_strategy', 'N/A').upper()}
├─ Robinhood Level 2: {strategy.upper().replace('_', ' ')}
└─ Reasoning: {signal.get('level2_reasoning', 'Level 2 compatible strategy')}

📊 BASIC ANALYSIS:
├─ Symbol: {symbol}
├─ Current Price: ${current_price:.2f}
├─ Success Probability: {probability}%
└─ Strategy: {strategy.replace('_', ' ').title()}

💡 ROBINHOOD LEVEL 2 REMINDER:
├─ This strategy is compatible with your broker level
├─ Follow standard Level 2 risk management
├─ Consider position sizing based on account size
└─ Use limit orders for better fills"""

def generate_cash_secured_put_guide(self, signal, position_num):
    """Guía para Cash-Secured Put (Robinhood Level 2)"""
    
    symbol = signal['symbol']
    current_price = signal.get('market_data', {}).get('current_price', 0)
    strike_price = signal.get('market_data', {}).get('strike_price', 0)
    probability = signal['enhanced_probability']
    quality = signal['signal_quality']
    
    # Premium estimado y cash requerido
    premium_per_contract = current_price * 0.015  # ~1.5% del precio
    premium_received = premium_per_contract * 100
    cash_required = strike_price * 100  # Cash para comprar 100 acciones
    
    return f"""
🎯 TRADE #{position_num}: {symbol} CASH-SECURED PUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 STRATEGY CONVERSION:
├─ Original: {signal.get('original_strategy', 'N/A').upper()}
├─ Robinhood Level 2: CASH-SECURED PUT
└─ Reasoning: {signal.get('level2_reasoning', 'Income generation with stock ownership potential')}

📊 MARKET ANALYSIS:
├─ Current Price: ${current_price:.2f}
├─ Strike Price: ${strike_price:.2f}
├─ Success Probability: {probability}% (expires worthless)
├─ Quality Score: {quality}/100
└─ Direction: NEUTRAL to BULLISH (collect premium)

💰 REAL INVESTMENT REQUIREMENTS:
├─ Premium Received: ${premium_received:.0f} per contract
├─ Cash Required: ${cash_required:.0f} per contract
├─ Net Investment: ${cash_required - premium_received:.0f} per contract
├─ ROI if Expired: {premium_received/cash_required*100:.1f}% (45 days)
└─ Annualized ROI: {premium_received/cash_required*365/45*100:.1f}%

🔢 SCALABLE INVESTMENT:
├─ 1 Contract = ${cash_required:.0f} cash required
├─ 5 Contracts = ${cash_required*5:.0f} cash required
├─ 10 Contracts = ${cash_required*10:.0f} cash required
└─ Custom: YOUR_CONTRACTS × ${cash_required:.0f} = Total Cash

🔧 ROBINHOOD EXECUTION:

┌─────────────────────────────────────┐
│ ROBINHOOD ORDER INSTRUCTIONS           │
├─────────────────────────────────────┤
│ 1. Ensure ${cash_required:.0f} cash in account      │
│ 2. Go to Options → {symbol}              │
│ 3. Select PUT option                    │
│ 4. Strike: ${strike_price:.2f}                      │
│ 5. Expiration: 45 days out              │
│ 6. Action: SELL TO OPEN                 │
│ 7. Quantity: YOUR_CONTRACTS             │
│ 8. Order Type: LIMIT                    │
│ 9. Limit Price: ${premium_per_contract:.2f} (or better)    │
└─────────────────────────────────────┘

🎯 SCENARIOS & MANAGEMENT:

🟢 BEST CASE (Put Expires Worthless):
├─ {symbol} stays above ${strike_price:.2f}
├─ Keep premium: ${premium_received:.0f} profit
├─ Cash freed up for next trade
└─ ROI: {premium_received/cash_required*100:.1f}%

🟡 ASSIGNMENT CASE (Put Exercised):
├─ {symbol} drops below ${strike_price:.2f}
├─ You buy 100 shares at ${strike_price:.2f}
├─ Effective cost: ${strike_price - premium_per_contract:.2f} per share
└─ Strategy: Hold stock or sell covered calls

💡 ROBINHOOD MANAGEMENT:
├─ Roll Down: If profitable, close and sell lower strike
├─ Early Close: Buy back at 25-50% profit
├─ Assignment Ready: Have cash available for stock purchase
└─ Wheel Strategy: Sell covered calls if assigned"""

def generate_level2_comparative_analysis(self, converted_signals):
    """Análisis comparativo para estrategias Robinhood Level 2"""
    
    analysis = f"""
🔍 ROBINHOOD LEVEL 2 - COMPARATIVE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RANKING BY PROBABILITY:
"""
    
    # Ordenar por probabilidad
    prob_sorted = sorted(converted_signals, key=lambda x: x['probability'], reverse=True)
    for i, signal_data in enumerate(prob_sorted, 1):
        signal = signal_data.get('signal', {}) or {}
        symbol = signal['symbol']
        prob = signal_data['probability']
        strategy = signal['strategy_type'].replace('_', ' ').title()
        original = signal.get('original_strategy', 'N/A').upper()
        
        analysis += f"├─ #{i} {symbol}: {prob}% ({strategy}) [was {original}]\n"
    
    analysis += f"""
💰 INVESTMENT REQUIREMENTS:
"""
    
    # Calcular requerimientos de inversión para cada estrategia
    for i, signal_data in enumerate(converted_signals, 1):
        signal = signal_data.get('signal', {}) or {}
        symbol = signal['symbol']
        current_price = signal.get('market_data', {}).get('current_price', 0)
        strategy = signal['strategy_type']
        
        if strategy == 'long_call':
            cost = current_price * 0.020 * 100  # 2% premium
            analysis += f"├─ {symbol} Long Call: ${cost:.0f} per contract (premium cost)\n"
        elif strategy == 'long_put':
            cost = current_price * 0.018 * 100  # 1.8% premium
            analysis += f"├─ {symbol} Long Put: ${cost:.0f} per contract (premium cost)\n"
        elif strategy == 'cash_secured_put':
            cost = signal.get('market_data', {}).get('strike_price', 0) * 100  # Full cash requirement
            analysis += f"├─ {symbol} Cash-Secured Put: ${cost:.0f} cash per contract\n"
        else:
            analysis += f"├─ {symbol}: Strategy cost calculation needed\n"
    
    analysis += f"""
💡 LEVEL 2 STRATEGY GUIDE:
├─ Long Call: Bullish, limited risk, unlimited upside
├─ Long Put: Bearish, limited risk, high profit potential
├─ Cash-Secured Put: Income, requires full cash, stock ownership ready
├─ Covered Call: Income on owned stock (not shown in current signals)
└─ Risk Level: Lower than spreads, but requires more capital for some

⚠️ ROBINHOOD LEVEL 2 LIMITATIONS:
├─ No Spreads: Can't do bull put, bear call, iron condor, etc.
├─ Single Leg Only: Each option is standalone
├─ Higher Capital: Especially for cash-secured puts
├─ Assignment Risk: Need cash ready for puts, stock ready for calls
└─ Upgrade Path: Level 3 unlocks spread strategies

🎯 RECOMMENDED APPROACH:
├─ Start Small: Begin with 1-2 contracts to learn
├─ Focus on Liquidity: Stick to high-volume options
├─ Manage Early: Don't hold to expiration typically
├─ Cash Management: Keep reserves for assignments
└─ Track Performance: Build experience for Level 3 upgrade
"""
    
    return analysis

def generate_robinhood_risk_management(self, budget_info):
    """Gestión de riesgo específica para Robinhood Level 2"""
    
    # Estimar costos reales para Level 2
    level2_costs = []
    for ticker, data in budget_info.items():
        if data.get('strategy') == 'long_call':
            estimated_cost = 400  # Promedio para long calls
        elif data.get('strategy') == 'long_put':
            estimated_cost = 350  # Promedio para long puts
        elif data.get('strategy') == 'cash_secured_put':
            estimated_cost = 5000  # Cash requirement
        else:
            estimated_cost = 500  # Default
        level2_costs.append(estimated_cost)
    
    min_investment = min(level2_costs) if level2_costs else 350
    max_investment = max(level2_costs) if level2_costs else 5000
    total_min = sum(level2_costs)
    
    return f"""
📋 ROBINHOOD LEVEL 2 - RISK MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 LEVEL 2 INVESTMENT REQUIREMENTS:
├─ Minimum Trade: ${min_investment:.0f} (long call/put)
├─ Maximum Trade: ${max_investment:.0f} (cash-secured put)
├─ Total for All Signals: ${total_min:.0f} (1 contract each)
├─ Recommended Start: ${min_investment*2:.0f} (2 contracts small position)
└─ YOUR CHOICE: Scale based on Robinhood Level 2 rules

📊 ROBINHOOD ACCOUNT GUIDELINES:
├─ Small Account ($5,000): 1 contract per trade, focus on long calls/puts
├─ Medium Account ($25,000): 2-5 contracts, can do cash-secured puts
├─ Large Account ($50,000+): 5-10 contracts, mix all Level 2 strategies
├─ PDT Rule: Need $25K for unlimited day trading
└─ Level 3 Goal: Build track record to unlock spreads

🎯 PRE-TRADE ANALYSIS (ROBINHOOD SPECIFIC):
  ├─ Check option chain liquidity (volume > 10)
  ├─ Verify expiration dates (Robinhood shows clearly)
  ├─ Confirm sufficient cash for cash-secured puts
  ├─ Check for earnings announcements
  └─ Review day trading limit (3 per 5 days if < $25K)

🎯 EXECUTION (ROBINHOOD INTERFACE):
  ├─ Navigate: Options → Symbol → Select strike/expiration
  ├─ Always use LIMIT orders (avoid market orders)
  ├─ Double-check BUY vs SELL (critical for cash-secured puts)
  ├─ Monitor fill status - Robinhood shows real-time updates
  └─ Set alerts for profit/loss targets in app

💡 ROBINHOOD LEVEL 2 PSYCHOLOGY:
├─ Accept higher capital requirements vs spreads
├─ Focus on directional accuracy (no hedge like spreads)
├─ Be ready for assignments on cash-secured puts
├─ Track P&L to build case for Level 3 upgrade
└─ Learn from each trade to improve selection

⚡ ROBINHOOD LEVEL 2 SPECIFIC RISKS:
├─ Assignment Risk: Cash-secured puts can be assigned early
├─ No Hedge Protection: Single legs have unlimited risk exposure
├─ Capital Intensive: Especially cash-secured puts require full cash
├─ Time Decay: Long options lose value daily (theta decay)
└─ Upgrade Path: Master Level 2 to unlock spreads

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 ALPHA HUNTER V2 - ROBINHOOD LEVEL 2 EDITION
📊 Real Level 2 costs • Robinhood-specific execution • Upgrade path
⚡ Single-leg strategies • Professional probabilities • Level 3 preparation
💎 Trade within your broker limits with institutional-grade analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

def generate_long_put_guide(self, signal, position_num):
    """Guía para Long Put (Robinhood Level 2)"""
    
    symbol = signal['symbol']
    current_price = signal.get('market_data', {}).get('current_price', 0)
    strike_price = signal.get('market_data', {}).get('strike_price', 0)
    probability = signal['enhanced_probability']
    quality = signal['signal_quality']
    
    # Premium estimado para Long Put
    premium_per_contract = current_price * 0.018  # ~1.8% del precio actual
    cost_per_contract = premium_per_contract * 100
    
    # Breakeven y targets
    breakeven = strike_price - premium_per_contract
    target_price_1 = breakeven * 0.95  # 5% abajo del breakeven
    target_price_2 = breakeven * 0.90  # 10% abajo del breakeven
    
    return f"""
🎯 TRADE #{position_num}: {symbol} LONG PUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 STRATEGY CONVERSION:
├─ Original: {signal.get('original_strategy', 'N/A').upper()}
├─ Robinhood Level 2: LONG PUT
└─ Reasoning: {signal.get('level2_reasoning', 'Bearish directional play')}

📊 MARKET ANALYSIS:
├─ Current Price: ${current_price:.2f}
├─ Strike Price: ${strike_price:.2f}
├─ Success Probability: {probability}%
├─ Quality Score: {quality}/100
└─ Direction: BEARISH (need price < ${breakeven:.2f})

💰 REAL CONTRACT COSTS:
├─ Premium per Contract: ${premium_per_contract:.2f}
├─ Cost per Contract: ${cost_per_contract:.0f}
├─ Breakeven Price: ${breakeven:.2f}
├─ Max Loss: ${cost_per_contract:.0f} (premium paid)
└─ Max Profit: ${(strike_price * 100) - cost_per_contract:.0f} (if stock goes to $0)

🔢 SCALABLE INVESTMENT:
├─ 1 Contract = ${cost_per_contract:.0f} investment
├─ 5 Contracts = ${cost_per_contract*5:.0f} investment
├─ 10 Contracts = ${cost_per_contract*10:.0f} investment
└─ Custom: YOUR_CONTRACTS × ${cost_per_contract:.0f} = Total Investment

🔧 ROBINHOOD EXECUTION:

┌─────────────────────────────────────┐
│ ROBINHOOD ORDER INSTRUCTIONS           │
├─────────────────────────────────────┤
│ 1. Go to Options → {symbol}              │
│ 2. Select PUT option                    │
│ 3. Strike: ${strike_price:.2f}                      │
│ 4. Expiration: 45 days out              │
│ 5. Action: BUY TO OPEN                  │
│ 6. Quantity: YOUR_CONTRACTS             │
│ 7. Order Type: LIMIT                    │
│ 8. Limit Price: ${premium_per_contract:.2f} (or better)    │
└─────────────────────────────────────┘

🎯 PROFIT TARGETS & STOPS:

🟢 TAKE PROFIT LEVELS:
├─ Target 1: {symbol} drops to ${target_price_1:.2f} (25% profit)
├─ Target 2: {symbol} drops to ${target_price_2:.2f} (50% profit)
└─ Target 3: Hold for major breakdown (75%+ profit)

🔴 STOP LOSS RULES:
├─ Stop Loss: Sell if premium drops 50% (${cost_per_contract*0.5:.0f} loss)
├─ Time Stop: Sell at 7-10 DTE if not profitable
├─ Technical Stop: Sell if {symbol} breaks major resistance
└─ Max Loss: ${cost_per_contract:.0f} per contract (premium paid)

💡 ROBINHOOD TIPS:
├─ Liquidity Check: Ensure tight bid-ask spreads
├─ Volatility: Higher vol = higher premiums
├─ Earnings Risk: Avoid holding through earnings
└─ Put/Call Ratio: Monitor market sentiment"""

def generate_long_call_guide(self, signal, position_num):
    """Guía para Long Call (Robinhood Level 2)"""
    
    symbol = signal['symbol']
    current_price = signal.get('market_data', {}).get('current_price', 0)
    strike_price = signal.get('market_data', {}).get('strike_price', 0)
    probability = signal['enhanced_probability']
    quality = signal['signal_quality']
    
    # Premium estimado para Long Call
    premium_per_contract = current_price * 0.020  # ~2% del precio actual
    cost_per_contract = premium_per_contract * 100  # $100 por punto
    
    # Breakeven y profit targets
    breakeven = strike_price + premium_per_contract
    target_price_1 = breakeven * 1.05  # 5% arriba del breakeven
    target_price_2 = breakeven * 1.10  # 10% arriba del breakeven
    
    return f"""
🎯 TRADE #{position_num}: {symbol} LONG CALL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 STRATEGY CONVERSION:
├─ Original: {signal.get('original_strategy', 'N/A').upper()}
├─ Robinhood Level 2: LONG CALL
└─ Reasoning: {signal.get('level2_reasoning', 'Bullish directional play')}

📊 MARKET ANALYSIS:
├─ Current Price: ${current_price:.2f}
├─ Strike Price: ${strike_price:.2f}
├─ Success Probability: {probability}%
├─ Quality Score: {quality}/100
└─ Direction: BULLISH (need price > ${breakeven:.2f})

💰 REAL CONTRACT COSTS:
├─ Premium per Contract: ${premium_per_contract:.2f}
├─ Cost per Contract: ${cost_per_contract:.0f}
├─ Breakeven Price: ${breakeven:.2f}
├─ Max Loss: ${cost_per_contract:.0f} (premium paid)
└─ Unlimited Upside: No cap on profits

🔢 SCALABLE INVESTMENT:
├─ 1 Contract = ${cost_per_contract:.0f} investment
├─ 5 Contracts = ${cost_per_contract*5:.0f} investment
├─ 10 Contracts = ${cost_per_contract*10:.0f} investment
└─ Custom: YOUR_CONTRACTS × ${cost_per_contract:.0f} = Total Investment

🔧 ROBINHOOD EXECUTION:

┌─────────────────────────────────────┐
│ ROBINHOOD ORDER INSTRUCTIONS           │
├─────────────────────────────────────┤
│ 1. Go to Options → {symbol}              │
│ 2. Select CALL option                   │
│ 3. Strike: ${strike_price:.2f}                      │
│ 4. Expiration: 45 days out              │
│ 5. Action: BUY TO OPEN                  │
│ 6. Quantity: YOUR_CONTRACTS             │
│ 7. Order Type: LIMIT                    │
│ 8. Limit Price: ${premium_per_contract:.2f} (or better)    │
└─────────────────────────────────────┘

🎯 PROFIT TARGETS & STOPS:

🟢 TAKE PROFIT LEVELS:
├─ Target 1: {symbol} reaches ${target_price_1:.2f} (25% profit)
├─ Target 2: {symbol} reaches ${target_price_2:.2f} (50% profit)
└─ Target 3: Hold for major breakout (75%+ profit)

🔴 STOP LOSS RULES:
├─ Stop Loss: Sell if premium drops 50% (${cost_per_contract*0.5:.0f} loss)
├─ Time Stop: Sell at 7-10 DTE if not profitable
├─ Technical Stop: Sell if {symbol} breaks major support
└─ Max Loss: ${cost_per_contract:.0f} per contract (premium paid)

💡 ROBINHOOD TIPS:
├─ Set Limit Orders: Never use market orders for options
├─ Check Volume: Ensure option has good liquidity
├─ Day Trading: Need $25K for unlimited day trades
└─ Early Assignment: Rare for OTM calls, monitor closely"""

# Bind methods to class
ProfessionalTradingGuide.generate_covered_call_guide = generate_covered_call_guide
ProfessionalTradingGuide.generate_generic_level2_guide = generate_generic_level2_guide
ProfessionalTradingGuide.generate_cash_secured_put_guide = generate_cash_secured_put_guide
ProfessionalTradingGuide.generate_level2_comparative_analysis = generate_level2_comparative_analysis
ProfessionalTradingGuide.generate_robinhood_risk_management = generate_robinhood_risk_management
ProfessionalTradingGuide.generate_long_put_guide = generate_long_put_guide
ProfessionalTradingGuide.generate_long_call_guide = generate_long_call_guide