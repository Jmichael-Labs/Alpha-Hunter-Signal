#!/usr/bin/env python3
"""
Alpha Hunter Signals - Nexus Utilities
Created by Michael David Jaramillo

Utility functions for logging and system communication.
"""

import sys
from datetime import datetime
from typing import Optional

def nexus_speak(level: str, message: str, prefix: Optional[str] = None) -> None:
    """
    Professional logging function with level-based formatting.
    
    Args:
        level: Log level (info, success, warning, error, debug)
        message: Message to log
        prefix: Optional prefix for the message
    """
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # Level formatting
    level_formats = {
        'info': f"ℹ️  [INFO]",
        'success': f"✅ [SUCCESS]", 
        'warning': f"⚠️  [WARNING]",
        'error': f"❌ [ERROR]",
        'debug': f"🔍 [DEBUG]",
        'system': f"🤖 [SYSTEM]"
    }
    
    level_indicator = level_formats.get(level.lower(), f"📝 [{level.upper()}]")
    
    # Build message
    if prefix:
        formatted_message = f"{level_indicator} {prefix}: {message}"
    else:
        formatted_message = f"{level_indicator} {message}"
    
    # Add timestamp if not error level
    if level.lower() != 'error':
        formatted_message = f"[{timestamp}] {formatted_message}"
    
    # Print to appropriate stream
    if level.lower() in ['error', 'warning']:
        print(formatted_message, file=sys.stderr)
    else:
        print(formatted_message)

def log_info(message: str, prefix: Optional[str] = None) -> None:
    """Log info message."""
    nexus_speak('info', message, prefix)

def log_success(message: str, prefix: Optional[str] = None) -> None:
    """Log success message."""
    nexus_speak('success', message, prefix)

def log_warning(message: str, prefix: Optional[str] = None) -> None:
    """Log warning message.""" 
    nexus_speak('warning', message, prefix)

def log_error(message: str, prefix: Optional[str] = None) -> None:
    """Log error message."""
    nexus_speak('error', message, prefix)

def log_debug(message: str, prefix: Optional[str] = None) -> None:
    """Log debug message."""
    nexus_speak('debug', message, prefix)

# For testing
if __name__ == "__main__":
    print("🧪 Testing Nexus Utils:")
    
    nexus_speak('info', 'System initializing...')
    nexus_speak('success', 'Connection established')
    nexus_speak('warning', 'Rate limit approaching')
    nexus_speak('error', 'API call failed')
    nexus_speak('debug', 'Variable value: 42')