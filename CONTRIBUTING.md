# Contributing to Alpha Hunter Signals

Thank you for your interest in contributing to Alpha Hunter Signals! This document provides guidelines for contributing to this AI-powered autonomous trading system.

## 🤝 Contributing Guidelines

### Before You Start

1. **Read the Documentation**: Familiarize yourself with the system architecture and features
2. **Review Open Issues**: Check existing issues to avoid duplicating work
3. **Understand the Mission**: Alpha Hunter focuses on autonomous, professional-grade trading signals

## 🚀 Getting Started

### Development Setup

1. **Fork the Repository**
```bash
git fork https://github.com/Jmichael-Labs/Alpha-Hunter-Signal
cd Alpha-Hunter-Signal
```

2. **Set Up Development Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your test credentials
```

4. **Run Tests**
```bash
python -m pytest tests/
python src/core/autonomous_sp500_scanner.py --test --tickers 3
```

### Development Workflow

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes**
   - Follow the coding standards below
   - Write tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python tests/test_system_integration.py

# Test with real data (small sample)
python src/core/autonomous_sp500_scanner.py --test --tickers 5
```

4. **Commit and Push**
```bash
git add .
git commit -m "feat: description of your feature"
git push origin feature/your-feature-name
```

5. **Create Pull Request**
   - Use descriptive title and description
   - Reference any related issues
   - Include test results

## 🎯 Areas for Contribution

### High Priority
- **🔍 Analysis Engines**: New technical indicators, ML models
- **📊 Data Sources**: Additional market data providers, APIs
- **⚡ Performance**: Optimization of analysis speed
- **🛡️ Risk Management**: Enhanced position sizing, stop loss logic

### Medium Priority
- **🎨 Signal Formatting**: Alternative message formats
- **📱 Integrations**: Discord, Slack, email delivery
- **📈 Backtesting**: Historical performance validation
- **🔧 Configuration**: More customizable parameters

### Low Priority
- **📚 Documentation**: Tutorial videos, examples
- **🌐 Internationalization**: Multi-language support
- **🎯 UI/Dashboard**: Web interface for monitoring

## 📋 Coding Standards

### Python Style
- **PEP 8 Compliance**: Use black formatter
- **Type Hints**: Include type annotations
- **Docstrings**: Google style docstrings for all functions
- **Error Handling**: Comprehensive try/catch blocks

### Example Function Structure
```python
def analyze_market_signal(ticker: str, timeframe: str = "1d") -> Dict[str, Any]:
    """
    Analyze market signals for a given ticker.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        timeframe: Analysis timeframe ('1d', '1h', '5m')
        
    Returns:
        Dictionary containing signal analysis results
        
    Raises:
        ValueError: If ticker is invalid
        APIError: If data source is unavailable
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Signal analysis failed for {ticker}: {e}")
        raise
```

### File Organization
```
src/
├── core/           # Main system components
├── analysis/       # Analysis engines and algorithms
├── data/          # Data fetching and processing
├── strategies/    # Trading strategies
├── telegram/      # Message delivery
└── utils/         # Utility functions

tests/
├── unit/          # Unit tests
├── integration/   # Integration tests
└── fixtures/      # Test data
```

## 🧪 Testing Requirements

### Test Coverage
- **Unit Tests**: All new functions must have tests
- **Integration Tests**: End-to-end system functionality
- **Mock Data**: Use realistic market data for testing
- **Edge Cases**: Test error conditions and boundary cases

### Test Examples
```python
def test_probability_engine():
    """Test probability calculation with known data."""
    engine = ProbabilityEngineV2()
    result = engine.calculate_probability("AAPL", mock_data)
    
    assert result["probability"] > 0.3
    assert result["confidence"] > 0.6
    assert "reasoning" in result
```

## 🔐 Security Guidelines

### Sensitive Data
- **Never commit**: API keys, tokens, personal credentials
- **Use .env files**: For all configuration
- **Sanitize logs**: Remove sensitive information from log files
- **API rate limits**: Respect all provider limits

### Code Review Checklist
- [ ] No hardcoded credentials or API keys
- [ ] Proper error handling for API failures
- [ ] Rate limiting implemented for external calls
- [ ] Input validation for user-provided data
- [ ] Logging doesn't expose sensitive information

## 📝 Commit Message Format

Use conventional commits:

```
type(scope): description

feat(analysis): add RSI divergence detection
fix(telegram): resolve duplicate message issue
docs(readme): update installation instructions
test(core): add unit tests for signal generation
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `style`: Code style changes

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues
2. Test with latest version
3. Try with minimal configuration

### Bug Report Template
```markdown
**Bug Description**
Clear description of the issue

**To Reproduce**
Steps to reproduce:
1. Configure system with...
2. Run command...
3. Observe error...

**Expected Behavior**
What should happen

**Environment**
- OS: [e.g., macOS 12.6]
- Python: [e.g., 3.11.0]
- Version: [e.g., v1.2.0]

**Additional Context**
- Error logs
- Configuration files (without credentials)
- Screenshots if applicable
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Mockups, examples, related issues
```

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Email**: [Contact Information] for private matters

## 🏆 Recognition

Contributors will be:
- Added to the contributors list
- Mentioned in release notes for significant contributions
- Invited to collaborate on future projects

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make Alpha Hunter Signals better! 🚀**

---

<div align="center">
<strong>Trade Smart. Code Smart. Contribute Smart.</strong>
</div>