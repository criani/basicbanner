import tkinter as tk
from screeninfo import get_monitors
import ctypes
from ctypes import wintypes
import win32api
import win32con
import win32gui
import threading

# Function to create a banner on each monitor (from basicbanner.py)
def create_banner_on_monitor(monitor):
    window = tk.Tk()
    window.title("System Classification Banner")
    window.attributes('-topmost', True)
    window.overrideredirect(True)
    label_text = "NOFORN (U-NNPI)"
    label = tk.Label(window, text=label_text, bg="green", fg="white")
    label.pack(fill=tk.BOTH, expand=True)
    window.geometry(f"{monitor.width}x30+{monitor.x}+0")
    return window

# AppBar message constants (from banner2.py)
ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003

# Edge constants for AppBar (from banner2.py)
ABE_TOP = 1

# APPBARDATA structure (from banner2.py)
class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", wintypes.RECT),
        ("lParam", wintypes.LPARAM),
    ]

# SHAppBarMessage function (from banner2.py)
def SHAppBarMessage(dwMessage, pData):
    SHAppBarMessageFunc = ctypes.windll.shell32.SHAppBarMessage
    SHAppBarMessageFunc.argtypes = [wintypes.DWORD, ctypes.POINTER(APPBARDATA)]
    SHAppBarMessageFunc.restype = ctypes.c_ulong
    return SHAppBarMessageFunc(dwMessage, pData)

# AppBar class (from banner2.py)
class AppBar:
    def __init__(self, name="UnclassifiedAppBar"):
        self.name = name
        self.hwnd = None

    def create_appbar(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wndproc
        wc.lpszClassName = self.name
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wc.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        wc.hCursor = win32api.LoadCursor(None, win32con.IDC_ARROW)
        class_atom = win32gui.RegisterClass(wc)

        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(class_atom, self.name, style, 0, 0, win32api.GetSystemMetrics(win32con.SM_CXSCREEN), 100, 0, 0, 0, None)
        win32gui.UpdateWindow(self.hwnd)
        win32gui.SetWindowText(self.hwnd, "Unclassified")

        self.register_appbar()
        self.set_appbar_position()

        win32gui.PumpMessages()

    def register_appbar(self):
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = self.hwnd
        abd.uCallbackMessage = win32con.WM_USER + 1
        SHAppBarMessage(ABM_NEW, ctypes.byref(abd))

    def set_appbar_position(self):
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = self.hwnd
        abd.uEdge = ABE_TOP

        # Get the size of the screen
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        abd.rc.left = 0
        abd.rc.top = 0
        abd.rc.right = screen_width
        abd.rc.bottom = 30  # Set the app bar to be 30 pixels high

        SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(abd))
        SHAppBarMessage(ABM_SETPOS, ctypes.byref(abd))

        win32gui.MoveWindow(self.hwnd, abd.rc.left, abd.rc.top, abd.rc.right, abd.rc.bottom, True)

    def wndproc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

# Function to create tkinter banners on each monitor
def create_tkinter_banners():
    print("Starting tkinter banners")
    monitors = get_monitors()
    windows = [create_banner_on_monitor(monitor) for monitor in monitors]
    tk.mainloop()

# Main function to run both AppBar and tkinter banners
def main():
    # Run tkinter banners in a separate thread
    tkinter_thread = threading.Thread(target=create_tkinter_banners)
    tkinter_thread.start()

    # Create and run AppBar
    print("Creating AppBar")
    appbar = AppBar()
    appbar.create_appbar()

if __name__ == "__main__":
    main()
