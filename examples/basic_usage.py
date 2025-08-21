#!/usr/bin/env python3
"""
Alpha Hunter Signals - Basic Usage Example
Created by Michael David Jaramillo

This example demonstrates basic usage of the Alpha Hunter system:
- Running a simple market scan
- Analyzing individual tickers
- Understanding the signal format
"""

import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir.parent / 'src'
sys.path.insert(0, str(src_path))

from core.autonomous_sp500_scanner import AutonomousS&P500Scanner
from analysis.probability_engine_v2 import ProbabilityEngineV2
from telegram.unified_telegram_messenger import UnifiedTelegramMessenger

def basic_scan_example():
    """Demonstrate basic market scanning."""
    print("🚀 Alpha Hunter - Basic Scan Example")
    print("=" * 50)
    
    # Initialize scanner (personal telegram mode for testing)
    scanner = AutonomousS&P500Scanner(telegram_mode="personal")
    
    print("📊 Scanning S&P 500 for opportunities...")
    print("⏳ This may take 5-15 minutes depending on market conditions...")
    
    try:
        # Run scan with small sample for demo
        opportunities = scanner.scan_opportunities(max_analyze=10)
        
        print(f"\n✅ Scan completed!")
        print(f"📈 Found {len(opportunities)} trading opportunities")
        
        if opportunities:
            print("\n🎯 Top Opportunities:")
            print("-" * 30)
            
            for i, opp in enumerate(opportunities[:3], 1):
                print(f"{i}. {opp['ticker']}")
                print(f"   Probability: {opp['probability']:.1f}%")
                print(f"   Strategy: {opp['strategy']}")
                print(f"   Expected Return: {opp.get('expected_return', 'N/A')}%")
                print()
        else:
            print("❌ No opportunities found with current market conditions")
            
    except Exception as e:
        print(f"❌ Error during scan: {e}")
        print("💡 Make sure your .env file is configured correctly")

def individual_analysis_example():
    """Demonstrate individual ticker analysis."""
    print("\n🔍 Alpha Hunter - Individual Analysis Example")
    print("=" * 50)
    
    # Initialize probability engine
    engine = ProbabilityEngineV2()
    
    # Analyze popular ticker
    ticker = "AAPL"
    print(f"📊 Analyzing {ticker}...")
    
    try:
        signal = engine.generate_professional_signal(ticker)
        
        print(f"\n✅ Analysis complete for {ticker}")
        print("-" * 30)
        print(f"💰 Current Price: ${signal['current_price']:.2f}")
        print(f"🎯 Signal: {signal['signal_direction']}")
        print(f"⚡ Probability: {signal['probability']:.1f}%")
        print(f"🔬 Confidence: {signal['confidence']:.1f}%")
        print(f"🚀 Strategy: {signal['strategy']}")
        print(f"💵 Strike Price: ${signal['strike_price']:.2f}")
        print(f"📅 Expiry: {signal['expiry_date']}")
        print(f"📈 Expected Return: {signal['expected_return']:.1f}%")
        print(f"⚖️ Risk Level: {signal['risk_level']}")
        print(f"\n💭 Reasoning: {signal['reasoning']}")
        
    except Exception as e:
        print(f"❌ Error analyzing {ticker}: {e}")

def telegram_delivery_example():
    """Demonstrate Telegram message delivery (requires configuration)."""
    print("\n📱 Alpha Hunter - Telegram Delivery Example")
    print("=" * 50)
    
    # Check if Telegram is configured
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("⚠️  Telegram not configured - set TELEGRAM_BOT_TOKEN in .env")
        print("💡 This example requires Telegram configuration")
        return
        
    messenger = UnifiedTelegramMessenger()
    
    # Create sample signal for demonstration
    sample_signal = {
        "ticker": "SPY",
        "current_price": 450.00,
        "signal_direction": "BULLISH",
        "probability": 72.5,
        "confidence": 85.0,
        "strategy": "long_call",
        "strike_price": 454.50,
        "expiry_date": "2025-09-15",
        "expected_return": 12.5,
        "risk_level": "MEDIUM",
        "take_profit": 463.50,
        "stop_loss": 438.75,
        "reasoning": "Strong technical confluence with earnings momentum",
        "timestamp": "2025-08-21 14:30:00"
    }
    
    print("📤 Sending sample signal to Telegram...")
    
    try:
        success = messenger.send_dual_signal(sample_signal)
        
        if success:
            print("✅ Signal sent successfully!")
            print("📱 Check your Telegram for the formatted message")
        else:
            print("❌ Failed to send signal")
            print("💡 Check your Telegram configuration in .env")
            
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")

def system_health_check():
    """Check system health and configuration."""
    print("\n🏥 Alpha Hunter - System Health Check")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    optional_vars = ['ALPHA_VANTAGE_KEY', 'POLYGON_API_KEY', 'FINNHUB_API_KEY']
    
    print("🔧 Configuration Check:")
    print("-" * 25)
    
    for var in required_vars:
        value = os.getenv(var)
        status = "✅" if value else "❌"
        print(f"{status} {var}: {'Configured' if value else 'Missing'}")
    
    print("\n🛠️  Optional Configuration:")
    print("-" * 25)
    
    for var in optional_vars:
        value = os.getenv(var)
        status = "✅" if value else "⚠️"
        print(f"{status} {var}: {'Configured' if value else 'Using fallback'}")
    
    # Test data source availability
    print("\n📊 Data Source Test:")
    print("-" * 20)
    
    try:
        engine = ProbabilityEngineV2()
        test_data = engine._fetch_market_data("SPY")
        
        if test_data is not None and not test_data.empty:
            print("✅ Market data: Available")
            print(f"   Latest price: ${test_data['Close'].iloc[-1]:.2f}")
        else:
            print("⚠️  Market data: Using fallback")
    except Exception as e:
        print(f"❌ Market data: Error ({e})")
    
    print("\n🏁 System Status: Ready for trading signals!")

if __name__ == "__main__":
    print("🚀 Alpha Hunter Signals - Example Suite")
    print("Created by Michael David Jaramillo")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run examples
    system_health_check()
    individual_analysis_example()
    
    # Ask user if they want to run full scan
    print("\n" + "=" * 60)
    run_scan = input("🤔 Run full market scan? This takes 5-15 minutes (y/n): ")
    
    if run_scan.lower() in ['y', 'yes']:
        basic_scan_example()
    else:
        print("⏭️  Skipping full scan")
    
    # Ask about Telegram test
    print("\n" + "=" * 60)
    test_telegram = input("📱 Test Telegram delivery? (requires configuration) (y/n): ")
    
    if test_telegram.lower() in ['y', 'yes']:
        telegram_delivery_example()
    else:
        print("⏭️  Skipping Telegram test")
    
    print("\n🎯 Example suite completed!")
    print("💡 For more examples, check the other files in examples/")
    print("📚 Read docs/API_DOCUMENTATION.md for detailed API reference")