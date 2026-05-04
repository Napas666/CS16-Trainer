"""
ESP / Wallhack + PenBox overlay.
PenBox: зелёный бокс = враг за простреливаемой поверхностью.
"""
import os, math, threading, time

C_VISIBLE = (255,  80,  80, 220)
C_WALL    = (255, 200,  50, 220)
C_PEN     = ( 60, 255, 120, 220)
C_SNAP    = (180,  60, 255, 180)
PEN_MAX_DIST = 500.0


class ESPOverlay:
    def __init__(self, mem):
        self.mem         = mem
        self.enabled     = False
        self.pen_enabled = False
        self.snaplines   = False
        self._stop       = threading.Event()
        self.w = self.h  = 0

    def start(self):
        self._stop.clear()
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._stop.set()

    @staticmethod
    def w2s(rel, angles, sw, sh, hfov=90):
        pitch = math.radians(angles[0])
        yaw   = math.radians(angles[1])
        cp, sp = math.cos(pitch), math.sin(pitch)
        cy, sy = math.cos(yaw),   math.sin(yaw)

        fwd   = ( cp*cy,  cp*sy, -sp)
        right = ( sy,    -cy,     0 )
        up    = ( sp*cy,  sp*sy,  cp)

        dx, dy, dz = rel
        dot_f = dx*fwd[0]   + dy*fwd[1]   + dz*fwd[2]
        dot_r = dx*right[0] + dy*right[1] + dz*right[2]
        dot_u = dx*up[0]    + dy*up[1]    + dz*up[2]

        if dot_f < 0.1:
            return None

        scale = sw / (2.0 * math.tan(math.radians(hfov / 2.0)))
        sx = int(sw/2 + dot_r / dot_f * scale)
        sy = int(sh/2 - dot_u / dot_f * scale)

        if -200 < sx < sw+200 and -200 < sy < sh+200:
            return sx, sy, dot_f
        return None

    @staticmethod
    def dist3(a, b):
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

    def _is_penetrable(self, my_pos, enemy):
        return self.dist3(my_pos, enemy['origin']) < PEN_MAX_DIST

    def _draw_box(self, surf, font_sm, sx, sy, dist, enemy, is_vis, is_pen):
        import pygame
        h = max(18, int(1600 / max(dist, 1)))
        w = max(10, h // 2)
        x1, y1 = sx - w//2, sy - h
        x2, y2 = sx + w//2, sy

        color = C_VISIBLE if is_vis else (C_PEN if (is_pen and self.pen_enabled) else C_WALL)
        r, g, b, a = color

        fill = pygame.Surface((w, h), pygame.SRCALPHA)
        fill.fill((r, g, b, 35))
        surf.blit(fill, (x1, y1))
        pygame.draw.rect(surf, color, (x1, y1, w, h), 2)

        hp = max(0, min(100, enemy['health']))
        bx = x1 - 5
        pygame.draw.rect(surf, (40, 40, 40, 180), (bx, y1, 3, h))
        fill_h = int(h * hp / 100)
        hp_c = (int(255*(1-hp/100)), int(255*hp/100), 40, 220)
        pygame.draw.rect(surf, hp_c, (bx, y2 - fill_h, 3, fill_h))

        t = font_sm.render(f"{hp}", True, (220, 220, 220))
        surf.blit(t, (x1, y2 + 2))

        if is_pen and self.pen_enabled and not is_vis:
            pt = font_sm.render("PEN", True, C_PEN[:3])
            surf.blit(pt, (x1, y1 - 13))

        if self.snaplines:
            pygame.draw.line(surf, C_SNAP[:3], (self.w//2, self.h), (sx, y2), 1)

    def _loop(self):
        try:
            import pygame
            import win32gui, win32con, win32api
        except ImportError as e:
            print(f"[ESP] Import error: {e}")
            return

        pygame.init()
        pygame.font.init()

        cs_hwnd = 0
        for _ in range(30):
            for title in ("Counter-Strike", "Half-Life"):
                cs_hwnd = win32gui.FindWindow(None, title)
                if cs_hwnd: break
            if cs_hwnd: break
            time.sleep(1)

        if not cs_hwnd:
            print("[ESP] CS 1.6 window not found")
            return

        rect = win32gui.GetWindowRect(cs_hwnd)
        self.w, self.h = rect[2]-rect[0], rect[3]-rect[1]

        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{rect[0]},{rect[1]}"
        screen = pygame.display.set_mode((self.w, self.h), pygame.NOFRAME | pygame.SRCALPHA)
        pygame.display.set_caption("__cs_overlay__")

        hwnd = pygame.display.get_wm_info()['window']
        exs = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
            exs | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), 0, win32con.LWA_COLORKEY)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, rect[0], rect[1], self.w, self.h, 0)

        font_sm = pygame.font.SysFont("Arial", 11, bold=True)
        clock   = pygame.time.Clock()

        while not self._stop.is_set():
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._stop.set()
            screen.fill((0, 0, 0))
            if self.enabled and self.mem.connected:
                self._render(screen, font_sm)
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def _render(self, surf, font_sm):
        local_idx = self.mem.get_local_index()
        if local_idx < 1:
            return
        my_pos  = self.mem.get_entity_origin(local_idx)
        angles  = self.mem.get_viewangles()
        enemies = self.mem.get_enemies(local_idx)
        for e in enemies:
            o   = e['origin']
            rel = (o[0]-my_pos[0], o[1]-my_pos[1], o[2]-my_pos[2]+36)
            proj = self.w2s(rel, angles, self.w, self.h)
            if proj is None:
                continue
            sx, sy, dist = proj
            is_vis = dist < 250
            is_pen = self._is_penetrable(my_pos, e)
            self._draw_box(surf, font_sm, sx, sy, dist, e, is_vis, is_pen)
