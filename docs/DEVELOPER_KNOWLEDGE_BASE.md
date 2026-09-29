# NoQuarter 1.3.1 Modernized - Developer Knowledge Base & Architecture Manual

> **Author**: NoQuarter Modernized Development Team  
> **Target Audience**: Engine Developers, Modders, Systems Engineers, and AI Development Agents  
> **Last Updated**: September 2026  
> **Version**: 1.3.1 Modernized

---

## Table of Contents
1. [Introduction & Historical Context](#1-introduction--historical-context)
2. [id Tech 3 Engine & Quake 3 VM Architecture](#2-id-tech-3-engine--quake-3-vm-architecture)
3. [Dual-Architecture System (32-Bit & 64-Bit Interoperability)](#3-dual-architecture-system-32-bit--64-bit-interoperability)
4. [Rendering Pipeline, Shaders & Asset Pitfalls](#4-rendering-pipeline-shaders--asset-pitfalls)
5. [Coordinate System, Widescreen Scaling & HUD Alignment](#5-coordinate-system-widescreen-scaling--hud-alignment)
6. [Gameplay Systems, Weapons & Limbo Mechanics](#6-gameplay-systems-weapons--limbo-mechanics)
7. [CVAR Engineering & Synchronization](#7-cvar-engineering--synchronization)
8. [Lua Scripting Subsystem](#8-lua-scripting-subsystem)
9. [Build, Compilation & PK3 Distribution Pipeline](#9-build-compilation--pk3-distribution-pipeline)
10. [Troubleshooting Playbook & Solved Engine Bugs](#10-troubleshooting-playbook--solved-engine-bugs)

---

## 1. Introduction & Historical Context

The original **NoQuarter (NQ)** mod for *Wolfenstein: Enemy Territory (W:ET)* was created in the mid-2000s by a passionate group of developers (including IRATA, jaquboss, Meyer, ReyalP, and Lucifer). Over the next 15 years, it became one of the most popular mods in ET history due to its expanded class skill trees, unique weaponry (Shotgun, Venom Gun, BAR, MP34, Bazooka), multi-level airstrikes, and rich Lua scripting capabilities.

However, historical releases (like 1.2.7, 1.2.9, and unreleased 1.3.0 development snapshots) suffered from severe modern compatibility hurdles:
* **The 32-Bit Limitation**: Built as 32-bit x86 DLLs/QVMs, unable to run natively on modern 64-bit ET:Legacy dedicated servers or 64-bit client builds.
* **Scabbed & Patchwork Code**: Over the years, community members patched pieces onto the codebase without centralized documentation, leaving cryptic bugs, struct packing landmines, and brittle UI scripts.
* **Asset & Shader Incompatibilities**: Older assets triggered silent crashes or memory corruption in newer OpenGL renderers (e.g. CMYK JPEGs in custom map packs).
* **Outdated UI & HUD Collisions**: Standard 4:3 UI layouts broke or overlapped on widescreen/ultrawide displays, and kill notifications collided directly with obituary feeds.

**NoQuarter 1.3.1 Modernized** resolves these challenges by introducing:
* Dual-architecture Windows and Linux binaries (native 32-bit and 64-bit).
* Universal multi-architecture PK3 packaging for seamless cross-play.
* Modernized ET:Legacy-style intermission, map voting panels, and widescreen calibration.
* Sanitized rendering pipelines, restored MD3 bomber animations, and resolved HUD text collisions.
* Clean CMake build automation with continuous cross-compilation support.

---

## 2. id Tech 3 Engine & Quake 3 VM Architecture

NoQuarter is built on id Software's **id Tech 3** engine. The game is divided into three distinct dynamically loaded modules (DLLs on Windows, `.so` shared libraries on Linux):

```
+-------------------------------------------------------------------------+
|                              ET ENGINE                                  |
|            (Networking, OpenGL Renderer, Sound System, Filesystem)       |
+------------------------------------+------------------------------------+
                                     |
               +---------------------+---------------------+
               |                     |                     |
               v                     v                     v
        +--------------+      +--------------+      +--------------+
        |    qagame    |      |    cgame     |      |      ui      |
        | (Server-Side |      | (Client-Side |      | (User Inter- |
        |  Simulation) |      |  Rendering & |      | face & Menu  |
        |              |      |  Prediction) |      |   Scripts)   |
        +--------------+      +--------------+      +--------------+
```

### Module Responsibilities:

1. **`qagame` (`src/game/`)**:
   * Runs exclusively on the host/server.
   * Authoritative simulation: physics, weapon firing, damage/hit detection, player spawning, AI/Omni-Bot routing, and Lua scripts.
   * Key structs: `gentity_t` (entities in the world), `gclient_t` (player session and gameplay state), `level_locals_t` (`level`, tracking server match state).

2. **`cgame` (`src/cgame/`)**:
   * Runs on each connected client.
   * Responsible for interpolation, client-side movement prediction (`CG_PredictPlayerState`), entity rendering (`CG_AddPacketEntities`), HUD drawing (`CG_DrawCenterString`, `CG_DrawPMItems`), sound triggering, and visual particle effects.
   * Key structs: `centity_t` (client entity representation), `cg_t` (`cg`, local client state), `cgs_t` (`cgs`, static media handles, shaders, fonts, and server info).

3. **`ui` (`src/ui/`)**:
   * Handles the in-game menus, limbo screen, server browser, options, and vote menus.
   * Interfaces with `.menu` script definitions located in `scripts/` and assets in PK3 archives.

### The Engine Trap Interface
Modules communicate with the core engine through system calls ("traps"):
* **Server Traps (`trap_*`)**: `trap_SendServerCommand()`, `trap_SnapVector()`, `trap_Cvar_Register()`, `trap_LinkEntity()`.
* **Client Traps (`trap_*`)**: `trap_R_RegisterModel()`, `trap_R_AddRefEntityToScene()`, `trap_S_StartSound()`.

---

## 3. Dual-Architecture System (32-Bit & 64-Bit Interoperability)

A major hurdle in Wolfenstein: Enemy Territory was that early engines ran mod modules inside a custom 32-bit virtual machine (QVM) or loaded 32-bit native DLLs. Modern servers and clients (such as ET:Legacy 64-bit) require native 64-bit shared libraries.

### 1. Pointer Sizing & Struct Packing
* On 32-bit x86, pointers are 4 bytes (`sizeof(void*) == 4`).
* On 64-bit x86_64, pointers are 8 bytes (`sizeof(void*) == 8`).

> [!CAUTION]
> **Never cast pointers to `int` or `long`**. Always use `intptr_t` or `uintptr_t` defined in `<stdint.h>`.
> Do not pass structs containing raw pointers across network RPCs or in snapshot buffers (`entityState_t`). Use entity numbers (`int number`) or indices.

### 2. Universal PK3 Multi-Architecture Layout
When clients connect to a pure server (`sv_pure 1`), the engine verifies that the client's PK3 checksums match the server's PK3 checksums. In legacy setups, splitting 32-bit and 64-bit binaries into separate PK3 files caused pure-server rejections when mixed clients joined.

NoQuarter 1.3.1 solves this cleanly with a **Unified Client Binary Package**:
```text
nq/
├── nq_v1.3.1b7.pk3            # Unified game assets (textures, sounds, models, menus, shaders)
└── nq_b_v1.3.1b7.pk3          # Unified client binaries (all architectures):
    ├── cgame_mp_x64.dll       # Windows x64 Client Game
    ├── ui_mp_x64.dll          # Windows x64 UI
    ├── cgame_mp_x86.dll       # Windows x86 Client Game
    ├── ui_mp_x86.dll          # Windows x86 UI
    ├── cgame.mp.x86_64.so     # Linux x64 Client Game
    ├── ui.mp.x86_64.so        # Linux x64 UI
    ├── cgame.mp.i386.so       # Linux x86 Client Game
    └── ui.mp.i386.so          # Linux x86 UI
```

These names are not a choice. ET:Legacy builds the file name it loads with `Sys_GetDLLName` (`qcommon.h`): `name "_mp_" ARCH ".dll"` on Windows (`x86`, `x64`) and `name ".mp." ARCH ".so"` on Linux (`i386`, `x86_64`). Any other spelling (for example `cgame.mp.x86_64.dll` or `qagame_mp_x64.so`) is never loaded and only adds download size.

The server binary (`qagame_mp_x64.dll`, `qagame_mp_x86.dll`, `qagame.mp.x86_64.so`, or `qagame.mp.i386.so`) is **never** placed inside a PK3; it resides directly on the server's filesystem in the `fs_game` folder (`nq/`), next to its libraries:

| Server | Game module | Lua runtime | SQLite driver (Lua scripts) | Omni-Bot (`nq/omni-bot/`) |
| :--- | :--- | :--- | :--- | :--- |
| Windows x64 | `qagame_mp_x64.dll` | `lua5.1.dll` (next to `etlded.exe`) | `nq/lualibs/luasql/sqlite3.dll` | `omnibot_et_x64.dll` |
| Windows x86 | `qagame_mp_x86.dll` | `lua5.1.dll` (next to `etlded.exe`) | `nq/lualibs/luasql/sqlite3.dll` | `omnibot_et.dll` |
| Linux x86_64 | `qagame.mp.x86_64.so` | built into qagame | built into qagame (`NQ_BUILTIN_LUASQL`) | `omnibot_et.x86_64.so` |
| Linux i386 | `qagame.mp.i386.so` | built into qagame | built into qagame (`NQ_BUILTIN_LUASQL`) | `omnibot_et.so` |

> **Linux Lua SQLite:** separate `liblua5.1.so` / `sqlite3.so` files never worked (they were built with `-fvisibility=hidden` and exported nothing, and qagame has its own Lua). Since 1.3.1b7, `build_linux.py` compiles LuaSQL + SQLite into `qagame` and `G_LuaInit` registers `package.preload["luasql.sqlite3"]`, so no extra files are needed. Verified on a Linux server.

Because all client binaries across all architectures reside inside `nq_b_v1.3.1b7.pk3`, every client computes the exact same PK3 checksum regardless of OS or bitness, eliminating pure-server mismatch errors permanently.

---

## 4. Rendering Pipeline, Shaders & Asset Pitfalls

### 1. The CMYK vs. sRGB JPEG Crash Bug
* **The Symptom**: A 32-bit client crashes with:
  `WARNING: (libjpeg) Unsupported color conversion request`
  `ERROR: Image loader failed to parse an image textures/...`
* **Root Cause**: Many map authors exported textures from Adobe Photoshop in **CMYK print mode (4 color channels)** rather than RGB (3 color channels). The 32-bit `libjpeg` engine module cannot decode CMYK JPEGs.
* **The Fix**:
  * Every JPEG texture must be strictly encoded as baseline **24-bit sRGB**.
  * Use Python's `PIL.Image.convert('RGB')` before packaging any custom map textures into mod PK3s.
  * Always provide a fallback `.tga` when a `.shader` file explicitly specifies a `.tga` extension.

### 2. MD3 Models & The Airstrike Flyover Restoration
* **Bomber Models**: Axis uses `junker88.md3`; Allies uses `b-25.md3`.
* **Registration**: Points to `models/mapobjects/etl_plane/junker88.md3` and `b-25.md3`. (Legacy 2.60b plane fallbacks were removed to avoid duplicate asset registration).
* **Propeller Animations**: Both the Junkers Ju-88 and B-25 Mitchell models contain **10 animation frames** (`DAnimFrames00` through `DAnimFrames09`).
  * In `src/cgame/cg_ents.c`:
    ```c
    #define NUM_FRAME_PROPELLER 10
    #define TIME_FRAME_PROPELLER (1000 / NUM_FRAME_PROPELLER)
    ```
  * Cycling with `(cg.time / TIME_FRAME_PROPELLER) % NUM_FRAME_PROPELLER` ensures smooth 360-degree blade rotation.
* **Staggered Multi-Wave Bombers**: For Level 3+ Field Ops airstrikes with two waves (`ent->count = 2`), the second wave has `pos.trTime = level.time + 2000`. In `CG_MovePlane()`, the model must remain hidden until `cg.time >= cent->currentState.pos.trTime`, preventing planes from hovering frozen in mid-air before their run begins.

---

## 5. Coordinate System, Widescreen Scaling & HUD Alignment

### 1. Virtual 640x480 Coordinate Space
All id Tech 3 UI and HUD calculations operate in a virtual `640x480` coordinate space. On widescreen (16:9, 16:10, 21:9) monitors, the engine computes an horizontal offset:
```c
float wideXoffset = (SCREEN_WIDTH - 640.0f) * 0.5f;
```
* **Left-anchored elements** (e.g. kill popups, chat feed): Must offset outward or remain at `0` depending on whether they are pinned to screen edge or 4:3 safe zone.
* **Center-anchored elements** (e.g. crosshair, center announcements): Centered at `320.0f`.
* **Right-anchored elements** (e.g. compass, ammo): Offset by `640.0f + wideXoffset * 2.0f`.

### 2. Resolving the Center Print vs. Obituary Collision
* **The Bug**: When killing someone, the center screen message (`You killed [Player]`) would stretch across the screen and collide with the left-hand kill obituary feed.
* **The Solution**:
  1. **Font Choice**: Never use `&cgs.media.limboFont1` for dynamic match announcements; its glyphs are too wide. Use `&cgs.media.limboFont2` with a scale of `0.22f`.
  2. **Vertical Clearance**: The left-hand popup feed spans `Y = 245` down to `Y = 360`. In `CG_DrawCenterString()` and `CG_Obituary()`:
     ```c
     // Enforce vertical safety floor below obituary feed
     if ( baseY < 384 ) {
         baseY = 384; // SCREEN_HEIGHT - (SCREEN_HEIGHT * 0.20f)
     }
     ```

---

## 6. Gameplay Systems, Weapons & Limbo Mechanics

### 1. Soldier Secondary Winchester M97 Shotgun
* **CVAR**: `g_soldierShotgun` (default: `1`).
* **Requirement**: Player class must be `PC_SOLDIER` with `SK_HEAVY_WEAPONS >= 4`.
* **Mechanics**: When enabled, the Limbo Menu adds the Shotgun (`WP_SHOTGUN`) to the secondary weapon carousel for Soldiers.
* **Implementation in `src/game/g_client.c` & `src/ui/ui_shared.c`**:
  * Evaluates `COM_BitCheck(ent->client->sess.skillBits, SK_HEAVY_WEAPONS, 4)`.
  * Dynamically populates or removes the shotgun entry from the Limbo secondary carousel.

### 2. Limbo Secondary Weapon Auto-Selection
* When opening Limbo or switching classes, the menu evaluates the player's skill level and automatically equips the best unlocked secondary:
  * **Soldier (Heavy Weapons $\ge 4$)**: Thompson / MP40 SMG.
  * **Any Class (Light Weapons $\ge 4$)**: Akimbo Pistols (or Silenced Akimbo for Covert Ops).
  * **Default / Lower Levels**: Standard single pistol.
* **Spawn State**: The player's active held weapon upon spawning is always their **Primary Weapon**, with the secondary weapon holstered.

### 3. Infinite Resource Cabinets
* **CVAR**: `g_infiniteCabinets` (default: `0`).
* **Behavior**: When set to `1`, health and ammo cabinets never deplete or enter cooldown recharge states, ideal for practice or deathmatch servers.
* Located in `src/game/g_items.c` (`Use_HealthCabinet` and `Use_AmmoCabinet`).

### 4. Allied Covert Ops Alternate Primary
* **CVAR**: `g_alliedCovertWeapon` (default: `0`, `SERVERINFO | ARCHIVE`).
* **Values**: `0` = Johnson M1941 (`WP_JOHNSON`), `1` = BAR (`WP_BAR`), `2` = FG42 (`WP_FG42`).
* **Implementation**: `src/game/g_main.c` sets `bg_allies_playerclasses[PC_COVERTOPS].classWeapons[1]` from the cvar and publishes the value to clients under the `CW` key (next to `SS` for `g_soldierShotgun`).

---

## 7. CVAR Engineering & Synchronization

CVARs (Console Variables) allow server administrators and clients to tune engine behavior.

### 1. CVAR Flags Table
| Flag | Name | Meaning |
| :--- | :--- | :--- |
| `0x0001` | `CVAR_ARCHIVE` | Written by the engine to its own config (`etconfig.cfg` on clients, `nq/etconfig_server.cfg` on ET:Legacy dedicated servers) and reloaded on restart. Never written to `noquarter.cfg`. |
| `0x0004` | `CVAR_SERVERINFO` | Broadcasted to server browsers and clients in `CS_SERVERINFO`. |
| `0x0008` | `CVAR_SYSTEMINFO` | Broadcasted in `CS_SYSTEMINFO` to all connected clients. |
| `0x0010` | `CVAR_INIT` | Can only be set on the command line at launch. |
| `0x0020` | `CVAR_LATCH` | Changes take effect only after a map restart (`map_restart`). |

### 2. Complete Recipe for Adding a Server CVAR
1. **Declare** in `src/game/g_local.h`:
   ```c
   extern vmCvar_t g_myCvar;
   ```
2. **Define & Register** in `src/game/g_main.c`:
   ```c
   vmCvar_t g_myCvar;
   // In G_RegisterCvars():
   { &g_myCvar, "g_myCvar", "0", CVAR_SERVERINFO | CVAR_ARCHIVE, 0, qfalse, qtrue },
   ```
   Table rows are `{ &cvar, "name", "default", flags, modificationCount, trackChange, fConfigReset }`; trailing fields may be omitted.
3. **Handle in Console/Scripts**:
   Update `docs/noquarter_commented.txt` and `config/noquarter3.0.cfg`.

### 3. Security & Timing CVARs (1.3.1)
| Cvar | Default | Meaning |
| :--- | :---: | :--- |
| `g_authFailures` | `3` | Wrong `/ref` passwords before the client is kicked and temp-banned. `0` = no lockout (failures still logged). |
| `g_authFailBanTime` | `300` | Temp-ban length in **seconds**. |
| `g_authFailExpireTime` | `900` | Seconds before a failed attempt stops counting. |
| `sv_fps` | `20` | NQ timing assumes 50 ms frames (`SERVER_FRAMETIME`); `G_InitGame` warns if it isn't 20. |

### 4. Command-Line `+set` vs. Config Files
The engine applies every `+set` on the command line **before** it runs any `+exec`. A cvar that `noquarter.cfg` also sets will therefore end up with the cfg's value, not the command-line one. Change such cvars in the cfg itself.

---

## 8. Lua Scripting Subsystem

NoQuarter includes an embedded Lua 5.1 runtime allowing server administrators to customize gameplay without recompiling C code. On Windows the runtime is `lua5.1.dll` (qagame imports it); on Linux it is compiled into `qagame`. Scripts that use SQLite (WolfAdmin, XPSave) load the LuaSQL driver via `require("luasql.sqlite3")`: `sqlite3.dll` on Windows (exports `luaopen_luasql_sqlite3`, installed as `nq/lualibs/luasql/sqlite3.dll`); on Linux the driver is compiled into `qagame` and registered in `package.preload`. Scripts to load are listed in the `lua_modules` cvar.

> Lua scripts must not hardcode server paths; build them from `et.trap_Cvar_Get("fs_homepath")` and `et.trap_Cvar_Get("fs_game")` at runtime. `et.G_LogPrint` prints its text as data (Audit H2), so player names containing `%` are safe to log.

### 1. Core Callbacks
* `et_InitGame(levelTime, randomSeed, restart)`: Called on map load.
* `et_ShutdownGame(restart)`: Called on map exit.
* `et_RunFrame(levelTime)`: Called every server frame (~50ms / 20Hz).
* `et_ClientConnect(clientNum, firstTime, isBot)`: Called during client handshake.
* `et_ClientCommand(clientNum, command)`: Intercepts client commands (`say`, `vsay`, custom commands). Returning `1` blocks the command.
* `et_UpgradeSkill(clientNum, skill)`: Triggered when a player earns a skill level.

### 2. Entity & Client Field Accessors
The full list of addressable entity and client memory fields is documented in [nqluadocu.htm](nqluadocu.htm).
* `et.gentity_get(entNum, fieldName, [arrayIndex])`
* `et.gentity_set(entNum, fieldName, [arrayIndex], value)`
* `et.gclient_get(clientNum, fieldName, [arrayIndex])`
* `et.gclient_set(clientNum, fieldName, [arrayIndex], value)`

---

## 9. Build, Compilation & PK3 Distribution Pipeline

### 1. Windows MSVC Build
Requirements: Visual Studio 2026 (its bundled CMake; the `Visual Studio 18 2026` generator produces `.slnx` solutions).
```powershell
# 1. Generate solutions
cmake -B build64 -S . -A x64
cmake -B build32 -S . -A Win32

# 2. Build Release DLLs (output: build64/src/Release, build32/src/Release)
msbuild build64/NoQuarterWrapper.slnx /p:Configuration=Release /m
msbuild build32/NoQuarterWrapper.slnx /p:Configuration=Release /m
```
Visual Studio "Open Folder" builds (**x64-Release** / **x86-Release** from `CMakeSettings.json`) go to `out/build/<config>/src/` instead. Both routes produce `qagame`, `cgame`, `ui`, `lua5.1.dll`, `sqlite3.dll` and matching `.pdb` files.

**Release builds don't embed build paths.** `src/CMakeLists.txt` passes `/d1trimfile:<repo root>` (shortens `__FILE__` strings) and links with `/PDBALTPATH:%_PDB%` (the DLL records only the `.pdb` file name). To debug a crash, keep the matching `.pdb` next to the DLL.

### 2. Linux Cross-Compilation via Zig
Using Zig as a cross-compiler allows building Linux `.so` shared libraries directly from Windows without setting up a Linux virtual machine:
```bash
python scripts/build_linux.py
```
This builds the following (Lua and LuaSQL/SQLite are compiled into `qagame`; the small `liblua5.1.so` / `sqlite3.so` stubs it also writes are not shipped):
* `qagame.mp.x86_64.so`, `cgame.mp.x86_64.so`, `ui.mp.x86_64.so` (Linux 64-bit, `build64/Release/linux/`)
* `qagame.mp.i386.so`, `cgame.mp.i386.so`, `ui.mp.i386.so` (Linux 32-bit, `build32/Release/linux/`)

Zig is found via `PATH`, the `ZIG_EXE` environment variable, or `~/zig/`. The script compiles with `-ffile-prefix-map=<repo>=.`, `-g0` and `-s`, so the `.so` files carry no debug info or build paths.

### 3. Automated Packaging (`package_release.py`)
Builds `nq_b_v1.3.1b7.pk3` (the 8 client binaries), refreshes `nq_v1.3.1b7.pk3` from the release folder's current copy plus the source overrides (menudefs, vote menu, `meyer.shader`, texture fixes), and fills `DLL's/<Windows|Linux>/<32 Bit|64 Bit>/` with the server files from the table in section 3.
```bash
python scripts/package_release.py
```
| Environment variable | Default | Purpose |
| :--- | :--- | :--- |
| `NQ_RELEASE_DIR` | `release/` in the repo (git-ignored) | Where the release is assembled. Must already contain the current `nq_v1.3.1b7.pk3`. |
| `NQ_BUILD64_DIR` / `NQ_BUILD32_DIR` | newer of `build64/src/Release` and `out/build/x64-Release/src` (x86 likewise) | Which Windows build to package. The script prints the folder it picked. |
| `ET64_DIR`, `ET32_DIR`, `NQ_CLIENT_DIR` | unset | Optional local `nq/` folders to copy the new build into for testing. Nothing is copied unless set. |

---

## 10. Troubleshooting Playbook & Solved Engine Bugs

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **`Image loader failed to parse an image textures/...`** | Texture was saved as CMYK 4-channel JPEG. | Re-save texture as baseline 24-bit sRGB JPEG or TGA using PIL/Photoshop. |
| **Airstrike called, sound plays, but planes do not appear** | Invalid model paths in `cg_main.c` (`planes/ju87.md3` instead of `etl_plane/junker88.md3`). | Update registration to `etl_plane/junker88.md3` and `etl_plane/b-25.md3`. |
| **Airstrike propeller jumps or stutters** | Propeller animation frames defined as 4 instead of 10. | Set `NUM_FRAME_PROPELLER 10` in `cg_ents.c`. |
| **Kill announcement text overlaps left-hand obituary feed** | Center print rendered at `Y=360` with wide `limboFont1`. | Switch font to `&cgs.media.limboFont2` (scale `0.22f`) and clamp `baseY >= 384`. |
| **`pure server` rejection when joining server** | Client has outdated binary PK3 or mismatched build. | Ensure both server and client use unified `nq_b_v1.3.1b7.pk3`. |
| **Crashing on 64-bit when casting pointers** | Casting `void*` directly to `int` (truncating 64-bit pointer to 32 bits). | Use `intptr_t` or `uintptr_t`. |
| **Shotgun not appearing in Limbo for Heavy Weapons Soldier** | `g_soldierShotgun` is set to 0 or skill check in `ui_shared.c` failed. | Ensure `g_soldierShotgun 1` and player has Heavy Weapons level 4. |
| **Server cabinets depleted and not recharging** | Standard cabinet gameplay cooldown. | Enable `g_infiniteCabinets 1` in `noquarter.cfg`. |
| **64-bit Windows server dies with `Received signal 11` right after `Game Initialization completed` (bots on)** | Old `BotLoadLibrary.cpp` loaded the 32-bit `omnibot_et.dll`, then crashed in `OB_ShowLastError`. | Fixed in 1.3.1: rebuild qagame and make sure `omni-bot/omnibot_et_x64.dll` exists. A failed bot load now prints an `Omni-bot:` error instead. |
| **`WARNING: G_Script_ScriptParse(): unknown action '...'`** | Map made for another mod (e.g. TC:E `wm_camo`). | Harmless; the action is skipped. Remove the map from the rotation if it doesn't play correctly. |
| **`BG_IndexForString: unknown token '...'` / many `BG_RegisterWeapon failed` errors** | `nq_v1.3.1b7.pk3` isn't in the server's `nq/` folder, so assets from other pk3s are used. | Put both NQ pk3s back in `nq/`. |
| **Server crashes on its first frame only when output is redirected (`> file.log`)** | ET:Legacy's Windows console code expects a real console. | Don't redirect; use `+set logfile 2` (writes `nq/etconsole.log`). |
| **`Received signal 11` with no other clue** | ET:Legacy only prints the signal number for access violations. | Run `etlded.exe` under the Visual Studio debugger with the matching `.pdb` next to the DLL; the call stack shows the line. |
| **A command-line `+set` has no effect** | `+set` runs before `+exec`, so `noquarter.cfg` overrides it. | Change the cvar in the cfg. |
| **`WARNING: sv_fps is N`** | `sv_fps` isn't 20. | Set `sv_fps 20`; NQ timing depends on it. |
| **A fix "didn't work" after rebuilding** | An older build was deployed (command-line and Visual Studio builds go to different folders). | Compare dates of `build64/src/Release` vs `out/build/x64-Release/src`, redeploy the newer DLL. |
