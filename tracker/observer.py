import win32gui
import win32process
import psutil
import json
import win32api  # To track mouse position
import hashlib

try: from . import utils
except ImportError: import utils

DEFAULT_EXCLUDED_TITLES = [
        "Media", 
        "Settings", 
        "Mail", 
        "Add an account",
]
DEFAULT_EXCLUDED_PROCESSES = [
        "ApplicationFrameHost.exe", 
        "explorer.exe", 
        "SystemSettings.exe",
        "HxOutlook.exe", 
        "WindowsStore.exe", 
        "SearchUI.exe",
]

class Observer:
    def __init__(self, excluded_titles=None, excluded_processes=None):
        # Default exclusions if no list is provided
        self.excluded_titles = excluded_titles if excluded_titles is not None else DEFAULT_EXCLUDED_TITLES
        self.excluded_processes = excluded_processes if excluded_processes is not None else DEFAULT_EXCLUDED_PROCESSES
        
        self.latest_screenshot = None
        self.latest_mousepos = None

    def get_window_title(self, hwnd):
        """Get the window title for the given window handle."""
        return win32gui.GetWindowText(hwnd)

    def get_process_name(self, hwnd):
        """Get the process name for the given window handle."""
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.name()

    def is_excluded(self, title, process_name):
        """Check if the window should be excluded based on its title or process name."""
        return (any(excluded_title in title for excluded_title in self.excluded_titles) or 
                process_name in self.excluded_processes)

    def get_all_windows(self):
        """Get all open windows with their titles, handles, and associated process names."""
        windows = []
        
        def enum_windows_callback(hwnd, lParam):
            if win32gui.IsWindowVisible(hwnd):  # Only visible windows
                title = self.get_window_title(hwnd)
                process_name = self.get_process_name(hwnd)
                if not self.is_excluded(title, process_name): 
                    windows.append((hwnd, title, process_name))
        
        win32gui.EnumWindows(enum_windows_callback, None)
        return windows

    def get_active_window_index(self, windows):
        """Get the index of the active window in the list of windows."""
        active_hwnd = win32gui.GetForegroundWindow()
        
        # Now we search for the active window's hwnd in the list of windows
        for i, (hwnd, title, process_name) in enumerate(windows):
            if hwnd == active_hwnd:
                return i
        return None
    
    def has_changed(self):
        """Check whether the screenshot or mouse position has changed."""
        current_screenshot = utils.screen_digest()
        current_mousepos = win32api.GetCursorPos()

        screenshot_changed = current_screenshot != self.latest_screenshot
        mousepos_changed = current_mousepos != self.latest_mousepos

        # Update the latest values
        self.latest_screenshot = current_screenshot
        self.latest_mousepos = current_mousepos

        # Return whether there was any change
        return screenshot_changed or mousepos_changed

    def get_status(self):
        """Return a dictionary representing what must be inserted into the database."""
        windows = self.get_all_windows()
        active_window_index = self.get_active_window_index(windows)
        is_afk = not self.has_changed()

        # Prepare the data to be returned in JSON format
        status = {
            "windows": [(title, process_name) for _, title, process_name in windows],
            "active_window_index": active_window_index,
            "is_afk": is_afk,
        }


