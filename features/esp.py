"""
ESP / Wallhack + PenBox overlay через pygame прозрачное окно.
PenBox: подсвечивает врагов за простреливаемыми поверхностями (зелёный).
CS 1.6: металл/дерево простреливается до ~500 ед., бетон — нет.
"""
import math, threading, time
import pygame, pygame.gfxdraw
import win32gui, win32con, win32api

# ── цвета (R,G,B,A) ───────────────────────────────────────────────────────────
C_VISIBLE = (255,  80,  80, 220)   # красный — прямой вид
C_WALL    = (255, 200,  50, 220)   # жёлтый  — за стеной
C_PEN     = ( 60, 255, 120, 220)   # зелёный — простреливается (PenBox)
C_WHITE   = (255, 255, 255, 255)
C_SNAP    = (180,  60, 255, 180)   # пурпурный — линия к врагу (snapline)

PEN_MAX_DIST = 500.0   # CS 1.6: максимальная дистанция прострела


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

    # ── проекция мировых координат на экран ───────────────────────────────────
    @staticmethod
    def w2s(rel_origin, angles, sw, sh, hfov=90):
        """
        rel_origin: (dx,dy,dz) — позиция цели относительно камеры
        angles: (pitch, yaw, roll) — углы обзора в градусах
        Возвращает (sx, sy, dist) или None если за спиной / вне экрана
        """
        pitch = math.radians(angles[0])
        yaw   = math.radians(angles[1])

        cp, sp = math.cos(pitch), math.sin(pitch)
        cy, sy_ = math.cos(yaw), math.sin(yaw)

        # базисные векторы камеры
        fwd   = ( cp*cy,  cp*sy_, -sp)
        right = ( sy_,   -cy,      0 )
        up    = ( sp*cy,  sp*sy_,  cp)

        dx, dy, dz = rel_origin
        dot_f = dx*fwd[0]   + dy*fwd[1]   + dz*fwd[2]
        dot_r = dx*right[0] + dy*right[1] + dz*right[2]
        dot_u = dx*up[0]    + dy*up[1]    + dz*up[2]

        if dot_f < 0.1:
            return None

        scale = sw / (2.0 * math.tan(math.radians(hfov / 2.0)))
        sx = int(sw/2 + dot_r / dot_f * scale)
        sy_ = int(sh/2 - dot_u / dot_f * scale)

        if -200 < sx < sw+200 and -200 < sy_ < sh+200:
            return sx, sy_, dot_f
        return None

    @staticmethod
    def dist3(a, b):
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

    def _is_penetrable(self, my_pos, enemy):
        """
        Эвристика: враг за стеной + расстояние < PEN_MAX_DIST →
        скорее всего тонкая поверхность (металл/дерево).
        Настоящий raycast требует hook в движок.
        """
        return self.dist3(my_pos, enemy['origin']) < PEN_MAX_DIST

    # ── рисование одного игрока ───────────────────────────────────────────────
    def _draw_box(self, surf, font_sm, sx, sy, dist, enemy, is_vis, is_pen):
        h = max(18, int(1600 / max(dist, 1)))
        w = max(10, h // 2)
        x1, y1 = sx - w//2, sy - h
        x2, y2 = sx + w//2, sy

        color = C_VISIBLE if is_vis else (C_PEN if (is_pen and self.pen_enabled) else C_WALL)
        r, g, b, a = color

        # Заливка полупрозрачная
        fill = pygame.Surface((w, h), pygame.SRCALPHA)
        fill.fill((r, g, b, 35))
        surf.blit(fill, (x1, y1))

        # Рамка
        pygame.draw.rect(surf, color, (x1, y1, w, h), 2)

        # HP-бар слева
        hp   = max(0, min(100, enemy['health']))
        bx   = x1 - 5
        bh   = h
        pygame.draw.rect(surf, (40, 40, 40, 180), (bx, y1, 3, bh))
        fill_h = int(bh * hp / 100)
        hp_c   = (int(255*(1-hp/100)), int(255*hp/100), 40, 220)
        pygame.draw.rect(surf, hp_c, (bx, y2 - fill_h, 3, fill_h))

        # Текст HP
        t = font_sm.render(f"{hp}", True, (220, 220, 220))
        surf.blit(t, (x1, y2 + 2))

        # Метка PEN
        if is_pen and self.pen_enabled and not is_vis:
            pt = font_sm.render("PEN", True, C_PEN[:3])
            surf.blit(pt, (x1, y1 - 13))

        # Snapline (линия к ногам)
        if self.snaplines:
            pygame.draw.line(surf, C_SNAP[:3], (self.w//2, self.h), (sx, y2), 1)

    # ── основной поток ────────────────────────────────────────────────────────
    def _loop(self):
        pygame.init()
        pygame.font.init()

        # Ищем окно CS 1.6
        cs_hwnd = 0
        for _ in range(20):
            for title in ("Counter-Strike", "Half-Life"):
                cs_hwnd = win32gui.FindWindow(None, title)
                if cs_hwnd: break
            if cs_hwnd: break
            time.sleep(1)
        if not cs_hwnd:
            return

        rect     = win32gui.GetWindowRect(cs_hwnd)
        self.w   = rect[2] - rect[0]
        self.h   = rect[3] - rect[1]

        import os
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{rect[0]},{rect[1]}"

        screen = pygame.display.set_mode((self.w, self.h),
                                         pygame.NOFRAME | pygame.SRCALPHA)
        pygame.display.set_caption("__overlay__")

        hwnd = pygame.display.get_wm_info()['window']
        exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
            exstyle | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST)
        # Чёрный пиксель = прозрачный
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,
                              rect[0], rect[1], self.w, self.h, 0)

        font_sm = pygame.font.SysFont("Arial", 11, bold=True)
        clock   = pygame.time.Clock()

        while not self._stop.is_set():
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._stop.set()

            screen.fill((0, 0, 0))   # чёрный = прозрачный (colorkey)

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
            is_vis = dist < 250  # грубая эвристика (без raycast в движке)
            is_pen = self._is_penetrable(my_pos, e)
            self._draw_box(surf, font_sm, sx, sy, dist, e, is_vis, is_pen)
