# oaf

The Oaf Aggregation Framework is a framework for monitoring various systems and
aggregating status information into a single view i.e. is everything ok? It
is designed to support an individual's view of their world and any number of
key inputs to it.

# Key resources - all descendant from resource.Resource

- Systems - Systems represent an input point, something in the real or virtual
  world has developed a status and would like to communicate it to you. They
  provide a simple end-point and get/post interface to accept data. Systems have
  a few basic properties:
  - status - a one word description of the status of the reporting state
    commonly something from \['none', 'ok', 'working', 'success', 'warning',
    'error'\]
  - message - A free-form description of the status
  - color - the color that this system matches to the given status as a rgb
    tuple
  - blink - a blink speed from 0-7
  - level - how important this status is compared to other statuses that
    this system might have
- Notifiers - notifiers expose the state of a system or systems for view. In
  the trivial case this is equivalent to going to read the systems page itself,
  but notifiers can report via other protocols, such as push, pager, or similar.
- Servers - Servers tie together lists of systems and notifiers. Beyond the
  simple repeating function they will process the levels and relative importance
  of the various systems to pick one system that should be the user's greatest
  concern. This is the color, status, blink, and message that is sent to all
  notifiers.
  - SubServers allow the summarization logic to be applied hierarchically,
    serving as servers and systems and thereby supporting notifications for
    designated areas.

## Testing and Development

We use `pytest` and `tox` for testing and verifying the codebase. To install testing dependencies and run the tests:

```bash
# Install development dependencies
pip install .[dev]

# Run the test suite via pytest
pytest tests

# Run all automated checks (tests, linters, formatters) via tox
tox
```
