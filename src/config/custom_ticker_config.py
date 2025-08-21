#!/usr/bin/env python3
"""
Alpha Hunter Signals - Custom Ticker Configuration
Created by Michael David Jaramillo

Configuration for S&P 500 ticker selection and filtering.
"""

from typing import List, Dict, Set
from datetime import datetime

# High-quality S&P 500 tickers with strong options liquidity
HIGH_QUALITY_SP500_TICKERS = [
    # Technology
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'CRM', 'ADBE',
    'INTC', 'AMD', 'CSCO', 'TXN', 'QCOM', 'NFLX', 'PYPL', 'INTU', 'AMAT', 'MU',
    
    # Healthcare & Pharmaceuticals  
    'UNH', 'JNJ', 'PFE', 'ABBV', 'TMO', 'ABT', 'DHR', 'BMY', 'LLY', 'MDT',
    'ISRG', 'SYK', 'BSX', 'EW', 'ZTS', 'REGN', 'GILD', 'BIIB', 'AMGN', 'CVS',
    
    # Financial Services
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SPGI', 'AXP', 'SCHW',
    'CB', 'MMC', 'TRV', 'AIG', 'AON', 'COF', 'USB', 'PNC', 'TFC', 'AFL',
    
    # Consumer & Retail
    'WMT', 'HD', 'PG', 'KO', 'PEP', 'MCD', 'COST', 'TJX', 'NKE', 'SBUX',
    'TGT', 'LOW', 'DG', 'MDLZ', 'CL', 'KMB', 'GIS', 'K', 'CPB', 'MKC',
    
    # Industrial & Manufacturing
    'BA', 'CAT', 'HON', 'GE', 'RTX', 'LMT', 'UNP', 'UPS', 'FDX', 'DE',
    'MMM', 'ITW', 'EMR', 'ETN', 'PH', 'ROK', 'DOV', 'IEX', 'XYL', 'FTV',
    
    # Energy & Utilities
    'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'VLO', 'PSX', 'KMI', 'OKE',
    'NEE', 'DUK', 'SO', 'D', 'EXC', 'SRE', 'AEP', 'XEL', 'PPL', 'ES',
    
    # ETFs (High Liquidity)
    'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'ARKK', 'XLF', 'XLE', 'XLI',
]

# Extended S&P 500 (additional valid tickers)
EXTENDED_SP500_TICKERS = [
    'PM', 'MO', 'LIN', 'LRCX', 'KLAC', 'MRVL', 'ADI', 'NXPI', 'MCHP', 'FTNT',
    'PANW', 'CRWD', 'ZM', 'DOCU', 'WORK', 'SNOW', 'DDOG', 'NET', 'OKTA', 'ZS',
    'MRNA', 'BNTX', 'JNJ', 'PFE', 'ABBV', 'GILD', 'REGN', 'VRTX', 'ILMN', 'TECH',
    'V', 'MA', 'PYPL', 'SQ', 'COIN', 'SOFI', 'AFRM', 'UPST', 'LC', 'ALLY',
]

# Sectors configuration for balanced analysis
SECTOR_CONFIGURATION = {
    'technology': {
        'weight': 0.25,  # 25% of analysis
        'tickers': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'CRM', 'ADBE'],
        'min_tickers': 3,
        'max_tickers': 8
    },
    'healthcare': {
        'weight': 0.20,  # 20% of analysis
        'tickers': ['UNH', 'JNJ', 'PFE', 'ABBV', 'TMO', 'ABT', 'LLY', 'MDT'],
        'min_tickers': 2,
        'max_tickers': 6
    },
    'financial': {
        'weight': 0.20,  # 20% of analysis  
        'tickers': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'SPGI', 'AXP'],
        'min_tickers': 2,
        'max_tickers': 6
    },
    'consumer': {
        'weight': 0.15,  # 15% of analysis
        'tickers': ['WMT', 'HD', 'PG', 'KO', 'PEP', 'MCD', 'COST', 'TJX'],
        'min_tickers': 2,
        'max_tickers': 5
    },
    'industrial': {
        'weight': 0.10,  # 10% of analysis
        'tickers': ['BA', 'CAT', 'HON', 'GE', 'RTX', 'LMT', 'UNP', 'DE'],
        'min_tickers': 1,
        'max_tickers': 4
    },
    'energy': {
        'weight': 0.10,  # 10% of analysis
        'tickers': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'NEE', 'DUK'],
        'min_tickers': 1,
        'max_tickers': 3
    }
}

# Market cap tiers for risk management
MARKET_CAP_TIERS = {
    'mega_cap': {  # >$200B
        'tickers': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA'],
        'risk_multiplier': 0.8,  # Lower risk
        'max_allocation': 0.4
    },
    'large_cap': {  # $10B-$200B
        'tickers': ['JPM', 'UNH', 'HD', 'PG', 'WMT', 'JNJ', 'V', 'MA'],
        'risk_multiplier': 1.0,  # Standard risk
        'max_allocation': 0.5
    },
    'mid_cap': {  # $2B-$10B
        'tickers': ['TGT', 'DG', 'SBUX', 'TJX', 'LOW'],
        'risk_multiplier': 1.2,  # Higher risk
        'max_allocation': 0.3
    }
}

# Options liquidity requirements
OPTIONS_LIQUIDITY_FILTER = {
    'min_daily_volume': 1000,      # Minimum options volume
    'min_open_interest': 500,      # Minimum open interest
    'max_bid_ask_spread': 0.10,    # Maximum 10 cent spread
    'required_strikes': 5,         # Minimum strike prices available
    'days_to_expiry_range': (7, 21)  # 1-3 weeks expiry
}

# Risk management parameters per ticker type
RISK_PARAMETERS = {
    'conservative': {
        'max_position_size': 0.02,    # 2% max per position
        'stop_loss': 0.025,           # 2.5% stop loss
        'take_profit': 0.03,          # 3% take profit
        'max_trades_per_day': 3
    },
    'moderate': {
        'max_position_size': 0.03,    # 3% max per position
        'stop_loss': 0.03,            # 3% stop loss  
        'take_profit': 0.05,          # 5% take profit
        'max_trades_per_day': 5
    },
    'aggressive': {
        'max_position_size': 0.05,    # 5% max per position
        'stop_loss': 0.05,            # 5% stop loss
        'take_profit': 0.08,          # 8% take profit
        'max_trades_per_day': 8
    }
}

def get_high_quality_tickers(limit: int = None) -> List[str]:
    """
    Get list of high-quality tickers for analysis.
    
    Args:
        limit: Maximum number of tickers to return
        
    Returns:
        List of ticker symbols
    """
    tickers = HIGH_QUALITY_SP500_TICKERS.copy()
    
    if limit:
        return tickers[:limit]
    
    return tickers

def get_sector_balanced_tickers(max_tickers: int = 50) -> List[str]:
    """
    Get sector-balanced ticker selection.
    
    Args:
        max_tickers: Maximum total tickers to return
        
    Returns:
        List of balanced ticker symbols
    """
    balanced_tickers = []
    
    for sector, config in SECTOR_CONFIGURATION.items():
        sector_allocation = int(max_tickers * config['weight'])
        sector_allocation = max(config['min_tickers'], 
                              min(config['max_tickers'], sector_allocation))
        
        sector_tickers = config['tickers'][:sector_allocation]
        balanced_tickers.extend(sector_tickers)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tickers = []
    for ticker in balanced_tickers:
        if ticker not in seen:
            seen.add(ticker)
            unique_tickers.append(ticker)
    
    return unique_tickers[:max_tickers]

def get_risk_parameters(ticker: str) -> Dict:
    """
    Get risk parameters for specific ticker.
    
    Args:
        ticker: Stock symbol
        
    Returns:
        Dict with risk parameters
    """
    # Determine ticker tier
    for tier, config in MARKET_CAP_TIERS.items():
        if ticker in config['tickers']:
            if tier == 'mega_cap':
                return RISK_PARAMETERS['conservative']
            elif tier == 'large_cap':
                return RISK_PARAMETERS['moderate']
            else:
                return RISK_PARAMETERS['aggressive']
    
    # Default to moderate for unknown tickers
    return RISK_PARAMETERS['moderate']

def is_high_liquidity_ticker(ticker: str) -> bool:
    """
    Check if ticker has high options liquidity.
    
    Args:
        ticker: Stock symbol
        
    Returns:
        bool: True if high liquidity
    """
    return ticker in HIGH_QUALITY_SP500_TICKERS

def get_ticker_sector(ticker: str) -> str:
    """
    Get sector for ticker.
    
    Args:
        ticker: Stock symbol
        
    Returns:
        Sector name or 'unknown'
    """
    for sector, config in SECTOR_CONFIGURATION.items():
        if ticker in config['tickers']:
            return sector
    
    return 'unknown'

# For testing
if __name__ == "__main__":
    print("🧪 Testing Custom Ticker Config:")
    
    print(f"High quality tickers (10): {get_high_quality_tickers(10)}")
    print(f"Sector balanced (20): {get_sector_balanced_tickers(20)}")
    print(f"AAPL risk params: {get_risk_parameters('AAPL')}")
    print(f"AAPL sector: {get_ticker_sector('AAPL')}")
    print(f"SPY high liquidity: {is_high_liquidity_ticker('SPY')}")
    
    print("✅ Custom Ticker Config test completed")