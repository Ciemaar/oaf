# Orb Aggregation Framework (OAF) - User Guide

The Orb Aggregation Framework (OAF) is a system designed to monitor the status of various components (like websites, servers, or custom metrics) and aggregate that information into a single visual status. It was originally designed to drive physical Ambient Orbs but can also display status via a web interface or a desktop tray icon.

## Core Concepts

Understanding OAF requires knowing a few key terms:

- **System:** A "System" is anything that can be monitored. It has a state (e.g., OK, Error, Working) and a color.
  - *PageMonitor:* Checks if a webpage is accessible.
  - *ProcessMonitor:* Checks if a process is updating within a given timeframe.
  - *CountSystem:* Tracks a number against a threshold.
- **OafServer (SubServer):** A container that holds multiple Systems. It aggregates the status of all its children. If any child System is in an "Error" state, the parent Server will reflect that "Error" state. This allows you to group related monitors.
- **Notifier:** A "Notifier" is an output method for the aggregated status.
  - *OrbNotifier:* Sends the color/status to a physical Ambient Orb.
  - *SLNotifier:* Sends the status to an object in Second Life.
  - *SerialIndyNotifier:* Sends the status to a locally connected Serial LED device.
  - *TrayIcon:* (Via desktopSLED) Displays the status in your desktop's system tray.

## Installation

OAF requires Python 3.10 or higher.

1. Clone the repository or download the source.
1. Install the package:

```bash
pip install .
```

*(Note: If you intend to use the desktop tray application `desktopSLED`, you will also need to install `wxpython`.)*

## Running the Main Server

The core of OAF is the web server that runs the monitors. You can start it using:

```bash
python -m orbLib.main
```

By default, the server will start on port `8585`. You can access the web interface by navigating to:
`http://localhost:8585/oaf`

From this interface, you can see the status of all configured systems and manually acknowledge errors.

### Command Line Arguments

You can specify a custom port by passing it as the first argument:

```bash
python -m orbLib.main 8080
```

## desktopSLED (Desktop Tray Icon)

`desktopSLED` is a companion application that puts a small icon in your system tray, reflecting the current status of your OAF server.

To run it, ensure `wxpython` is installed, then run:

```bash
python -m desktopSLED
```

*(Note: desktopSLED relies on the `src/desktopSLED` module being in your python path. Running it via `python -m desktopSLED` from the root of the repo with the package installed in editable mode is recommended).*

### Configuration

1. Right-click the tray icon and select **Config**.
1. **OAF:** Enter the URL of your OAF server's pickle endpoint (e.g., `http://localhost:8585/oaf`).
1. **Serial Port:** (Optional) If you have a local Serial Indicator connected, enter the COM port (e.g., `COM3` or `/dev/ttyUSB0`).
1. Click **Open** to connect.

## Connecting a Physical Ambient Orb

If you have an Ambient Orb account, you can pass your Device ID as an argument to the server to have it automatically update the orb:

```bash
python -m orbLib.main 8585 YOUR-DEVICE-ID
```
