# Copilot Instructions for Orb Aggregation Framework (OAF)

This repository contains the source code for the Orb Aggregation Framework, a Python-based system for monitoring and aggregating system statuses.

## Tech Stack
- **Python Version:** 3.10+ (Targeting 3.13)
- **Networking:** `twisted` (Asynchronous networking)
- **Database:** `sqlalchemy` 2.0+ (Declarative mapping)
- **Testing:** `pytest` (legacy tests migrated from `twisted.trial`)
- **Linting:** `ruff`
- **Type Checking:** `pyright`

## Project Structure
This project follows a standard `src` layout:
- `src/orbLib`: Core logic.
- `src/db`: Database models.
- `src/desktopSLED`: wxPython GUI code.
- `tests/`: Unit tests.

## Coding Guidelines

### General
- Use modern Python 3.10+ syntax.
- Prefer `pathlib` over `os.path`.
- Ensure all new dependencies are added to `pyproject.toml`.

### Twisted & Async
- When working with Twisted Web resources (`render_GET`, etc.), ensure methods return `bytes`, not `str`. Encode strings using `.encode('utf-8')`.
- Use `twisted.web.client.Agent` for HTTP requests instead of the deprecated `client.getPage`.
- Be mindful of reactor management in tests. Use `pytest` fixtures where possible, but respect existing `twisted.trial` patterns if modifying legacy tests.

### Database (SQLAlchemy)
- Use SQLAlchemy 2.0 declarative style (`DeclarativeBase`, `Mapped`, `mapped_column`).
- Avoid legacy imperative mapping (`mapper()`).
- Use `Session.scalars(select(...))` for queries.

### Testing
- Write tests using `pytest` style.
- When testing Twisted code, use `twisted.web.test.requesthelper.DummyRequest` for mocking web requests.
- Ensure `LoopingCall` tasks are stopped in `tearDown` or fixtures to prevent dirty reactor errors.

### Type Hinting
- Add type hints to new code.
- Run `pyright` to verify types.
