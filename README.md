# Automations

A collection of enhanced automation scripts for system monitoring and maintenance.

## 📋 Features

### 🖱️ Mouse Movement (`move_mouse_pointer.py`)
- **Prevents screen lock** by moving mouse during idle periods
- **Native macOS integration** using CoreGraphics framework
- **Smart boundary detection** keeps cursor within screen limits
- **Configurable idle threshold** (default: 10 seconds)
- **Graceful shutdown** with Ctrl+C support

### 🌐 Internet Connection Monitor (`internet_dropoff.py`)
- **Multi-server monitoring** (Google DNS, Cloudflare, OpenDNS)
- **Comprehensive logging** with file and console output
- **Historical statistics** tracking uptime and response times
- **Configurable thresholds** and monitoring intervals
- **Professional reporting** with downtime analysis
- **JSON configuration** for easy customization

### ⚡ Internet Speed Test (`internet_speed_test.py`)
- **Historical tracking** of all speed tests
- **Multiple test methods** with automatic fallback
- **Detailed ping analysis** including jitter and packet loss
- **Flexible output units** (Mbps, Kbps, Gbps)
- **Alert system** for performance thresholds
- **Multiple test modes** (quick, multiple, statistics)
- **Server information** with distance and latency details

## 🚀 Quick Start

### Prerequisites
- macOS (for mouse movement script)
- Python 3.7+
- Optional: `speedtest-cli` for enhanced speed testing

### Installation
```bash
# Clone the repository
git clone https://github.com/bhuiyanmobasshir94/automations.git
cd automations

# Make scripts executable
chmod +x *.py

# Install optional dependencies
pip install speedtest-cli
```

### Usage

#### Mouse Movement
```bash
# Start mouse movement prevention
./move_mouse_pointer.py

# Or with Python
python move_mouse_pointer.py
```

#### Internet Monitoring
```bash
# Start continuous monitoring
./internet_dropoff.py

# Show current statistics
./internet_dropoff.py --stats

# View configuration
./internet_dropoff.py --config
```

#### Speed Testing
```bash
# Run single speed test
./internet_speed_test.py

# Quick test (no ping analysis)
./internet_speed_test.py --quick

# Run multiple tests
./internet_speed_test.py --multiple 3

# View historical statistics
./internet_speed_test.py --stats
```

## 🔧 Configuration

All scripts support JSON-based configuration files:

- `internet_monitor_config.json` - Internet monitoring settings
- `speed_test_config.json` - Speed test preferences

Configuration files are automatically created with sensible defaults on first run.

## 📊 Data Storage

Scripts maintain their data in local JSON files:

- `internet_connectivity.log` - Connection monitoring log
- `internet_stats.json` - Connection statistics
- `speed_test_history.json` - Historical speed test results

## 🛠️ Advanced Features

### Internet Monitoring
- **Multiple server redundancy** for accurate connectivity detection
- **Configurable alert thresholds** for response time monitoring
- **Statistical analysis** of connection quality over time
- **Uptime percentage tracking** with detailed breakdown

### Speed Testing
- **Automatic server selection** for optimal testing conditions
- **Comprehensive ping analysis** with packet loss detection
- **Historical trend analysis** for performance monitoring
- **Customizable alert thresholds** for speed and latency

### Mouse Movement
- **Native system integration** for reliable operation
- **Screen boundary respect** prevents cursor from disappearing
- **Minimal resource usage** with efficient timing
- **Accessibility permission handling** with clear instructions

## 🔒 Privacy & Security

- **Local data storage** - all logs and statistics remain on your device
- **No external dependencies** for core functionality
- **Minimal network usage** - only for necessary connectivity tests
- **Open source** - full transparency of operations

## 🆘 Troubleshooting

### Mouse Movement Issues
If the mouse movement script fails:
1. Grant accessibility permissions: System Preferences > Security & Privacy > Accessibility
2. Add Terminal or Python to the allowed applications list

### Speed Test Dependencies
If speed tests fail:
```bash
# Install speedtest-cli as fallback
pip install speedtest-cli

# Or use system package manager
brew install speedtest-cli  # macOS with Homebrew
```

### Internet Monitoring
For connectivity monitoring issues:
- Check firewall settings for ping permissions
- Verify DNS resolution is working
- Review configuration file for correct server addresses

## 📈 Statistics and Reporting

All scripts provide detailed statistics and reporting:

### Internet Monitoring Reports
- Uptime percentage calculations
- Average response times
- Downtime period analysis
- Connection failure tracking

### Speed Test Analytics
- Historical speed trends
- Performance comparisons over time
- Server selection statistics
- Alert threshold monitoring

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
```bash
# Clone and enter directory
git clone https://github.com/bhuiyanmobasshir94/automations.git
cd automations

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install development dependencies
pip install -r requirements.txt  # if available
```

## 📝 License

This project is open source. See [CHANGELOG.md](CHANGELOG.md) for version history and detailed change information.

## 🔗 Links

- [Repository](https://github.com/bhuiyanmobasshir94/automations)
- [Issues](https://github.com/bhuiyanmobasshir94/automations/issues)
- [Changelog](CHANGELOG.md)

---

**Note**: These scripts are designed for macOS. Windows and Linux compatibility may require modifications.