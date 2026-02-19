# PresenceChecker

A WiFi packet sniffer and presence detection tool for Linux. Captures wireless traffic in monitor mode, detects nearby devices by MAC address and signal strength, and exports data to XML logs for later analysis.

## Features

- **Real-time device detection** via WiFi packet sniffing in monitor mode
- **Automatic channel hopping** across channels 1-13 for full coverage
- **Live terminal UI** showing detected MAC addresses and signal strength (dBm)
- **Configurable ignore list** to filter out known access points or devices
- **XML export** of captured data with timestamps (every 5 seconds)
- **Signal analysis tool** (`Analyzer.py`) with matplotlib graphs and MAC vendor lookup

## Usage

### Capture

```bash
python PresenceChecker.py -i wlan0mon
```

| Flag | Description |
|---|---|
| `-i` / `--interface` | Monitor mode interface (required) |
| `-o` / `--outfolder` | Output folder (default: `~/PresenceCheckerLOG/`) |
| `-il` / `--ignorelist` | XML file with MAC addresses to ignore |
| `-pl` / `--printline` | Number of lines to display (default: 10) |
| `-am` / `--automonitor` | Auto enable/disable monitor mode |

### Analyze

```bash
python Analyzer.py -d ~/PresenceCheckerLOG/ -m 00:11:22:33:44:55
```

Generates a signal strength vs. time graph for the given MAC address, with vendor name lookup via macvendors.co API.

## Project structure

```
PresenceChecker/
├── PresenceChecker.py   # Main sniffer with multi-threaded capture and UI
├── Analyzer.py          # Signal analysis and graph generation
├── ignore.xml           # MAC addresses to exclude from capture
└── Relazione.pdf        # Project report
```

## Dependencies

- Python 2
- `pcapy` - packet capture
- `impacket` - frame decoding (RadioTap, Dot11)
- `reprint` - dynamic terminal output
- `matplotlib` - graph generation
- `requests` - MAC vendor API calls
- A Linux wireless adapter in monitor mode

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
