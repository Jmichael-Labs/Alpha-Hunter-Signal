#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - INTELLIGENT API CONTROLLER
Control lógico inteligente para optimizar uso de APIs
Distribución, rate limiting, cache y monitoreo de recursos
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
import threading
from collections import defaultdict, deque
import hashlib
from ticker_validator import validate_ticker, log_invalid_ticker

# Import our systems
try:
    from api_credentials_manager import api_manager
    from robust_data_sources import robust_data_manager
except ImportError:
    print("⚠️ Required modules not found")
    api_manager = None
    robust_data_manager = None

class IntelligentAPIController:
    """Control lógico inteligente para optimizar uso de APIs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # API Budget Management (calls per day) - Solo APIs funcionales
        self.api_daily_limits = {
            'alphavantage': 400,   # 500/day - buffer de 100 (FUNCIONAL)
            'polygon': 5000,       # 5/min * 60min * 16h = conservative (FUNCIONAL)
            'yahoo': 40000,        # Conservative limit (PROBLEMÁTICO pero disponible)
            'finnhub': 0,          # DISABLED - 403 Forbidden
            'iex': 0,              # DISABLED - No funciona según usuario
            'fmp': 0               # DISABLED - Por configurar
        }
        
        # Current usage tracking
        self.api_usage_today = defaultdict(int)
        self.api_last_call = defaultdict(float)
        
        # Cache system
        self.data_cache = {}
        self.cache_ttl = {
            'stock_price': 60,     # 1 minute for stock prices
            'market_data': 300,    # 5 minutes for detailed data
            'fundamentals': 3600   # 1 hour for fundamentals
        }
        
        # Request queue and batch processing
        self.request_queue = deque()
        self.batch_size = 5  # Process 5 tickers at a time
        self.concurrent_limit = 3  # Max 3 APIs working simultaneously
        
        # Load usage stats
        self.usage_file = "/Volumes/DiskExFAT 1/system_data/nucleo_agi/alpha_hunter/api_usage_stats.json"
        self.load_usage_stats()
        
        # API health and performance tracking
        self.api_performance = defaultdict(lambda: {'success_rate': 1.0, 'avg_response_time': 1.0})
        
        # Lock for thread safety
        self.lock = threading.Lock()
    
    def get_optimal_data_source(self, data_type: str = 'stock_price') -> str:
        """
        Selecciona la API óptima basada en:
        - Límites diarios restantes
        - Performance histórica
        - Rate limiting
        - Tipo de datos solicitados
        """
        
        # APIs por tipo de dato (ordenadas por preferencia y confiabilidad)
        api_preferences = {
            'stock_price': ['alphavantage', 'polygon', 'yahoo', 'finnhub'],  # Alpha Vantage primero por confiabilidad
            'options': ['polygon', 'yahoo', 'alphavantage'],
            'crypto': ['polygon', 'finnhub'], 
            'fundamentals': ['alphavantage', 'fmp', 'finnhub']
        }
        
        available_apis = api_preferences.get(data_type, ['yahoo', 'alphavantage'])
        
        # Calcular score para cada API
        api_scores = {}
        
        for api in available_apis:
            if api not in self.api_daily_limits:
                continue
            
            daily_limit = self.api_daily_limits[api]
            # Skip disabled APIs (limit = 0)
            if daily_limit <= 0:
                continue
                
            # Factor 1: Calls restantes hoy (peso 40%)
            used_today = self.api_usage_today[api]
            remaining_calls = max(0, daily_limit - used_today)
            remaining_factor = remaining_calls / daily_limit
            
            # Factor 2: Rate limiting (peso 25%)
            last_call = self.api_last_call[api]
            time_since_last = time.time() - last_call
            rate_factor = min(1.0, time_since_last / 1.0)  # 1 segundo mínimo
            
            # Factor 3: Performance histórica (peso 25%)
            performance = self.api_performance[api]
            perf_factor = performance['success_rate'] * max(0.1, 2.0 - performance['avg_response_time'])
            
            # Factor 4: Tipo de dato específico (peso 10%)
            type_factor = 1.0
            if data_type == 'stock_price' and api == 'finnhub':
                type_factor = 1.2  # Finnhub es mejor para precios
            elif data_type == 'options' and api == 'polygon':
                type_factor = 1.2  # Polygon mejor para opciones
            
            # Score total
            total_score = (
                remaining_factor * 0.4 +
                rate_factor * 0.25 +
                perf_factor * 0.25 +
                type_factor * 0.1
            )
            
            api_scores[api] = {
                'score': total_score,
                'remaining': remaining_calls,
                'rate_ok': rate_factor > 0.8,
                'details': f"Remaining: {remaining_calls}, Rate: {rate_factor:.2f}, Perf: {perf_factor:.2f}"
            }
        
        # Seleccionar la mejor API disponible
        if not api_scores:
            self.logger.warning("⚠️ No APIs available for data type: " + data_type)
            return 'yahoo'  # Fallback
        
        best_api = max(api_scores.keys(), key=lambda x: api_scores[x]['score'])
        
        self.logger.info(f"🎯 Selected {best_api} for {data_type} (score: {api_scores[best_api]['score']:.3f})")
        return best_api
    
    def get_cached_data(self, cache_key: str, data_type: str) -> Optional[Dict]:
        """Obtener datos del cache si están disponibles y frescos"""
        if cache_key not in self.data_cache:
            return None
        
        cached_item = self.data_cache[cache_key]
        cache_age = time.time() - cached_item['timestamp']
        ttl = self.cache_ttl.get(data_type, 300)
        
        if cache_age < ttl:
            self.logger.info(f"📦 Cache hit for {cache_key} (age: {cache_age:.1f}s)")
            return cached_item['data']
        else:
            # Remove expired cache
            del self.data_cache[cache_key]
            return None
    
    def cache_data(self, cache_key: str, data: Dict, data_type: str):
        """Cachear datos con timestamp"""
        self.data_cache[cache_key] = {
            'data': data,
            'timestamp': time.time(),
            'type': data_type
        }
        
        # Cleanup old cache (keep last 1000 items)
        if len(self.data_cache) > 1000:
            # Remove oldest 200 items
            oldest_keys = sorted(self.data_cache.keys(), 
                               key=lambda x: self.data_cache[x]['timestamp'])[:200]
            for key in oldest_keys:
                del self.data_cache[key]
    
    def get_smart_stock_data(self, symbol: str, period: str = "5d", 
                           data_type: str = "stock_price") -> Tuple[Optional[Dict], str, Dict]:
        """
        Obtener datos de stock con control inteligente:
        - Cache primero
        - API óptima seleccionada
        - Rate limiting respetado
        - Usage tracking
        """
        
        # Generate cache key
        cache_key = f"{symbol}_{period}_{data_type}"
        
        # Try cache first
        cached_data = self.get_cached_data(cache_key, data_type)
        if cached_data is not None:
            return cached_data, 'cache', {'from_cache': True}
        
        # Select optimal API
        optimal_api = self.get_optimal_data_source(data_type)
        
        # Check if we can make the call (rate limiting + daily limits)
        if not self.can_make_api_call(optimal_api):
            # Try fallback APIs
            fallback_apis = ['yahoo', 'alphavantage', 'finnhub']
            for fallback_api in fallback_apis:
                if fallback_api != optimal_api and self.can_make_api_call(fallback_api):
                    optimal_api = fallback_api
                    self.logger.warning(f"⚠️ Using fallback API: {optimal_api}")
                    break
            else:
                self.logger.error(f"❌ No APIs available for {symbol}")
                return None, 'failed', {'error': 'No APIs available'}
        
        # Make the API call
        start_time = time.time()
        
        try:
            # Use robust data manager with selected API
            if robust_data_manager:
                # Force use of specific API
                original_priority = robust_data_manager.data_source_priority.copy()
                robust_data_manager.data_source_priority[data_type] = [optimal_api]
                
                data, source = robust_data_manager.get_stock_data(symbol, period, data_type)
                
                # Restore original priority
                robust_data_manager.data_source_priority = original_priority
                
                if data is not None:
                    # Convert DataFrame to dict for caching
                    data_dict = {
                        'dataframe': data.to_dict(),
                        'symbol': symbol,
                        'period': period,
                        'source': source
                    }
                    
                    # Record successful call
                    response_time = time.time() - start_time
                    self.record_api_call(optimal_api, True, response_time)
                    
                    # Cache the result
                    self.cache_data(cache_key, data_dict, data_type)
                    
                    return data_dict, source, {
                        'api_used': optimal_api,
                        'response_time': response_time,
                        'cached': True
                    }
                else:
                    # Record failed call
                    self.record_api_call(optimal_api, False, time.time() - start_time)
                    return None, 'failed', {'api_used': optimal_api, 'error': 'No data returned'}
            
        except Exception as e:
            self.record_api_call(optimal_api, False, time.time() - start_time)
            self.logger.error(f"❌ API call failed for {symbol}: {e}")
            return None, 'failed', {'api_used': optimal_api, 'error': str(e)}
        
        return None, 'failed', {'error': 'Robust data manager not available'}
    
    def can_make_api_call(self, api_name: str) -> bool:
        """Verificar si podemos hacer una llamada a la API"""
        
        # Check daily limit
        if api_name in self.api_daily_limits:
            daily_limit = self.api_daily_limits[api_name]
            used_today = self.api_usage_today[api_name]
            
            if used_today >= daily_limit:
                self.logger.warning(f"⚠️ {api_name} daily limit reached: {used_today}/{daily_limit}")
                return False
        
        # Check rate limiting (minimum time between calls) - OPTIMIZED FOR SPEED
        min_interval = {
            'finnhub': 1.0,     # 1 second (60/min)
            'polygon': 8.0,     # 8 seconds (7.5/min) - FASTER
            'alphavantage': 10.0, # 10 seconds (6/min) - FASTER  
            'fmp': 2.0,         # 2 seconds (30/min) - FASTER
            'yahoo': 0.2,       # 0.2 seconds - MUCH FASTER
            'iex': 30.0         # 30 seconds - FASTER
        }
        
        last_call = self.api_last_call[api_name]
        min_wait = min_interval.get(api_name, 1.0)
        time_since_last = time.time() - last_call
        
        if time_since_last < min_wait:
            wait_time = min_wait - time_since_last
            self.logger.info(f"⏰ Rate limiting: waiting {wait_time:.1f}s for {api_name}")
            time.sleep(wait_time)
        
        return True
    
    def record_api_call(self, api_name: str, success: bool, response_time: float):
        """Registrar llamada a API para tracking"""
        with self.lock:
            # Update usage counter
            self.api_usage_today[api_name] += 1
            self.api_last_call[api_name] = time.time()
            
            # Update performance metrics
            perf = self.api_performance[api_name]
            
            # Exponential moving average for success rate
            alpha = 0.1  # Learning rate
            perf['success_rate'] = (1 - alpha) * perf['success_rate'] + alpha * (1.0 if success else 0.0)
            perf['avg_response_time'] = (1 - alpha) * perf['avg_response_time'] + alpha * response_time
            
            # Save usage stats periodically
            if self.api_usage_today[api_name] % 10 == 0:  # Every 10 calls
                self.save_usage_stats()
    
    def batch_process_tickers(self, tickers: List[str], period: str = "5d", 
                            max_concurrent: int = 3) -> Dict[str, Dict]:
        """
        Procesamiento inteligente por lotes:
        - Máximo 3-5 tickers simultáneos
        - Distribución inteligente entre APIs
        - Respeta rate limits
        """
        results = {}
        
        # Split into batches
        batch_size = min(self.batch_size, max_concurrent)
        batches = [tickers[i:i + batch_size] for i in range(0, len(tickers), batch_size)]
        
        self.logger.info(f"🔄 Processing {len(tickers)} tickers in {len(batches)} batches of {batch_size}")
        
        for batch_num, batch in enumerate(batches, 1):
            self.logger.info(f"📊 Batch {batch_num}/{len(batches)}: {batch}")
            
            batch_results = {}
            
            # Process batch with different APIs to distribute load
            for i, ticker_raw in enumerate(batch):
                # Validate ticker before using as dictionary key
                ticker = validate_ticker(ticker_raw)
                if not ticker:
                    log_invalid_ticker(ticker_raw, f"Invalid ticker in batch processing at index {i}")
                    continue
                    
                try:
                    # Distribute across different APIs
                    data_type = 'stock_price'
                    if i % 3 == 1:
                        data_type = 'market_data'
                    
                    data, source, metadata = self.get_smart_stock_data(ticker, period, data_type)
                    
                    if data is not None:
                        batch_results[ticker] = {
                            'data': data,
                            'source': source,
                            'metadata': metadata
                        }
                        self.logger.info(f"✅ {ticker}: {source} ({metadata.get('response_time', 0):.2f}s)")
                    else:
                        self.logger.warning(f"❌ {ticker}: failed")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error processing {ticker}: {e}")
            
            results.update(batch_results)
            
            # Inter-batch delay to respect rate limits
            if batch_num < len(batches):
                delay = 2.0  # 2 seconds between batches
                self.logger.info(f"⏰ Batch delay: {delay}s")
                time.sleep(delay)
        
        return results
    
    def get_usage_report(self) -> Dict:
        """Generar reporte detallado de uso de APIs"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'daily_usage': dict(self.api_usage_today),
            'daily_limits': self.api_daily_limits.copy(),
            'remaining_calls': {},
            'performance': dict(self.api_performance),
            'cache_stats': {
                'total_items': len(self.data_cache),
                'cache_types': defaultdict(int)
            }
        }
        
        # Calculate remaining calls
        for api, limit in self.api_daily_limits.items():
            used = self.api_usage_today[api]
            remaining = max(0, limit - used)
            usage_pct = (used / limit) * 100 if limit > 0 else 0
            
            report['remaining_calls'][api] = {
                'remaining': remaining,
                'used': used,
                'limit': limit,
                'usage_percentage': usage_pct
            }
        
        # Cache statistics
        for cache_key, cache_item in self.data_cache.items():
            cache_type = cache_item.get('type', 'unknown')
            report['cache_stats']['cache_types'][cache_type] += 1
        
        return report
    
    def save_usage_stats(self):
        """Guardar estadísticas de uso"""
        try:
            stats = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'usage_today': dict(self.api_usage_today),
                'performance': dict(self.api_performance),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.usage_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving usage stats: {e}")
    
    def load_usage_stats(self):
        """Cargar estadísticas de uso del día"""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r') as f:
                    stats = json.load(f)
                
                # Only load if it's from today
                stats_date = stats.get('date')
                today = datetime.now().strftime('%Y-%m-%d')
                
                if stats_date == today:
                    self.api_usage_today.update(stats.get('usage_today', {}))
                    self.api_performance.update(stats.get('performance', {}))
                    self.logger.info(f"📈 Loaded usage stats from today: {sum(self.api_usage_today.values())} total calls")
                else:
                    self.logger.info("🆕 Starting fresh usage stats for new day")
            
        except Exception as e:
            self.logger.error(f"Error loading usage stats: {e}")

# Global intelligent controller instance
intelligent_controller = IntelligentAPIController()

def smart_scan_tickers(tickers: List[str], max_tickers: int = 10) -> Dict[str, Dict]:
    """
    Función principal para escaneo inteligente de tickers:
    - Máximo 10 tickers por proceso
    - Control automático de APIs
    - Cache inteligente
    - Rate limiting respetado
    """
    
    # Limit number of tickers
    limited_tickers = tickers[:max_tickers]
    
    if len(tickers) > max_tickers:
        logging.getLogger(__name__).warning(
            f"⚠️ Limiting scan from {len(tickers)} to {max_tickers} tickers to preserve API limits"
        )
    
    # Process with intelligent controller
    return intelligent_controller.batch_process_tickers(limited_tickers)

def get_api_status() -> Dict:
    """Obtener estado actual de todas las APIs"""
    return intelligent_controller.get_usage_report()

if __name__ == "__main__":
    # Test the intelligent controller
    print("🧠 TESTING INTELLIGENT API CONTROLLER")
    print("=" * 50)
    
    # Test with small batch
    test_tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    print(f"\n📊 Testing batch processing with {len(test_tickers)} tickers...")
    results = smart_scan_tickers(test_tickers, max_tickers=3)
    
    print(f"\n✅ Results: {len(results)} successful")
    for ticker, result in results.items():
        source = result.get('source', 'unknown')
        response_time = result.get('metadata', {}).get('response_time', 0)
        print(f"   {ticker}: {source} ({response_time:.2f}s)")
    
    # Show usage report
    print(f"\n📈 API USAGE REPORT:")
    report = get_api_status()
    
    for api, stats in report['remaining_calls'].items():
        if stats['used'] > 0:
            print(f"   {api}: {stats['used']}/{stats['limit']} ({stats['usage_percentage']:.1f}%)")
    
    cache_items = report['cache_stats']['total_items']
    print(f"\n📦 Cache: {cache_items} items stored")