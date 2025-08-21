#!/usr/bin/env python3
"""
Alpha Hunter Signals - Safe Send Utility
Created by Michael David Jaramillo

Robust Telegram sending with error tolerance and retry logic.
"""

import time
import requests
from typing import Dict, Optional, Any
import logging

# Statistics tracking
_send_stats = {
    'total_attempts': 0,
    'successful_sends': 0,
    'failed_sends': 0,
    'brokenpipe_errors': 0,
    'timeout_errors': 0,
    'other_errors': 0
}

def safe_telegram_send(url: str, payload: Dict[str, Any], 
                      timeout: int = 10, max_retries: int = 3) -> bool:
    """
    Send Telegram message with robust error handling and retries.
    
    Args:
        url: Telegram API URL
        payload: Message payload
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        
    Returns:
        bool: True if message sent successfully
    """
    global _send_stats
    
    for attempt in range(max_retries):
        _send_stats['total_attempts'] += 1
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                timeout=timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Alpha-Hunter-Signals/1.0'
                }
            )
            
            if response.status_code == 200:
                _send_stats['successful_sends'] += 1
                return True
            else:
                logging.warning(f"Telegram API returned status {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            _send_stats['timeout_errors'] += 1
            logging.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
            
        except BrokenPipeError:
            _send_stats['brokenpipe_errors'] += 1
            logging.warning(f"BrokenPipeError on attempt {attempt + 1}/{max_retries}")
            
        except Exception as e:
            _send_stats['other_errors'] += 1
            logging.warning(f"Error on attempt {attempt + 1}/{max_retries}: {e}")
        
        # Wait before retry (exponential backoff)
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)
    
    _send_stats['failed_sends'] += 1
    return False

def safe_send(url: str, payload: Dict[str, Any], timeout: int = 10) -> bool:
    """
    Simplified safe send function - alias for safe_telegram_send.
    
    Args:
        url: API URL
        payload: Request payload
        timeout: Request timeout
        
    Returns:
        bool: True if successful
    """
    return safe_telegram_send(url, payload, timeout)

def get_safe_send_stats() -> Dict[str, Any]:
    """
    Get statistics about send operations.
    
    Returns:
        Dict with send statistics
    """
    global _send_stats
    
    total = _send_stats['total_attempts']
    if total > 0:
        success_rate = (_send_stats['successful_sends'] / total) * 100
    else:
        success_rate = 0.0
    
    return {
        'total_attempts': total,
        'successful_sends': _send_stats['successful_sends'],
        'failed_sends': _send_stats['failed_sends'],
        'success_rate': f"{success_rate:.1f}%",
        'error_breakdown': {
            'brokenpipe': _send_stats['brokenpipe_errors'],
            'timeout': _send_stats['timeout_errors'],
            'other': _send_stats['other_errors']
        }
    }

def reset_safe_send_stats() -> None:
    """Reset send statistics."""
    global _send_stats
    _send_stats = {
        'total_attempts': 0,
        'successful_sends': 0,
        'failed_sends': 0,
        'brokenpipe_errors': 0,
        'timeout_errors': 0,
        'other_errors': 0
    }

# For testing
if __name__ == "__main__":
    print("🧪 Testing Safe Send Utility:")
    
    # Test with invalid URL (should fail gracefully)
    test_url = "https://httpbin.org/status/500"
    test_payload = {"test": "message"}
    
    result = safe_telegram_send(test_url, test_payload)
    print(f"Test result: {result}")
    
    stats = get_safe_send_stats()
    print(f"Stats: {stats}")
    
    print("✅ Safe Send Utility test completed")