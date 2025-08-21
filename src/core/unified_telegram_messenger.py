#!/usr/bin/env python3
"""
🚀 UNIFIED TELEGRAM MESSENGER
Sistema de mensajes que refleja el ECOSISTEMA UNIFICADO completo
Todas las probabilidades + Estrategia óptima + Análisis multi-dimensional
"""

import requests
import json
import os
from datetime import datetime

class UnifiedTelegramMessenger:
    """Generador de mensajes del ecosistema unificado"""
    
    def __init__(self):
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.telegram_channel_id = os.getenv('TELEGRAM_CHANNEL_ID')  # Para canal de señales
        
        # DEBUG: Log configuration on init
        print(f"🔧 UnifiedTelegramMessenger initialized:")
        print(f"   Personal chat: {self.telegram_chat_id}")
        print(f"   Channel: {self.telegram_channel_id}")
        print(f"   Bot token: {self.telegram_bot_token[:20] if self.telegram_bot_token else None}...")
        
        self.ecosystem_components = [
            'technical', 'fundamental', 'sentiment', 
            'machine_learning', 'quantum', 'market_psychology'
        ]
    
    def generate_unified_opportunity_alert(self, unified_analysis):
        """
        Generar alerta clara y organizada del ecosistema unificado
        Formato simplificado para fácil comprensión
        """
        
        ticker = unified_analysis.get('ticker', 'UNKNOWN')
        price = unified_analysis.get('current_price', 0.0)
        breakdown = unified_analysis.get('analysis_breakdown', {})
        unified = unified_analysis.get('unified_probability', {})
        strategy = unified_analysis.get('optimal_strategy', {})
        
        message_parts = []
        
        # 🎯 HEADER CLARO Y SIMPLE
        message_parts.append("🚀 ALPHA HUNTER - OPORTUNIDAD DETECTADA")
        message_parts.append("")
        message_parts.append(f"📊 TICKER: {ticker}")
        message_parts.append(f"💰 PRECIO: ${price:.2f}")
        message_parts.append(f"🎯 DIRECCION: {unified.get('dominant_direction', 'NEUTRAL')}")
        message_parts.append(f"⚡ PROBABILIDAD: {unified.get('dominant_probability', 0)}%")
        message_parts.append(f"🔬 CONFIANZA DEL ECOSISTEMA: {unified.get('confidence', 75)}%")
        message_parts.append("")
        
        # 🧮 ANÁLISIS SIMPLIFICADO POR COMPONENTES
        message_parts.append("🔍 ANALISIS COMPONENTES:")
        message_parts.append("")
        
        # Solo mostrar los 3 componentes más importantes
        important_components = ['technical', 'fundamental', 'sentiment']
        
        for component in important_components:
            if component in breakdown:
                data = breakdown[component]
                bull_prob = data.get('bullish_probability', 0)
                bear_prob = data.get('bearish_probability', 0)
                confidence = data.get('confidence', 0)
                
                # Icono simple
                icons = {'technical': '📈', 'fundamental': '💼', 'sentiment': '📰'}
                icon = icons.get(component, '🔍')
                
                # Señal dominante clara
                if bull_prob > bear_prob:
                    signal = f"ALCISTA {bull_prob:.0f}%"
                else:
                    signal = f"BAJISTA {bear_prob:.0f}%"
                
                message_parts.append(f"{icon} {component.title()}: {signal} (confianza: {confidence:.0f}%)")
        
        message_parts.append("")
        # 🎯 RESUMEN CONSOLIDADO  
        message_parts.append("🎯 RESUMEN:")
        bull_prob = unified.get('bullish_probability', 0)
        bear_prob = unified.get('bearish_probability', 0)
        message_parts.append(f"📈 Alcista: {bull_prob:.0f}% | 📉 Bajista: {bear_prob:.0f}%")
        message_parts.append(f"🔥 Señal: {unified.get('dominant_direction', 'NEUTRAL')}")
        message_parts.append("")
        
        # 🚀 ESTRATEGIA RECOMENDADA SIMPLE
        message_parts.append("🚀 ESTRATEGIA RECOMENDADA:")
        strategy_name = strategy.get('recommended_strategy', 'HOLD')
        expected_return = strategy.get('expected_return', 0)
        risk_level = strategy.get('risk_level', 'MEDIUM')
        
        # 🎯 PRESENT CONTINUOUS MAPPING: Solo estrategias permitidas (7-14 días)
        level_2_strategy_mapping = {
            'bull_put_spread': 'long_call',  # Bull Put Spread -> Long Call (both bullish)
            'bear_call_spread': 'long_put',  # Bear Call Spread -> Long Put (both bearish)
            'iron_condor': 'long_call',  # Iron Condor -> Long Call (simple)
            'iron_butterfly': 'long_call',  # Iron Butterfly -> Long Call (simple)
            'short_straddle': 'long_call',  # Short Straddle -> Long Call (simple)
            'short_strangle': 'long_call',  # Short Strangle -> Long Call (simple)
            'long_straddle': 'long_call',  # Long Straddle -> Long Call (directional)
            'long_strangle': 'long_put',  # Long Strangle -> Long Put (directional)
            'collar': 'long_call',  # Collar -> Long Call (simple)
            'protective_put': 'long_put'  # Protective Put -> Long Put (defensive)
        }
        
        # Apply Level 2 mapping if needed for DISPLAY NAME
        display_strategy_name = strategy_name
        if strategy_name in level_2_strategy_mapping:
            original_strategy = strategy_name
            display_strategy_name = level_2_strategy_mapping[strategy_name]
            strategy_name = display_strategy_name  # Use mapped name for operational details too
            print(f"[LEVEL_2_MAPPING] {original_strategy} -> {strategy_name}")
        
        message_parts.append(f"🎯 {display_strategy_name.upper().replace('_', ' ')}")
        message_parts.append(f"💰 Retorno esperado: {expected_return}%")
        message_parts.append(f"⚖️ Riesgo: {risk_level}")
        message_parts.append("")
        # 📋 DETALLES OPERACIONALES COMPLETOS
        message_parts.append("📋 DETALLES OPERACIONALES:")
        
        # Calcular fechas y strikes basados en estrategia
        from datetime import datetime, timedelta
        
        # Fecha de vencimiento PRESENTE CONTINUO (7-14 días máximo)
        expiry_date = datetime.now() + timedelta(days=10)  # 10 días = presente continuo
        expiry_str = expiry_date.strftime("%d/%m")
        
        if strategy_name == 'long_call':
            strike = price * 1.01  # 1% OTM for affordability (cheaper contracts)
            take_profit = price * 1.03  # +3% realistic for 7-14 day options
            stop_loss = price * 0.975  # -2.5% conservative stop
            
            message_parts.append(f"🎯 LONG CALL (1% OTM) - Strike: ${strike:.2f} - Vence: {expiry_str}")
            message_parts.append(f"💰 Take Profit: ${take_profit:.2f} (+3%) | 🛑 Stop Loss: ${stop_loss:.2f} (-2.5%)")
            
        elif strategy_name == 'long_put':
            strike = price * 0.99  # 1% OTM for affordability (cheaper contracts)
            take_profit = price * 0.97  # -3% realistic for 7-14 day options
            stop_loss = price * 1.025  # +2.5% conservative stop
            
            message_parts.append(f"🎯 LONG PUT (1% OTM) - Strike: ${strike:.2f} - Vence: {expiry_str}")
            message_parts.append(f"💰 Take Profit: ${take_profit:.2f} (-3%) | 🛑 Stop Loss: ${stop_loss:.2f} (+2.5%)")
            
        elif strategy_name == 'long_straddle':
            call_strike = price  # ATM
            put_strike = price   # ATM
            take_profit = price * 1.04  # +4% conservative for volatility plays
            stop_loss = price * 0.975   # -2.5% tight stop
            
            message_parts.append(f"🎯 LONG STRADDLE - Strikes: ${call_strike:.2f}C/${put_strike:.2f}P - Vence: {expiry_str}")
            message_parts.append(f"💰 Take Profit: ${take_profit:.2f} (+4%) | 🛑 Stop Loss: ${stop_loss:.2f} (-2.5%)")
            
        elif strategy_name == 'long_strangle':
            call_strike = price * 1.03  # 3% OTM
            put_strike = price * 0.97   # 3% OTM
            take_profit = price * 1.04  # +4% conservative
            stop_loss = price * 0.975   # -2.5% tight stop
            
            message_parts.append(f"🎯 LONG STRANGLE - Strikes: ${call_strike:.2f}C/${put_strike:.2f}P - Vence: {expiry_str}")
            message_parts.append(f"💰 Take Profit: ${take_profit:.2f} (+4%) | 🛑 Stop Loss: ${stop_loss:.2f} (-2.5%)")
            
        elif strategy_name == 'collar':
            call_strike = price * 1.03  # 3% OTM Call (sell)
            put_strike = price * 0.97   # 3% OTM Put (buy)
            take_profit = price * 1.025 # +2.5% conservative
            stop_loss = price * 0.975   # -2.5% balanced
            
            message_parts.append(f"🎯 COLLAR - Call: ${call_strike:.2f} Put: ${put_strike:.2f} - Vence: {expiry_str}")
            message_parts.append(f"💰 Take Profit: ${take_profit:.2f} (+2.5%) | 🛑 Stop Loss: ${stop_loss:.2f} (-2.5%)")
            
        elif strategy_name == 'protective_put':
            put_strike = price * 0.97   # 3% OTM protective put
            take_profit = price * 1.03  # +3% conservative
            stop_loss = price * 0.975   # -2.5% conservative stop
            
            message_parts.append(f"🎯 PROTECTIVE PUT - Strike: ${put_strike:.2f} - Vence: {expiry_str}")
            message_parts.append(f"💰 Take Profit: ${take_profit:.2f} (+3%) | 🛑 Stop Loss: ${stop_loss:.2f} (-2.5%)")
            
        # covered_call REMOVED - handled as long_call above
        else:  # Default case - shares (conservative targets)
            take_profit = price * 1.03  # +3% conservative for shares
            stop_loss = price * 0.975   # -2.5% conservative stop
            
            message_parts.append(f"🎯 POSICIÓN EN ACCIONES")
            message_parts.append(f"💰 Take Profit: ${take_profit:.2f} (+3%) | 🛑 Stop Loss: ${stop_loss:.2f} (-2.5%)")
        
        # 🧠 LÓGICA DE LA DECISIÓN (TRADER PROFESIONAL)
        message_parts.append("🧠 LÓGICA DE LA DECISIÓN:")
        
        # Generar explicación profesional basada en los datos del análisis
        tech_signal = "alcista" if breakdown.get('technical', {}).get('bullish_probability', 0) > 50 else "bajista"
        fund_signal = "sólido" if breakdown.get('fundamental', {}).get('bullish_probability', 0) > 50 else "débil"
        sent_signal = "positivo" if breakdown.get('sentiment', {}).get('bullish_probability', 0) > 50 else "negativo"
        
        prob = unified.get('dominant_probability', 0)
        direction = unified.get('dominant_direction', 'NEUTRAL')
        
        # Construir explicación lógica profesional con Level 2 strategies ONLY
        if direction == 'BULLISH' and prob > 55:
            if strategy_name == 'long_call':
                explanation = f"Confluencia alcista: técnico {tech_signal}, fundamentales {fund_signal}. {prob}% de probabilidad alcista justifica long call ITM. Target conservador ${price * 1.03:.2f} (+3%) apropiado para plazo 7-14 días con Level 2 approval."
            elif strategy_name == 'long_straddle':
                explanation = f"Volatilidad esperada: análisis técnico {tech_signal} con fundamentales {fund_signal}. {prob}% probabilidad de movimiento significativo. Long straddle captura breakout en cualquier dirección. Level 2 strategy ideal para alta volatilidad."
            elif strategy_name == 'long_strangle':
                explanation = f"Volatilidad esperada alta: técnico {tech_signal}, fundamentales {fund_signal}. {prob}% probabilidad de movimiento significativo. Long strangle captura breakout direccional. Level 2 strategy para alta volatilidad."
            else:
                explanation = f"Señales convergentes: análisis técnico {tech_signal}, base fundamental {fund_signal}. {prob}% probabilidad alcista con soporte clave en ${price * 0.95:.2f}. Estrategia Level 2 conservadora para aprovechar tendencia sin sobreexposición."
                
        elif direction == 'BEARISH' and prob > 55:
            if strategy_name == 'long_put':
                explanation = f"Confluencia bajista confirmada: {prob}% probabilidad de caída. Múltiples señales (técnico {tech_signal}, fundamentales {fund_signal}) sugieren debilidad. Long put ITM con target conservador ${price * 0.97:.2f} (-3%) apropiado para 7-14 días con Level 2 approval."
            elif strategy_name == 'protective_put':
                explanation = f"Protección defensiva: análisis técnico {tech_signal}, fundamentales {fund_signal}. {prob}% probabilidad bajista requiere protección. Protective put asegura posición mientras mantenemos upside potential. Level 2 strategy de protección."
            elif strategy_name == 'collar':
                explanation = f"Estrategia defensiva balanceada: técnico {tech_signal}, fundamentales {fund_signal}. {prob}% probabilidad bajista. Collar protege downside while capping upside. Level 2 strategy ideal para mercados inciertos."
            else:
                explanation = f"Presión bajista evidente: análisis técnico {tech_signal}, base {fund_signal}. {prob}% probabilidad bajista con resistencia en ${price * 1.05:.2f}. Estrategia Level 2 defensiva para proteger capital."
        else:
            # Mercado lateral o baja convicción
            if strategy_name == 'long_strangle':
                explanation = f"Volatilidad lateral esperada: técnico {tech_signal}, fundamentales {fund_signal}. {prob}% probabilidad de breakout direccional. Long strangle captura movimiento en rango amplio. Level 2 strategy neutral."
            else:
                explanation = f"Señales mixtas: técnico {tech_signal}, fundamentales {fund_signal}, sentimiento {sent_signal}. Probabilidad {prob}% sugiere rango lateral. Estrategia Level 2 neutral busca generar ingresos en consolidación entre ${price * 0.96:.2f}-${price * 1.04:.2f}."
        
        message_parts.append(f"💡 {explanation}")
        message_parts.append("")
        # 🔥 FIRMA SIMPLE
        message_parts.append("🔥 ALPHA HUNTER - AI ANALYSIS")
        message_parts.append(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
        message_parts.append("🚀 Sistema automatizado activo")
        
        return "\n".join(message_parts)
    
    def send_unified_alert(self, unified_analysis):
        """Enviar alerta unificada por Telegram a múltiples destinos"""
        
        if not self.telegram_bot_token:
            print("❌ Telegram bot token not configured")
            return False
        
        message = self.generate_unified_opportunity_alert(unified_analysis)
        ticker = unified_analysis.get('ticker', 'UNKNOWN')
        
        results = []
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        
        # 1. Enviar a chat personal (si está configurado)
        if self.telegram_chat_id:
            try:
                payload = {
                    "chat_id": int(self.telegram_chat_id),
                    "text": message,
                    "parse_mode": "HTML"
                }
                print(f"📱 ENVIANDO A CHAT PERSONAL {self.telegram_chat_id}...")
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Alert sent to personal chat: {ticker}")
                    results.append(True)
                else:
                    print(f"❌ Failed to send to personal chat: {response.status_code}")
                    print(f"   Response: {response.text}")
                    results.append(False)
            except Exception as e:
                print(f"❌ Error sending to personal chat: {e}")
                results.append(False)
        else:
            print("⚠️ TELEGRAM_CHAT_ID not configured - skipping personal chat")
        
        # 2. Enviar a canal de señales (si está configurado)
        if self.telegram_channel_id:
            try:
                payload = {
                    "chat_id": self.telegram_channel_id,  # Channel ID como string
                    "text": message,
                    "parse_mode": "HTML"
                }
                print(f"📡 ENVIANDO A CANAL {self.telegram_channel_id}...")
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Alert sent to signals channel: {ticker}")
                    results.append(True)
                else:
                    print(f"❌ Failed to send to channel: {response.status_code}")
                    print(f"   Response: {response.text}")
                    results.append(False)
            except Exception as e:
                print(f"❌ Error sending to channel: {e}")
                results.append(False)
        else:
            print("⚠️ TELEGRAM_CHANNEL_ID not configured - skipping channel")
        
        # Retornar True si al menos uno fue exitoso
        return any(results) if results else False
    
    def generate_market_summary(self, multiple_analyses):
        """Generar resumen del mercado con múltiples análisis"""
        
        if not multiple_analyses:
            return "No hay análisis disponibles"
        
        message_parts = []
        
        # Header
        message_parts.append("📊 ALPHA HUNTER - RESUMEN DEL MERCADO")
        message_parts.append(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        message_parts.append("")
        message_parts.append(f"🎯 OPORTUNIDADES ENCONTRADAS: {len(multiple_analyses)}")
        message_parts.append("")
        
        # Summary by strategy
        strategies = {}
        directions = {'BULLISH': 0, 'BEARISH': 0, 'SIDEWAYS': 0}
        total_return = 0
        
        for analysis in multiple_analyses:
            strategy_name = analysis['optimal_strategy']['recommended_strategy']
            direction = analysis['unified_probability']['dominant_direction']
            expected_return = analysis['optimal_strategy']['expected_return']
            
            if strategy_name not in strategies:
                strategies[strategy_name] = []
            strategies[strategy_name].append(analysis.get('ticker', 'UNKNOWN'))
            
            directions[direction] += 1
            total_return += expected_return
        
        # Market direction summary
        message_parts.append("📈 DIRECCIONES DEL MERCADO:")
        for direction, count in directions.items():
            percentage = (count / len(multiple_analyses)) * 100
            message_parts.append(f"   {direction}: {count} tickers ({percentage:.1f}%)")
        
        message_parts.append("")
        
        # Strategy distribution
        message_parts.append("🎲 ESTRATEGIAS RECOMENDADAS:")
        for strategy_name, tickers in strategies.items():
            message_parts.append(f"   {strategy_name}: {', '.join(tickers)}")
        
        message_parts.append("")
        
        # Performance metrics
        avg_return = total_return / len(multiple_analyses)
        message_parts.append(f"💰 RETORNO PROMEDIO ESPERADO: {avg_return:.1f}%")
        message_parts.append(f"🎯 TOTAL OPORTUNIDADES: {len(multiple_analyses)}")
        message_parts.append("")
        
        # Top opportunities
        sorted_analyses = sorted(multiple_analyses, 
                               key=lambda x: x['optimal_strategy']['expected_return'], 
                               reverse=True)
        
        message_parts.append("🏆 TOP 3 OPORTUNIDADES:")
        for i, analysis in enumerate(sorted_analyses[:3], 1):
            ticker = analysis.get('ticker', 'UNKNOWN')
            return_pct = analysis['optimal_strategy']['expected_return']
            strategy = analysis['optimal_strategy']['recommended_strategy']
            message_parts.append(f"   {i}. {ticker}: {return_pct:.1f}% ({strategy})")
        
        message_parts.append("")
        message_parts.append("🚀 ECOSISTEMA UNIFICADO ACTIVO - TODAS LAS OPORTUNIDADES CAPTURADAS")
        
        return "\n".join(message_parts)


def test_unified_messenger():
    """Test del messenger unificado"""
    
    # Mock data que simula el resultado del ecosistema unificado
    mock_analysis = {
        'ticker': 'BAC',
        'current_price': 45.32,
        'analysis_breakdown': {
            'technical': {
                'bullish_probability': 65.0,
                'bearish_probability': 35.0,
                'confidence': 78.5,
                'rsi': 52.3,
                'macd_signal': 'bullish'
            },
            'fundamental': {
                'bullish_probability': 70.0,
                'bearish_probability': 30.0,
                'confidence': 84.0,
                'pe_ratio': 12.5,
                'pb_ratio': 1.2
            },
            'sentiment': {
                'bullish_probability': 76.6,
                'bearish_probability': 23.4,
                'confidence': 75.4,
                'analyst_rating': 'buy',
                'news_sentiment': 0.3
            },
            'machine_learning': {
                'bullish_probability': 50.0,
                'bearish_probability': 50.0,
                'confidence': 91.0,
                'average_prediction': 2.5
            },
            'quantum': {
                'bullish_probability': 58.9,
                'bearish_probability': 41.1,
                'confidence': 87.7,
                'coherence': 0.875,
                'superposition': 'constructive'
            },
            'market_psychology': {
                'bullish_probability': 50.0,
                'bearish_probability': 50.0,
                'confidence': 79.9,
                'fear_greed_index': 45.2,
                'crowd_behavior': 'neutral'
            }
        },
        'unified_probability': {
            'bullish_probability': 62.1,
            'bearish_probability': 37.9,
            'sideways_probability': 15.3,
            'dominant_direction': 'BULLISH',
            'signal_strength': 'MODERATE',
            'dominant_probability': 62.1,
            'confidence': 82.4,
            'total_components': 6
        },
        'optimal_strategy': {
            'recommended_strategy': 'bull_put_spread',
            'reasoning': 'Moderate bullish - collect premium with protection',
            'expected_return': 12.8,
            'risk_level': 'MEDIUM',
            'time_horizon': '2-4 weeks',
            'success_probability': 62.1
        },
        'timestamp': datetime.now().isoformat()
    }
    
    messenger = UnifiedTelegramMessenger()
    
    print("🚀 TESTING UNIFIED TELEGRAM MESSENGER")
    print("=" * 60)
    
    # Generate message
    message = messenger.generate_unified_opportunity_alert(mock_analysis)
    
    print("📱 GENERATED MESSAGE:")
    print("=" * 60)
    print(message.replace('\\n', '\n'))
    
    print("\n" + "=" * 60)
    print("✅ UNIFIED MESSAGE SYSTEM READY")
    
    return message


if __name__ == "__main__":
    test_unified_messenger()