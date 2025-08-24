#!/usr/bin/env python3
import ctypes
import time
import platform
import sys

# Define the idle threshold in seconds
idle_threshold = 10  # Adjust as needed
idle_time = 0

def setup_macos_mouse():
    """Setup CoreGraphics on macOS"""
    try:
        # Load CoreGraphics framework
        cg = ctypes.CDLL('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
        
        # Define CGPoint structure
        class CGPoint(ctypes.Structure):
            _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]
        
        # Function prototypes
        cg.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, CGPoint, ctypes.c_uint32]
        cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p
        cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cg.CGEventGetLocation.argtypes = [ctypes.c_void_p]
        cg.CGEventGetLocation.restype = CGPoint
        cg.CGEventCreate.argtypes = [ctypes.c_void_p]
        cg.CGEventCreate.restype = ctypes.c_void_p
        cg.CFRelease.argtypes = [ctypes.c_void_p]
        
        return cg, CGPoint
    except Exception as e:
        return None, None

def get_mouse_position_macos(cg, CGPoint):
    """Get current mouse position on macOS"""
    try:
        # Create an event to get current cursor position
        event = cg.CGEventCreate(None)
        if not event:
            return None
        pos = cg.CGEventGetLocation(event)
        cg.CFRelease(event)
        return (int(pos.x), int(pos.y))
    except Exception:
        return None

def move_mouse_macos(cg, CGPoint, x, y):
    """Move mouse on macOS"""
    try:
        point = CGPoint(x, y)
        # Create mouse move event (kCGEventMouseMoved = 5)
        event = cg.CGEventCreateMouseEvent(None, 5, point, 0)
        if event:
            # Post event (kCGHIDEventTap = 0)
            cg.CGEventPost(0, event)
            cg.CFRelease(event)
            return True
    except Exception:
        pass
    return False

def get_screen_size():
    """Get screen dimensions"""
    try:
        if platform.system() == "Darwin":
            # macOS - use system_profiler as fallback
            import subprocess
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                  capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Resolution:' in line:
                    res = line.split('Resolution:')[1].strip()
                    if ' x ' in res:
                        width, height = map(int, res.split(' x '))
                        return width, height
    except Exception:
        pass
    return 1920, 1080  # Default fallback

def main():
    print("Mouse movement script starting...")
    
    # Check if we're on macOS
    if platform.system() != "Darwin":
        print("This script is designed for macOS only.")
        sys.exit(1)
    
    # Setup macOS mouse functions
    cg, CGPoint = setup_macos_mouse()
    if not cg:
        print("Failed to initialize CoreGraphics. This may require accessibility permissions.")
        print("Please go to System Preferences > Security & Privacy > Accessibility")
        print("and grant permission to Terminal or your Python executable.")
        sys.exit(1)
    
    # Get initial mouse position
    prev_mouse_position = get_mouse_position_macos(cg, CGPoint)
    if prev_mouse_position is None:
        print("Failed to get initial mouse position.")
        sys.exit(1)
    
    print(f"Mouse movement script started. Press Ctrl+C to stop.")
    print(f"Idle threshold: {idle_threshold} seconds")
    print(f"Initial mouse position: {prev_mouse_position}")
    
    idle_time = 0
    
    while True:
        try:
            # Wait for a short interval
            time.sleep(1)  # Check every second
            
            # Get the current mouse position
            current_mouse_position = get_mouse_position_macos(cg, CGPoint)
            if current_mouse_position is None:
                continue
            
            # Check if the mouse position has changed
            if current_mouse_position != prev_mouse_position:
                # Reset the idle timer if the mouse has moved
                prev_mouse_position = current_mouse_position
                idle_time = 0
                print(f"Mouse moved to: {current_mouse_position}")
            else:
                # Increment idle time
                idle_time += 1
                print(f"Idle time: {idle_time}s")
                
                # If idle time exceeds the threshold, move the mouse
                if idle_time >= idle_threshold:
                    # Move the mouse pointer to a new position
                    new_x = current_mouse_position[0] + 5
                    new_y = current_mouse_position[1] + 5
                    
                    # Ensure new position is within screen boundaries
                    screen_width, screen_height = get_screen_size()
                    new_x = min(max(new_x, 10), screen_width - 10)
                    new_y = min(max(new_y, 10), screen_height - 10)
                    
                    # Move mouse and reset idle time
                    if move_mouse_macos(cg, CGPoint, new_x, new_y):
                        print(f"Moved mouse from {current_mouse_position} to ({new_x}, {new_y})")
                        idle_time = 0
                        prev_mouse_position = (new_x, new_y)
                    else:
                        print("Failed to move mouse")
        
        except KeyboardInterrupt:
            print("\nScript interrupted by user. Exiting.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
