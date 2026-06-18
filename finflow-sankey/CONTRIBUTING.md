# Contributing to FinFlow Sankey

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository.
2. Clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/finflow-sankey.git finflow-sankey-repo
cd finflow-sankey-repo/finflow-sankey
```

3. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
```

## Development Workflow

1. Create a branch:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes.
3. Run tests and lint:

```bash
python -m pytest tests/ -q
ruff check finflow_sankey tests
mkdocs build
```

4. Update `CHANGELOG.md` under the `[Unreleased]` section.
5. Commit with a clear message.
6. Push and open a pull request.

## Code Style

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.
- Follow Google-style docstrings.
- Keep functions small and focused.
- Prefer Polars over pandas.

## Adding Tests

- Add tests in the `tests/` directory.
- Use pytest.
- Aim to cover both success and edge cases.

## Documentation

- Update `README.md` if you change user-facing behavior.
- Add or update docs in `docs/` for new features.
- API changes should be reflected in `docs/api.md` automatically via `mkdocstrings` if public symbols are documented.

## Reporting Issues

Please use GitHub Issues when filing a bug, feature request, or question.

For general questions and usage help, use [GitHub Discussions](https://github.com/min9lin9/finflow-sankey/discussions).

## Code of Conduct

Be respectful and constructive. We welcome contributors of all experience levels.
