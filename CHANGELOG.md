# Changelog

All notable changes to the Automations project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-08-24

### Added

#### Mouse Movement Script (`move_mouse_pointer.py`)
- **Complete rewrite** using native macOS CoreGraphics framework
- **Enhanced reliability** - removed pyautogui dependency that had compatibility issues
- **Intelligent mouse movement** - moves mouse slightly after configurable idle period (default: 10 seconds)
- **Screen boundary detection** - ensures mouse stays within visible screen area
- **Graceful error handling** - proper exception handling and user feedback
- **Keyboard interrupt support** - clean exit with Ctrl+C
- **Executable permissions** - script can be run directly with `./move_mouse_pointer.py`
- **Detailed logging** - shows current position, movements, and status updates
- **Cross-platform detection** - validates macOS environment before execution

#### Internet Connection Monitor (`internet_dropoff.py`)
- **Complete transformation** from basic ping checker to enterprise-grade monitoring solution
- **Multi-server monitoring** - monitors Google DNS (8.8.8.8), Cloudflare (1.1.1.1), and OpenDNS (208.67.222.222)
- **Comprehensive logging system**:
  - File logging with timestamps (`internet_connectivity.log`)
  - JSON statistics export (`internet_stats.json`)
  - Real-time console output with status updates
- **Advanced statistics tracking**:
  - Uptime percentage calculations
  - Downtime period tracking with duration analysis
  - Response time statistics (min/max/average/median)
  - Connection failure counting and analysis
- **Configurable monitoring parameters**:
  - JSON configuration file (`internet_monitor_config.json`)
  - Adjustable check intervals, timeouts, and thresholds
  - Customizable alert sensitivity
- **Professional reporting**:
  - Detailed summary reports with uptime statistics
  - Historical downtime analysis
  - Response time performance metrics
- **Command-line interface**:
  - `--help` - Show usage information
  - `--stats` - Display current statistics
  - `--config` - Show current configuration
- **Graceful shutdown** - generates final report on exit with Ctrl+C
- **Signal handling** - proper cleanup on termination

#### Internet Speed Test Tool (`internet_speed_test.py`)
- **Complete overhaul** from basic speed checker to comprehensive testing suite
- **Historical tracking system**:
  - JSON-based test history storage (`speed_test_history.json`)
  - Long-term performance trend analysis
  - Statistical summaries of past tests
- **Multiple testing methods**:
  - Primary: speedtest-py library integration
  - Fallback: speedtest-cli command-line tool
  - Automatic fallback on library unavailability
- **Comprehensive ping analysis**:
  - Detailed latency measurements (min/avg/max)
  - Jitter calculation and reporting
  - Packet loss detection and analysis
  - Multi-ping sampling for accuracy
- **Advanced server selection**:
  - Automatic best server selection
  - Server information display (sponsor, location, distance)
  - Configurable server preferences
- **Flexible unit conversion**:
  - Support for Mbps, Kbps, and Gbps
  - User-configurable preferred units
- **Alert system**:
  - Configurable speed and latency thresholds
  - Automatic performance alerts
  - Below-threshold warnings
- **Multiple test modes**:
  - `--quick` - Fast test without detailed ping analysis
  - `--multiple N` - Run N consecutive tests with summary
  - `--stats` - Historical statistics only
  - `--config` - Configuration display
- **Professional output formatting**:
  - Detailed test results with server information
  - Multi-test summaries with statistical analysis
  - Progress indicators during testing
- **Error handling and recovery**:
  - Graceful handling of network failures
  - Test interruption recovery
  - Partial result saving

### Fixed

#### Mouse Movement Script
- **Resolved pyautogui compatibility issues** on macOS systems
- **Fixed infinite loop** without sleep that consumed excessive CPU
- **Corrected mouse position detection** using native macOS APIs
- **Improved error messages** for accessibility permission requirements

#### Internet Connection Monitor
- **Fixed missing sleep statement** that caused 100% CPU usage
- **Resolved basic connectivity detection** limitations
- **Improved ping parsing** for accurate response time extraction
- **Enhanced error handling** for network failures

#### Internet Speed Test Tool
- **Added missing error handling** for network failures
- **Fixed basic output formatting** issues
- **Resolved dependency management** with fallback options
- **Improved test reliability** with timeout handling

### Changed

#### Overall Project Structure
- **Enhanced code organization** with proper class-based architecture
- **Improved documentation** with comprehensive docstrings
- **Professional code formatting** and style consistency
- **Added type hints** for better code maintainability

#### Configuration Management
- **Implemented JSON-based configuration** for all scripts
- **Added default configuration creation** for first-time users
- **Configurable parameters** for customization without code changes

#### Logging and Monitoring
- **Centralized logging systems** with file and console output
- **Structured data storage** using JSON formats
- **Historical data preservation** across script executions

### Security

#### Access Control
- **Proper permission handling** for macOS system access
- **Secure file operations** with error handling
- **Safe subprocess execution** with timeout protections

#### Data Privacy
- **Local data storage** - all logs and statistics stored locally
- **No external data transmission** beyond necessary speed tests
- **User-controlled data retention** and configuration

### Technical Improvements

#### Performance
- **Reduced CPU usage** through proper sleep intervals
- **Optimized network operations** with configurable timeouts
- **Efficient data structures** for historical tracking
- **Memory-conscious data handling** for long-running processes

#### Reliability
- **Robust error handling** throughout all scripts
- **Graceful degradation** when services are unavailable
- **Automatic recovery** from transient failures
- **Signal handling** for clean shutdowns

#### Maintainability
- **Modular code structure** with clear separation of concerns
- **Comprehensive documentation** for all functions and classes
- **Consistent coding standards** across all files
- **Easy configuration** through external files

## [1.0.0] - Previous Version (Original Scripts)

### Initial Implementation
- Basic mouse movement script using pyautogui
- Simple internet connectivity ping checker
- Basic speed test using speedtest library
- Minimal error handling and logging
- No configuration management
- No historical tracking or statistics

---

## Migration Guide

### For Existing Users

If you were using the previous versions of these scripts:

1. **Mouse Movement**: The new version requires macOS accessibility permissions. Grant permission to Terminal or your Python executable in System Preferences > Security & Privacy > Accessibility.

2. **Internet Monitoring**: The new version creates configuration and log files. Your monitoring will be more comprehensive but may require adjusting default settings.

3. **Speed Testing**: The enhanced version maintains test history. Your previous test results won't be imported, but all future tests will be tracked.

### Configuration Files

The enhanced scripts create several configuration and data files:

- `internet_monitor_config.json` - Internet monitoring settings
- `speed_test_config.json` - Speed test preferences
- `internet_connectivity.log` - Connection monitoring log
- `internet_stats.json` - Connection statistics
- `speed_test_history.json` - Historical speed test results

### Dependencies

Install required dependencies:

```bash
# For enhanced speed testing (optional - CLI fallback available)
pip install speedtest-cli

# All other functionality uses only Python standard library
```

---

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/bhuiyanmobasshir94/automations).