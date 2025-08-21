#!/usr/bin/env python3
"""
Alpha Hunter Signals - Ticker Validator
Created by Michael David Jaramillo

Validates S&P 500 ticker symbols and filters valid trading symbols.
"""

import re
from typing import List, Set, Optional

class TickerValidator:
    """Validates and filters S&P 500 ticker symbols."""
    
    def __init__(self):
        # Core S&P 500 tickers (most common and liquid)
        self.sp500_core_tickers = {
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'WMT', 'LLY',
            'JPM', 'UNH', 'XOM', 'V', 'PG', 'JNJ', 'MA', 'HD', 'NFLX', 'ABBV',
            'PEP', 'KO', 'COST', 'MRK', 'ADBE', 'WFC', 'CVX', 'LIN', 'TMO', 'MCD',
            'ABT', 'CSCO', 'ACN', 'DHR', 'TXN', 'PM', 'VZ', 'INTC', 'CRM', 'AMD',
            'BMY', 'QCOM', 'CMCSA', 'NEE', 'RTX', 'AMGN', 'HON', 'COP', 'T', 'UNP',
            'LOW', 'BA', 'SPGI', 'LMT', 'PFE', 'ISRG', 'BLK', 'CAT', 'DE', 'AXP',
            'BKNG', 'TJX', 'GE', 'MDT', 'ADP', 'GILD', 'TMUS', 'SYK', 'CB', 'MDLZ',
            'CI', 'SO', 'SCHW', 'MO', 'ZTS', 'CVS', 'REGN', 'PLD', 'DUK', 'EOG',
            'ITW', 'BDX', 'MMC', 'TGT', 'USB', 'APH', 'SLB', 'BSX', 'FI', 'EMR',
            'CL', 'NSC', 'AON', 'GD', 'ICE', 'FCX', 'PGR', 'DG', 'CME', 'HUM'
        }
        
        # Extended S&P 500 (additional valid tickers)
        self.sp500_extended = {
            'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'ARKK', 'SQQQ', 'TQQQ', 'SOXL',
            'XLF', 'XLE', 'XLI', 'XLK', 'XLV', 'XLP', 'XLY', 'XLU', 'XLB', 'XLRE',
            'GS', 'MS', 'BAC', 'C', 'WFC', 'COF', 'AIG', 'TRV', 'ALL', 'MET',
            'PRU', 'AFL', 'AMP', 'BRK.B', 'BRK.A', 'HCA', 'UHS', 'DVA', 'ANTM', 'CNC'
        }
        
        # All valid tickers combined
        self.all_valid_tickers = self.sp500_core_tickers | self.sp500_extended
        
        # Invalid patterns to exclude
        self.invalid_patterns = [
            r'^[A-Z]{5,}$',  # Too long (likely not major stock)
            r'.*\.',          # Contains periods (some class shares)
            r'.*-',           # Contains dashes
            r'^[0-9]',        # Starts with number
        ]
    
    def is_valid_ticker(self, ticker: str) -> bool:
        """
        Check if a ticker is valid for options trading.
        
        Args:
            ticker: Stock symbol to validate
            
        Returns:
            bool: True if ticker is valid for trading
        """
        if not ticker or not isinstance(ticker, str):
            return False
        
        ticker = ticker.upper().strip()
        
        # Check if in known valid set
        if ticker in self.all_valid_tickers:
            return True
        
        # Check against invalid patterns
        for pattern in self.invalid_patterns:
            if re.match(pattern, ticker):
                return False
        
        # Basic validation: 1-5 characters, all letters
        if not re.match(r'^[A-Z]{1,5}$', ticker):
            return False
        
        return True
    
    def filter_valid_tickers(self, tickers: List[str]) -> List[str]:
        """
        Filter list of tickers to only include valid ones.
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            List of valid ticker symbols
        """
        valid_tickers = []
        
        for ticker in tickers:
            if self.is_valid_ticker(ticker):
                valid_tickers.append(ticker.upper().strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_valid = []
        for ticker in valid_tickers:
            if ticker not in seen:
                seen.add(ticker)
                unique_valid.append(ticker)
        
        return unique_valid
    
    def get_high_quality_tickers(self, limit: Optional[int] = None) -> List[str]:
        """
        Get list of high-quality S&P 500 tickers for analysis.
        
        Args:
            limit: Maximum number of tickers to return
            
        Returns:
            List of high-quality ticker symbols
        """
        # Start with core tickers (most liquid and reliable)
        quality_tickers = sorted(list(self.sp500_core_tickers))
        
        if limit:
            return quality_tickers[:limit]
        
        return quality_tickers
    
    def validate_ticker_format(self, ticker: str) -> dict:
        """
        Detailed validation of ticker format with reasons.
        
        Args:
            ticker: Ticker symbol to validate
            
        Returns:
            Dict with validation results and reasons
        """
        result = {
            'ticker': ticker,
            'valid': False,
            'reasons': [],
            'suggestions': []
        }
        
        if not ticker:
            result['reasons'].append('Empty ticker')
            return result
        
        ticker = ticker.upper().strip()
        result['ticker'] = ticker
        
        # Length check
        if len(ticker) > 5:
            result['reasons'].append(f'Too long ({len(ticker)} chars, max 5)')
        elif len(ticker) < 1:
            result['reasons'].append('Too short')
        
        # Character validation
        if not ticker.isalpha():
            result['reasons'].append('Contains non-alphabetic characters')
        
        # Known ticker check
        if ticker in self.all_valid_tickers:
            result['valid'] = True
            result['reasons'].append('Known valid S&P 500 ticker')
        
        # Pattern checks
        for pattern in self.invalid_patterns:
            if re.match(pattern, ticker):
                result['reasons'].append(f'Matches invalid pattern: {pattern}')
        
        # If no major issues found and basic format is correct
        if (len(ticker) <= 5 and len(ticker) >= 1 and 
            ticker.isalpha() and not any(re.match(p, ticker) for p in self.invalid_patterns)):
            if not result['valid']:  # Not in known list but format is OK
                result['valid'] = True
                result['reasons'].append('Valid format, unknown ticker')
        
        return result

# Convenience functions for backward compatibility
def is_valid_ticker(ticker: str) -> bool:
    """Check if ticker is valid for trading."""
    validator = TickerValidator()
    return validator.is_valid_ticker(ticker)

def filter_valid_tickers(tickers: List[str]) -> List[str]:
    """Filter list to only valid tickers."""
    validator = TickerValidator()
    return validator.filter_valid_tickers(tickers)

def get_high_quality_tickers(limit: Optional[int] = None) -> List[str]:
    """Get high-quality S&P 500 tickers."""
    validator = TickerValidator()
    return validator.get_high_quality_tickers(limit)

# For testing
if __name__ == "__main__":
    validator = TickerValidator()
    
    # Test cases
    test_tickers = ['AAPL', 'INVALID123', 'GOOGL', 'TOOLONG', 'SPY', '']
    
    print("🔍 Ticker Validation Test:")
    for ticker in test_tickers:
        result = validator.validate_ticker_format(ticker)
        status = "✅" if result['valid'] else "❌"
        print(f"{status} {ticker}: {', '.join(result['reasons'])}")
    
    print(f"\n📊 High Quality Tickers (top 10): {validator.get_high_quality_tickers(10)}")