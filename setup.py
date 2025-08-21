#!/usr/bin/env python3
"""
Alpha Hunter Signals - Professional Setup Script
Created by Michael David Jaramillo

Automated setup and configuration for Alpha Hunter autonomous trading system.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class AlphaHunterSetup:
    """Professional setup manager for Alpha Hunter Signals."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.venv_path = self.root_dir / "venv"
        self.env_file = self.root_dir / ".env"
        self.env_example = self.root_dir / ".env.example"
        
    def print_banner(self):
        """Display professional setup banner."""
        print("=" * 70)
        print("🚀 ALPHA HUNTER SIGNALS - PROFESSIONAL SETUP")
        print("=" * 70)
        print("Created by Michael David Jaramillo")
        print("AI-Powered Autonomous Options Trading Signal System")
        print("=" * 70)
        print()
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        print("🐍 Checking Python version...")
        
        version = sys.version_info
        required = (3, 11)
        
        if version >= required:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.11+")
            print("Please install Python 3.11 or higher and try again.")
            return False
    
    def create_virtual_environment(self) -> bool:
        """Create Python virtual environment."""
        print("\n🛠️  Creating virtual environment...")
        
        try:
            if self.venv_path.exists():
                print("⚠️  Virtual environment already exists - skipping")
                return True
            
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], check=True, capture_output=True)
            
            print("✅ Virtual environment created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        print("\n📦 Installing dependencies...")
        
        # Determine pip path
        if sys.platform == "win32":
            pip_path = self.venv_path / "Scripts" / "pip"
        else:
            pip_path = self.venv_path / "bin" / "pip"
        
        try:
            # Upgrade pip first
            subprocess.run([
                str(pip_path), "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Install requirements
            requirements_file = self.root_dir / "requirements.txt"
            if requirements_file.exists():
                subprocess.run([
                    str(pip_path), "install", "-r", str(requirements_file)
                ], check=True)
                
                print("✅ Dependencies installed successfully")
                return True
            else:
                print("❌ requirements.txt not found")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def setup_environment_variables(self) -> bool:
        """Setup .env file from template."""
        print("\n⚙️ Setting up environment variables...")
        
        if self.env_file.exists():
            print("⚠️  .env file already exists")
            overwrite = input("Overwrite existing .env file? (y/N): ").lower()
            if overwrite != 'y':
                print("✅ Keeping existing .env file")
                return True
        
        if not self.env_example.exists():
            print("❌ .env.example template not found")
            return False
        
        try:
            shutil.copy(self.env_example, self.env_file)
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your credentials")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    
    def collect_credentials(self) -> Dict[str, str]:
        """Collect user credentials interactively."""
        print("\n🔑 Credential Collection (Optional)")
        print("You can skip this and manually edit .env file later")
        print()
        
        credentials = {}
        
        # Telegram credentials (required)
        print("📱 Telegram Configuration (Required for signals):")
        bot_token = input("Bot Token (from @BotFather): ").strip()
        if bot_token:
            credentials["TELEGRAM_BOT_TOKEN"] = bot_token
        
        chat_id = input("Chat ID (from @userinfobot): ").strip()
        if chat_id:
            credentials["TELEGRAM_CHAT_ID"] = chat_id
        
        channel_id = input("Channel ID (optional, for public signals): ").strip()
        if channel_id:
            credentials["TELEGRAM_CHANNEL_ID"] = channel_id
        
        # API keys (optional)
        print("\n📊 Market Data APIs (Optional - system has fallbacks):")
        
        apis = [
            ("Alpha Vantage", "ALPHA_VANTAGE_KEY", "https://www.alphavantage.co/support/#api-key"),
            ("Polygon.io", "POLYGON_API_KEY", "https://polygon.io/"),
            ("Finnhub", "FINNHUB_API_KEY", "https://finnhub.io/register")
        ]
        
        for name, key, url in apis:
            print(f"\n{name} ({url}):")
            api_key = input(f"{key} (optional): ").strip()
            if api_key:
                credentials[key] = api_key
        
        return credentials
    
    def update_env_file(self, credentials: Dict[str, str]) -> bool:
        """Update .env file with provided credentials."""
        if not credentials or not self.env_file.exists():
            return True
        
        try:
            # Read existing file
            with open(self.env_file, 'r') as f:
                lines = f.readlines()
            
            # Update lines with new credentials
            updated_lines = []
            for line in lines:
                line = line.strip()
                updated = False
                
                for key, value in credentials.items():
                    if line.startswith(f"{key}="):
                        updated_lines.append(f"{key}={value}\n")
                        updated = True
                        break
                
                if not updated:
                    updated_lines.append(line + '\n' if line else '\n')
            
            # Write updated file
            with open(self.env_file, 'w') as f:
                f.writelines(updated_lines)
            
            print("✅ Environment file updated with credentials")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update .env file: {e}")
            return False
    
    def create_directories(self) -> bool:
        """Create necessary directories."""
        print("\n📁 Creating directories...")
        
        directories = [
            "logs",
            "data/cache", 
            "exports",
            "backups"
        ]
        
        try:
            for dir_name in directories:
                dir_path = self.root_dir / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
            
            print("✅ Directories created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create directories: {e}")
            return False
    
    def run_system_test(self) -> bool:
        """Run basic system test."""
        print("\n🧪 Running system test...")
        
        # Determine python path
        if sys.platform == "win32":
            python_path = self.venv_path / "Scripts" / "python"
        else:
            python_path = self.venv_path / "bin" / "python"
        
        try:
            # Test basic imports
            test_script = """
import sys
import os
from pathlib import Path

# Add src to path
root_dir = Path(__file__).parent
src_path = root_dir / 'src'
sys.path.insert(0, str(src_path))

try:
    from core.autonomous_sp500_scanner import AutonomousS&P500Scanner
    from analysis.probability_engine_v2 import ProbabilityEngineV2
    print("✅ Core modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("🚀 Alpha Hunter Signals - System test passed!")
"""
            
            test_file = self.root_dir / "system_test.py"
            with open(test_file, 'w') as f:
                f.write(test_script)
            
            result = subprocess.run([
                str(python_path), str(test_file)
            ], capture_output=True, text=True, cwd=self.root_dir)
            
            # Cleanup test file
            test_file.unlink()
            
            if result.returncode == 0:
                print("✅ System test passed")
                return True
            else:
                print(f"❌ System test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to run system test: {e}")
            return False
    
    def print_usage_instructions(self):
        """Print usage instructions."""
        print("\n" + "=" * 70)
        print("🎯 SETUP COMPLETE - USAGE INSTRUCTIONS")
        print("=" * 70)
        
        # Determine activation command
        if sys.platform == "win32":
            activate_cmd = r"venv\Scripts\activate"
            python_cmd = r"venv\Scripts\python"
        else:
            activate_cmd = "source venv/bin/activate"
            python_cmd = "venv/bin/python"
        
        instructions = f"""
🚀 Quick Start:

1. Activate virtual environment:
   {activate_cmd}

2. Run basic example:
   {python_cmd} examples/basic_usage.py

3. Run full system scan:
   {python_cmd} src/core/autonomous_sp500_scanner.py --test --tickers 10

📱 Telegram Setup:
   - Create bot with @BotFather on Telegram
   - Get your chat ID from @userinfobot  
   - Update .env file with your credentials

📊 Optional API Keys:
   - Alpha Vantage: Free 500 calls/day
   - Polygon.io: Free 5 calls/minute
   - Finnhub: Free 60 calls/minute

🔧 Configuration:
   - Edit .env file with your credentials
   - Modify src/config/ files for custom settings
   - Check docs/API_DOCUMENTATION.md for details

📚 Documentation:
   - README.md: System overview
   - docs/API_DOCUMENTATION.md: Detailed API reference
   - examples/: Usage examples
   - CONTRIBUTING.md: Development guidelines

🎯 Support:
   - GitHub Issues: Bug reports and feature requests
   - Created by Michael David Jaramillo
"""
        
        print(instructions)
        print("=" * 70)
        print("🚀 Alpha Hunter Signals is ready for autonomous trading!")
        print("=" * 70)
    
    def run_setup(self) -> bool:
        """Run complete setup process."""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_python_version():
            return False
        
        # Setup steps
        setup_steps = [
            ("Virtual Environment", self.create_virtual_environment),
            ("Dependencies", self.install_dependencies), 
            ("Environment Variables", self.setup_environment_variables),
            ("Directories", self.create_directories),
            ("System Test", self.run_system_test)
        ]
        
        for step_name, step_func in setup_steps:
            if not step_func():
                print(f"\n❌ Setup failed at: {step_name}")
                return False
        
        # Optional credential collection
        print("\n" + "=" * 50)
        collect = input("Configure credentials now? (y/N): ").lower()
        if collect == 'y':
            credentials = self.collect_credentials()
            if credentials:
                self.update_env_file(credentials)
        
        # Print final instructions
        self.print_usage_instructions()
        
        return True

def main():
    """Main setup entry point."""
    try:
        setup = AlphaHunterSetup()
        success = setup.run_setup()
        
        if success:
            print("\n🎉 Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Setup failed - please check errors above")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()