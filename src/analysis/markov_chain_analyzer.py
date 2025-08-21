import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

class MarkovChainAnalyzer:
    """
    Analizador de Cadenas de Markov para estados de mercado (precio y volatilidad).
    """
    def __init__(self):
        # Definición de estados de movimiento de precio (retorno diario)
        self.price_states = {
            'FUERTE_ALCISTA': (0.015, np.inf), # > +1.5%
            'MODERADO_ALCISTA': (0.002, 0.015), # +0.2% a +1.5%
            'LATERAL': (-0.002, 0.002), # -0.2% a +0.2%
            'MODERADO_BAJISTA': (-0.015, -0.002), # -1.5% a -0.2%
            'FUERTE_BAJISTA': (-np.inf, -0.015) # < -1.5%
        }
        # Definición de estados de volatilidad implícita (ej. de opciones ATM)
        self.iv_states = {
            'BAJA_VOLATILIDAD': (0.0, 0.20), # < 20%
            'MEDIA_VOLATILIDAD': (0.20, 0.40), # 20% a 40%
            'ALTA_VOLATILIDAD': (0.40, np.inf) # > 40%
        }
        self.all_states = self._generate_combined_states()
        self.transition_matrix = None

    def _generate_combined_states(self):
        """Genera todos los estados combinados posibles (precio_volatilidad)."""
        combined_states = []
        for p_state in self.price_states.keys():
            for iv_state in self.iv_states.keys():
                combined_states.append(f'{p_state}_{iv_state}')
        return sorted(combined_states)

    def _get_state(self, price_return, iv):
        """Determina el estado combinado para un retorno de precio y IV dados."""
        p_state = 'UNKNOWN_PRICE'
        for state, (lower, upper) in self.price_states.items():
            if lower <= price_return < upper:
                p_state = state
                break
        
        iv_state = 'UNKNOWN_IV'
        for state, (lower, upper) in self.iv_states.items():
            if lower <= iv < upper:
                iv_state = state
                break
        
        return f'{p_state}_{iv_state}'

    def _fetch_historical_data(self, ticker, period="2y"):
        """Obtiene datos históricos de precios y calcula retornos diarios."""
        print(f"[MarkovChainAnalyzer] Obteniendo datos históricos para {ticker}...")
        ticker_obj = yf.Ticker(ticker)
        hist_data = ticker_obj.history(period=period, interval="1d")
        if hist_data.empty:
            print(f"[MarkovChainAnalyzer ERROR] No se pudieron obtener datos históricos para {ticker}.")
            return None
        
        hist_data['Daily_Return'] = hist_data['Close'].pct_change()
        
        # TODO: Implementar la obtención de volatilidad implícita histórica de opciones ATM.
        # Por ahora, usaremos una volatilidad histórica simple como placeholder.
        hist_data['Implied_Volatility'] = hist_data['Close'].rolling(window=20).std() * np.sqrt(252) # Volatilidad anualizada de 20 días
        
        hist_data.dropna(inplace=True)
        return hist_data

    def build_transition_matrix(self, ticker_or_returns, period="2y"):
        """
        Construye la matriz de transición de Markov para un ticker dado.
        Acepta ticker string o pandas Series de returns directamente.
        """
        # Check if we received returns directly (from probability_engine_v2.py)
        if hasattr(ticker_or_returns, 'iloc'):  # pandas Series
            print(f"[MarkovChainAnalyzer] Using provided returns series...")
            returns_series = ticker_or_returns
            state_sequence = []
            for return_val in returns_series:
                # 🚨 CRITICAL FIX: Handle division by zero in state classification
                if pd.isna(return_val) or return_val == float('inf') or return_val == float('-inf'):
                    continue
                state = self._get_state(return_val, 0.25)  # Default IV
                state_sequence.append(state)
        else:
            # Original ticker string logic
            hist_data = self._fetch_historical_data(ticker_or_returns, period)
            if hist_data is None: 
                return None
            
            print(f"[MarkovChainAnalyzer] Construyendo secuencia de estados para {ticker_or_returns}...")
            state_sequence = []
            for index, row in hist_data.iterrows():
                # 🚨 CRITICAL FIX: Validate data before state calculation
                daily_return = row['Daily_Return']
                implied_vol = row['Implied_Volatility']
                
                if pd.isna(daily_return) or pd.isna(implied_vol):
                    continue
                if daily_return == float('inf') or daily_return == float('-inf'):
                    continue
                    
                state = self._get_state(daily_return, implied_vol)
                state_sequence.append(state)
        
        # Inicializar la matriz de conteo de transiciones
        state_to_index = {state: i for i, state in enumerate(self.all_states)}
        num_states = len(self.all_states)
        transition_counts = np.zeros((num_states, num_states))

        print(f"[MarkovChainAnalyzer] Calculando transiciones para {ticker}...")
        for i in range(len(state_sequence) - 1):
            current_state = state_sequence[i]
            next_state = state_sequence[i+1]
            
            if current_state in state_to_index and next_state in state_to_index:
                current_idx = state_to_index[current_state]
                next_idx = state_to_index[next_state]
                transition_counts[current_idx, next_idx] += 1

        # 🚨 CRITICAL FIX: Convertir conteos a probabilidades with ZeroDivisionError protection
        transition_matrix = np.zeros((num_states, num_states))
        for i in range(num_states):
            row_sum = transition_counts[i, :].sum()
            if row_sum > 0:
                transition_matrix[i, :] = transition_counts[i, :] / row_sum
            else:
                # Fallback: uniform distribution if no transitions observed
                transition_matrix[i, :] = 1.0 / num_states
        
        self.transition_matrix = pd.DataFrame(transition_matrix, index=self.all_states, columns=self.all_states)
        ticker_name = ticker_or_returns if isinstance(ticker_or_returns, str) else "returns_series"
        print(f"[MarkovChainAnalyzer] Matriz de transición construida para {ticker_name}.\n")
        return self.transition_matrix

    def get_current_state(self, ticker):
        """Determina el estado actual del mercado para un ticker."""
        ticker_obj = yf.Ticker(ticker)
        
        # 1. Obtener datos de precios para el retorno diario
        hist_data = ticker_obj.history(period="2d", interval="1d")
        if hist_data.empty or len(hist_data) < 2:
            print(f"[MarkovChainAnalyzer ERROR] No hay suficientes datos de precios para determinar el estado actual de {ticker}.")
            return 'UNKNOWN_STATE'
        
        last_close = hist_data['Close'].iloc[-1]
        prev_close = hist_data['Close'].iloc[-2]
        # 🚨 CRITICAL FIX: Prevent ZeroDivisionError
        daily_return = (last_close - prev_close) / prev_close if prev_close > 0 else 0

        # 2. Obtener IV actual de la opción ATM más cercana
        current_iv = 0.20 # Valor por defecto
        try:
            # Obtener la primera fecha de expiración
            exp_date = ticker_obj.options[0]
            # Obtener la cadena de opciones para esa fecha
            opt_chain = ticker_obj.option_chain(exp_date)
            
            # Encontrar la opción de compra (call) At-The-Money (ATM)
            atm_calls = opt_chain.calls
            if not atm_calls.empty:
                # Encontrar el strike más cercano al último precio de cierre
                atm_strike_idx = (atm_calls['strike'] - last_close).abs().argmin()
                atm_call = atm_calls.iloc[atm_strike_idx]
                current_iv = atm_call['impliedVolatility']
                print(f"[MarkovChainAnalyzer] IV obtenida de la opción Call ATM {atm_call['contractSymbol']}: {current_iv:.4f}")
            else:
                print(f"[MarkovChainAnalyzer WARNING] No se encontraron opciones de compra para {ticker} en la fecha {exp_date}.")

        except Exception as e:
            print(f"[MarkovChainAnalyzer WARNING] No se pudo obtener la IV de la cadena de opciones para {ticker}. Usando valor por defecto. Error: {e}")

        return self._get_state(daily_return, current_iv)
    
    def classify_return_state(self, return_value):
        """Clasifica un valor de retorno en su estado correspondiente (solo precio)."""
        if pd.isna(return_value) or return_value == float('inf') or return_value == float('-inf'):
            return 'LATERAL_MEDIA_VOLATILIDAD'  # Default fallback
        
        # Solo clasificar por precio, usar volatilidad media por defecto
        for state, (lower, upper) in self.price_states.items():
            if lower <= return_value < upper:
                return f"{state}_MEDIA_VOLATILIDAD"  # Default to medium volatility
        
        return 'LATERAL_MEDIA_VOLATILIDAD'  # Fallback

    def predict_next_state_probabilities(self, current_state):
        """
        Predice las probabilidades de los próximos estados dado el estado actual.
        """
        if self.transition_matrix is None:
            print("[MarkovChainAnalyzer ERROR] La matriz de transición no ha sido construida.")
            return None
        
        if current_state not in self.all_states:
            print(f"[MarkovChainAnalyzer ERROR] Estado actual desconocido: {current_state}")
            return None
        
        return self.transition_matrix.loc[current_state]
    
    def predict_next_state(self, current_state):
        """
        Predice el próximo estado más probable (para compatibilidad con alpha_hunter_v2_unified.py).
        """
        if self.transition_matrix is None:
            print("[MarkovChainAnalyzer ERROR] La matriz de transición no ha sido construida.")
            return {'bullish': 0.4, 'bearish': 0.3, 'lateral': 0.3}
        
        if current_state not in self.all_states:
            print(f"[MarkovChainAnalyzer ERROR] Estado actual desconocido: {current_state}")
            return {'bullish': 0.4, 'bearish': 0.3, 'lateral': 0.3}
        
        probs = self.transition_matrix.loc[current_state]
        
        # Aggregate probabilities by direction
        bullish_prob = 0
        bearish_prob = 0  
        lateral_prob = 0
        
        for state, prob in probs.items():
            if 'FUERTE_ALCISTA' in state or 'MODERADO_ALCISTA' in state:
                bullish_prob += prob
            elif 'FUERTE_BAJISTA' in state or 'MODERADO_BAJISTA' in state:
                bearish_prob += prob
            elif 'LATERAL' in state:
                lateral_prob += prob
        
        return {
            'bullish': round(bullish_prob, 3),
            'bearish': round(bearish_prob, 3),
            'lateral': round(lateral_prob, 3)
        }

# Ejemplo de uso (para pruebas)
# if __name__ == '__main__':
#     analyzer = MarkovChainAnalyzer()
#     ticker = 'SPY'
#     matrix = analyzer.build_transition_matrix(ticker)
#     if matrix is not None:
#         print("Matriz de Transición:")
#         print(matrix)
#         
#         current_state = analyzer.get_current_state(ticker)
#         print(f"\nEstado actual para {ticker}: {current_state}")
#         
#         if current_state != 'UNKNOWN_STATE':
#             next_state_probs = analyzer.predict_next_state_probabilities(current_state)
#             if next_state_probs is not None:
#                 print("Probabilidades de los próximos estados:")
#                 print(next_state_probs.sort_values(ascending=False).head(5))