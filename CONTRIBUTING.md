# Contributing to ParcelFlow

Thank you for your interest in contributing to ParcelFlow! This project is designed as a reference implementation for teaching workflow execution concepts, with an emphasis on simplicity and clarity.

## Getting Started

ParcelFlow is intentionally minimal with zero external dependencies (for the Python reference implementation). Getting started is straightforward:

```bash
# Clone the repository
git clone https://github.com/DarekDev/parcel-flow.git
cd parcel-flow

# No installation needed! Just run:
python main.py array

# Run tests
python run_tests.py
```

## How to Contribute

We welcome contributions! Here's how to get involved:

### Reporting Issues

Found a bug or have a suggestion? Please open an issue on GitHub:
- **Bug reports**: Describe what happened, what you expected, and steps to reproduce
- **Feature requests**: Explain the use case and why it would benefit the project
- **Questions**: Feel free to ask for clarification on how things work

[Open an issue](https://github.com/DarekDev/parcel-flow/issues)

### Proposing Changes

1. **Fork the repository** on GitHub
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Write clear, readable code
   - Add tests for new functionality
   - Update documentation as needed
4. **Run the test suite**:
   ```bash
   python run_tests.py
   ```
   All tests must pass before submitting.
5. **Commit your changes**:
   ```bash
   git commit -m "Brief description of changes"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Submit a pull request** via GitHub

## Development Guidelines

### Code Style

- **Follow PEP 8** for Python code style
- **Keep it simple**: This is a teaching tool—clarity over cleverness
- **Add docstrings**: All classes and public methods should have clear docstrings
- **Use meaningful names**: Variable and function names should be self-documenting
- **Avoid dependencies**: The reference implementation should remain dependency-free

### Testing Requirements

- **All new features must include tests**
- **Existing tests must continue to pass**
- Tests should be clear and demonstrate the feature's behavior
- Run tests before submitting: `python run_tests.py`

### Documentation

- Update README.md if you change user-facing functionality
- Add docstrings to new classes and methods
- Include usage examples for new features
- Keep explanations beginner-friendly (this is for teaching!)

## What We're Looking For

### High Priority Contributions

- **Bug fixes**: Corrections to existing functionality
- **Test coverage**: Additional tests for edge cases
- **Documentation improvements**: Clearer explanations, more examples
- **Example workflows**: New demonstration workflows in `workflows.py`

### Medium Priority

- **Performance improvements**: As long as they don't sacrifice clarity
- **Error messages**: More helpful error messages for common mistakes
- **Teaching materials**: Tutorials, diagrams, or explanatory content

### Lower Priority (Discuss First)

- **New features**: Open an issue to discuss before implementing
- **Breaking changes**: These should be avoided unless absolutely necessary
- **External dependencies**: The reference implementation should remain dependency-free

## Questions?

Not sure about something? Have questions about the architecture or design decisions?

- **Open an issue** for discussion
- **Check existing issues** to see if it's already been discussed
- **Review the code**: It's intentionally minimal and readable

## Code of Conduct

Be respectful and constructive. This is a teaching project—questions are welcome, and all skill levels are encouraged to contribute.

## License

By contributing to ParcelFlow, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping improve ParcelFlow!**
