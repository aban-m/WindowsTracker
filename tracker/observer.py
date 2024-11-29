import win32gui
import win32api
import win32process
import psutil
import hashlib
import logging

from . import utils

logger = logging.getLogger('observer')

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
        self.excluded_titles = DEFAULT_EXCLUDED_TITLES if excluded_titles is None\
                               else excluded_titles
        self.excluded_processes = DEFAULT_EXCLUDED_PROCESSES if excluded_processes is None\
                               else excluded_processes
        
        self.latest_screenshot = None
        self.latest_mousepos = None

    def get_all_windows(self):
        """Get all open windows with their titles, handles, and associated process names."""
        windows = []
        active_index = None
        
        active_hwnd = win32gui.GetForegroundWindow()

        def enum_windows_callback(hwnd, lParam):
            # First test: Must be visible
            if not win32gui.IsWindowVisible(hwnd): return

            # Second test: Must not be excluded
            title = win32gui.GetWindowText(hwnd)
            if not title.strip(): return # title must be non-empty. (debatable!)
            if title in self.excluded_titles: return

            process_name = psutil.Process(win32process.GetWindowThreadProcessId(hwnd)[1]).name()
            if process_name in self.excluded_processes: return

            windows.append((hwnd, title, process_name))
        
        win32gui.EnumWindows(enum_windows_callback, None)

        active_hwnd = win32gui.GetForegroundWindow()
        active_index = [i for i in range(len(windows)) if windows[i][0] == active_hwnd] + [None]
        
        return windows, active_index[0]
    
    def has_changed(self):
        """Check whether the screenshot or mouse position has changed."""
        current_screenshot = utils.screen_digest()
        current_mousepos = win32api.GetCursorPos()

        screenshot_changed = current_screenshot != self.latest_screenshot
        mousepos_changed = current_mousepos != self.latest_mousepos

        logger.debug(f'Screen digest: {current_screenshot}. Mouse position: {current_mousepos}.')

        # Update the latest values
        self.latest_screenshot = current_screenshot
        self.latest_mousepos = current_mousepos

        # Return whether there was any change
        return screenshot_changed or mousepos_changed

    def observe(self):
        """Return a dictionary representing what must be inserted into the database."""
        windows, active_index = self.get_all_windows()
        is_afk = not self.has_changed()

        status = {
            "windows": [(title, process_name) for _, title, process_name in windows],
            "active_index": active_index,
            "afk": is_afk,
        }
        logger.info(f'Observation made: {len(windows)} windows found.{" AFK detected." if is_afk else ""}')
        
        return status


