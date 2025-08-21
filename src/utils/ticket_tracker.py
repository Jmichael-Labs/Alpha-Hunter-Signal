#!/usr/bin/env python3
"""
TICKET TRACKER - Sistema para evitar repetición de tickets en Alpha Hunter
Mantiene historial de tickets enviados y asegura solo oportunidades nuevas
"""

import json
import os
from datetime import datetime, timedelta
import hashlib

class TicketTracker:
    def __init__(self):
        self.tracker_file = "/Volumes/DiskExFAT 1/system_data/nucleo_agi/alpha_hunter/sent_tickets.json"
        self.daily_tickets = self.load_daily_tickets()
        
    def load_daily_tickets(self):
        """Carga tickets enviados del día actual."""
        try:
            if os.path.exists(self.tracker_file):
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
                
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Limpiar datos antiguos (mantener solo últimos 3 días)
                cutoff_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
                cleaned_data = {}
                
                for date, tickets in data.items():
                    if date >= cutoff_date:
                        cleaned_data[date] = tickets
                
                # Guardar datos limpiados
                with open(self.tracker_file, 'w') as f:
                    json.dump(cleaned_data, f, indent=2)
                
                return cleaned_data.get(today, [])
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ Error cargando tickets: {e}")
            return []
    
    def save_daily_tickets(self):
        """Guarda tickets del día actual."""
        try:
            # Cargar datos existentes
            if os.path.exists(self.tracker_file):
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Actualizar día actual
            today = datetime.now().strftime('%Y-%m-%d')
            data[today] = self.daily_tickets
            
            # Guardar
            with open(self.tracker_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error guardando tickets: {e}")
    
    def generate_ticket_hash(self, symbol, option_type, strike, expiry_date):
        """Genera hash único para un ticket."""
        ticket_string = f"{symbol}_{option_type}_{strike}_{expiry_date}"
        return hashlib.md5(ticket_string.encode()).hexdigest()[:8]
    
    def is_ticket_already_sent(self, symbol, option_type, strike, expiry_date):
        """Verifica si un ticket ya fue enviado hoy."""
        ticket_hash = self.generate_ticket_hash(symbol, option_type, strike, expiry_date)
        
        for sent_ticket in self.daily_tickets:
            if sent_ticket.get('hash') == ticket_hash:
                return True, sent_ticket.get('sent_time', 'unknown')
        
        return False, None
    
    def mark_ticket_as_sent(self, symbol, option_type, strike, expiry_date, additional_data=None):
        """Marca un ticket como enviado."""
        ticket_hash = self.generate_ticket_hash(symbol, option_type, strike, expiry_date)
        
        ticket_record = {
            'hash': ticket_hash,
            'symbol': symbol,
            'option_type': option_type,
            'strike': strike,
            'expiry_date': expiry_date,
            'sent_time': datetime.now().strftime('%H:%M:%S'),
            'timestamp': datetime.now().isoformat()
        }
        
        if additional_data:
            ticket_record.update(additional_data)
        
        self.daily_tickets.append(ticket_record)
        self.save_daily_tickets()
        
        return ticket_hash
    
    def get_todays_sent_count(self):
        """Obtiene cantidad de tickets enviados hoy."""
        return len(self.daily_tickets)
    
    def get_sent_symbols_today(self):
        """Obtiene lista de símbolos ya enviados hoy."""
        return list(set([str(ticket.get('symbol', '')) if isinstance(ticket, dict) else str(ticket) for ticket in self.daily_tickets]))
    
    def filter_new_opportunities(self, opportunities):
        """
        COMPUERTA LÓGICA DE SALIDA - Filtro anti-repetición de símbolos
        Bloquea CUALQUIER repetición del mismo símbolo+estrategia en el día
        Fuerza diversificación - máximo 1 ticket por símbolo por día
        """
        new_opportunities = []
        sent_symbols_today = self.get_sent_symbols_today()
        
        print(f"🛡️  ANTI-REPETITION GATE: {len(sent_symbols_today)} symbols already sent today: {sent_symbols_today}")
        
        for opp in opportunities:
            symbol = opp.get('symbol', '')
            option_type = opp.get('option_type', '').upper()
            strike = opp.get('strike', 0)
            expiry_date = opp.get('expiry_date', '')
            
            # BLOQUEO CRÍTICO: Si el símbolo ya fue enviado HOY, SKIP completamente
            if symbol in sent_symbols_today:
                print(f"🚫 SYMBOL GATE BLOCKED: {symbol} {option_type} ${strike} - Symbol already used today (diversification enforced)")
                continue
            
            # Verificar ticket exacto (backup check)
            is_sent, sent_time = self.is_ticket_already_sent(symbol, option_type, strike, expiry_date)
            
            if not is_sent:
                new_opportunities.append(opp)
            else:
                print(f"🔄 EXACT TICKET BLOCKED: {symbol} {option_type} ${strike} - Already sent at {sent_time}")
        
        # DIVERSIFICATION REPORT
        total_blocked = len(opportunities) - len(new_opportunities)
        if total_blocked > 0:
            print(f"🎯 DIVERSIFICATION ENFORCED: {total_blocked} opportunities blocked for symbol repetition")
            print(f"✅ PORTFOLIO DIVERSITY MAINTAINED: {len(new_opportunities)} unique symbols selected")
        
        return new_opportunities
    
    def get_sent_symbols_today_with_details(self):
        """Obtiene símbolos enviados hoy con detalles completos para exclusión."""
        sent_details = []
        
        for ticket in self.daily_tickets:
            sent_details.append({
                'symbol': ticket['symbol'],
                'option_type': ticket['option_type'],
                'strike': ticket['strike'],
                'expiry_date': ticket['expiry_date'],
                'sent_time': ticket['sent_time'],
                'hash': ticket['hash']
            })
        
        return sent_details
    
    def should_skip_symbol_analysis(self, symbol):
        """
        BLOQUEO PREVENTIVO DE ANÁLISIS - Evita repeticiones desde el origen
        Si un símbolo ya fue enviado HOY, NO lo analices para forzar diversificación
        """
        sent_symbols_today = self.get_sent_symbols_today()
        
        # BLOQUEO CRÍTICO: Si el símbolo ya fue usado HOY, SKIP análisis completamente
        if symbol in sent_symbols_today:
            return True, f"Symbol {symbol} already sent today - DIVERSIFICATION ENFORCED"
        
        # Backup: Si se enviaron múltiples tickets para este símbolo (edge case)
        symbol_tickets = [t for t in self.daily_tickets if t['symbol'] == symbol]
        if len(symbol_tickets) >= 1:  # Cambiado de 3 a 1 para máxima restricción
            return True, f"Symbol {symbol} already used - PORTFOLIO DIVERSITY PRIORITY"
        
        return False, None
    
    def get_daily_stats(self):
        """Obtiene estadísticas del día."""
        today_symbols = self.get_sent_symbols_today()
        
        stats = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_sent': self.get_todays_sent_count(),
            'unique_symbols': len(today_symbols),
            'symbols_sent': today_symbols,
            'last_sent': self.daily_tickets[-1]['sent_time'] if self.daily_tickets else None
        }
        
        return stats
    
    def clear_today_tickets(self):
        """Limpia tickets del día (para testing)."""
        self.daily_tickets = []
        self.save_daily_tickets()
        print("🧹 Tickets del día limpiados")
    
    def get_excluded_symbols_for_scanning(self):
        """
        LISTA DE EXCLUSIÓN PARA SCANNER - Fuerza búsqueda de símbolos diferentes
        Retorna lista de símbolos que deben ser completamente excluidos del análisis
        """
        sent_symbols_today = self.get_sent_symbols_today()
        
        if sent_symbols_today:
            print(f"🚫 EXCLUSION LIST FOR SCANNER: {len(sent_symbols_today)} symbols to skip: {sent_symbols_today}")
        
        return sent_symbols_today
    
    def enforce_portfolio_diversification(self, candidate_symbols):
        """
        FUERZA DIVERSIFICACIÓN DE PORTAFOLIO - Remueve símbolos repetidos
        Input: Lista de símbolos candidatos
        Output: Lista filtrada sin símbolos ya enviados hoy
        """
        sent_symbols_today = self.get_sent_symbols_today()
        
        # Filtrar símbolos que ya fueron enviados
        diversified_symbols = [symbol for symbol in candidate_symbols if symbol not in sent_symbols_today]
        
        removed_count = len(candidate_symbols) - len(diversified_symbols)
        
        if removed_count > 0:
            print(f"🎯 PORTFOLIO DIVERSIFICATION: {removed_count} symbols removed for repetition")
            print(f"   Removed symbols: {[s for s in candidate_symbols if s in sent_symbols_today]}")
            print(f"✅ Diversified symbols: {len(diversified_symbols)} unique candidates")
        
        return diversified_symbols

def test_ticket_tracker():
    """Test del sistema de tracking."""
    print("🧪 TESTING TICKET TRACKER")
    print("=" * 40)
    
    tracker = TicketTracker()
    
    # Test 1: Verificar ticket nuevo
    symbol, option_type, strike, expiry = "AAPL", "CALL", 150, "2024-09-20"
    
    is_sent, sent_time = tracker.is_ticket_already_sent(symbol, option_type, strike, expiry)
    print(f"1. AAPL CALL $150 ya enviado: {is_sent}")
    
    # Test 2: Marcar como enviado
    if not is_sent:
        ticket_hash = tracker.mark_ticket_as_sent(symbol, option_type, strike, expiry, {
            'probability': 75,
            'quality_score': 85
        })
        print(f"2. Ticket marcado como enviado: {ticket_hash}")
    
    # Test 3: Verificar nuevamente
    is_sent, sent_time = tracker.is_ticket_already_sent(symbol, option_type, strike, expiry)
    print(f"3. AAPL CALL $150 ahora enviado: {is_sent} at {sent_time}")
    
    # Test 4: Estadísticas
    stats = tracker.get_daily_stats()
    print(f"4. Stats del día: {stats}")
    
    # Test 5: Filtrar oportunidades
    test_opportunities = [
        {'symbol': 'AAPL', 'option_type': 'CALL', 'strike': 150, 'expiry_date': '2024-09-20'},
        {'symbol': 'MSFT', 'option_type': 'PUT', 'strike': 300, 'expiry_date': '2024-09-20'},
        {'symbol': 'AAPL', 'option_type': 'CALL', 'strike': 155, 'expiry_date': '2024-09-20'},
    ]
    
    filtered = tracker.filter_new_opportunities(test_opportunities)
    print(f"5. Oportunidades filtradas: {len(filtered)}/{len(test_opportunities)}")
    
    print("\n✅ Test completado")

if __name__ == "__main__":
    test_ticket_tracker()