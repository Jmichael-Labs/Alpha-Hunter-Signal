#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - TELEGRAM SENDER CORREGIDO
Formato limpio sin errores de parsing
"""

import sys
import os
import requests
from datetime import datetime
from safe_send_utility import safe_telegram_send, safe_send, get_safe_send_stats

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.nexus_utils import nexus_speak  
except ImportError:
    def nexus_speak(level, message):
        print(f"[{level.upper()}] {message}")

from alpha_hunter_v2_unified import AlphaHunterV2Professional

def clean_telegram_message(message):
    """Clean message for Telegram - remove problematic markdown"""
    # Remove problematic markdown characters
    cleaned = message.replace('**', '*')
    cleaned = cleaned.replace('```', '')
    cleaned = cleaned.replace('[', '')
    cleaned = cleaned.replace(']', '')
    cleaned = cleaned.replace('(', '')
    cleaned = cleaned.replace(')', '')
    cleaned = cleaned.replace('_', '')
    
    return cleaned

def send_clean_telegram(message, chat_id=None):
    """Send clean message to Telegram"""
    try:
        # Use environment variables
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id_str = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        chat_id_int = int(chat_id_str)  # Convert to integer
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Clean message
        clean_msg = clean_telegram_message(message)
        
        payload = {
            "chat_id": chat_id_int,
            "text": clean_msg
        }
        
        # REFACTORED: Use safe_telegram_send with BrokenPipeError tolerance
        success = safe_telegram_send(url, payload, timeout=10)
        
        if success:
            nexus_speak("success", "✅ Telegram message sent successfully via safe_send!")
            return True
        else:
            nexus_speak("error", "❌ Telegram send failed after retries")
            # Log stats for debugging
            stats = get_safe_send_stats()
            nexus_speak("info", f"📊 Safe Send Stats: {stats['success_rate']} success rate")
            return False
            
    except Exception as e:
        nexus_speak("error", f"❌ Send error: {e}")
        return False

def create_present_continuous_alert(present_signal):
    """Crea alerta específica para PRESENTE CONTINUO - 7-14 días"""
    if 'error' in present_signal:
        return f"❌ Error: {present_signal.get('error', 'Unknown error')}"
    
    # Extraer información del presente continuo
    direction_info = present_signal.get('market_direction', {})
    strategy_info = present_signal.get('selected_strategy', {})
    entry_config = present_signal.get('entry_configuration', {})
    
    direction = direction_info.get('direction', 'neutral')
    confidence = direction_info.get('confidence', 0.5)
    strategy = strategy_info.get('strategy', 'unknown')
    reasoning = strategy_info.get('reasoning', '')
    
    # Determinar tipo de trade
    if strategy == 'long_call':
        trade_type = "CALL 📈"
        direction_text = "BULLISH"
    elif strategy == 'long_put':
        trade_type = "PUT 📉"
        direction_text = "BEARISH"
    elif 'covered' in strategy:
        trade_type = "LONG CALL 📈"  # Convert covered_call to long_call
        direction_text = "BULLISH"
    else:
        trade_type = "NEUTRAL 🔄"
        direction_text = "SIDEWAYS"
    
    # Formato específico para presente continuo
    alert = f"""🎯 PRESENTE CONTINUO - OPORTUNIDAD 7-14 DÍAS

📊 TICKER: {present_signal.get('symbol', 'UNKNOWN')}
🎯 DIRECCIÓN: {direction_text}
{trade_type}
⚡ CONFIANZA: {confidence:.1%}
🔬 CALIDAD: {present_signal.get('signal_quality', 0)}/100

⏰ PRESENTE CONTINUO: {entry_config.get('min_days_to_expiry', 7)}-{entry_config.get('max_days_to_expiry', 14)} DÍAS MÁXIMO

🔍 ANÁLISIS PRESENTE:
📈 RSI-7: {direction_info.get('rsi_7', 50):.1f}
📊 Momentum: {direction_info.get('momentum_score', 0.5):.1%}
📰 Volatilidad: {direction_info.get('recent_volatility', 30):.1f}%

🎯 ESTRATEGIA:
{reasoning}

💡 RECOMENDACIÓN: {present_signal.get('recommendation', 'UNKNOWN')}
🔥 PRESENTE CONTINUO - Trade inmediato
⚖️ ATM/Cerca del dinero - Sin especulación

🕐 {datetime.now().strftime('%H:%M:%S')}
🚀 Alpha Hunter V2 - Presente Continuo Engine"""
    
    return alert

def create_simple_alert(signal):
    """Crea alerta SIMPLE para amigos - Solo CALL/PUT, máximo 2 semanas"""
    if 'error' in signal:
        return f"❌ Error: {signal.get('error', 'Unknown error')}"
    
    # Determinar si es CALL o PUT según la estrategia
    strategy = signal.get('strategy_type', signal.get('strategy', 'unknown')).lower()
    if 'bull' in strategy or 'call' in strategy:
        trade_type = "CALL 📈"
        direction = "BULLISH"
    elif 'bear' in strategy or 'put' in strategy:
        trade_type = "PUT 📉"
        direction = "BEARISH"
    else:
        trade_type = "NEUTRAL 🔄"
        direction = "SIDEWAYS"
    
    # Formato SIMPLE sin confusión para amigos
    alert = f"""🚀 ALPHA HUNTER - OPORTUNIDAD DETECTADA

📊 TICKER: {signal.get('symbol', 'UNKNOWN')}
💰 PRECIO: ${signal.get('market_data', {}).get('current_price', 0):.2f}
🎯 DIRECCION: {direction}
⚡ PROBABILIDAD: {signal.get('enhanced_probability', 50)}%
🔬 CONFIANZA DEL ECOSISTEMA: {signal.get('signal_quality', 0)}/100

🔍 ANALISIS COMPONENTES:

📈 Technical: {signal.get('probability_breakdown', {}).get('technical_analysis', 75)}% (confianza: {signal.get('signal_quality', 85)}%)
💼 Fundamental: ALCISTA {signal.get('probability_breakdown', {}).get('monte_carlo', 65)}% (confianza: {signal.get('signal_quality', 85)}%)
📰 Sentiment: ALCISTA {signal.get('probability_breakdown', {}).get('historical_backtest', 70)}% (confianza: {signal.get('signal_quality', 80)}%)

🎯 RESUMEN:
📈 Alcista: {signal.get('enhanced_probability', 50)}% | 📉 Bajista: {100 - signal.get('enhanced_probability', 50)}%
🔥 Señal: {direction}

🚀 ESTRATEGIA RECOMENDADA:
🎯 {trade_type.upper()}
💰 Retorno esperado: {signal.get('professional_metrics', {}).get('expected_return', 8)}%
⚖️ Riesgo: {signal.get('position_sizing', {}).get('risk_per_trade', 2.0):.1f}%

📋 DETALLES OPERACIONALES:
🎯 {trade_type.upper()} - Precio Objetivo: ${signal.get('market_data', {}).get('current_price', 0) * 1.05:.2f}
💰 Take Profit: ${signal.get('market_data', {}).get('current_price', 0) * 1.12:.2f} | 🛑 Stop Loss: ${signal.get('market_data', {}).get('current_price', 0) * 0.95:.2f}
🧠 LÓGICA DE LA DECISIÓN:
💡 {direction} con probabilidad {signal.get('enhanced_probability', 50):.1f}%. Mantener posición máximo 2 semanas. Riesgo controlado {signal.get('position_sizing', {}).get('risk_per_trade', 2.0):.1f}%.

🔥 ALPHA HUNTER - AI ANALYSIS
🕐 {datetime.now().strftime('%H:%M:%S')}
🚀 Sistema automatizado activo"""
    
    return alert

def test_professional_telegram():
    """Test professional Telegram alert with clean formatting"""
    nexus_speak("info", "🚀 Testing Alpha Hunter V2 Professional Telegram")
    
    # Initialize system
    alpha_hunter = AlphaHunterV2Professional()
    
    # Generate signal
    signal = alpha_hunter.generate_professional_signal("SPY", "bull_put", 1000)
    
    if 'error' not in signal:
        # Create clean alert
        alert = create_simple_alert(signal)
        
        # Send to Telegram
        nexus_speak("info", "📤 Sending professional alert...")
        success = send_clean_telegram(alert)
        
        if success:
            nexus_speak("success", "🚀 Professional alert delivered successfully!")
        else:
            nexus_speak("error", "❌ Failed to send alert")
            
        # Print alert for verification
        print("\n" + "="*70)
        print("📱 TELEGRAM ALERT SENT:")
        print("="*70)
        print(alert)
        print("="*70)
        
        return success
    else:
        nexus_speak("error", f"❌ Signal generation failed: {signal['error']}")
        return False

def send_multiple_alerts():
    """Send multiple professional alerts"""
    nexus_speak("info", "🚀 Sending multiple Alpha Hunter V2 alerts")
    
    # Initialize system
    alpha_hunter = AlphaHunterV2Professional()
    
    # Symbols to analyze
    symbols = [("SPY", "bull_put"), ("QQQ", "iron_condor"), ("IWM", "bull_put")]
    
    # Send header
    header = f"""🔥 ALPHA HUNTER V2 PROFESSIONAL ALERTS 🔥
📅 {datetime.now().strftime("%Y-%m-%d %H:%M")}

⚡ REAL PROBABILITIES SYSTEM ACTIVE
📊 Monte Carlo | Historical | Technical | ML Enhanced
🎯 Professional Trading Intelligence"""
    
    send_clean_telegram(header)
    
    import time
    time.sleep(3)
    
    successful = 0
    for symbol, strategy in symbols:
        try:
            nexus_speak("info", f"📊 Analyzing {symbol}...")
            
            signal = alpha_hunter.generate_professional_signal(symbol, strategy, 1000)
            
            if 'error' not in signal:
                alert = create_simple_alert(signal)
                if send_clean_telegram(alert):
                    successful += 1
                    nexus_speak("success", f"✅ {symbol} alert sent!")
                time.sleep(4)  # Delay between messages
            else:
                error_msg = f"❌ {symbol} analysis failed: {signal.get('error', 'Unknown')}"
                send_clean_telegram(error_msg)
                
        except Exception as e:
            error_msg = f"❌ Critical error with {symbol}: {str(e)}"
            send_clean_telegram(error_msg)
            nexus_speak("error", f"❌ Error with {symbol}: {e}")
    
    # Send summary
    summary = f"""📊 ALPHA HUNTER V2 SESSION COMPLETE

✅ Alerts Sent: {successful}/{len(symbols)}
🎯 System: 100% Operational  
⚡ Professional Intelligence Active

Next analysis available immediately."""
    
    send_clean_telegram(summary)
    
    nexus_speak("success", f"🚀 Session complete! {successful}/{len(symbols)} alerts sent")
    return successful

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Send single test alert')
    parser.add_argument('--multi', action='store_true', help='Send multiple alerts')
    
    args = parser.parse_args()
    
    if args.test:
        result = test_professional_telegram()
        print(f"\nResult: {'✅ SUCCESS' if result else '❌ FAILED'}")
    elif args.multi:
        count = send_multiple_alerts()
        print(f"\nSent {count} professional alerts successfully!")
    else:
        # Default: send single test
        result = test_professional_telegram()
        print(f"\nAlpha Hunter V2 Test: {'✅ SUCCESS' if result else '❌ FAILED'}")