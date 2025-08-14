# Contributing to Omega AI Data Analyst

Thank you for your interest in contributing to Omega! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
1. Check existing [issues](../../issues) first
2. Use the issue template
3. Include:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages (without sensitive data)

### Suggesting Features
1. Check if the feature is already requested
2. Open a feature request issue
3. Describe:
   - The problem it solves
   - Proposed solution
   - Alternative solutions considered
   - Additional context

### Code Contributions

#### Development Setup
```bash
git clone https://github.com/LegitScarf/omega-ai-analyst.git
cd omega-ai-analyst
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Making Changes
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Write tests for new functionality
5. Ensure all tests pass: `pytest tests/`
6. Update documentation if needed
7. Commit with clear messages
8. Push to your fork
9. Create a pull request

#### Pull Request Guidelines
- Use clear, descriptive titles
- Reference related issues
- Include screenshots for UI changes
- Add tests for new features
- Update documentation
- Follow the existing code style

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### Agent Development
When adding new agents:
```python
def new_agent(data, query, client):
    """
    Brief description of agent purpose
    
    Args:
        data (pd.DataFrame): The dataset
        query (str): User query
        client (OpenAI): OpenAI client instance
    
    Returns:
        Appropriate return type based on agent function
    """
    try:
        # Agent logic here
        pass
    except Exception as e:
        st.error(f"Error in {agent_name}: {str(e)}")
        return fallback_value
```

### Testing
- Write unit tests for new functions
- Test error handling scenarios
- Mock OpenAI API calls in tests
- Test with various data formats

### Documentation
- Update README.md for new features
- Add docstrings to new functions
- Include examples where helpful
- Update troubleshooting section for new issues

## 🚀 Areas for Contribution

### High Priority
- [ ] Support for additional file formats (JSON, Parquet)
- [ ] Enhanced error handling and user feedback
- [ ] Performance optimizations for large datasets
- [ ] Mobile-responsive UI improvements
- [ ] Additional chart types and customization options

### Medium Priority
- [ ] SQL database connectivity
- [ ] Advanced statistical functions
- [ ] Export functionality (PDF, PowerPoint)
- [ ] Custom color themes
- [ ] Multi-language support

### Low Priority
- [ ] Integration with cloud storage services
- [ ] Collaborative features
- [ ] Advanced ML capabilities
- [ ] Real-time data streaming
- [ ] Plugin system for custom agents

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=omega_analyst tests/

# Run specific test file
pytest tests/test_agents.py
```

### Writing Tests
Create test files in the `tests/` directory:
```python
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from omega_analyst import context_checker_agent

def test_context_checker_intent_analyze():
    """Test context checker correctly identifies analysis intent"""
    # Mock OpenAI client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices[0].message.content = "analyze"
    mock_client.chat.completions.create.return_value = mock_response
    
    # Test data
    data = pd.DataFrame({'sales': [1, 2, 3]})
    query = "show me sales trends"
    
    # Test
    result = context_checker_agent(data, query, mock_client)
    assert result == "analyze"
```

## 📚 Documentation Standards

### Code Documentation
- Use clear, concise docstrings
- Include parameter and return type information
- Provide examples for complex functions
- Document any side effects

### README Updates
When adding features:
- Update the features list
- Add usage examples
- Update installation instructions if needed
- Add to troubleshooting if applicable

## 🔒 Security Guidelines

### API Key Handling
- Never commit API keys to the repository
- Use environment variables or secrets management
- Validate API key formats before use
- Handle API errors gracefully

### Data Privacy
- Don't log sensitive user data
- Ensure temporary files are cleaned up
- Don't store user data beyond the session
- Be transparent about data usage

## 🐛 Debugging Tips

### Common Development Issues
1. **OpenAI API Errors**: Check API key validity and rate limits
2. **Streamlit Caching**: Clear cache with `streamlit cache clear`
3. **Import Errors**: Verify all dependencies are installed
4. **Visualization Issues**: Check matplotlib backend settings

### Debugging Tools
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Streamlit debug mode
streamlit run omega_analyst.py --logger.level debug
```

## 📝 Commit Message Format
```
type(scope): brief description

Longer description if needed

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(agents): add new statistical analysis agent`
- `fix(ui): resolve sidebar visibility issues`
- `docs(readme): update installation instructions`

## 🎉 Recognition

Contributors will be:
- Listed in the README contributors section
- Credited in release notes
- Invited to join our Discord community
- Given appropriate GitHub badges

## 📞 Getting Help

- 📧 Email: arpanmallik173@gmail.com

Thank you for contributing to Omega! 🚀
