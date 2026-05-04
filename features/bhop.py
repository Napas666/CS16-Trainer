"""
Bunny Hop — автопрыжок в момент приземления.
"""
import threading, time
from offsets import CURSTATE_OFF, CL_ENTITY_SIZE, ENTITY_LIST_BASE

# onground хранится в curstate (offset 0x130) + 0xD4 внутри entity_state_t
ONGROUND_OFF = CURSTATE_OFF + 0xD4   # = 0x130 + 0xD4 = 0x204

class Bhop:
    def __init__(self, mem):
        self.mem      = mem
        self.enabled  = False
        self._stop    = threading.Event()
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
            time.sleep(0.005)

    def _tick(self):
        try:
            import win32api, win32con
        except ImportError:
            return

        local_idx = self.mem.get_local_index()
        if local_idx < 1:
            return

        ent_base  = self.mem.client_base + ENTITY_LIST_BASE + local_idx * CL_ENTITY_SIZE
        onground  = self.mem._ri(ent_base + ONGROUND_OFF)
        on_ground = onground != 0

        if self._was_air and on_ground:
            win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)
            time.sleep(0.015)
            win32api.keybd_event(win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0)

        self._was_air = not on_ground
