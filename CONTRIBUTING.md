# Contributing to baleio

Thanks for your interest in improving **baleio**! 🎉

## Getting started

```bash
git clone https://github.com/ehsndvr/baleio && cd baleio
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Guidelines

- **Match the surrounding style.** baleio mirrors aiogram's public API where it makes
  sense; keep naming and patterns consistent with existing code.
- **Type everything.** All public functions are type-annotated (Pydantic v2 models for
  API objects).
- **Add tests.** New behaviour needs coverage in `tests/`. Tests run fully offline via
  the `FakeSession` fixture — no network or real bot token required.
- **Keep it async-first.** The whole framework runs on `asyncio` / `aiohttp`.
- **Document public API.** Update the relevant page under `docs/` and, if user-facing,
  both `README.md` and `README.fa.md`.

## Running the docs locally

```bash
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
# open docs/_build/html/index.html
```

## Pull requests

1. Fork and create a feature branch.
2. Make your change with tests and docs.
3. Ensure `pytest` passes.
4. Open a PR describing the change and linking any related issue.

## Reporting bugs

Open an issue with a minimal reproduction, the traceback, and your Python / baleio
versions. For API mismatches with Bale, include the method name and the raw request /
response if possible (redact your token!).

By contributing, you agree that your contributions are licensed under the MIT License.
