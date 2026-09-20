# Project Assumptions

This document outlines the core technical, architectural, and operational assumptions embedded in the Orb Aggregation Framework (OAF) codebase.

## 1. Execution Environment

- **Python Version:** The codebase assumes execution on Python 3.10 through 3.14. Compatibility with older Python 2 code has been explicitly stripped or refactored during modernization.
- **Operating System:** While mostly OS-agnostic due to Python and Twisted, the `desktopSLED` component (using `wxPython`) makes assumptions about local desktop GUI rendering environments.

## 2. Architecture and Framework

- **Asynchronous Paradigm:** The entire server architecture strictly assumes it runs inside a single-threaded `twisted.internet.reactor` event loop. Blocking operations (like intensive I/O or heavy computation) must be deferred to threads or refactored into async/await (`ensureDeferred`) to avoid freezing the system.
- **Network Protocols:** HTTP communication via Twisted Web is the primary interface.
- **Twisted Web Byte-Strings:** Twisted Web `Resource.render_*` methods and header keys/values are strictly expected to return and accept `bytes` in Python 3. The codebase frequently converts strings using `.encode('utf-8')`.

## 3. Data and Persistence

- **Database ORM:** It is assumed that data persistence is managed via SQLAlchemy 2.0+ using the declarative mapping style (e.g., `Mapped[int]`).
- **Local Storage:** The default `engine` binding assumes a local SQLite database file (`sqlite:///./testdb.db`) for testing and default operational development.
- **Serialization Safety:** We assume remote configuration endpoints and pickled objects communicate via `json` rather than inherently insecure modules like `pickle` or `marshal` to mitigate RCE risks.
- **HTML Safety:** We assume the output of `render_GET` strings containing user-configurable statuses and system names could be vulnerable to XSS and thus must be processed using `html.escape()`.

## 4. Dependencies and Configuration

- **Single Source of Truth:** `pyproject.toml` is the sole source of truth for dependencies, build configurations, test execution environments (`tox`, `pytest`), and linting configs (`ruff`, `pyright`). Legacy `setup.py` scripts are assumed obsolete.
- **Missing Types in External Libraries:** It is assumed that some Twisted constructs lack complete type stubs. Therefore, `# type: ignore` comments are selectively applied where `pyright` checks fail on legacy interfaces that are nonetheless correct at runtime.
- **Future Secrets Management:** Current dummy credentials (e.g., `MAIL_SERVER = ""`) assume future roadmap tasks will replace them with environment variables or external vault configurations.
