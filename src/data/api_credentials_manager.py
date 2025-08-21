#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - API CREDENTIALS MANAGER
Gestión segura de credenciales y APIs múltiples
Created by AGI Nuclei Coordination System
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class APICredentialsManager:
    """Gestor centralizado de credenciales y APIs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.credentials_file = "/Volumes/DiskExFAT 1/system_data/nucleo_agi/alpha_hunter/api_credentials.json"
        self.usage_tracking_file = "/Volumes/DiskExFAT 1/system_data/nucleo_agi/alpha_hunter/api_usage.json"
        
        # Load credentials
        self.credentials = self.load_credentials()
        self.usage_stats = self.load_usage_stats()
        
        # API Rate Limits (calls per minute/hour/day)
        self.rate_limits = {
            "yahoo": {"per_minute": 60, "per_hour": 2000, "per_day": 48000},
            "polygon": {"per_minute": 5, "per_hour": 300, "per_day": 7200},  # Free tier
            "alphavantage": {"per_minute": 5, "per_hour": 300, "per_day": 500},  # Free tier
            "iex": {"per_minute": 100, "per_hour": 6000, "per_day": 144000},  # Free tier
            "fmp": {"per_minute": 10, "per_hour": 300, "per_day": 250},  # Free tier
            "quandl": {"per_minute": 10, "per_hour": 300, "per_day": 300},  # Free tier
            "finnhub": {"per_minute": 30, "per_hour": 1800, "per_day": 43200},  # Free tier
            "worldtradingdata": {"per_minute": 5, "per_hour": 100, "per_day": 250}
        }
    
    def load_credentials(self) -> Dict:
        """Load API credentials from secure file"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r') as f:
                    return json.load(f)
            else:
                return self.create_default_credentials()
        except Exception as e:
            self.logger.error(f"Error loading credentials: {e}")
            return self.create_default_credentials()
    
    def create_default_credentials(self) -> Dict:
        """Create default credentials using user's existing keys from ~/.gemini_keys.env"""
        default_creds = {
            # Financial Data APIs - usando tus claves reales
            "yahoo": {"api_key": "", "status": "active"},
            "polygon": {"api_key": os.getenv('POLYGON_API_KEY', ''), "status": "active"},
            "alphavantage": {"api_key": os.getenv('ALPHA_VANTAGE_KEY', ''), "status": "active"},
            "iex": {"api_key": os.getenv('IEX_API_KEY', ''), "status": "inactive"},  # IEX no funciona según usuario
            "fmp": {"api_key": os.getenv('FMP_API_KEY', ''), "status": "inactive"},
            "quandl": {"api_key": os.getenv('QUANDL_API_KEY', ''), "status": "inactive"},
            "finnhub": {"api_key": os.getenv('FINNHUB_API_KEY', ''), "status": "active"},
            "worldtradingdata": {"api_key": os.getenv('WTD_API_KEY', ''), "status": "inactive"},
            
            
            # Communication APIs - usando tus claves reales
            "telegram": {
                "bot_token": os.getenv('TELEGRAM_BOT_TOKEN', ''),
                "chat_id": os.getenv('TELEGRAM_CHAT_ID', ''),
                "status": "active"
            }
        }
        
        # Save default credentials
        self.save_credentials(default_creds)
        return default_creds
    
    def save_credentials(self, credentials: Dict):
        """Save credentials to secure file"""
        try:
            os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            # Set restrictive permissions
            os.chmod(self.credentials_file, 0o600)
        except Exception as e:
            self.logger.error(f"Error saving credentials: {e}")
    
    def load_usage_stats(self) -> Dict:
        """Load API usage statistics"""
        try:
            if os.path.exists(self.usage_tracking_file):
                with open(self.usage_tracking_file, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error loading usage stats: {e}")
            return {}
    
    def save_usage_stats(self):
        """Save API usage statistics"""
        try:
            with open(self.usage_tracking_file, 'w') as f:
                json.dump(self.usage_stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving usage stats: {e}")
    
    def get_credentials(self, api_name: str) -> Optional[Dict]:
        """Get credentials for specific API"""
        return self.credentials.get(api_name)
    
    def update_credentials(self, api_name: str, new_creds: Dict):
        """Update credentials for specific API"""
        if api_name in self.credentials:
            self.credentials[api_name].update(new_creds)
            self.save_credentials(self.credentials)
            self.logger.info(f"✅ Updated credentials for {api_name}")
        else:
            self.logger.error(f"❌ API {api_name} not found")
    
    def check_rate_limit(self, api_name: str) -> bool:
        """Check if API is within rate limits"""
        if api_name not in self.rate_limits:
            return True
        
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        current_hour = now.strftime('%Y-%m-%d-%H')
        current_minute = now.strftime('%Y-%m-%d-%H-%M')
        
        # Initialize usage tracking for API
        if api_name not in self.usage_stats:
            self.usage_stats[api_name] = {}
        
        usage = self.usage_stats[api_name]
        limits = self.rate_limits[api_name]
        
        # Check per minute limit
        minute_calls = usage.get(current_minute, 0)
        if minute_calls >= limits['per_minute']:
            self.logger.warning(f"⚠️ {api_name} rate limit exceeded: {minute_calls}/{limits['per_minute']} per minute")
            return False
        
        # Check per hour limit
        hour_calls = usage.get(current_hour, 0)
        if hour_calls >= limits['per_hour']:
            self.logger.warning(f"⚠️ {api_name} rate limit exceeded: {hour_calls}/{limits['per_hour']} per hour")
            return False
        
        # Check per day limit
        day_calls = usage.get(today, 0)
        if day_calls >= limits['per_day']:
            self.logger.warning(f"⚠️ {api_name} rate limit exceeded: {day_calls}/{limits['per_day']} per day")
            return False
        
        return True
    
    def record_api_call(self, api_name: str):
        """Record an API call for rate limiting"""
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        current_hour = now.strftime('%Y-%m-%d-%H')
        current_minute = now.strftime('%Y-%m-%d-%H-%M')
        
        if api_name not in self.usage_stats:
            self.usage_stats[api_name] = {}
        
        usage = self.usage_stats[api_name]
        
        # Increment counters
        usage[current_minute] = usage.get(current_minute, 0) + 1
        usage[current_hour] = usage.get(current_hour, 0) + 1
        usage[today] = usage.get(today, 0) + 1
        
        # Clean old entries (keep only last 7 days)
        cutoff_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        keys_to_remove = [k for k in usage.keys() if k < cutoff_date and len(k) == 10]
        for key in keys_to_remove:
            del usage[key]
        
        self.save_usage_stats()
    
    def get_next_available_api(self, api_list: List[str]) -> Optional[str]:
        """Get next available API from list that's within rate limits"""
        for api_name in api_list:
            if self.check_rate_limit(api_name):
                creds = self.get_credentials(api_name)
                if creds and creds.get('status') == 'active':
                    if api_name == 'yahoo' or creds.get('api_key'):
                        return api_name
        return None
    
    def mark_api_failed(self, api_name: str, error_msg: str):
        """Mark API as temporarily failed"""
        if api_name in self.credentials:
            self.credentials[api_name]['last_error'] = error_msg
            self.credentials[api_name]['last_error_time'] = datetime.now().isoformat()
            self.save_credentials(self.credentials)
            self.logger.warning(f"⚠️ Marked {api_name} as failed: {error_msg}")
    
    def get_usage_report(self) -> Dict:
        """Get usage report for all APIs"""
        report = {}
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        
        for api_name, limits in self.rate_limits.items():
            usage = self.usage_stats.get(api_name, {})
            daily_usage = usage.get(today, 0)
            
            report[api_name] = {
                'daily_usage': daily_usage,
                'daily_limit': limits['per_day'],
                'usage_percentage': (daily_usage / limits['per_day'] * 100) if limits['per_day'] > 0 else 0,
                'status': self.credentials.get(api_name, {}).get('status', 'unknown')
            }
        
        return report

# Global instance
api_manager = APICredentialsManager()

def setup_credentials_interactively():
    """Interactive setup for missing credentials"""
    print("🔧 ALPHA HUNTER API CREDENTIALS SETUP")
    print("=" * 40)
    
    missing_creds = []
    creds = api_manager.credentials
    
    # Check for missing credentials
    
    if not creds.get('telegram', {}).get('bot_token') or creds.get('telegram', {}).get('bot_token').startswith('746390'):
        missing_creds.append('telegram')
    
    if not creds.get('polygon', {}).get('api_key'):
        missing_creds.append('polygon')
    
    if missing_creds:
        print(f"❌ Missing credentials for: {', '.join(missing_creds)}")
        print("\n📋 TO CONFIGURE:")
        print("1. Telegram Bot: @BotFather on Telegram")
        print("2. Polygon.io: https://polygon.io/")
        print("3. IEX Cloud: https://iexcloud.io/")
        print("4. Financial Modeling Prep: https://financialmodelingprep.com/")
        return False
    else:
        print("✅ All critical credentials are configured!")
        return True

if __name__ == "__main__":
    setup_credentials_interactively()
    
    # Show usage report
    report = api_manager.get_usage_report()
    print("\n📊 API USAGE REPORT:")
    for api, stats in report.items():
        print(f"{api}: {stats['daily_usage']}/{stats['daily_limit']} ({stats['usage_percentage']:.1f}%)")