"""
Bunny Hop — автоматически прыгает в момент приземления.
CS 1.6 позволяет bhop: если нажать пробел точно в кадр приземления,
скорость сохраняется и накапливается.
"""
import threading, time
import win32api, win32con
from offsets import RENDER_ORIGIN, CL_ENTITY_SIZE, ENTITY_LIST_BASE

ONGROUND_OFF = 0x2A0 + 0xD4   # curstate.onground

class Bhop:
    def __init__(self, mem):
        self.mem     = mem
        self.enabled = False
        self._stop   = threading.Event()
        self._was_air = False

    def start(self):
        self._stop.clear()
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._stop.set()

    def _loop(self):
        while not self._stop.is_set():
            if self.enabled and self.mem.connected:
                self._tick()
            time.sleep(0.005)   # 200 Гц для точности

    def _tick(self):
        local_idx = self.mem.get_local_index()
        if local_idx < 1:
            return

        ent_base  = self.mem.client_base + ENTITY_LIST_BASE + local_idx * CL_ENTITY_SIZE
        onground  = self.mem._ri(ent_base + ONGROUND_OFF)
        on_ground = onground != 0

        if self._was_air and on_ground:
            # Приземлились — мгновенный прыжок
            win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)
            time.sleep(0.015)
            win32api.keybd_event(win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0)

        self._was_air = not on_ground
