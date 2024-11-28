from threading import Thread
import time
import ctypes
import hashlib
from ctypes import wintypes

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD)
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', wintypes.BYTE * 3)
    ]

def screen_digest():
    """Capture the screen using Windows API and return its hash."""

    hdc_screen = user32.GetDC(0)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)

    # Get the screen dimensions
    screen_width = user32.GetSystemMetrics(0)  # Screen width
    screen_height = user32.GetSystemMetrics(1)  # Screen height

    h_bitmap = gdi32.CreateCompatibleBitmap(hdc_screen, screen_width, screen_height)
    gdi32.SelectObject(hdc_mem, h_bitmap)

    gdi32.BitBlt(hdc_mem, 0, 0, screen_width, screen_height, hdc_screen, 0, 0, 13369376)  # SRCCOPY

    bmp_info = BITMAPINFO()
    bmp_info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmp_info.bmiHeader.biWidth = screen_width
    bmp_info.bmiHeader.biHeight = -screen_height  # Negative for top-down image
    bmp_info.bmiHeader.biPlanes = 1
    bmp_info.bmiHeader.biBitCount = 24
    bmp_info.bmiHeader.biCompression = 0  # BI_RGB
    bmp_info.bmiHeader.biSizeImage = screen_width * screen_height * 3  # RGB

    buffer = ctypes.create_string_buffer(bmp_info.bmiHeader.biSizeImage)

    gdi32.GetDIBits(hdc_mem, h_bitmap, 0, screen_height, buffer, ctypes.byref(bmp_info), 0)

    screenshot_hash = hashlib.md5(buffer.raw).hexdigest()

    gdi32.DeleteObject(h_bitmap)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(0, hdc_screen)

    return screenshot_hash



class Runner:
    def __init__(self, frequency, func, *args, **kwargs):
        self.func = func
        sefl.args = args
        self.kwargsr = kwargs
        self.frequency = frequency
        self.running = False

    def _loop(self):
        while self.running:
            time.sleep(self.frequency)
            if not self.running: break
            self.func(*self.args, **self.kwargs)

    def run(self):
        self.running = True
        Thread(target = self._loop).start()

    def stop(self):
        self.running = False
