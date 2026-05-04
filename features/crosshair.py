"""
Кастомный прицел — рисуется поверх игры через pygame overlay.
Параметры настраиваются из UI: цвет, стиль, размер, толщина, gap, dot.
"""
import pygame
import math

STYLES = ["КРЕСТ", "Т-ОБРАЗНЫЙ", "ТОЧКА", "КРУГ", "КВАДРАТ"]

class Crosshair:
    def __init__(self):
        self.enabled   = False
        self.style     = 0          # индекс из STYLES
        self.size      = 10         # длина линий (px)
        self.thickness = 2          # толщина линий
        self.gap       = 4          # gap между центром и линиями
        self.dot       = True       # центральная точка
        self.color     = (0, 255, 80)  # RGB
        self.outline   = True       # чёрная обводка

    def draw(self, surf, cx, cy):
        if not self.enabled:
            return
        s, t, g = self.size, self.thickness, self.gap
        c = self.color
        oc = (0, 0, 0)

        def line(x1, y1, x2, y2, col, width):
            pygame.draw.line(surf, col, (x1, y1), (x2, y2), width)

        def rect(x, y, w, h, col):
            pygame.draw.rect(surf, col, (x, y, w, h))

        style = STYLES[self.style]

        if style == "КРЕСТ":
            if self.outline:
                line(cx-s-g, cy, cx-g, cy, oc, t+2)
                line(cx+g,   cy, cx+s+g, cy, oc, t+2)
                line(cx, cy-s-g, cx, cy-g, oc, t+2)
                line(cx, cy+g,   cx, cy+s+g, oc, t+2)
            line(cx-s-g, cy, cx-g, cy, c, t)
            line(cx+g,   cy, cx+s+g, cy, c, t)
            line(cx, cy-s-g, cx, cy-g, c, t)
            line(cx, cy+g,   cx, cy+s+g, c, t)

        elif style == "Т-ОБРАЗНЫЙ":
            if self.outline:
                line(cx-s-g, cy, cx-g, cy, oc, t+2)
                line(cx+g,   cy, cx+s+g, cy, oc, t+2)
                line(cx, cy+g, cx, cy+s+g, oc, t+2)
            line(cx-s-g, cy, cx-g, cy, c, t)
            line(cx+g,   cy, cx+s+g, cy, c, t)
            line(cx, cy+g, cx, cy+s+g, c, t)

        elif style == "ТОЧКА":
            r = max(2, t+1)
            if self.outline:
                pygame.draw.circle(surf, oc, (cx, cy), r+1)
            pygame.draw.circle(surf, c, (cx, cy), r)

        elif style == "КРУГ":
            r = s + g
            if self.outline:
                pygame.draw.circle(surf, oc, (cx, cy), r+1, t+2)
            pygame.draw.circle(surf, c, (cx, cy), r, t)

        elif style == "КВАДРАТ":
            half = s + g
            if self.outline:
                rect(cx-half-1, cy-half-1, half*2+2, half*2+2, oc)
            rect(cx-half, cy-t//2, half, t, c)
            rect(cx, cy-t//2, half, t, c)
            rect(cx-t//2, cy-half, t, half, c)
            rect(cx-t//2, cy, t, half, c)

        # центральная точка
        if self.dot and style != "ТОЧКА":
            if self.outline:
                pygame.draw.circle(surf, oc, (cx, cy), t)
            pygame.draw.circle(surf, c, (cx, cy), max(1, t-1))
