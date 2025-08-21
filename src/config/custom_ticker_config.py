#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - CONFIGURACIÓN PERSONALIZADA DE TICKERS
Lista personalizada de acciones para análisis enfocado y especializado
"""

# Lista personalizada de tickers para análisis enfocado - CONFIGURACIÓN DEFINITIVA
# 🎯 PRIORIDAD MÁXIMA: Tickers con mejores oportunidades y estrategias fáciles de seguir
CUSTOM_FOCUS_TICKERS = {
    # ETFs Principales - Máxima liquidez y opciones
    'SPY': {
        'name': 'SPDR S&P 500 ETF Trust',
        'exchange': 'NYSE Arca',
        'type': 'ETF',
        'sector': 'Market Index',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'iron_condor', 'covered_call', 'straddle'],
        'priority': 10  # MÁXIMA PRIORIDAD - Índice principal
    },
    'QQQ': {
        'name': 'Invesco QQQ Trust (NASDAQ-100 ETF)',
        'exchange': 'NASDAQ',
        'type': 'ETF',
        'sector': 'Technology',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'iron_condor', 'covered_call', 'straddle'],
        'priority': 10  # MÁXIMA PRIORIDAD - Tech Index
    },
    'DIA': {
        'name': 'SPDR Dow Jones Industrial Average ETF Trust',
        'exchange': 'NYSE Arca',
        'type': 'ETF',
        'sector': 'Market Index',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'iron_condor', 'covered_call'],
        'priority': 10  # MÁXIMA PRIORIDAD (upgraded from 9) - Dow Index
    },
    
    # Tech Giants - MÁXIMA PRIORIDAD - Alta volatilidad y opciones líquidas
    'AAPL': {
        'name': 'Apple Inc.',
        'exchange': 'NASDAQ',
        'type': 'Stock',
        'sector': 'Technology',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'iron_condor', 'covered_call', 'straddle'],
        'priority': 10  # MÁXIMA PRIORIDAD - Tech líder
    },
    'TSLA': {
        'name': 'Tesla, Inc.',
        'exchange': 'NASDAQ',
        'type': 'Stock',
        'sector': 'Automotive/Energy',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'straddle', 'iron_condor'],
        'priority': 10  # MÁXIMA PRIORIDAD (upgraded from 9) - Alta volatilidad
    },
    'NVDA': {
        'name': 'NVIDIA Corporation',
        'exchange': 'NASDAQ',
        'type': 'Stock',
        'sector': 'Technology/AI',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'iron_condor', 'straddle'],
        'priority': 10  # MÁXIMA PRIORIDAD - AI líder
    },
    'AMZN': {
        'name': 'Amazon.com, Inc.',
        'exchange': 'NASDAQ',
        'type': 'Stock',
        'sector': 'Technology/E-commerce',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'iron_condor', 'covered_call'],
        'priority': 10  # MÁXIMA PRIORIDAD (upgraded from 9) - E-commerce líder
    },
    'META': {
        'name': 'Meta Platforms, Inc.',
        'exchange': 'NASDAQ',
        'type': 'Stock',
        'sector': 'Technology/Social Media',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'iron_condor', 'straddle'],
        'priority': 10  # MÁXIMA PRIORIDAD (upgraded from 9) - Social Media líder
    },
    'NFLX': {
        'name': 'Netflix, Inc.',
        'exchange': 'NASDAQ',
        'type': 'Stock',
        'sector': 'Technology/Streaming',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'iron_condor', 'straddle'],
        'priority': 10  # MÁXIMA PRIORIDAD (upgraded from 8) - Streaming líder
    },
    
    # Traditional Sectors - GUARANTEED HIGH PRIORITY WINNERS
    'BAC': {
        'name': 'Bank of America Corporation',
        'exchange': 'NYSE',
        'type': 'Stock',
        'sector': 'Financial',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'covered_call', 'iron_condor'],
        'priority': 10  # INCREASED TO MAXIMUM (was 7) - V3 99.9/100 WINNER
    },
    'JPM': {
        'name': 'JPMorgan Chase & Co.',
        'exchange': 'NYSE',
        'type': 'Stock',
        'sector': 'Financial',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'covered_call', 'iron_condor'],
        'priority': 10  # MAXIMUM PRIORITY - V3 78.8/100 WINNER
    },
    'WFC': {
        'name': 'Wells Fargo & Company',
        'exchange': 'NYSE',
        'type': 'Stock',
        'sector': 'Financial',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'covered_call', 'iron_condor'],
        'priority': 10  # MAXIMUM PRIORITY - V3 88.1/100 WINNER
    },
    'XOM': {
        'name': 'Exxon Mobil Corporation',
        'exchange': 'NYSE',
        'type': 'Stock',
        'sector': 'Energy',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'covered_call', 'iron_condor'],
        'priority': 10  # MÁXIMA PRIORIDAD (upgraded from 7) - Energy líder
    },
    
    # Commodities ETFs - MÁXIMA PRIORIDAD
    'GLD': {
        'name': 'SPDR Gold Shares (ETF)',
        'exchange': 'NYSE Arca',
        'type': 'ETF',
        'sector': 'Commodities/Gold',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'iron_condor', 'straddle'],
        'priority': 10  # MÁXIMA PRIORIDAD (upgraded from 8) - Gold hedge
    },
    'SLV': {
        'name': 'iShares Silver Trust (ETF)',
        'exchange': 'NYSE Arca',
        'type': 'ETF',
        'sector': 'Commodities/Silver',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'iron_condor'],
        'priority': 10  # MÁXIMA PRIORIDAD (upgraded from 7) - Silver hedge
    },
    'USO': {
        'name': 'United States Oil Fund LP (ETF)',
        'exchange': 'NYSE Arca',
        'type': 'ETF',
        'sector': 'Commodities/Oil',
        'options_liquid': True,
        'strategies': ['bull_put', 'bear_call', 'straddle', 'iron_condor'],
        'priority': 10  # MÁXIMA PRIORIDAD (upgraded from 8) - Oil volatility
    },
    
    # Índices y Volatilidad - PRIORIDAD MÁXIMA
    '^IXIC': {
        'name': 'NASDAQ Composite Index',
        'exchange': 'NASDAQ',
        'type': 'Index',
        'sector': 'Market Index',
        'options_liquid': False,  # Index tracking only
        'strategies': ['market_analysis', 'trend_following'],
        'priority': 10  # MÁXIMA PRIORIDAD - NASDAQ tracking
    },
    'VIX': {
        'name': 'CBOE Volatility Index',
        'exchange': 'CBOE',
        'type': 'Index',
        'sector': 'Volatility',
        'options_liquid': True,
        'strategies': ['volatility_play', 'market_hedge', 'contrarian'],
        'priority': 10  # MÁXIMA PRIORIDAD - Volatility trading
    },
    
    # Futuros - PRIORIDAD MÁXIMA
    'GC=F': {
        'name': 'Gold Futures',
        'exchange': 'COMEX',
        'type': 'Future',
        'sector': 'Commodities/Gold',
        'options_liquid': True,
        'strategies': ['futures_trading', 'commodity_hedge', 'inflation_play'],
        'priority': 10  # MÁXIMA PRIORIDAD - Gold futures
    },
    'CL=F': {
        'name': 'Crude Oil Futures',
        'exchange': 'NYMEX',
        'type': 'Future',
        'sector': 'Commodities/Oil',
        'options_liquid': True,
        'strategies': ['futures_trading', 'energy_hedge', 'volatility_play'],
        'priority': 10  # MÁXIMA PRIORIDAD - Oil futures
    },
    'CUX': {
        'name': 'Copper Futures (Extended)',
        'exchange': 'COMEX',
        'type': 'Future',
        'sector': 'Commodities/Metal',
        'options_liquid': True,
        'strategies': ['futures_trading', 'industrial_hedge', 'economic_indicator'],
        'priority': 10  # MÁXIMA PRIORIDAD - Industrial metals
    }
    
    # NOTA: CONFIGURACIÓN DEFINITIVA PERSONALIZADA
    # ✅ Incluye TODOS los tickers de máxima oportunidad y estrategias fáciles de seguir
    # ✅ ETFs, Stocks, Índices y Futuros con mejores opciones de trading
}

# Funciones de utilidad
def get_priority_tickers(min_priority=9):
    """Obtiene tickers por prioridad mínima"""
    return {ticker: data for ticker, data in CUSTOM_FOCUS_TICKERS.items() 
            if data['priority'] >= min_priority}

def get_tickers_by_type(ticker_type):
    """Obtiene tickers por tipo (ETF, Stock)"""
    return {ticker: data for ticker, data in CUSTOM_FOCUS_TICKERS.items() 
            if data['type'] == ticker_type}

def get_tickers_by_sector(sector):
    """Obtiene tickers por sector"""
    return {ticker: data for ticker, data in CUSTOM_FOCUS_TICKERS.items() 
            if sector.lower() in data['sector'].lower()}

def get_strategies_for_ticker(ticker):
    """Obtiene estrategias específicas para un ticker"""
    return CUSTOM_FOCUS_TICKERS.get(ticker, {}).get('strategies', [])

def is_high_priority(ticker):
    """Verifica si un ticker es de alta prioridad"""
    return CUSTOM_FOCUS_TICKERS.get(ticker, {}).get('priority', 0) >= 9

# Lista simple para compatibilidad
FOCUS_TICKER_LIST = list(CUSTOM_FOCUS_TICKERS.keys())

# Configuración de análisis especializado
ANALYSIS_CONFIG = {
    'max_concurrent_analysis': 25,  # AUMENTADO A 25 (was 5) - Procesar todos los prioritarios
    'priority_first': True,        # Analizar primero los de alta prioridad
    'sector_diversification': True, # Diversificar por sectores
    'etf_preference': True,        # Preferir ETFs por liquidez
    'min_quality_threshold': 50.0  # Threshold mínimo de calidad (LOWERED from 70.0)
}

if __name__ == "__main__":
    print("🎯 ALPHA HUNTER V2 - CUSTOM TICKER CONFIGURATION")
    print("=" * 60)
    
    print(f"📊 Total Tickers: {len(FOCUS_TICKER_LIST)}")
    
    high_priority = get_priority_tickers(9)
    print(f"⭐ High Priority (≥9): {len(high_priority)} tickers")
    for ticker in high_priority:
        print(f"   └─ {ticker}: {high_priority[ticker]['name']}")
    
    etfs = get_tickers_by_type('ETF')
    print(f"\n📈 ETFs: {len(etfs)} tickers")
    for ticker in etfs:
        print(f"   └─ {ticker}: {etfs[ticker]['name']}")
    
    stocks = get_tickers_by_type('Stock')
    print(f"\n🏢 Stocks: {len(stocks)} tickers")
    
    print(f"\n🎯 Focus Configuration:")
    print(f"├─ Max Concurrent: {ANALYSIS_CONFIG['max_concurrent_analysis']}")
    print(f"├─ Priority First: {ANALYSIS_CONFIG['priority_first']}")  
    print(f"└─ Min Quality: {ANALYSIS_CONFIG['min_quality_threshold']}%")