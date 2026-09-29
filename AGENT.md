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

5. **Universal Unified PK3 Multi-Architecture Layout**:
   - All client binaries are bundled into a single unified binary package so 32-bit and 64-bit clients on Windows and Linux connect without pure-server checksum or PK3 mismatch errors:
     - `nq_b_v1.3.1b7.pk3`: Contains exactly 8 client binaries: `cgame_mp_x64.dll`, `ui_mp_x64.dll`, `cgame_mp_x86.dll`, `ui_mp_x86.dll`, `cgame.mp.x86_64.so`, `ui.mp.x86_64.so`, `cgame.mp.i386.so`, `ui.mp.i386.so`.
     - `nq_v1.3.1b7.pk3`: Core game assets (models, sounds, textures, animations). Always zip an exported/clean copy; a working folder with `.svn`/`.git` metadata roughly doubles its size.
   - **Module file names are fixed by the engine** (ET:Legacy `Sys_GetDLLName` in `qcommon.h`): Windows uses underscores and `x86`/`x64` (`qagame_mp_x64.dll`), Linux uses dots and `i386`/`x86_64` (`qagame.mp.x86_64.so`). Names like `cgame.mp.x86_64.dll` or `qagame_mp_x64.so` are never loaded; don't produce or ship them.
   - The server module (`qagame`) is **never** put inside a pk3; it ships as a loose file in the server's `nq/` folder.

6. **Bad Content Must Not Shut Down the Server**:
   - On ET:Legacy, `G_Error()` in qagame shuts the whole server down and drops every player. Don't use it for problems caused by maps, assets, configs or player input; log a warning (`G_Printf`/`G_LogPrintf`) and skip the bad item instead (see the MapScript fix below). Keep `G_Error()` for genuine internal bugs where continuing would corrupt state.
   - Anything a client sends (vote IDs, fireteam targets, client numbers, string lengths) must be range-checked before it's used as an index.

7. **Server Timing Assumes `sv_fps 20`**:
   - NoQuarter's game code assumes 50 ms server frames (`SERVER_FRAMETIME`, used in ~230 places). `G_InitGame` warns if `sv_fps` isn't 20. Don't add code that depends on a different frame rate.

8. **No Machine-Specific Paths in Committed Files or Releases**:
   - Never hardcode a developer's own paths (user folders, local test-server installs, drive letters) in scripts, configs, Lua or docs. Use paths relative to the repo, engine cvars (`fs_homepath`, `fs_game`) at runtime, or environment variables.
   - The build configs strip build paths from the binaries: `src/CMakeLists.txt` uses `/d1trimfile:` and `/PDBALTPATH:%_PDB%` (MSVC), and `scripts/build_linux.py` uses `-ffile-prefix-map`, `-g0` and `-s`. Keep those flags when editing the builds.
   - Never ship personal admin GUIDs, passwords or keys in release configs or Lua scripts.

---

## 🏛️ Codebase Anatomy

The codebase is organized into modules, support libraries, and packaging tooling:

```text
NoQuarter-v1.3.1-Source/    # Git Repository Root
├── src/
│   ├── game/               # Server Game Module (Windows: qagame_mp_x86/x64.dll, Linux: qagame.mp.i386/x86_64.so)
│   │   ├── g_main.c        # Lifecycle, CVAR initialization, client connection, PK3 check
│   │   ├── g_weapon.c      # Weapon mechanics, firing logic, airstrikes, artillery
│   │   ├── g_combat.c      # Damage calculations, hit detection, death events, obituaries
│   │   ├── g_client.c      # Player spawning, inventory, class selection, IP handling
│   │   ├── g_referee.c     # Referee commands, authentication lockout tracking
│   │   ├── g_shrubbot.c    # Shrubbot admin system, permission levels, IP bans
│   │   ├── g_svcmds.c      # Server console commands
│   │   ├── g_script.c      # Map script parser (unknown actions/events are skipped with a warning)
│   │   ├── g_etbot_interface.cpp # Omni-Bot glue (Bot_Interface_Init loads the bot library)
│   │   └── bg_*.c          # Shared logic (classes, weapon definitions, physics)
│   ├── cgame/              # Client Game Module (Windows: cgame_mp_x86/x64.dll, Linux: cgame.mp.i386/x86_64.so)
│   │   ├── cg_main.c       # Client lifecycle, media registration, event dispatch
│   │   ├── cg_draw.c       # HUD drawing, center print, obituary popups, vote overlays
│   │   ├── cg_ents.c       # Entity interpolation and rendering (airstrike planes, projectiles)
│   │   ├── cg_event.c      # Sound and visual event handling
│   │   └── cg_predict.c    # Client-side movement prediction
│   ├── ui/                 # In-Game User Interface (Windows: ui_mp_x86/x64.dll, Linux: ui.mp.i386/x86_64.so)
│   │   ├── ui_main.c       # UI manager, menu loading, font registration
│   │   ├── ui_gameinfo.c   # Map and campaign metadata parsing
│   │   └── ui_shared.c     # Menu parsing, panel buttons, slider controls
│   ├── lua/lua-5.1.5/      # Lua 5.1 runtime (lua5.1.dll on Windows; built into qagame on Linux)
│   ├── luasql/ + sqlite3/  # LuaSQL SQLite driver used by Lua scripts (Windows sqlite3.dll; built into Linux qagame)
│   └── CMakeLists.txt      # Windows build flags (incl. path stripping, see rule 8)
├── Omnibot/                # Omni-Bot interface headers; Common/BotLoadLibrary.cpp loads the bot DLL/.so
├── etmain/                 # Base engine UI definitions & headers (menudef.h, menudef2.h)
├── mapscripts/             # Custom map script fixes
├── Lua-libs/               # Legacy LuaSQL / LuaSocket packages (not used by the current build)
├── Lua-scripts/            # Server administration and gameplay Lua scripts
├── config/                 # Reference server configuration files (noquarter3.0.cfg)
├── docs/                   # Documentation, knowledge base, Lua API manual, CVAR guides
│   └── AUDIT_2026-09-25.md # Every 1.3.1 audit fix, by ID (grep the code for "[NQ 1.3.1 - Audit <ID>]")
└── scripts/                # Build and packaging automation
    ├── build_linux.py      # Cross-compiles 32-bit & 64-bit Linux .so binaries using Zig cc
    └── package_release.py  # Builds the unified PK3s and the DLL's/ server folders into release/ (see below)

Build output (git-ignored):
build64/, build32/          # Command-line CMake builds (Windows: build64/src/Release/)
out/build/x64-Release/src/  # Visual Studio "Open Folder" builds (from CMakeSettings.json)
build64/Release/linux/      # build_linux.py output (and build32/Release/linux/)
release/                    # package_release.py output (default)

Parent Trunk Directory Structure (Outside Git Repo):
../assets/                  # SVN base asset repository (unpacked models, textures, sounds, scripts)
```

---

## 🔧 Solved Engine Gotchas & Historical Bugfixes

When working on this repository, keep these past issues and solutions in mind:

### 1. Airstrike Flyover Bomber Planes
- **Problem**: Calling an airstrike played audio, but bombers were invisible.
- **Root Cause**: `cg_main.c` attempted to register `models/mapobjects/planes/ju87.md3` and `spitfire.md3`, which did not exist in modern asset packages. Furthermore, `NUM_FRAME_PROPELLER` was set to `4` while the models had 10 animation frames (`DAnimFrames00`–`DAnimFrames09`).
- **Fix**: Registered `models/mapobjects/etl_plane/junker88.md3` (Axis) and `models/mapobjects/etl_plane/b-25.md3` (Allied). Updated propeller animation cycle to 10 frames in `cg_ents.c` and delayed second plane drawing until `cent->currentState.pos.trTime`. Legacy 2.60b fallbacks and obsolete `models/mapobjects/planes/` clones were removed.

### 2. CMYK JPEG Crash on 32-bit Clients
- **Problem**: 32-bit ET:Legacy client crashed when loading maps like `ctf_pool_v2` with `WARNING: (libjpeg) Unsupported color conversion request`.
- **Root Cause**: The 32-bit `libjpeg` does not support CMYK 4-channel JPEGs. The 64-bit client had a newer `libjpeg-turbo` that converted them automatically.
- **Fix**: Re-encoded all custom map textures to baseline 24-bit sRGB and packaged fallback TGA textures directly in `nq_v1.3.1b7.pk3`.

### 3. Kill Print vs. Obituary Feed Collision
- **Problem**: Long player names in center kill notifications clipped across the screen into the left-hand obituary feed.
- **Root Cause**: Center print was rendered at `Y = 360` with wide `limboFont1`.
- **Fix**: Switched center kill notices in `cg_draw.c` and `cg_event.c` to `&cgs.media.limboFont2` (scale `0.22f`) and forced `baseY >= 384` (`SCREEN_HEIGHT - (SCREEN_HEIGHT * 0.20f)`).

### 4. Soldier Shotgun & Secondary Weapon Auto-Selection
- **Mechanic**: Added `g_soldierShotgun` CVAR. When enabled, Soldiers with Heavy Weapons $\ge 4$ can select the Winchester M97 Shotgun as their secondary weapon in the Limbo Menu.
- **Auto-Selection**: When changing classes or skills, the Limbo Menu automatically assigns the best unlocked secondary (SMG for Level 4 Soldier, Akimbo for Level 4 Light Weapons) without forcing the player to hold it upon spawning—the primary weapon stays holstered and active.

### 5. NQKey Buffer Overflow & 31-Char Truncation
- **Problem**: In `g_main.c`, `NQKey` generation used a `char key[32]` buffer with `Q_strncpyz(..., 32)`. A 32-byte key was truncated to 31 bytes plus a NUL terminator, causing potential stack buffer overflows on oversized keys.
- **Fix**: Widened `key` to `char key[64]` and bound copying to `sizeof(key)`.

### 6. IPv6 Truncation and Buffer Widening
- **Problem**: Legacy 16-byte `char ip[16]` buffers truncated standard IPv6 addresses (up to 45 chars) and caused crashes or invalid ban comparisons.
- **Fix**: Defined `MAX_IP_LENGTH_V6 64` in `g_local.h`. Widened `clientPersistant_t.client_ip` and `g_shrubbot_ban_t.ip` to 64 bytes. Replaced unsafe in-place mutation of `client_ip` in `!finger` with a dedicated, buffer-safe `G_StripPort()`.

### 7. ConfigString Index Overflow Safety
- **Problem**: When configstrings filled up, `G_FindConfigstringIndex` returned `0`. Index 0 is a valid configstring (`CS_SERVERINFO`), leading to silent string overwriting and data corruption.
- **Fix**: On overflow, `G_FindConfigstringIndex` immediately calls `G_Error()`, halting before memory or asset state can be corrupted.

### 8. Configurable Referee Authentication Lockout
- **Problem**: Failed referee logins used a hardcoded 900-second lockout and used `level.time`, which is subject to integer rollover and map restarts.
- **Fix**: Added three CVARs used in `g_referee.c`: `g_authFailures` (default 3 failed `/ref` passwords before a kick + temp-ban; 0 = no lockout, still logged), `g_authFailBanTime` (default 300, ban length in **seconds**), and `g_authFailExpireTime` (default 900 seconds before a failure is forgotten). Replaced `level.time` with `time(NULL)` (epoch seconds) and implemented Y2038-safe eviction logic. Failures are tracked per address without the port (Audit L5) and every attempt is logged with `SECURITY:`.

### 9. Omni-Bot Crash on 64-bit Windows Servers
- **Problem**: A 64-bit Windows server with `omnibot_enable 1` died with `Received signal 11` right after `Game Initialization completed`, on every map.
- **Root Cause**: `Omnibot_LoadLibrary()` (`Omnibot/Common/BotLoadLibrary.cpp`) only looked for `omnibot_et.dll`, the 32-bit build, so `LoadLibrary` failed with error 193. The error reporter `OB_ShowLastError()` then called `FormatMessage` without `FORMAT_MESSAGE_IGNORE_INSERTS`; error 193's text contains `%1`, so `FormatMessage` failed and the code ran `strlen()` on a NULL buffer.
- **Fix**: On `_WIN64`, try `omnibot_et_x64.dll` first (mirroring the `.x86_64.so` lookup Linux already had), then the old names. `OB_ShowLastError()` now uses `FORMAT_MESSAGE_IGNORE_INSERTS`, checks the result, and prints the error number, so a failed bot load logs a message and the server keeps running.

### 10. Maps From Other Mods Shut Down the Server
- **Problem**: Maps made for other mods (e.g. True Combat: Elite: `dem_snowtown`, `obj_office`) use map-script actions such as `wm_camo` that NQ doesn't have. `G_Script_ScriptParse()` called `G_Error()`, which ET:Legacy turns into a full server shutdown.
- **Fix**: `g_script.c` now warns and skips an unknown action (and a `{ }` block right after it) or an unknown event with its whole block. Truncated scripts and mismatched braces are still fatal. Tagged `[NQ 1.3.1 - MapScript]`.

### 11. 1.3.1 Source Audit (2026-09-25)
- A full review fixed player-triggerable server crashes (e.g. `/fireteam kick` on yourself), unchecked client-supplied indexes (map vote IDs), IPv6 player rejection, `et.G_LogPrint` format-string use, XP-save path traversal via fake GUIDs, shrubbot table overflows, 64-bit Linux `long`/`SinCos`/`Q_rsqrt` bugs, and client/UI off-by-one indexes.
- Every fix is tagged `[NQ 1.3.1 - Audit <ID>]` in the code and listed in `docs/AUDIT_2026-09-25.md`. Read it before touching those areas.

### 12. Debugging Server Crashes on Windows
- **`Received signal 11` with no location**: ET:Legacy catches access violations itself and only prints the signal number; NQ's own crash reporter (`g_crash.c` -> `nq/crash.log`) only fires for some exception types (e.g. stack overflow). To find the exact line, open `etlded.exe` in Visual Studio (File > Open > Project/Solution), set the launch arguments and working directory, keep the matching `qagame_mp_x64.pdb` next to the DLL, enable Win32 Exceptions, and press F5. The call stack shows the NQ function and line.
- **Don't redirect the dedicated server's output** (`etlded.exe ... > file.log`). ET:Legacy's Windows console code (`con_win32.c`) doesn't check whether stdout is a real console, and a redirected server crashes on its first frame. Capture output with `+set logfile 2` instead (writes `nq/etconsole.log`).
- **Command-line `+set` loses to cfg files**: the engine applies every `+set` before running any `+exec`, so a value set in `noquarter.cfg` overrides the same cvar given on the command line. To change a cvar for a test, edit the cfg (or `+set` it *after* the map starts via rcon).
- **Check which build you deployed**: command-line builds go to `build64/src/Release`, Visual Studio "Open Folder" builds to `out/build/x64-Release/src`. Compare file dates, and look for a string added by the latest fix in the DLL, before assuming a fix didn't work.

### 13. Lua SQLite (LuaSQL) on Linux and Windows
- **Linux**: separate `liblua5.1.so` / `sqlite3.so` never worked (built with `-fvisibility=hidden`, so they exported nothing, and qagame already has its own Lua). Fix: `build_linux.py` compiles LuaSQL + SQLite into `qagame` with `-DNQ_BUILTIN_LUASQL`, and `G_LuaInit` (`src/game/g_lua.c`) registers `package.preload["luasql.sqlite3"]`. `require("luasql.sqlite3")` then needs no files. Verified on the Linux VPS ("XPSave: SQLite Database initialized successfully."). Don't ship the small stub `.so` files the script still writes.
- **Windows**: `qagame` imports `lua5.1.dll`, which must sit next to `etlded.exe`. The LuaSQL driver `sqlite3.dll` (exports `luaopen_luasql_sqlite3`) goes in `nq/lualibs/luasql/sqlite3.dll`, because the C module path is `<fs_homepath>/<fs_game>/lualibs/?.dll`.
- **`lua_allowedModules`**: if non-empty, only scripts whose SHA1 is listed load ("disallowed by ACL"). Ship it as `""`.

---

## ⚠️ Known Issues

- None open. (Linux Lua SQLite was fixed in 1.3.1b7; see Solved #13.)
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
   // Add a row to gameCvarTable[]:
   // { &cvar, "name", "default", flags, modificationCount, trackChange, fConfigReset }
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
Requires Visual Studio 2026 (the `Visual Studio 18 2026` CMake generator produces `.slnx` solutions).
```powershell
# Generate 64-bit solution
cmake -B build64 -S . -A x64

# Generate 32-bit solution
cmake -B build32 -S . -A Win32

# Compile Release binaries (output: build64/src/Release, build32/src/Release)
msbuild build64/NoQuarterWrapper.slnx /p:Configuration=Release /m
msbuild build32/NoQuarterWrapper.slnx /p:Configuration=Release /m
```
Or open the folder in Visual Studio, pick **x64-Release** / **x86-Release** (`CMakeSettings.json`) and Build All; output goes to `out/build/<config>/src/`.

### Building for Linux
```bash
python scripts/build_linux.py            # uses zig from PATH, ZIG_EXE, or ~/zig/
```
Outputs `qagame/cgame/ui.mp.x86_64.so` to `build64/Release/linux/`, and the `i386` set to `build32/Release/linux/`. Lua and LuaSQL/SQLite are compiled into `qagame` (`NQ_BUILTIN_LUASQL`); the small `liblua5.1.so` / `sqlite3.so` it also writes are not shipped.

### Packaging PK3 Files
PK3 files are standard ZIP archives containing files without leading root path components.
- `nq_b_v1.3.1b7.pk3` holds exactly the 8 client binaries listed in rule 5, at the root of the zip.
- The server game module (`qagame_mp_x64.dll`, `qagame_mp_x86.dll`, `qagame.mp.x86_64.so`, `qagame.mp.i386.so`) goes loose in the server's `nq/` folder, **never** inside a client-downloaded PK3.
- `python scripts/package_release.py` builds both pk3s and the `DLL's/<Windows|Linux>/<32 Bit|64 Bit>/` server folders. It uses whichever Windows build folder is newer (override with `NQ_BUILD64_DIR` / `NQ_BUILD32_DIR`) and needs the current `nq_v1.3.1b7.pk3` in the release folder as its base.
  - `NQ_RELEASE_DIR`: release folder (default `release/` in the repo, git-ignored).
  - `ET64_DIR`, `ET32_DIR`, `NQ_CLIENT_DIR`: optional local install `nq/` folders to copy the build into for testing. Nothing is copied unless these are set.

---

## 🤖 Using with Local AI Models (Ollama)
For offline development without internet access:
1. Navigate to `docs/ai/`
2. Run `ollama create nq-dev -f Modelfile`
3. Launch with `ollama run nq-dev`
See `docs/ai/README.md` for full instructions.
