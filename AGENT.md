# NoQuarter 1.3.1 Modernized - Developer & AI Agent Guidelines

Welcome to the **NoQuarter 1.3.1 Modernized** repository. This document serves as the master instruction set for AI coding agents (such as Cursor, GitHub Copilot, Claude Code, Antigravity, and local LLMs) as well as human developers maintaining, debugging, or extending this codebase.

---

## 🧭 Core Directives & Golden Rules

1. **Dual Architecture Preservation (32-bit & 64-bit)**:
   - Every change **MUST** compile and run cleanly on both **32-bit (x86)** and **64-bit (x86_64)** systems for both **Windows** (MSVC) and **Linux** (GCC/Clang/Zig).
   - Never assume pointer sizes (`sizeof(void*)` is 4 bytes on x86, 8 bytes on x64).
   - Be vigilant with struct packing, network serialization, and engine-VM interface structs (`entityState_t`, `playerState_t`). Padding discrepancies between 32-bit and 64-bit builds will desynchronize the network snapshot or crash the engine.

2. **Strict String & Memory Safety**:
   - Never use raw `strcpy`, `strcat`, or unbounded `sprintf`.
   - **Always** use `Q_strncpyz(dst, src, sizeof(dst))` and `Com_sprintf(dst, sizeof(dst), ...)`.
   - Memory allocation must use engine-managed pools (`G_Alloc`, `trap_Alloc`, or mod-specific heaps). Never allocate across DLL boundaries with raw `malloc`/`free`.

3. **No CMYK Textures / Assets**:
   - The classic id Tech 3 OpenGL renderer and 32-bit `libjpeg` implementations **crash** when loading CMYK JPEGs (`Unsupported color conversion request`).
   - All textures in PK3 archives **MUST** be baseline 24-bit sRGB JPEG or uncompressed TGA (Truevision Targa).

4. **HUD & Screen Space Alignment**:
   - The UI and HUD operate in a virtual `640x480` coordinate space scaled to widescreen via `wideXoffset`.
   - Never hardcode screen-width assumptions.
   - Kill popups and center prints have strict vertical layout constraints: Center announcements must start at or below `Y = 384` (`SCREEN_HEIGHT - (SCREEN_HEIGHT * 0.20f)`) using `&cgs.media.limboFont2` (scale `0.22f`) to prevent collision with the left-hand obituary feed.

5. **Universal PK3 Multi-Architecture Layout**:
   - Client and server binaries are separated into architecture-specific PK3 packages so 32-bit and 64-bit clients can connect to the same server without `pure` checksum or PK3 mismatch errors:
     - `nq_b_v1.3.1_64.pk3`: Contains 64-bit binaries (`cgame.mp.x86_64.dll`, `ui.mp.x86_64.dll`, `*.so`).
     - `nq_b_v1.3.1_32.pk3`: Contains 32-bit binaries (`cgame_mp_x86.dll`, `ui_mp_x86.dll`, `*.so`).
     - `nq_v1.3.1_a.pk3` & `nq_v1.3.1_b.pk3`: Core game assets (models, sounds, textures, animations).

---

## 🏛️ Codebase Anatomy

The codebase is split into three primary DLL modules plus scripting libraries:

```
NoQuarter-v1.3.1-Source/
├── src/
│   ├── game/               # Server-Side Game Module (qagame_mp_x86 / qagame.mp.x86_64)
│   │   ├── g_main.c        # Server lifecycle, CVAR initialization, client connection
│   │   ├── g_weapon.c      # Weapon mechanics, firing logic, airstrikes, artillery
│   │   ├── g_combat.c      # Damage calculations, hit detection, death events, obituaries
│   │   ├── g_client.c      # Player spawning, inventory setup, class selection
│   │   ├── g_svcmds.c      # Server console commands and PK3 validation
│   │   └── bg_*.c          # Both-games shared logic (classes, weapon definitions, physics)
│   ├── cgame/              # Client-Side Game Module (cgame_mp_x86 / cgame.mp.x86_64)
│   │   ├── cg_main.c       # Client lifecycle, media registration, event dispatch
│   │   ├── cg_draw.c       # HUD drawing, center print, obituary popups, vote overlays
│   │   ├── cg_ents.c       # Entity interpolation and rendering (airstrike planes, projectiles)
│   │   ├── cg_event.c      # Sound and visual event handling
│   │   └── cg_predict.c    # Client-side movement prediction
│   └── ui/                 # In-Game User Interface (ui_mp_x86 / ui.mp.x86_64)
│       ├── ui_main.c       # UI manager, menu loading, font registration
│       ├── ui_gameinfo.c   # Map and campaign metadata parsing
│       └── ui_shared.c     # Menu parsing, panel buttons, slider controls
├── Lua-libs/               # Embedded Lua 5.1 and SQLite3 native dependencies
├── Lua-scripts/            # Server administration and gameplay Lua scripts
├── config/                 # Reference server configuration files (noquarter3.0.cfg)
├── docs/                   # Documentation, Lua API manual (nqluadocu.htm), and CVAR guides
└── scripts/                # Packaging, texture processing, and Linux cross-compilation tools
```

---

## 🔧 Solved Engine Gotchas & Historical Bugfixes

When working on this repository, keep these past issues and solutions in mind:

### 1. Airstrike Flyover Bomber Planes
- **Problem**: Calling an airstrike played audio, but bombers were invisible.
- **Root Cause**: `cg_main.c` attempted to register `models/mapobjects/planes/ju87.md3` and `spitfire.md3`, which did not exist in modern asset packages. Furthermore, `NUM_FRAME_PROPELLER` was set to `4` while the models had 10 animation frames (`DAnimFrames00`–`DAnimFrames09`).
- **Fix**: Registered `models/mapobjects/etl_plane/junker88.md3` (Axis) and `models/mapobjects/etl_plane/b-25.md3` (Allied) with fallback paths. Updated propeller animation cycle to 10 frames in `cg_ents.c` and delayed second plane drawing until `cent->currentState.pos.trTime`.

### 2. CMYK JPEG Crash on 32-bit Clients
- **Problem**: 32-bit ET:Legacy client crashed when loading maps like `ctf_pool_v2` with `WARNING: (libjpeg) Unsupported color conversion request`.
- **Root Cause**: The 32-bit `libjpeg` does not support CMYK 4-channel JPEGs. The 64-bit client had a newer `libjpeg-turbo` that converted them automatically.
- **Fix**: Re-encoded all custom map textures to baseline 24-bit sRGB and packaged fallback TGA textures directly in `nq_v1.3.1_b.pk3`.

### 3. Kill Print vs. Obituary Feed Collision
- **Problem**: Long player names in center kill notifications clipped across the screen into the left-hand obituary feed.
- **Root Cause**: Center print was rendered at `Y = 360` with wide `limboFont1`.
- **Fix**: Switched center kill notices in `cg_draw.c` and `cg_event.c` to `&cgs.media.limboFont2` (scale `0.22f`) and forced `baseY >= 384` (`SCREEN_HEIGHT - (SCREEN_HEIGHT * 0.20f)`).

### 4. Soldier Shotgun & Secondary Weapon Auto-Selection
- **Mechanic**: Added `g_soldierShotgun` CVAR. When enabled, Soldiers with Heavy Weapons $\ge 4$ can select the Winchester M97 Shotgun as their secondary weapon in the Limbo Menu.
- **Auto-Selection**: When changing classes or skills, the Limbo Menu automatically assigns the best unlocked secondary (SMG for Level 4 Soldier, Akimbo for Level 4 Light Weapons) without forcing the player to hold it upon spawning—the primary weapon stays holstered and active.

---

## 📋 Common Development Workflows

### How to Add a New Server CVAR
1. **Declare the Cvar Struct** in `src/game/g_local.h`:
   ```c
   extern vmCvar_t g_myNewCvar;
   ```
2. **Define and Register in `src/game/g_main.c`**:
   ```c
   vmCvar_t g_myNewCvar;
   // In G_RegisterCvars():
   { &g_myNewCvar, "g_myNewCvar", "1", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qfalse, qtrue },
   ```
   * *Flags*: Use `CVAR_SERVERINFO` to broadcast to clients/browsers, `CVAR_ARCHIVE` to persist in configs, `CVAR_LATCH` if a map restart is required to take effect.
3. **If Needed on Client (`cgame`)**:
   - Declare `cg_myNewCvar` in `src/cgame/cg_local.h`.
   - Register in `src/cgame/cg_main.c` within `cvarTable[]`.
   - Sync via `CS_SYSTEMINFO` or `CS_SERVERINFO` configstring.
4. **Document**:
   - Add the CVAR to `docs/noquarter_commented.txt` and `config/noquarter3.0.cfg`.

### Building the Project (Windows MSVC)
```powershell
# Generate 64-bit solution
cmake -B build64 -S . -A x64

# Generate 32-bit solution
cmake -B build32 -S . -A Win32

# Compile Release binaries
msbuild build64/NoQuarter.slnx /p:Configuration=Release /m
msbuild build32/NoQuarter.slnx /p:Configuration=Release /m
```

### Packaging PK3 Files
PK3 files are standard ZIP archives containing files without leading root path components.
- Binaries go into root of PK3: `cgame.mp.x86_64.dll`, `ui.mp.x86_64.dll`, `cgame.mp.x86_64.so`, etc.
- Server game module (`qagame.mp.x86_64.dll` / `qagame_mp_x86.dll`) resides directly in the server installation root folder (`fs_game/nq/`), **never** inside client-downloaded PK3s.

---

## 🤖 Using with Local AI Models (Ollama)
For offline development without internet access:
1. Navigate to `docs/ai/`
2. Run `ollama create nq-dev -f Modelfile`
3. Launch with `ollama run nq-dev`
See `docs/ai/README.md` for full instructions.
