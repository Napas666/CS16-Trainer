import math, threading, time
from offsets import HEAD_OFFSET

class Aimbot:
    def __init__(self, mem):
        self.mem      = mem
        self.enabled  = False
        self.fov      = 15.0    # угол захвата цели (градусы)
        self.smooth   = 4.0     # 1 = мгновенно, 20 = очень плавно
        self.head_aim = True    # True = целиться в голову, False = в центр
        self._stop    = threading.Event()

    def start(self):
        self._stop.clear()
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._stop.set()

    # ── математика ────────────────────────────────────────────────────────────
    @staticmethod
    def calc_angle(src, dst):
        dx = dst[0] - src[0]
        dy = dst[1] - src[1]
        dz = dst[2] - src[2]
        pitch = -math.degrees(math.atan2(dz, math.hypot(dx, dy)))
        yaw   =  math.degrees(math.atan2(dy, dx))
        return pitch, yaw

    @staticmethod
    def normalize(a):
        while a >  180: a -= 360
        while a < -180: a += 360
        return a

    def fov_dist(self, ca, ta):
        return math.hypot(self.normalize(ca[0] - ta[0]),
                          self.normalize(ca[1] - ta[1]))

    # ── главный цикл ──────────────────────────────────────────────────────────
    def _loop(self):
        while not self._stop.is_set():
            if self.enabled and self.mem.connected:
                self._tick()
            time.sleep(0.007)   # ~140 тиков/сек

    def _tick(self):
        local_idx = self.mem.get_local_index()
        if local_idx < 1:
            return

        my_pos     = self.mem.get_entity_curstate_origin(local_idx)
        cur_angles = self.mem.get_viewangles()
        enemies    = self.mem.get_enemies(local_idx)
        if not enemies:
            return

        best, best_fov = None, self.fov

        for e in enemies:
            o = e['aim_origin']
            # смещение в голову или центр
            target_z = o[2] + (HEAD_OFFSET if self.head_aim else 0)
            target   = (o[0], o[1], target_z)
            ta = self.calc_angle(my_pos, target)
            d  = self.fov_dist(cur_angles, ta)
            if d < best_fov:
                best_fov, best = d, ta

        if best is None:
            return

        # Плавное наведение
        dp = self.normalize(best[0] - cur_angles[0]) / self.smooth
        dy = self.normalize(best[1] - cur_angles[1]) / self.smooth
        self.mem.set_viewangles(cur_angles[0] + dp, cur_angles[1] + dy)
