# Developer Guide - Orb Aggregation Framework

This document outlines the architecture, development setup, and contribution guidelines for the Orb Aggregation Framework.

## Architecture Overview

OAF is built on top of the **Twisted** framework. Twisted provides the asynchronous event loop (reactor) that allows OAF to continuously check remote systems, serve web pages, and push notifications without blocking.

### Core Components

- **`src/orbLib/OaF.py`**: The heart of the system. Contains the base classes:
  - `System`: A Twisted Web `Resource` representing a single monitor. It handles its own status and HTML rendering.
  - `OafServer`: A collection of `System`s. It calculates the aggregated status (highest severity wins) and pushes that state to `Notifier`s.
  - `Notifier`: An abstract class for outputting the aggregated state.
  - `Monitor`: A subclass of `System` that uses `twisted.internet.task.LoopingCall` to perform periodic checks.
- **`src/db/`**: Handles database persistence using **SQLAlchemy 2.0** Declarative mapping. It stores configurations for users and their specific OAF setups.
- **`src/desktopSLED/`**: A GUI client built with **wxPython**. It uses a `PickledSystem` to regularly pull the state from a remote OAF server and displays it in the system tray.

## Development Setup

We use modern Python tooling for dependency management, testing, and linting.

### 1. Environment Setup

It is recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the project with development dependencies:

```bash
pip install -e .[dev]
```

### 2. Tooling

- **Testing**: We use `pytest`. The tests themselves still inherit from `twisted.trial.unittest.TestCase` to utilize Twisted's testing utilities.
- **Linting & Formatting**: We use `ruff`.
- **Type Checking**: We use `pyright` (configured in "basic" mode to accommodate the legacy nature of some Twisted code).
- **Markdown Formatting**: We use `mdformat`.

### 3. Running Checks Locally

The easiest way to ensure your code is ready for a Pull Request is to use `tox`, which orchestrates all the tools in isolated environments.

```bash
# Run tests across available python versions
tox

# Run linters and format checkers
tox -e lint

# Apply formatting automatically
tox -e format
```

## Adding a New System Type

To add a new type of monitor:

1. Inherit from `orbLib.OaF.System` (or `Monitor` if it needs to poll).
1. If inheriting from `Monitor`, implement the `checkSystem(self)` method. This method should execute the check (preferably asynchronously, returning a Deferred) and update `self.status`, `self.message`, and `self.level`.
1. Call `self.oaf.statusChange(self)` when the status changes to trigger a re-calculation of the aggregate state.

Example:

```python
from twisted.internet import defer
from orbLib.OaF import Monitor, INFO, ERROR

class MyCustomMonitor(Monitor):
    def __init__(self, name, interval=60):
        super().__init__(name, interval)

    def checkSystem(self):
        # Do some async check...
        d = self.perform_check()
        d.addCallbacks(self._success, self._failure)

    def _success(self, result):
        self.status = "ok"
        self.level = INFO
        self.oaf.statusChange(self)

    def _failure(self, err):
        self.status = "error"
        self.level = ERROR
        self.message = str(err)
        self.oaf.statusChange(self)
```

## Important Considerations

- **Twisted Web Rendering**: In Python 3, Twisted Web `render_*` methods **must** return `bytes`. Ensure you encode your HTML strings using `.encode('utf-8')`.
- **Reactor Cleanup in Tests**: If your code uses `LoopingCall` or `callLater`, you must ensure these are stopped/cancelled during test teardown. Failure to do so will result in a `DirtyReactorAggregateError` in `trial`/`pytest`. See `tests/test_SLOaf.py` for examples of cleaning up `LoopingCall`s.
