#!/usr/bin/env python3
"""
Enhanced Internet Connection Monitor
Monitors internet connectivity, logs dropoffs, and provides detailed statistics.
"""
import subprocess
import time
import json
import os
import signal
import sys
from datetime import datetime, timedelta
from statistics import mean, median
from typing import List, Dict, Optional, Tuple

class InternetMonitor:
    def __init__(self, config_file: str = "internet_monitor_config.json"):
        self.config_file = config_file
        self.load_config()
        self.running = True
        self.connection_log: List[Dict] = []
        self.downtime_periods: List[Dict] = []
        self.current_downtime_start: Optional[datetime] = None
        self.setup_signal_handlers()
        
    def load_config(self):
        """Load configuration from file or create default config."""
        default_config = {
            "target_servers": ["8.8.8.8", "1.1.1.1", "208.67.222.222"],  # Google, Cloudflare, OpenDNS
            "threshold_ms": 1000,
            "check_interval": 5,
            "log_file": "internet_connectivity.log",
            "stats_file": "internet_stats.json",
            "ping_count": 3,
            "timeout_seconds": 5,
            "alert_after_failures": 3,
            "verbose": True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults for any missing keys
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
            
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.running = False
        
    def ping_server(self, server: str) -> Tuple[bool, Optional[float]]:
        """Ping a server and return success status and response time."""
        try:
            cmd = ["ping", "-c", str(self.config["ping_count"]), "-W", str(self.config["timeout_seconds"] * 1000), server]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config["timeout_seconds"] + 2)
            
            if result.returncode == 0:
                # Extract average response time
                lines = result.stdout.split('\n')
                for line in lines:
                    if "avg" in line and "min/avg/max" in line:
                        avg_time = float(line.split('/')[4])
                        return True, avg_time
                # Fallback: extract from individual ping
                for line in lines:
                    if "time=" in line:
                        time_str = line.split("time=")[1].split(" ")[0]
                        return True, float(time_str)
                return True, None
            else:
                return False, None
                
        except Exception as e:
            if self.config["verbose"]:
                print(f"Error pinging {server}: {e}")
            return False, None
            
    def check_connectivity(self) -> Tuple[bool, List[float], str]:
        """Check internet connectivity using multiple servers."""
        successful_pings = []
        failed_servers = []
        
        for server in self.config["target_servers"]:
            success, response_time = self.ping_server(server)
            if success and response_time is not None:
                if response_time <= self.config["threshold_ms"]:
                    successful_pings.append(response_time)
                else:
                    failed_servers.append(f"{server} (slow: {response_time:.1f}ms)")
            else:
                failed_servers.append(server)
                
        # Consider connection good if at least one server responds well
        is_connected = len(successful_pings) > 0
        status_detail = f"Good servers: {len(successful_pings)}/{len(self.config['target_servers'])}"
        if failed_servers:
            status_detail += f", Failed: {', '.join(failed_servers)}"
            
        return is_connected, successful_pings, status_detail
        
    def log_event(self, event_type: str, message: str, response_times: List[float] = None):
        """Log an event to file and console."""
        timestamp = datetime.now()
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "event": event_type,
            "message": message,
            "response_times": response_times or []
        }
        
        # Log to file
        try:
            with open(self.config["log_file"], 'a') as f:
                f.write(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {event_type}: {message}\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")
            
        # Console output
        if event_type == "DOWN" or self.config["verbose"]:
            avg_response = f" (avg: {mean(response_times):.1f}ms)" if response_times else ""
            print(f"[{timestamp.strftime('%H:%M:%S')}] {event_type}: {message}{avg_response}")
            
        self.connection_log.append(log_entry)
        
    def handle_connection_down(self, status_detail: str):
        """Handle internet connection down event."""
        if self.current_downtime_start is None:
            self.current_downtime_start = datetime.now()
            self.log_event("DOWN", f"Internet connection lost - {status_detail}")
            
    def handle_connection_restored(self, response_times: List[float], status_detail: str):
        """Handle internet connection restored event."""
        if self.current_downtime_start is not None:
            downtime_duration = datetime.now() - self.current_downtime_start
            downtime_record = {
                "start": self.current_downtime_start.isoformat(),
                "end": datetime.now().isoformat(),
                "duration_seconds": downtime_duration.total_seconds()
            }
            self.downtime_periods.append(downtime_record)
            
            duration_str = str(downtime_duration).split('.')[0]  # Remove microseconds
            self.log_event("UP", f"Internet connection restored after {duration_str} - {status_detail}", response_times)
            self.current_downtime_start = None
        else:
            # Regular check while connected
            if self.config["verbose"]:
                self.log_event("UP", status_detail, response_times)
                
    def generate_stats(self) -> Dict:
        """Generate connectivity statistics."""
        if not self.connection_log:
            return {}
            
        now = datetime.now()
        total_checks = len(self.connection_log)
        down_events = len([e for e in self.connection_log if e["event"] == "DOWN"])
        
        # Calculate uptime percentage
        if self.downtime_periods:
            total_downtime = sum(p["duration_seconds"] for p in self.downtime_periods)
            # Add current downtime if still down
            if self.current_downtime_start:
                current_downtime = (now - self.current_downtime_start).total_seconds()
                total_downtime += current_downtime
                
            # Estimate total monitoring time
            if self.connection_log:
                first_check = datetime.fromisoformat(self.connection_log[0]["timestamp"])
                total_time = (now - first_check).total_seconds()
                uptime_percentage = ((total_time - total_downtime) / total_time) * 100
            else:
                uptime_percentage = 100.0
        else:
            uptime_percentage = 100.0
            total_downtime = 0
            
        # Calculate response time stats
        all_response_times = []
        for entry in self.connection_log:
            if entry["response_times"]:
                all_response_times.extend(entry["response_times"])
                
        stats = {
            "monitoring_start": self.connection_log[0]["timestamp"] if self.connection_log else now.isoformat(),
            "last_updated": now.isoformat(),
            "total_checks": total_checks,
            "connection_failures": down_events,
            "total_downtime_periods": len(self.downtime_periods),
            "total_downtime_seconds": total_downtime,
            "uptime_percentage": round(uptime_percentage, 2),
            "average_response_time_ms": round(mean(all_response_times), 2) if all_response_times else 0,
            "median_response_time_ms": round(median(all_response_times), 2) if all_response_times else 0,
            "min_response_time_ms": round(min(all_response_times), 2) if all_response_times else 0,
            "max_response_time_ms": round(max(all_response_times), 2) if all_response_times else 0,
        }
        
        if self.downtime_periods:
            downtime_durations = [p["duration_seconds"] for p in self.downtime_periods]
            stats.update({
                "average_downtime_seconds": round(mean(downtime_durations), 2),
                "longest_downtime_seconds": max(downtime_durations),
                "shortest_downtime_seconds": min(downtime_durations)
            })
            
        return stats
        
    def save_stats(self):
        """Save statistics to file."""
        stats = self.generate_stats()
        try:
            with open(self.config["stats_file"], 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
            
    def print_summary(self):
        """Print monitoring summary."""
        stats = self.generate_stats()
        if not stats:
            print("No statistics available yet.")
            return
            
        print(f"\n{'='*60}")
        print("INTERNET CONNECTIVITY MONITORING SUMMARY")
        print(f"{'='*60}")
        print(f"Monitoring started: {stats['monitoring_start']}")
        print(f"Total checks: {stats['total_checks']}")
        print(f"Connection failures: {stats['connection_failures']}")
        print(f"Uptime: {stats['uptime_percentage']:.2f}%")
        
        if stats['total_downtime_periods'] > 0:
            print(f"Total outages: {stats['total_downtime_periods']}")
            print(f"Total downtime: {timedelta(seconds=stats['total_downtime_seconds'])}")
            print(f"Average outage duration: {timedelta(seconds=stats['average_downtime_seconds'])}")
            print(f"Longest outage: {timedelta(seconds=stats['longest_downtime_seconds'])}")
            
        if stats['average_response_time_ms'] > 0:
            print(f"Average response time: {stats['average_response_time_ms']:.1f}ms")
            print(f"Response time range: {stats['min_response_time_ms']:.1f}ms - {stats['max_response_time_ms']:.1f}ms")
            
    def run(self):
        """Main monitoring loop."""
        print("Enhanced Internet Connection Monitor Started")
        print(f"Checking every {self.config['check_interval']} seconds")
        print(f"Servers: {', '.join(self.config['target_servers'])}")
        print(f"Threshold: {self.config['threshold_ms']}ms")
        print("Press Ctrl+C to stop and view summary\n")
        
        consecutive_failures = 0
        
        try:
            while self.running:
                is_connected, response_times, status_detail = self.check_connectivity()
                
                if is_connected:
                    consecutive_failures = 0
                    self.handle_connection_restored(response_times, status_detail)
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= self.config["alert_after_failures"]:
                        self.handle_connection_down(status_detail)
                        
                # Save stats periodically
                if len(self.connection_log) % 10 == 0:
                    self.save_stats()
                    
                time.sleep(self.config["check_interval"])
                
        except KeyboardInterrupt:
            self.running = False
            
        finally:
            # Final cleanup
            if self.current_downtime_start:
                # Close any open downtime period
                downtime_duration = datetime.now() - self.current_downtime_start
                downtime_record = {
                    "start": self.current_downtime_start.isoformat(),
                    "end": datetime.now().isoformat(),
                    "duration_seconds": downtime_duration.total_seconds()
                }
                self.downtime_periods.append(downtime_record)
                
            self.save_stats()
            self.print_summary()

def main():
    """Main function with command line argument handling."""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Enhanced Internet Connection Monitor")
            print("Usage: python internet_dropoff.py [options]")
            print("  -h, --help    Show this help message")
            print("  -s, --stats   Show current statistics only")
            print("  -c, --config  Show current configuration")
            return
        elif sys.argv[1] in ['-s', '--stats']:
            monitor = InternetMonitor()
            monitor.print_summary()
            return
        elif sys.argv[1] in ['-c', '--config']:
            monitor = InternetMonitor()
            print("Current configuration:")
            print(json.dumps(monitor.config, indent=2))
            return
            
    monitor = InternetMonitor()
    monitor.run()

if __name__ == "__main__":
    main()

