import struct, time
import pymem, pymem.process
from offsets import *

class GameMemory:
    def __init__(self):
        self.pm          = None
        self.hw_base     = 0
        self.client_base = 0
        self.connected   = False

    def connect(self):
        try:
            self.pm          = pymem.Pymem(PROCESS_NAME)
            self.hw_base     = pymem.process.module_from_name(self.pm.process_handle, HW_DLL).lpBaseOfDll
            self.client_base = pymem.process.module_from_name(self.pm.process_handle, CLIENT_DLL).lpBaseOfDll
            self.connected   = True
            return True, "OK"
        except Exception as e:
            self.connected = False
            return False, str(e)

    def alive(self):
        try:
            self.pm.read_int(self.hw_base + VIEWANGLES)
            return True
        except:
            self.connected = False
            return False

    # ── примитивы ─────────────────────────────────────────────────────────────
    def _ri(self, addr):
        try: return self.pm.read_int(addr)
        except: return 0

    def _rf(self, addr):
        try: return self.pm.read_float(addr)
        except: return 0.0

    def _rv3(self, addr):
        try:
            d = self.pm.read_bytes(addr, 12)
            return struct.unpack('fff', d)
        except:
            return (0.0, 0.0, 0.0)

    def _wf(self, addr, v):
        try: self.pm.write_float(addr, v)
        except: pass

    def _wv3(self, addr, x, y, z):
        try: self.pm.write_bytes(addr, struct.pack('fff', x, y, z), 12)
        except: pass

    # ── viewangles ────────────────────────────────────────────────────────────
    def get_viewangles(self):
        return self._rv3(self.hw_base + VIEWANGLES)

    def set_viewangles(self, pitch, yaw, roll=0.0):
        self._wv3(self.hw_base + VIEWANGLES, pitch, yaw, roll)

    # ── entity helpers ────────────────────────────────────────────────────────
    def _ent_base(self, idx):
        return self.client_base + ENTITY_LIST_BASE + idx * CL_ENTITY_SIZE

    def get_local_index(self):
        return self._ri(self.client_base + LOCAL_PLAYER_INDEX)

    def get_entity_origin(self, idx):
        # Рендер-позиция (сглаженная, точнее для ESP)
        return self._rv3(self._ent_base(idx) + RENDER_ORIGIN)

    def get_entity_curstate_origin(self, idx):
        # Точная позиция из curstate (для aim)
        return self._rv3(self._ent_base(idx) + CURSTATE_ORIGIN)

    def get_entity_health(self, idx):
        return self._ri(self._ent_base(idx) + CURSTATE_HEALTH)

    def get_entity_team(self, idx):
        return self._ri(self._ent_base(idx) + CURSTATE_TEAM)

    def is_valid_player(self, idx, local_idx):
        if idx == local_idx or not (1 <= idx <= MAX_PLAYERS):
            return False
        hp = self.get_entity_health(idx)
        return 1 <= hp <= 100

    def get_enemies(self, local_idx):
        local_team = self.get_entity_team(local_idx)
        result = []
        for i in range(1, MAX_PLAYERS + 1):
            if not self.is_valid_player(i, local_idx):
                continue
            team = self.get_entity_team(i)
            if team != local_team and team in (TEAM_T, TEAM_CT):
                result.append({
                    'index':  i,
                    'origin': self.get_entity_origin(i),
                    'aim_origin': self.get_entity_curstate_origin(i),
                    'health': self.get_entity_health(i),
                    'team':   team,
                })
        return result
