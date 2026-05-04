import threading, time
import customtkinter as ctk
from tkinter import colorchooser

from memory import GameMemory
from features.aimbot    import Aimbot
from features.esp       import ESPOverlay
from features.bhop      import Bhop
from features.crosshair import Crosshair, STYLES

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

ACCENT   = "#c850ff"
BG_DARK  = "#0d0d0d"
BG_CARD  = "#161616"
BG_CARD2 = "#1a1a1a"


class TrainerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CS 1.6 Trainer")
        self.geometry("360x700")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)

        self.mem   = GameMemory()
        self.aim   = Aimbot(self.mem)
        self.esp   = ESPOverlay(self.mem)
        self.bhop  = Bhop(self.mem)
        self.xhair = Crosshair()

        self._build_ui()
        self.aim.start()
        self.bhop.start()
        self.esp.start()
        self._status_loop()

    def _build_ui(self):
        hdr = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0, height=54)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="CS 1.6 TRAINER",
                     font=("Arial", 16, "bold"), text_color=ACCENT).pack(side="left", padx=16, pady=14)
        self._dot = ctk.CTkLabel(hdr, text="●", font=("Arial", 18), text_color="#ff4444")
        self._dot.pack(side="right", padx=14)
        self._status_lbl = ctk.CTkLabel(hdr, text="NOT ATTACHED", font=("Arial", 10), text_color="#666")
        self._status_lbl.pack(side="right")

        ctk.CTkButton(self, text="ATTACH TO CS 1.6", command=self._attach,
                      fg_color="#1e1040", hover_color="#2e1860",
                      border_color=ACCENT, border_width=1,
                      font=("Arial", 12, "bold"), height=36,
                      corner_radius=8).pack(fill="x", padx=14, pady=(14, 4))

        tabs = ctk.CTkTabview(self, fg_color=BG_CARD,
                              segmented_button_fg_color=BG_CARD2,
                              segmented_button_selected_color="#2a1040",
                              segmented_button_selected_hover_color="#3a1860",
                              text_color="#bbb", text_color_disabled="#555")
        tabs.pack(fill="both", expand=True, padx=14, pady=6)

        for name in ("AIM", "ESP", "PEN", "BHOP", "XHAIR"):
            tabs.add(name)

        self._build_aim_tab(tabs.tab("AIM"))
        self._build_esp_tab(tabs.tab("ESP"))
        self._build_pen_tab(tabs.tab("PEN"))
        self._build_bhop_tab(tabs.tab("BHOP"))
        self._build_xhair_tab(tabs.tab("XHAIR"))

    def _build_aim_tab(self, tab):
        self._aim_sw = self._sw_row(tab, "AIMBOT", self._toggle_aim)
        self._slider_row(tab, "FOV",    2, 60, 15, 1, self._set_fov,    "deg")
        self._slider_row(tab, "SMOOTH", 1, 20,  4, 1, self._set_smooth, "x")
        row = ctk.CTkFrame(tab, fg_color="transparent")
        row.pack(fill="x", padx=6, pady=(4,2))
        ctk.CTkLabel(row, text="TARGET", font=("Arial",11), text_color="#aaa", width=70).pack(side="left")
        self._aim_target = ctk.CTkSegmentedButton(
            row, values=["HEAD","BODY"], command=self._set_aim_target,
            selected_color="#2a1040", selected_hover_color="#3a1860",
            unselected_color=BG_CARD2, font=("Arial",11,"bold"))
        self._aim_target.set("HEAD")
        self._aim_target.pack(side="right")

    def _build_esp_tab(self, tab):
        self._esp_sw  = self._sw_row(tab, "ESP / WALLHACK", self._toggle_esp)
        self._snap_sw = self._sw_row(tab, "SNAPLINES",      self._toggle_snap)
        leg = ctk.CTkFrame(tab, fg_color=BG_CARD2, corner_radius=8)
        leg.pack(fill="x", padx=6, pady=(10,4))
        for col, lbl in [("#ff5050","Direct sight"),("#ffc832","Behind wall"),("#50ff78","PenBox")]:
            r = ctk.CTkFrame(leg, fg_color="transparent")
            r.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(r, text="●", font=("Arial",13), text_color=col).pack(side="left")
            ctk.CTkLabel(r, text=lbl, font=("Arial",11), text_color="#aaa").pack(side="left", padx=6)

    def _build_pen_tab(self, tab):
        self._pen_sw = self._sw_row(tab, "PENBOX", self._toggle_pen)
        info = ctk.CTkFrame(tab, fg_color=BG_CARD2, corner_radius=8)
        info.pack(fill="x", padx=6, pady=(10,4))
        for line in ["Green box = enemy behind a", "penetrable surface.",
                     "", "CS 1.6: metal/wood up to ~500 units.", "Concrete/brick = no penetration."]:
            ctk.CTkLabel(info, text=line, font=("Arial",10),
                         text_color="#666", justify="left").pack(anchor="w", padx=12, pady=1)

    def _build_bhop_tab(self, tab):
        self._bhop_sw = self._sw_row(tab, "BUNNY HOP", self._toggle_bhop)
        info = ctk.CTkFrame(tab, fg_color=BG_CARD2, corner_radius=8)
        info.pack(fill="x", padx=6, pady=(10,4))
        for line in ["Hold SPACE — bhop runs automatically.", "",
                     "Detects landing frame and presses", "SPACE at the exact right moment."]:
            ctk.CTkLabel(info, text=line, font=("Arial",10),
                         text_color="#777", justify="left").pack(anchor="w", padx=12, pady=1)

    def _build_xhair_tab(self, tab):
        self._xh_sw = self._sw_row(tab, "CUSTOM CROSSHAIR", self._toggle_xhair)
        row = ctk.CTkFrame(tab, fg_color="transparent")
        row.pack(fill="x", padx=6, pady=(6,2))
        ctk.CTkLabel(row, text="STYLE", font=("Arial",11), text_color="#aaa", width=70).pack(side="left")
        self._xh_style = ctk.CTkOptionMenu(
            row, values=STYLES, command=self._set_xh_style,
            fg_color=BG_CARD2, button_color="#2a1040",
            button_hover_color="#3a1860", font=("Arial",11))
        self._xh_style.pack(side="right")
        self._slider_row(tab, "SIZE",  2, 30, 10, 1, self._set_xh_size,  "px")
        self._slider_row(tab, "WIDTH", 1,  6,  2, 1, self._set_xh_thick, "px")
        self._slider_row(tab, "GAP",   0, 20,  4, 1, self._set_xh_gap,   "px")
        self._xh_dot_sw = self._sw_row(tab, "CENTER DOT", self._toggle_xh_dot)
        self._xh_dot_sw.select()
        self._xh_out_sw = self._sw_row(tab, "OUTLINE", self._toggle_xh_outline)
        self._xh_out_sw.select()
        row_c = ctk.CTkFrame(tab, fg_color="transparent")
        row_c.pack(fill="x", padx=6, pady=(8,4))
        ctk.CTkLabel(row_c, text="COLOR", font=("Arial",11), text_color="#aaa", width=70).pack(side="left")
        self._color_prev = ctk.CTkLabel(row_c, text="  ", fg_color="#00ff50",
                                        corner_radius=4, width=28, height=18)
        self._color_prev.pack(side="right", padx=(0,4))
        ctk.CTkButton(row_c, text="Pick", command=self._pick_color,
                      fg_color=BG_CARD2, hover_color="#2a1040",
                      font=("Arial",11), height=26, width=70,
                      corner_radius=6).pack(side="right", padx=4)

    def _sw_row(self, parent, label, cmd):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=6, pady=(8,2))
        ctk.CTkLabel(row, text=label, font=("Arial",12,"bold"), text_color="#ddd").pack(side="left")
        sw = ctk.CTkSwitch(row, text="", command=cmd, onvalue=True, offvalue=False,
                           button_color=ACCENT, progress_color="#3d1a6e", width=44)
        sw.pack(side="right")
        return sw

    def _slider_row(self, parent, label, mn, mx, default, step, cmd, unit=""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=6, pady=(2,0))
        ctk.CTkLabel(row, text=label, font=("Arial",10), text_color="#888", width=70).pack(side="left")
        val_lbl = ctk.CTkLabel(row, text=f"{default}{unit}",
                               font=("Arial",10,"bold"), text_color=ACCENT, width=40)
        val_lbl.pack(side="right")
        def _cb(v):
            val_lbl.configure(text=f"{int(v)}{unit}")
            cmd(v)
        sl = ctk.CTkSlider(row, from_=mn, to=mx, number_of_steps=int((mx-mn)/step),
                           command=_cb, button_color=ACCENT, progress_color=ACCENT)
        sl.set(default)
        sl.pack(side="left", fill="x", expand=True, padx=8)

    def _attach(self):
        ok, msg = self.mem.connect()
        if ok:
            self._dot.configure(text_color="#44ff88")
            self._status_lbl.configure(text="ATTACHED — hl.exe")
        else:
            self._dot.configure(text_color="#ff4444")
            self._status_lbl.configure(text=f"ERROR: {msg[:30]}")

    def _toggle_aim(self):        self.aim.enabled      = self._aim_sw.get()
    def _toggle_esp(self):        self.esp.enabled      = self._esp_sw.get()
    def _toggle_pen(self):        self.esp.pen_enabled  = self._pen_sw.get()
    def _toggle_snap(self):       self.esp.snaplines    = self._snap_sw.get()
    def _toggle_bhop(self):       self.bhop.enabled     = self._bhop_sw.get()
    def _toggle_xhair(self):      self.xhair.enabled    = self._xh_sw.get()
    def _toggle_xh_dot(self):     self.xhair.dot        = self._xh_dot_sw.get()
    def _toggle_xh_outline(self): self.xhair.outline    = self._xh_out_sw.get()

    def _set_fov(self, v):        self.aim.fov          = float(v)
    def _set_smooth(self, v):     self.aim.smooth       = float(v)
    def _set_xh_size(self, v):    self.xhair.size       = int(v)
    def _set_xh_thick(self, v):   self.xhair.thickness  = int(v)
    def _set_xh_gap(self, v):     self.xhair.gap        = int(v)
    def _set_aim_target(self, v): self.aim.head_aim     = (v == "HEAD")
    def _set_xh_style(self, v):   self.xhair.style      = STYLES.index(v)

    def _pick_color(self):
        col = colorchooser.askcolor(title="Crosshair color",
                                    color='#%02x%02x%02x' % self.xhair.color)
        if col and col[0]:
            self.xhair.color = tuple(int(c) for c in col[0])
            self._color_prev.configure(fg_color='#%02x%02x%02x' % self.xhair.color)

    def _status_loop(self):
        if self.mem.connected and not self.mem.alive():
            self._dot.configure(text_color="#ff4444")
            self._status_lbl.configure(text="DISCONNECTED")
        self.after(2000, self._status_loop)


if __name__ == "__main__":
    TrainerApp().mainloop()
