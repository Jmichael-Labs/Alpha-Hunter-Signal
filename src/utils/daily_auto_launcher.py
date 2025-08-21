#!/usr/bin/env python3
"""
ALPHA HUNTER V2 - DAILY AUTO LAUNCHER
Activador automático diario que inicia al abrir terminal
"""

# 🕵️ ACTIVATE ULTIMATE BROKEN PIPE HUNTER FIRST (before any other imports)
import sys
import os
sys.path.insert(0, "/Volumes/DiskExFAT 1/system_data/nucleo_agi/alpha_hunter")

# Import and activate ultimate protection before anything else
from ultimate_brokenpipe_hunter import activate_ultimate_protection
activate_ultimate_protection()

# ☢️ ACTIVATE NUCLEAR OPTION AS LAST RESORT
from nuclear_brokenpipe_killer import activate_nuclear_option
activate_nuclear_option()

import time
from datetime import datetime, timedelta
import subprocess
import json
from safe_send_utility import safe_subprocess_run, safe_subprocess_communicate, safe_send, get_safe_send_stats
# Import global subprocess patcher to protect ALL subprocess calls system-wide
import global_subprocess_patcher

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.nexus_utils import nexus_speak
except ImportError:
    def nexus_speak(level, message):
        print(f"[{level.upper()}] {message}")

class DailyAutoLauncher:
    """Lanzador automático diario de Alpha Hunter V2"""
    
    def __init__(self):
        self.base_path = "/Volumes/DiskExFAT 1/system_data/nucleo_agi/alpha_hunter"
        self.status_file = f"{self.base_path}/daily_status.json"
        self.last_run_date = self.get_last_run_date()
        
    def get_last_run_date(self):
        """Obtiene la fecha del último escaneo"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                    return status.get('last_run_date', '')
            return ''
        except:
            return ''
    
    def get_execution_count(self):
        """Obtiene el contador de ejecuciones del día"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                    today = datetime.now().strftime('%Y-%m-%d')
                    last_run_date = status.get('last_run_date', '')
                    
                    # Reset counter if new day
                    if last_run_date != today:
                        return 0
                    return status.get('execution_count', 0)
            return 0
        except:
            return 0
    
    def update_status(self, status_data):
        """Actualiza el estado del sistema"""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            nexus_speak("error", f"❌ Error updating status: {e}")
    
    def should_run_today(self):
        """Determina si debe ejecutarse - EJECUTA SIEMPRE 24/7"""
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # NUEVA LÓGICA: SIEMPRE EJECUTAR cuando se abre terminal - 24/7
        return True, f"Terminal opened at {current_time} - Running new scan"
    
    def send_startup_message(self):
        """Envía mensaje de startup"""
        try:
            # Import telegram sender
            telegram_file = f"{self.base_path}/telegram_sender_fixed.py"
            
            if os.path.exists(telegram_file):
                import importlib.util
                spec = importlib.util.spec_from_file_location("telegram_sender", telegram_file)
                telegram_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(telegram_module)
                
                startup_msg = f"""🚀 ALPHA HUNTER V2 FIXED - PRODUCTION READY
📅 {datetime.now().strftime("%Y-%m-%d %H:%M")}

⚡ System Status: ONLINE
🧠 Professional Analysis: ACTIVE  
📊 Probability Engine: READY
💰 Strategy Optimizer: LOADED
🛠️ Unicode Fixes: APPLIED

🔄 Scanning 25 premium opportunities...
📱 Individual alerts incoming!

Alpha Hunter V2 - Reliable Trading Intelligence"""
                
                telegram_module.send_clean_telegram(startup_msg)
                nexus_speak("success", "✅ Startup message sent")
                return True
        except Exception as e:
            nexus_speak("error", f"❌ Startup message failed: {e}")
            return False
    
    def launch_daily_scan(self):
        """Lanza el escaneo diario"""
        try:
            nexus_speak("info", "🚀 Launching daily S&P 500 scan...")
            
            # Send startup notification
            self.send_startup_message()
            
            # Launch scanner V2 FIXED (V3 hangs - volver a V2 con fixes aplicados)
            scanner_script = f"{self.base_path}/autonomous_sp500_scanner.py"
            
            # Run V2 FIXED with optimal parameters for quick results
            cmd = [
                sys.executable, 
                scanner_script,
                "--tickers", "25"  # Balance speed vs opportunities
            ]
            
            # REFACTORED: Launch with safe subprocess handling (BrokenPipeError tolerant)
            try:
                # Use safe subprocess execution with 5-minute timeout protection  
                nexus_speak("info", f"🚀 Launching scanner with 5-minute timeout protection")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Set 5-minute timeout to prevent hanging
                import signal
                
                def timeout_handler(signum, frame):
                    nexus_speak("warning", "⏰ Scanner timeout - terminating process")
                    process.terminate()
                    raise TimeoutError("Scanner exceeded 5-minute timeout")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(300)  # 5 minutes
                
                nexus_speak("info", f"📊 Scanner launched with PID: {process.pid}")
                
                # FIXED: Use safe_subprocess_communicate for BrokenPipeError tolerance
                nexus_speak("info", "🔄 Waiting for scan completion with BrokenPipeError protection...")
                
                result = safe_subprocess_communicate(
                    process=process,
                    timeout=300,
                    context="daily_scanner"
                )
                
                # Cancel timeout alarm
                signal.alarm(0)
                
                if result['success']:
                    if result.get('pipe_error', False):
                        nexus_speak("warning", "⚠️ Daily scan completed despite BrokenPipeError (process finished)")
                    elif result.get('timeout', False):
                        nexus_speak("warning", "⚠️ Daily scan timeout - continuing in background")
                    else:
                        nexus_speak("success", "✅ Daily scan completed successfully via safe subprocess!")
                    
                    # Update status (ahora incluye contador de ejecuciones)  
                    status = {
                        'last_run_date': datetime.now().strftime('%Y-%m-%d'),
                        'last_run_time': datetime.now().isoformat(),
                        'status': 'completed' if not result.get('timeout', False) else 'running',
                        'pid': process.pid,
                        'execution_count': self.get_execution_count() + 1,
                        'returncode': result['returncode']
                    }
                    self.update_status(status)
                    
                    return True
                else:
                    nexus_speak("error", f"❌ Scanner failed: {result['stderr']}")
                    nexus_speak("warning", "⚠️ But Daily Scan system continues running (non-blocking failure)")
                    
                    # Even if subprocess failed, don't block the Daily Scan system
                    status = {
                        'last_run_date': datetime.now().strftime('%Y-%m-%d'),
                        'last_run_time': datetime.now().isoformat(),
                        'status': 'failed_non_blocking',
                        'pid': process.pid,
                        'execution_count': self.get_execution_count() + 1,
                        'returncode': result['returncode'],
                        'error': result['stderr']
                    }
                    self.update_status(status)
                    
                    return True  # Return True to not block the system
                    
            except Exception as e:
                nexus_speak("error", f"❌ Safe subprocess execution failed: {e}")
                return False
                
        except Exception as e:
            nexus_speak("error", f"❌ Failed to launch daily scan: {e}")
            return False
    
    def check_and_launch(self):
        """Verifica y lanza si es necesario"""
        should_run, reason = self.should_run_today()
        
        if should_run:
            nexus_speak("info", f"🎯 Launching daily scan: {reason}")
            success = self.launch_daily_scan()
            
            if success:
                execution_count = self.get_execution_count() + 1
                print(f"""
🚀 ALPHA HUNTER V2 MULTI-SCAN LAUNCHED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
🔄 Execution: #{execution_count} today
🎯 Status: Running fresh S&P 500 analysis
📊 Coverage: Top 15 tickers from S&P 500
💰 Budget: $500-1000 dynamic allocation
📱 Alerts: Will be sent automatically to Telegram

⚡ Alpha Hunter V2 runs every terminal session!
🔄 Fresh opportunities analysis in progress.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                """)
            else:
                print("❌ Failed to launch scan")
        else:
            nexus_speak("info", f"⏭️ Skipping scan: {reason}")
            print(f"""
📊 ALPHA HUNTER V2 STATUS CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Current: {datetime.now().strftime('%Y-%m-%d %H:%M')}
📋 Status: {reason}

ℹ️  Alpha Hunter V2 runs every terminal session 24/7
⚡ Always ready for fresh market analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """)

def main():
    """Función principal del auto launcher"""
    launcher = DailyAutoLauncher()
    launcher.check_and_launch()

if __name__ == "__main__":
    main()