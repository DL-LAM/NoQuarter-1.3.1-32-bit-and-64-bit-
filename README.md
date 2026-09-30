# NoQuarter CE V1.3.1 (32-bit & 64-bit) *Community Edition*

Maintained and updated by **Hawkeye** (`nqv1.3.1help@gmail.com`)

Welcome to NoQuarter 1.3.1! This unoffical community update modernizes the classic Wolfenstein: Enemy Territory mod so it runs great on modern systems, high-res widescreen/ultrawide monitors, and modern engines (ET:Legacy as well as classic ET 2.60b). 

We've got full native 64-bit and 32-bit support across both Windows and Linux, cleaner menus, tons of crash-proofing, quality-of-life gameplay tweaks, and unified packaging so players and server admins don't get hit with annoying pure-server PK3 mismatch errors.

Stuff was fixed, enjoy! If you run into any issues, have questions, or need help getting things dialed in, feel free to reach out!

---

## 🎮 What's New & Highlight Features

### 1. Intermission & Map Voting Overhaul (ET:Legacy Style)
* **Real Debriefing Navigation Tabs**:
  * Ditched the clunky old static debriefing buttons for interactive tabs docked on the bottom right:
    * **SCOREBOARD** — Live player scoreboard and match outcome.
    * **AWARDS** — End-of-game medals, badges, and Roll of Honor.
    * **STATS** — In-depth weapon accuracy and class stats.
    * **VOTE NOW / MAP VOTE** — Map voting screen. Features a pulsing visual indicator if you haven't cast your vote yet so you don't forget.
    * **NEXT** — Quickly flips to the next screen.
  * Active tabs highlight in gold with sound feedback on click.
* **Side-by-Side Horizontal Chat**:
  * Positioned neatly right next to the button panel without any awkward overlapping.
  * Easy-access buttons for `SAY:`, `TEAM:`, chat input, `READY`, and `QUICK CHAT` so you can chat or ready up while checking scores.
* **Redesigned Map Voting Screen**:
  * Clean multi-column map list with checkbox indicators (`Name`, `Votes`, `Popularity`).
  * Easy voting buttons (`VOTE #1`, `VOTE #2`, `VOTE #3` / `SEND VOTE`).
  * Map info box displaying display name, bsp filename, last time played, and vote counts.
  * Proper 4:3 levelshot previews supporting `.tga`, `.jpg`, and shader scripts with fallback placeholders if a custom map is missing a preview.
* **Widescreen & Ultrawide Native Fit**:
  * All menus, HUD elements, and debriefing screens use proper widescreen offset math (`wideXoffset`). Whether you play on 4:3, 16:9, 16:10, or 21:9 ultrawide, nothing stretches, clips, or overlaps.

---

### 2. Gameplay & Weapon Tweaks
* **Soldier Secondary Shotgun (`g_soldierShotgun 1`)**:
  * Soldiers who earn **Heavy Weapons Level 4** can now equip the Winchester M97 Shotgun right in their secondary slot from the Limbo menu. Server admins can toggle this on or off.
* **Allied Covert Ops Primary Choice (`g_alliedCovertWeapon`)**:
  * Server admins pick which rifle Allied Covert Ops get as their alternate primary: the Johnson M1941 (default), the BAR, or the FG42.
* **Automatic Best Secondary in Limbo**:
  * No more clicking back and forth in the limbo menu every time you gain a skill rank. The menu automatically equips the best secondary you've unlocked:
    * **Soldier (Heavy Weapons $\ge 4$)**: Pre-selects an SMG (Thompson / MP40).
    * **Any Class (Light Weapons $\ge 4$)**: Pre-selects Akimbo pistols (or silenced akimbos for Covert Ops).
    * **Lower Skill Levels**: Standard single pistol.
  * Your manual limbo choices are always remembered.
  * When you spawn into the battlefield, you'll still spawn holding your **Primary Weapon** ready to shoot, with your upgraded secondary holstered and ready for quick swaps.
* **Infinite Cabinets Toggle (`g_infiniteCabinets 1`)**:
  * Server admins can toggle unlimited supply cabinets with `g_infiniteCabinets 1`. Health and ammo stands won't deplete or make players wait on long cooldowns.
* **Upside-Down Revive Icon Fixed**:
  * Finally fixed that long-standing bug where the Caduceus medic revival / Battlefield Resuscitation icon showed up flipped upside-down when aiming at downed teammates!
* **Weapon HUD Glow**:
  * Dynamic weapon state glow on the HUD inspired by ET:Legacy.
* **Engine & Server Crash Hardening**:
  * Added rock-solid guards across referee commands, voting handlers, fireteam logic, bot memory bounds, and server tickrate divisions. Tested through 30 consecutive stress boundary checks with zero crashes.

---

### 3. Security & Stability (1.3.1 Source Audit)

The whole game code got a line-by-line review. Every fix is tagged in the source with `[NQ 1.3.1 - Audit <ID>]`, and `docs/AUDIT_2026-09-25.md` lists each one. The highlights:

* **Referee Password Lockout**:
  * Too many wrong `/ref` passwords now gets the player kicked and temp-banned, and every failed attempt is written to the server log with the player's name and IP. Tune it with `g_authFailures`, `g_authFailBanTime`, and `g_authFailExpireTime` (see the cvar table below).
* **Players Can't Crash Your Server Anymore**:
  * Closed holes where a player could shut the server down or poke at server memory, like `/fireteam kick` on yourself or sending a bogus map vote ID.
* **Maps From Other Mods Won't Take the Server Down**:
  * Maps built for other mods (True Combat: Elite and friends) use map-script commands NQ doesn't have. Those used to shut the whole server down. Now NQ logs a warning, skips the unknown command, and keeps the map running.
* **IPv6 & UTF-8 Players Welcome**:
  * Players connecting over IPv6 on ET:Legacy are no longer refused with "Bad userinfo", and IP bans now match whole addresses instead of partial text.
  * Player names with proper UTF-8 characters are allowed; broken or garbage bytes are still rejected.
* **64-bit Linux Fixes**:
  * Fixed 64-bit Linux bugs that scrambled movement and aiming, caused a solid-color screen, and made players drown.
* **Omni-Bot on 64-bit Windows**:
  * 64-bit Windows servers now load `omnibot_et_x64.dll` (they used to grab the 32-bit `omnibot_et.dll` and crash). If Omni-Bot can't load for any reason, the server prints the error and keeps running without bots.
* **Safer XP Saves & Lua Logging**:
  * XP save files can't be pointed outside the save folder with a fake GUID, and old 32-bit Linux XP saves are converted automatically.
  * Lua scripts can't break the server log with stray `%` characters in player names or chat.
* **Server Tickrate Warning**:
  * NoQuarter's timing (weapons, spawns, timers) is built around `sv_fps 20`. The server now prints a warning at map start if it's set to anything else.

---

### 4. Server CVARs

| Cvar | Default | Description | Flags |
| :--- | :---: | :--- | :--- |
| `g_soldierShotgun` | `1` | `1` = Soldier with Heavy Weapons Level 4 can equip the Shotgun as a secondary weapon.<br>`0` = Disables Soldier secondary shotgun (Limbo menu updates dynamically). | `SERVERINFO`<br>`ARCHIVE` |
| `g_infiniteCabinets` | `0` | `1` = Health and ammo supply cabinets provide unlimited resources without running empty.<br>`0` = Standard cabinet supply depletion and cooldown timer. | `SERVERINFO`<br>`ARCHIVE` |
| `g_alliedCovertWeapon` | `0` | Allied Covert Ops alternate primary weapon.<br>`0` = Johnson M1941, `1` = BAR, `2` = FG42. | `SERVERINFO`<br>`ARCHIVE` |
| `g_authFailures` | `3` | Wrong `/ref` passwords allowed before the player is kicked and temp-banned.<br>`0` = no lockout (failed attempts are still logged). | `ARCHIVE` |
| `g_authFailBanTime` | `300` | Length of the lockout temp-ban, **in seconds** (`300` = 5 minutes). | `ARCHIVE` |
| `g_authFailExpireTime` | `900` | How long, in seconds, a failed attempt counts toward the limit before it's forgotten. | `ARCHIVE` |

> **Keep `sv_fps` at `20`.** ET:Legacy lets you raise it, but NoQuarter's gameplay timing assumes 20 server frames per second. The server warns you at map start if it's set to anything else.

---

### 5. PK3 Packaging & Architecture (`v1.3.1b7`)

To keep things dead simple and prevent pure-server checksum mismatches, this release uses a **unified PK3 architecture**:

* **`nq_b_v1.3.1b7.pk3` (Unified Binaries)**:
  * Contains the client binaries for **both** 64-bit and 32-bit on Windows and Linux (`cgame` and `ui` DLLs and `.so` files), with exactly the file names each engine looks for.
  * **Why unified?** In the past, separating 32-bit and 64-bit binary PK3s caused headaches: players on 32-bit clients couldn't join 64-bit servers, server admins would misconfigure the pk3 files, and players would get hit with pure-server checksum errors. Having all client binaries bundled in `nq_b_v1.3.1b7.pk3` means it just works out of the box regardless of what system people are running.
  * If a server admin really wants stripped-down, arch-specific packages for a dedicated box, they can repackage it, but the unified PK3 is standard to protect players from mismatch errors.
* **`nq_v1.3.1b7.pk3` (Core Assets)**:
  * Contains updated assets, menus, textures, and shader fixes (including the right-side-up Caduceus fix in `meyer.shader`).

The server game module (`qagame`) is **never** put in a pk3. Only the server needs it, and it stays a loose file in the server's `nq/` folder (see below).

---

## 📦 Directory Structure

**Players** only need the two pk3s in their `nq/` folder. A server with downloads enabled (`sv_allowDownload 1`) sends them automatically when a player connects.

```text
nq/
├── nq_v1.3.1b7.pk3            # Core assets, menus, shaders, textures
└── nq_b_v1.3.1b7.pk3          # Unified client binaries (32-bit & 64-bit Win DLLs and Linux .so)
```

**Servers** need the same two pk3s plus the server files for their platform. These are in the release's `DLL's/<Windows|Linux>/<32 Bit|64 Bit>/` folders; copy the one matching your server into `nq/`:

| Server platform | Game module (`nq/`) | Lua runtime | SQLite driver for WolfAdmin / XPSave | Omni-Bot (`nq/omni-bot/`) |
| :--- | :--- | :--- | :--- | :--- |
| Windows 64-bit | `qagame_mp_x64.dll` | `lua5.1.dll` next to `etlded.exe` | `lualibs/luasql/sqlite3.dll` $\rightarrow$ `nq/lualibs/luasql/` | `omnibot_et_x64.dll` |
| Windows 32-bit | `qagame_mp_x86.dll` | `lua5.1.dll` next to `etlded.exe` | `lualibs/luasql/sqlite3.dll` $\rightarrow$ `nq/lualibs/luasql/` | `omnibot_et.dll` |
| Linux 64-bit | `qagame.mp.x86_64.so` | built into `qagame` | built into `qagame` | `omnibot_et.x86_64.so` |
| Linux 32-bit | `qagame.mp.i386.so` | built into `qagame` | built into `qagame` | `omnibot_et.so` |

On every platform, also copy the release's shared `lualibs/` folder (it holds `toml.lua`, which WolfAdmin needs) into `nq/lualibs/`. On Linux, Lua and the SQLite driver are compiled into `qagame`, so there are no extra `.so` files to install.

> Windows uses underscore names (`qagame_mp_x64.dll`) and Linux uses dot names (`qagame.mp.x86_64.so`). That's how ET:Legacy builds the file name it looks for, so don't rename them.

The release also includes `noquarter.cfg`, `shrubbot.cfg`, `config/` (sample configs), `omni-bot/`, `wolfadmin-1.2.1/`, `luascripts/`, `lualibs/`, and `docs/` (including the full `INSTALLATION_AND_ADMIN_GUIDE.md`).

---

## 🛠️ Building from Source

### Requirements
* **Windows**: Visual Studio 2026 (Community / Professional / Build Tools with C/C++). Its bundled CMake is used for the builds.
* **Linux / Cross-Compilation**: GCC/Clang or [Zig Compiler](https://ziglang.org/) ($\ge 0.13.0$).
* **Python 3**: For build and packaging scripts.

---

### Building on Windows (MSVC)

#### Option A: Command Line

##### 1. Generate CMake Solutions:
```powershell
# 64-bit solution
cmake -B build64 -S . -A x64

# 32-bit solution
cmake -B build32 -S . -A Win32
```

##### 2. Compile Binaries:
```powershell
# Build 64-bit Release
msbuild build64/NoQuarterWrapper.slnx /p:Configuration=Release /m

# Build 32-bit Release
msbuild build32/NoQuarterWrapper.slnx /p:Configuration=Release /m
```

#### Option B: Visual Studio "Open Folder"

Open the source folder in Visual Studio, pick the **x64-Release** or **x86-Release** configuration (from `CMakeSettings.json`), and choose **Build > Build All**. These builds go to a different place than Option A:

* `out/build/x64-Release/src/` $\rightarrow$ `qagame_mp_x64.dll`, `cgame_mp_x64.dll`, `ui_mp_x64.dll`, `lua5.1.dll`, `sqlite3.dll` (plus `.pdb` debug symbols)
* `out/build/x86-Release/src/` $\rightarrow$ `qagame_mp_x86.dll`, `cgame_mp_x86.dll`, `ui_mp_x86.dll`, `lua5.1.dll`, `sqlite3.dll`

---

### Building for Linux (via Zig Cross-Compilation)

A Python cross-compilation script is included so you can compile Linux `.so` shared libraries directly from Windows or Linux using Zig:

```bash
python scripts/build_linux.py
```

This compiles:
* `build64/Release/linux/` $\rightarrow$ `qagame.mp.x86_64.so`, `cgame.mp.x86_64.so`, `ui.mp.x86_64.so`
* `build32/Release/linux/` $\rightarrow$ `qagame.mp.i386.so`, `cgame.mp.i386.so`, `ui.mp.i386.so`

Lua and LuaSQL/SQLite are compiled into the Linux `qagame` (`NQ_BUILTIN_LUASQL`), so `require("luasql.sqlite3")` works with no extra files. Any small `liblua5.1.so` / `sqlite3.so` the script also writes are not needed and should not be shipped.

---

### Packaging PK3s

Create standard zip files (without any leading folder paths) containing the binaries and assets, then rename the extension to `.pk3`:

* `nq_b_v1.3.1b7.pk3`: Pack exactly these 8 client files, with these exact names:
  * Windows: `cgame_mp_x64.dll`, `ui_mp_x64.dll`, `cgame_mp_x86.dll`, `ui_mp_x86.dll`
  * Linux: `cgame.mp.x86_64.so`, `ui.mp.x86_64.so`, `cgame.mp.i386.so`, `ui.mp.i386.so`
* `nq_v1.3.1b7.pk3`: Pack your assets (scripts, shaders, textures, and UI menudefs). Zip an **exported/clean copy**, never a working folder with `.svn` or `.git` metadata in it, or the pk3 roughly doubles in size.

---

## 📜 Credits & Big Thanks

* **Hawkeye** (`nqv1.3.1help@gmail.com`) — Modernization, 64-bit / 32-bit cross-compile pipeline, UI overhaul, bugfixes, and maintenance.
* **NoQuarter Team**: IRATA, jaquboss, Meyer, ReyalP, Lucifer, and all past contributors who made NQ great.
* **ET:Legacy Team**: For awesome modern UI concepts, weapon HUD references, and 64-bit id Tech 3 insights.
* **Splash Damage & id Software**: For creating *Wolfenstein: Enemy Territory*.
* **Omni-Bot Team**: For bot navigation and AI support.
* **The Community**: Everyone still fragging, running servers, and keeping Enemy Territory alive after all these years!

---

## ⚖️ License
This project is open-source software licensed under the **GNU General Public License v3 (GPLv3)**. See `License.txt` for details.
