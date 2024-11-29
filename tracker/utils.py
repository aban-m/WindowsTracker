from threading import Thread
import time
import ctypes
import hashlib
from ctypes import wintypes
import logging
from . import db

logger = logging.getLogger('runner')

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
    @classmethod
    def from_observer(cls, frequency, observer, conn):
        def write_callback(observer):
            status = observer.observe()
            db.insert(conn, status['windows'], status['active_index'],
                      status['afk'], timestamp = None, commit = True
            )

        runner = cls(frequency, write_callback, observer)
        logger.debug('Prepared periodic observer.')
        return runner

    def __init__(self, frequency, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.frequency = int(frequency)
        self._ftol = 3
        self._fcount = self._ftol    # Failure count
        self.running = False

    def _loop(self):
        while self.running:
            # Execution.
            try:
                self.func(*self.args, **self.kwargs)
                logger.debug(f'Made a succesful function call.')
                self._fcount = self._ftol
            except Exception as e:
                logger.error(f'Error in function call. Remaining failures: {self._fcount}.', exc_info = e)
                self._fcount -= 1
                if self._fcount <= 0:
                    self.running = False
                    logging.critical(f'Stopped due to too many errors ({self._ftol}).')
                    break

            # Sleeping sequence.
            for _ in range(int(self.frequency) + 1):
                time.sleep(1)            
                if not self.running:
                    logger.debug('Stopped!')
                    break
                

    def run(self):
        self.running = True
        Thread(target = self._loop).start()

    def stop(self):
        logger.debug('Attempting to stop.')
        self.running = False
