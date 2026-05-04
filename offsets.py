# CS 1.6 Steam (hl.exe) — build 4554
# Если что-то не работает — меняй VIEWANGLES и ENTITY_LIST_BASE через Cheat Engine

PROCESS_NAME = "hl.exe"   # Steam; non-Steam = "cstrike.exe"

HW_DLL     = "hw.dll"
CLIENT_DLL = "client.dll"

# ── hw.dll ────────────────────────────────────────────────────────────────────
VIEWANGLES   = 0x6E3440   # float[3]: pitch, yaw, roll
CLIENT_STATE = 0x68A600   # int: 5 = in-game, 4 = loading

# ── client.dll ────────────────────────────────────────────────────────────────
LOCAL_PLAYER_INDEX = 0x9A8EC4   # int: индекс локального игрока (1–32)
ENTITY_LIST_BASE   = 0x1136F8C  # cl_entity_t array — 33 записи

# ── cl_entity_t structure (GoldSrc) ───────────────────────────────────────────
# struct cl_entity_t {
#   int            index;      // 0x00 (4)
#   qboolean       player;     // 0x04 (4)
#   entity_state_t baseline;   // 0x08 → size 0x94 (148 bytes)
#   entity_state_t prevstate;  // 0x9C → size 0x94
#   entity_state_t curstate;   // 0x130 → size 0x94
#   ...
#   vec3_t         origin;     // 0x44C — рендер-позиция (интерполированная)
# }
CL_ENTITY_SIZE = 0x4CC    # ~1228 байт

# entity_state_t.origin внутри curstate:
CURSTATE_OFF    = 0x130   # curstate начинается здесь
CURSTATE_ORIGIN = CURSTATE_OFF + 0x10   # = 0x140
CURSTATE_HEALTH = CURSTATE_OFF + 0xB0   # = 0x1E0 — health в curstate CS-расширении
CURSTATE_TEAM   = CURSTATE_OFF + 0xFC   # = 0x22C — iuser1 хранит team

RENDER_ORIGIN   = 0x44C   # интерполированная позиция для рисования (точнее)

# ── Константы игры ────────────────────────────────────────────────────────────
TEAM_T       = 1
TEAM_CT      = 2
MAX_PLAYERS  = 32
PLAYER_EYE_Z = 28.0   # высота глаз над origin (для aim в голову +36 ещё)
HEAD_OFFSET  = 64.0   # примерная высота головы над происхождением
