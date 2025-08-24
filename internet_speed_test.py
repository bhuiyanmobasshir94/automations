#!/usr/bin/env python3
"""
Enhanced Internet Speed Test Tool
Comprehensive speed testing with historical tracking, multiple servers, and detailed analysis.
"""
import json
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from statistics import mean, median
from typing import Dict, List, Optional, Tuple
import signal

try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    SPEEDTEST_AVAILABLE = False

class SpeedTester:
    def __init__(self, config_file: str = "speed_test_config.json"):
        self.config_file = config_file
        self.load_config()
        self.test_history: List[Dict] = []
        self.load_history()
        self.setup_signal_handlers()
        
    def load_config(self):
        """Load configuration from file or create default config."""
        default_config = {
            "history_file": "speed_test_history.json",
            "log_file": "speed_test.log",
            "test_servers": [],  # Empty means auto-select best servers
            "test_count": 1,
            "include_ping": True,
            "include_jitter": True,
            "timeout_seconds": 60,
            "preferred_units": "Mbps",  # Mbps, Kbps, Gbps
            "save_detailed_results": True,
            "alert_thresholds": {
                "min_download_mbps": 10.0,
                "min_upload_mbps": 1.0,
                "max_ping_ms": 100.0
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config = {**default_config, **loaded_config}
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            self.config = default_config
            
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def load_history(self):
        """Load test history from file."""
        try:
            if os.path.exists(self.config["history_file"]):
                with open(self.config["history_file"], 'r') as f:
                    self.test_history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.test_history = []
            
    def save_history(self):
        """Save test history to file."""
        try:
            with open(self.config["history_file"], 'w') as f:
                json.dump(self.test_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
            
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nTest interrupted. Saving partial results...")
        self.save_history()
        sys.exit(0)
        
    def convert_speed(self, speed_bps: float) -> Tuple[float, str]:
        """Convert speed from bps to preferred units."""
        unit = self.config["preferred_units"]
        if unit == "Kbps":
            return speed_bps / 1000, "Kbps"
        elif unit == "Gbps":
            return speed_bps / 1_000_000_000, "Gbps"
        else:  # Default to Mbps
            return speed_bps / 1_000_000, "Mbps"
            
    def ping_test(self, target: str = "8.8.8.8", count: int = 10) -> Optional[Dict]:
        """Perform ping test for latency and packet loss."""
        try:
            cmd = ["ping", "-c", str(count), target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                
                # Extract ping times
                ping_times = []
                for line in lines:
                    if "time=" in line:
                        time_str = line.split("time=")[1].split(" ")[0]
                        ping_times.append(float(time_str))
                
                # Extract packet loss
                packet_loss = 0
                for line in lines:
                    if "packet loss" in line:
                        loss_str = line.split("%")[0].split()[-1]
                        packet_loss = float(loss_str)
                        break
                
                if ping_times:
                    return {
                        "target": target,
                        "packet_loss_percent": packet_loss,
                        "min_ms": min(ping_times),
                        "max_ms": max(ping_times),
                        "avg_ms": mean(ping_times),
                        "median_ms": median(ping_times),
                        "jitter_ms": max(ping_times) - min(ping_times),
                        "ping_count": len(ping_times)
                    }
        except Exception as e:
            print(f"Ping test failed: {e}")
            
        return None
        
    def speedtest_cli_fallback(self) -> Optional[Dict]:
        """Fallback speed test using speedtest-cli command."""
        try:
            print("Using speedtest-cli as fallback...")
            cmd = ["speedtest-cli", "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config["timeout_seconds"])
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "download_bps": data.get("download", 0),
                    "upload_bps": data.get("upload", 0),
                    "ping_ms": data.get("ping", 0),
                    "server": data.get("server", {}),
                    "client": data.get("client", {}),
                    "method": "speedtest-cli"
                }
        except Exception as e:
            print(f"speedtest-cli fallback failed: {e}")
            
        return None
        
    def run_speedtest_py(self) -> Optional[Dict]:
        """Run speed test using speedtest-py library."""
        if not SPEEDTEST_AVAILABLE:
            return None
            
        try:
            print("Initializing speedtest...")
            st = speedtest.Speedtest()
            
            # Get server list and select best server
            print("Getting server list...")
            if self.config["test_servers"]:
                st.get_servers(self.config["test_servers"])
            else:
                st.get_servers()
                
            print("Selecting best server...")
            st.get_best_server()
            
            server_info = st.best
            print(f"Using server: {server_info['sponsor']} in {server_info['name']}, {server_info['country']}")
            print(f"Server distance: {server_info['d']:.1f} km")
            
            # Run tests
            print("Testing download speed...")
            download_speed = st.download()
            
            print("Testing upload speed...")
            upload_speed = st.upload()
            
            # Get ping if available
            ping_ms = getattr(st.best, 'latency', 0) if hasattr(st.best, 'latency') else 0
            
            return {
                "download_bps": download_speed,
                "upload_bps": upload_speed,
                "ping_ms": ping_ms,
                "server": {
                    "id": server_info['id'],
                    "sponsor": server_info['sponsor'],
                    "name": server_info['name'],
                    "country": server_info['country'],
                    "distance_km": server_info['d'],
                    "latency_ms": server_info.get('latency', 0)
                },
                "method": "speedtest-py"
            }
            
        except Exception as e:
            print(f"speedtest-py failed: {e}")
            return None
            
    def run_single_test(self) -> Optional[Dict]:
        """Run a single comprehensive speed test."""
        test_start = datetime.now()
        print(f"\n{'='*60}")
        print(f"Starting speed test at {test_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Try speedtest-py first, then fallback to CLI
        speed_result = self.run_speedtest_py()
        if not speed_result:
            speed_result = self.speedtest_cli_fallback()
            
        if not speed_result:
            print("All speed test methods failed!")
            return None
            
        # Run ping test if enabled
        ping_result = None
        if self.config["include_ping"]:
            print("\nRunning ping test...")
            ping_result = self.ping_test()
            
        # Compile results
        test_end = datetime.now()
        duration = (test_end - test_start).total_seconds()
        
        # Convert speeds to preferred units
        download_speed, speed_unit = self.convert_speed(speed_result["download_bps"])
        upload_speed, _ = self.convert_speed(speed_result["upload_bps"])
        
        result = {
            "timestamp": test_start.isoformat(),
            "duration_seconds": duration,
            "download_bps": speed_result["download_bps"],
            "upload_bps": speed_result["upload_bps"],
            "download_speed": download_speed,
            "upload_speed": upload_speed,
            "speed_unit": speed_unit,
            "ping_ms": speed_result.get("ping_ms", 0),
            "server": speed_result.get("server", {}),
            "method": speed_result.get("method", "unknown")
        }
        
        if ping_result:
            result["ping_test"] = ping_result
            
        # Check against thresholds
        alerts = []
        thresholds = self.config["alert_thresholds"]
        
        if speed_unit == "Mbps":
            if download_speed < thresholds["min_download_mbps"]:
                alerts.append(f"Download speed ({download_speed:.2f} Mbps) below threshold ({thresholds['min_download_mbps']} Mbps)")
            if upload_speed < thresholds["min_upload_mbps"]:
                alerts.append(f"Upload speed ({upload_speed:.2f} Mbps) below threshold ({thresholds['min_upload_mbps']} Mbps)")
                
        ping_to_check = ping_result["avg_ms"] if ping_result else result["ping_ms"]
        if ping_to_check > thresholds["max_ping_ms"]:
            alerts.append(f"Ping ({ping_to_check:.1f} ms) above threshold ({thresholds['max_ping_ms']} ms)")
            
        result["alerts"] = alerts
        
        return result
        
    def print_test_result(self, result: Dict):
        """Print formatted test result."""
        print(f"\n{'='*60}")
        print("SPEED TEST RESULTS")
        print(f"{'='*60}")
        print(f"Date/Time: {result['timestamp']}")
        print(f"Test Duration: {result['duration_seconds']:.1f} seconds")
        print(f"Test Method: {result['method']}")
        
        if result.get('server'):
            server = result['server']
            if isinstance(server, dict) and server.get('sponsor'):
                print(f"Server: {server['sponsor']} ({server.get('name', 'N/A')}, {server.get('country', 'N/A')})")
                if server.get('distance_km'):
                    print(f"Distance: {server['distance_km']:.1f} km")
        
        print(f"\nDownload: {result['download_speed']:.2f} {result['speed_unit']}")
        print(f"Upload: {result['upload_speed']:.2f} {result['speed_unit']}")
        
        if result['ping_ms'] > 0:
            print(f"Ping: {result['ping_ms']:.1f} ms")
            
        if result.get('ping_test'):
            ping = result['ping_test']
            print(f"\nDetailed Ping Analysis:")
            print(f"  Target: {ping['target']}")
            print(f"  Packet Loss: {ping['packet_loss_percent']:.1f}%")
            print(f"  Min/Avg/Max: {ping['min_ms']:.1f}/{ping['avg_ms']:.1f}/{ping['max_ms']:.1f} ms")
            print(f"  Jitter: {ping['jitter_ms']:.1f} ms")
            
        if result.get('alerts'):
            print(f"\n⚠️  ALERTS:")
            for alert in result['alerts']:
                print(f"  • {alert}")
                
    def generate_stats(self) -> Dict:
        """Generate historical statistics."""
        if not self.test_history:
            return {}
            
        # Filter recent tests (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_tests = [
            test for test in self.test_history 
            if datetime.fromisoformat(test['timestamp']) > thirty_days_ago
        ]
        
        if not recent_tests:
            recent_tests = self.test_history[-10:] if len(self.test_history) > 10 else self.test_history
            
        download_speeds = [test['download_speed'] for test in recent_tests]
        upload_speeds = [test['upload_speed'] for test in recent_tests]
        ping_times = [test['ping_ms'] for test in recent_tests if test['ping_ms'] > 0]
        
        stats = {
            "total_tests": len(self.test_history),
            "recent_tests_count": len(recent_tests),
            "speed_unit": recent_tests[0]['speed_unit'] if recent_tests else "Mbps",
            "first_test": self.test_history[0]['timestamp'] if self.test_history else None,
            "last_test": self.test_history[-1]['timestamp'] if self.test_history else None,
        }
        
        if download_speeds:
            stats.update({
                "download_stats": {
                    "average": round(mean(download_speeds), 2),
                    "median": round(median(download_speeds), 2),
                    "min": round(min(download_speeds), 2),
                    "max": round(max(download_speeds), 2)
                }
            })
            
        if upload_speeds:
            stats.update({
                "upload_stats": {
                    "average": round(mean(upload_speeds), 2),
                    "median": round(median(upload_speeds), 2),
                    "min": round(min(upload_speeds), 2),
                    "max": round(max(upload_speeds), 2)
                }
            })
            
        if ping_times:
            stats.update({
                "ping_stats": {
                    "average": round(mean(ping_times), 2),
                    "median": round(median(ping_times), 2),
                    "min": round(min(ping_times), 2),
                    "max": round(max(ping_times), 2)
                }
            })
            
        return stats
        
    def print_stats(self):
        """Print historical statistics."""
        stats = self.generate_stats()
        if not stats:
            print("No test history available.")
            return
            
        print(f"\n{'='*60}")
        print("SPEED TEST STATISTICS")
        print(f"{'='*60}")
        print(f"Total tests: {stats['total_tests']}")
        print(f"Recent tests (30 days): {stats['recent_tests_count']}")
        
        if stats.get('first_test'):
            print(f"First test: {stats['first_test']}")
        if stats.get('last_test'):
            print(f"Last test: {stats['last_test']}")
            
        unit = stats.get('speed_unit', 'Mbps')
        
        if stats.get('download_stats'):
            dl = stats['download_stats']
            print(f"\nDownload Speed ({unit}):")
            print(f"  Average: {dl['average']} | Median: {dl['median']}")
            print(f"  Range: {dl['min']} - {dl['max']}")
            
        if stats.get('upload_stats'):
            ul = stats['upload_stats']
            print(f"\nUpload Speed ({unit}):")
            print(f"  Average: {ul['average']} | Median: {ul['median']}")
            print(f"  Range: {ul['min']} - {ul['max']}")
            
        if stats.get('ping_stats'):
            ping = stats['ping_stats']
            print(f"\nPing (ms):")
            print(f"  Average: {ping['average']} | Median: {ping['median']}")
            print(f"  Range: {ping['min']} - {ping['max']}")
            
    def run_multiple_tests(self, count: int):
        """Run multiple speed tests and show summary."""
        results = []
        
        for i in range(count):
            print(f"\n{'='*20} Test {i+1} of {count} {'='*20}")
            result = self.run_single_test()
            
            if result:
                self.print_test_result(result)
                results.append(result)
                self.test_history.append(result)
                self.save_history()
                
                if i < count - 1:
                    print(f"\nWaiting 10 seconds before next test...")
                    time.sleep(10)
            else:
                print(f"Test {i+1} failed!")
                
        # Show summary if multiple tests
        if len(results) > 1:
            self.print_multi_test_summary(results)
            
        return results
        
    def print_multi_test_summary(self, results: List[Dict]):
        """Print summary of multiple test results."""
        download_speeds = [r['download_speed'] for r in results]
        upload_speeds = [r['upload_speed'] for r in results]
        ping_times = [r['ping_ms'] for r in results if r['ping_ms'] > 0]
        
        unit = results[0]['speed_unit']
        
        print(f"\n{'='*60}")
        print(f"SUMMARY OF {len(results)} TESTS")
        print(f"{'='*60}")
        
        print(f"Download Speed ({unit}):")
        print(f"  Average: {mean(download_speeds):.2f} | Best: {max(download_speeds):.2f} | Worst: {min(download_speeds):.2f}")
        
        print(f"Upload Speed ({unit}):")
        print(f"  Average: {mean(upload_speeds):.2f} | Best: {max(upload_speeds):.2f} | Worst: {min(upload_speeds):.2f}")
        
        if ping_times:
            print(f"Ping (ms):")
            print(f"  Average: {mean(ping_times):.1f} | Best: {min(ping_times):.1f} | Worst: {max(ping_times):.1f}")

def main():
    """Main function with command line argument handling."""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Enhanced Internet Speed Test Tool")
            print("Usage: python internet_speed_test.py [options]")
            print("  -h, --help       Show this help message")
            print("  -s, --stats      Show historical statistics only")
            print("  -c, --config     Show current configuration")
            print("  -m, --multiple N Run N speed tests")
            print("  -q, --quick      Quick test (no ping analysis)")
            return
        elif sys.argv[1] in ['-s', '--stats']:
            tester = SpeedTester()
            tester.print_stats()
            return
        elif sys.argv[1] in ['-c', '--config']:
            tester = SpeedTester()
            print("Current configuration:")
            print(json.dumps(tester.config, indent=2))
            return
        elif sys.argv[1] in ['-m', '--multiple']:
            if len(sys.argv) > 2:
                try:
                    count = int(sys.argv[2])
                    tester = SpeedTester()
                    tester.run_multiple_tests(count)
                    return
                except ValueError:
                    print("Invalid number for multiple tests")
                    return
            else:
                print("Please specify number of tests")
                return
        elif sys.argv[1] in ['-q', '--quick']:
            tester = SpeedTester()
            tester.config["include_ping"] = False
            result = tester.run_single_test()
            if result:
                tester.print_test_result(result)
                tester.test_history.append(result)
                tester.save_history()
            return
    
    # Check dependencies
    if not SPEEDTEST_AVAILABLE:
        print("Warning: speedtest-py library not found. Install with: pip install speedtest-cli")
        print("Attempting to use speedtest-cli command as fallback...\n")
    
    # Default: run single test
    tester = SpeedTester()
    result = tester.run_single_test()
    
    if result:
        tester.print_test_result(result)
        tester.test_history.append(result)
        tester.save_history()
        
        # Show brief stats if history exists
        if len(tester.test_history) > 1:
            print(f"\n📊 You have {len(tester.test_history)} tests in history. Use --stats to see detailed statistics.")

if __name__ == "__main__":
    main()

