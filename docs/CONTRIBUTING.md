# Contributing to SmartPLC AI Agent

Thank you for considering contributing! 🎉

## 🚀 Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/SmartPLC_AI_Agent.git
cd SmartPLC_AI_Agent/SmartPLC_AI_Agent
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-cov black ruff mypy pylint
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## 📝 Development Workflow

### Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

Run before committing:

```bash
# Format code
black .

# Check linting
ruff check .

# Type check
mypy core/ --ignore-missing-imports
```

Or use the Makefile:

```bash
make format  # Auto-format
make lint    # Check code quality
```

### Testing

Write tests for new features:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=core --cov-report=html

# Or use Makefile
make test
make test-cov
```

### Test Structure

```python
# tests/test_your_feature.py
import pytest

def test_your_feature():
    """Test description"""
    # Arrange
    ...
    
    # Act
    result = your_function()
    
    # Assert
    assert result == expected
```

## 📋 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**

```bash
git commit -m "feat(rag): add support for PDF documents"
git commit -m "fix(plc): correct tank overflow detection"
git commit -m "docs: update installation instructions"
```

## 🔍 Pull Request Process

1. **Update Documentation**
   - Add docstrings to new functions
   - Update README.md if needed
   - Add examples for new features

2. **Run Tests**
   ```bash
   make test
   make lint
   ```

3. **Create Pull Request**
   - Use a descriptive title
   - Reference related issues
   - Describe changes in detail
   - Include screenshots for UI changes

4. **Review Process**
   - Wait for CI checks to pass
   - Address reviewer comments
   - Keep commits clean

## 🏗️ Project Structure

```
SmartPLC_AI_Agent/
├── core/              # Business logic
│   ├── plc/          # PLC simulation
│   ├── llm/          # RAG + OpenAI
│   └── data/         # Database models
├── gui/              # PySide6 GUI
│   └── views/        # UI components
├── tests/            # Test suite
└── knowledge_base/   # RAG documents
```

## 📚 Adding Features

### Example: Adding a New Signal

1. **Update Mock PLC** (`core/plc/mock_plc.py`):

```python
self.add_signal(IOSignal(
    name="AI_05_NewSensor",
    type=SignalType.AI,
    address="%IW108",
    description="Your sensor description",
    value=0.0,
    unit="unit",
    min_value=0.0,
    max_value=100.0
))
```

2. **Add Documentation** (`knowledge_base/manuals/signal_documentation.md`):

```markdown
### AI_05_NewSensor
**Description:** ...
**Range:** 0-100 unit
...
```

3. **Write Tests** (`tests/test_new_signal.py`):

```python
def test_new_signal(mock_plc):
    value = mock_plc.read_signal("AI_05_NewSensor")
    assert 0 <= value <= 100
```

4. **Re-initialize Knowledge Base**:

```bash
python init_knowledge_base.py
```

## 🐛 Reporting Bugs

Create an issue with:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: How to trigger the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, etc.
- **Logs**: Relevant error messages

## 💡 Feature Requests

Create an issue with:

- **Use Case**: Why is this feature needed?
- **Proposal**: How should it work?
- **Alternatives**: Other solutions considered
- **Examples**: Similar features in other tools

## 📄 Documentation

- Keep README.md up to date
- Add docstrings to all functions
- Update ARCHITECTURE.md for major changes
- Add examples for new features

## ❓ Questions?

- Open a Discussion on GitHub
- Check existing Issues
- Review documentation

## 🙏 Thank You!

Your contributions make this project better! ⭐
