# Future Features and Roadmap

This document outlines potential enhancements, logical extensions, and planned features for the Orb Aggregation Framework (OAF).

## 1. Integrations and Notifiers

Currently, OAF aggregates statuses and can output via specific endpoints (e.g., `SLNotifier` or generic `JsonNotifier`). Extending notification channels will make the system more versatile.

- **Modern Webhook Integrations:** Support for posting status changes directly to Slack, Discord, Microsoft Teams, or custom webhooks.
- **Email Alerts Enhancements:** While there are mail monitors (`POP3MailMonitor`, `IMAPMailMonitor`), outbound email notification capabilities could be generalized into standard `Notifier` classes.
- **IoT & Physical Devices:** The framework could natively support more IoT protocols (e.g., MQTT) to trigger physical ambient orbs, smart lights, or displays natively beyond existing generic or Second Life specific methods.

## 2. Modernization & Core Framework

The system is built on Twisted. While significant modernization has already taken place, further improvements can be made.

- **Full `async`/`await` Migration:** Convert remaining explicit `Deferred` chains and `.addCallbacks()` usages into native `async`/`await` syntax wrapped by `ensureDeferred` for cleaner error handling and readability.
- **FastAPI / Starlette Integration:** Investigate if the presentation and API layer could eventually transition to or run alongside a modern ASGI framework (like FastAPI) to leverage auto-generating OpenAPI documentation, while maintaining Twisted's async reactor for background polling.
- **Containerization:** Provide a standard `Dockerfile` and `docker-compose.yml` to simplify deployment and execution in cloud environments.

## 3. Storage and Persistence

The backend storage currently utilizes SQLAlchemy 2.0 with SQLite locally.

- **Time-Series Metrics:** The current model logs history arrays. Expanding the system to support dumping metrics to a time-series database (e.g., InfluxDB, Prometheus) would allow for robust dashboarding using tools like Grafana.
- **Database Migrations:** Introduce Alembic for database migrations as the data models evolve.

## 4. User Interface

The desktop UI (`desktopSLED`) is currently built with `wxPython`.

- **Web-Based Dashboard:** A centralized, reactive web dashboard (e.g., built with React or Vue) to visualize the status of all `OafServer` networks in real-time without relying on a desktop client.
- **Dynamic Configuration UI:** Currently, systems and notifiers are largely instantiated in code (like `main.py`). A web interface to add, edit, and remove monitors dynamically would greatly improve usability.
