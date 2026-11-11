# Tooling Evaluation

As part of the modernization of the Orb Aggregation Framework (OAF), we evaluated several tools across different categories to ensure a modern, robust, and maintainable developer experience.

## Formatting & Linting

### Selected Tool: `ruff`

- **Evaluation:** `ruff` is an extremely fast Python linter and formatter written in Rust. It serves as a drop-in replacement for `flake8` (and its dozens of plugins), `isort`, and `black`.
- **Suitability for OAF:** Excellent. Its speed is unmatched. More importantly, its configuration via `pyproject.toml` is centralized and easy to manage. Given OAF's legacy roots (specifically its adherence to Twisted's `camelCase` naming conventions which violate PEP 8), `ruff`'s granular rule selection allowed us to easily disable specific PEP 8 naming checks (`N802`, `N815`, etc.) while keeping all other critical checks enabled.
- **Alternatives Considered:** `black` + `flake8` + `isort`. Rejected due to slower execution, distributed configuration, and generally being superseded by `ruff` in modern setups.

## Type Checking

### Selected Tool: `pyright`

- **Evaluation:** `pyright` (by Microsoft) is a fast static type checker.
- **Suitability for OAF:** Very Good. We evaluated both `mypy` and `pyright` against this legacy Twisted codebase. `mypy` struggled significantly with the namespace package structure and circular imports inherent in some of the legacy `wxPython` GUI code (`desktopSLED`), requiring extensive stubbing to even run a basic pass. `pyright`, when run in `basic` mode, was much more forgiving of the legacy structure while still catching genuine type mismatches (like passing `str` instead of `bytes` to Twisted Web methods).

## Testing & Task Runner

### Selected Tools: `pytest` and `tox`

- **Evaluation:**
  - `pytest` is the undisputed standard for Python testing. We successfully migrated legacy `twisted.trial` tests to run under `pytest`, allowing us to use `pytest-cov` to enforce a strict minimum test coverage baseline (`--cov-fail-under`).
  - `tox` is a virtual environment management and test command line tool.
- **Suitability for OAF:** Excellent. `tox` handles the matrix testing (`py310`, `py311`, `py312`, `py313`, `py314`) and orchestrates our linting and formatting environments effortlessly.
- **Alternatives Considered:** `nox`. `nox` uses Python scripts instead of `.ini` syntax for configuration. While powerful, `tox`'s legacy `.ini` format within `pyproject.toml` is concise and perfectly adequate for our needs.

## Documentation

### Selected Tool: `MkDocs` (with `mkdocs-material` theme)

- **Evaluation:** `MkDocs` is a fast, simple static site generator geared towards building project documentation from Markdown files.
- **Suitability for OAF:** Excellent. Previously, documentation existed as disjointed Markdown files in the repo. `MkDocs` allows us to compile these (`user_guide.md`, `developer_guide.md`, `tooling_evaluation.md`) into a cohesive, searchable, and highly readable static site. We chose the `mkdocs-material` theme as it is the industry standard for beautiful MkDocs sites.
- **Alternatives Considered:** `Sphinx`. Sphinx is incredibly powerful but relies heavily on reStructuredText (`.rst`) and is arguably overkill for a project of this scale that is already using Markdown.

## Markdown Formatting

### Selected Tool: `mdformat`

- **Evaluation:** An opinionated Markdown formatter.
- **Suitability for OAF:** Excellent. We integrated it into our `tox` linting pipeline to ensure all documentation (including our new MkDocs files) is uniformly formatted across all PRs.
