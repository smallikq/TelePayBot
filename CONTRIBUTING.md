# Contributing to TelePayBot

Thank you for considering contributing to TelePayBot! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/TelePayBot.git
   cd TelePayBot
   ```
3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## 🔧 Development Setup

1. Copy `.env.example` to `.env` and configure it
2. Run tests to ensure everything works:
   ```bash
   pytest tests/ -v
   ```

## 📝 Making Changes

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring

Example: `feature/add-payment-export`

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

```bash
pytest tests/ -v --cov=.
```

### Commit Messages

Use clear and descriptive commit messages:

```
<type>: <subject>

<body>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

Example:
```
feat: add payment export functionality

- Add export to CSV feature
- Add admin command /export
- Include tests for export functionality
```

## 🧪 Testing Guidelines

- Write unit tests for new functionality
- Test edge cases and error conditions
- Mock external dependencies (Telegram API, database)
- Ensure tests are deterministic

## 📚 Documentation

- Update README.md if adding new features
- Update CHANGELOG.md following Keep a Changelog format
- Add docstrings to new functions
- Include usage examples where appropriate

## 🔍 Pull Request Process

1. **Update your fork**
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

4. **Run tests**
   ```bash
   pytest tests/ -v
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add my new feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/my-new-feature
   ```

7. **Create Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Include screenshots if UI changes
   - Ensure CI passes

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts
- [ ] Commits are meaningful and well-organized

## 🐛 Bug Reports

When reporting bugs, include:

- Clear description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version and OS
- Relevant logs or error messages

## 💡 Feature Requests

When suggesting features:

- Explain the use case
- Describe the expected behavior
- Consider implementation complexity
- Check if feature already exists

## 🤝 Code Review

- Be respectful and constructive
- Focus on the code, not the person
- Explain reasoning for suggestions
- Approve when satisfied or suggest changes

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions

If you have questions, feel free to:
- Open an issue
- Start a discussion
- Contact maintainers

Thank you for contributing! 🎉
