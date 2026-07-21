# Contributing to PIA Industrial

Thank you for your interest in contributing to PIA Industrial! This project aims to bring deterministic intelligence and knowledge graphs to heavy industry.

## Development Environment Setup

1. **Prerequisites**
   - Python 3.10+
   - Node.js 18+

2. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/pia-industrial.git
   cd pia-industrial
   ```

3. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

## Branching Conventions

- `main` is the primary branch.
- Feature branches should be named `feature/<feature-name>`.
- Bugfix branches should be named `bugfix/<bug-name>`.

## Commit Expectations

Write clear, descriptive commit messages.
- **Good:** `feat(ingestion): add support for Maximo API v2`
- **Bad:** `fixed stuff`

## Code Style

- Backend: Follow PEP 8 guidelines. Use type hints extensively.
- Frontend: Use TypeScript. Strictly use Vanilla CSS for styling.

## Testing Requirements

All new intelligence rules, parsers, and APIs must have corresponding unit tests in `backend/tests/unit/`.
Run tests locally before opening a pull request:
```bash
python -m pytest tests/
```

## Pull Request Process

1. Ensure your code passes all tests.
2. Update documentation if you added new features.
3. Open a Pull Request against `main`.
4. Wait for review.

## Extending the Platform

- **Adding Domain Entities**: Update the schema in `app/domain/industrial/`.
- **Adding Intelligence Rules**: Add new rules to `app/intelligence/causal/rules/`.
- **Adding Document Adapters**: Create a new parser in `app/ingestion/observation/adapters/`.
- **Adding API Endpoints**: Add routers to `app/api/routers/v1/industrial.py`.

## Documentation Expectations

Ensure that you add accurate docstrings to all public Python classes and functions. Describe the inputs, outputs, exceptions, and the deterministic nature of the algorithms used.
