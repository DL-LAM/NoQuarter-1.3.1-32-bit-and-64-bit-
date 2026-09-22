# NoQuarter 1.3.1 (32-bit & 64-bit)

Maintained and updated by **Hawkeye** (`nqv1.3.1help@gmail.com`)

Welcome to NoQuarter 1.3.1! This update modernizes the classic Wolfenstein: Enemy Territory mod so it runs great on modern systems, high-res widescreen/ultrawide monitors, and modern engines (ET:Legacy as well as classic ET 2.60b). 

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

### 3. Server CVARs

| Cvar | Default | Description | Flags |
| :--- | :---: | :--- | :--- |
| `g_soldierShotgun` | `1` | `1` = Soldier with Heavy Weapons Level 4 can equip the Shotgun as a secondary weapon.<br>`0` = Disables Soldier secondary shotgun (Limbo menu updates dynamically). | `SERVERINFO`<br>`ARCHIVE` |
| `g_infiniteCabinets` | `0` | `1` = Health and ammo supply cabinets provide unlimited resources without running empty.<br>`0` = Standard cabinet supply depletion and cooldown timer. | `SERVERINFO`<br>`ARCHIVE` |

---

### 4. PK3 Packaging & Architecture (`v1.3.1b6`)

To keep things dead simple and prevent pure-server checksum mismatches, this release uses a **unified PK3 architecture**:

* **`nq_b_v1.3.1b6.pk3` (Unified Binaries)**:
  * Contains the client binaries for **both** 64-bit and 32-bit on Windows and Linux (`cgame` and `ui` DLLs and `.so` files).
  * **Why unified?** In the past, separating 32-bit and 64-bit binary PK3s caused headaches: players on 32-bit clients couldn't join 64-bit servers, server admins would misconfigure the pk3 files, and players would get hit with pure-server checksum errors. Having all client binaries bundled in `nq_b_v1.3.1b6.pk3` means it just works out of the box regardless of what system people are running.
  * If a server admin really wants stripped-down, arch-specific packages for a dedicated box, they can repackage it, but the unified PK3 is standard to protect players from mismatch errors.
* **`nq_v1.3.1b6.pk3` (Core Assets)**:
  * Contains updated assets, menus, textures, and shader fixes (including the right-side-up Caduceus fix in `meyer.shader`).

---

## 📦 Directory Structure

On your server or game client installation, your `nq/` folder should look like this:

```text
nq/
├── nq_v1.3.1b6.pk3            # Core assets, menus, shaders, textures
├── nq_b_v1.3.1b6.pk3          # Unified client binaries (32-bit & 64-bit Win DLLs and Linux .so)
├── qagame.mp.x86_64.dll / .so # 64-Bit Server Game Module
├── qagame_mp_x86.dll / .so    # 32-Bit Server Game Module
└── sqlite3.dll / .so          # SQLite3 database engine
```

---

## 🛠️ Building from Source

### Requirements
* **Windows**: Visual Studio 2022 (Community / Professional / Build Tools with C/C++) and CMake $\ge 3.20$.
* **Linux / Cross-Compilation**: GCC/Clang or [Zig Compiler](https://ziglang.org/) ($\ge 0.13.0$).
* **Python 3**: For build and packaging scripts.

---

### Building on Windows (MSVC)

#### 1. Generate CMake Solutions:
```powershell
# 64-bit solution
cmake -B build64 -S . -A x64

# 32-bit solution
cmake -B build32 -S . -A Win32
```

#### 2. Compile Binaries:
```powershell
# Build 64-bit Release
msbuild build64/NoQuarterWrapper.slnx /p:Configuration=Release /m

# Build 32-bit Release
msbuild build32/NoQuarterWrapper.slnx /p:Configuration=Release /m
```

---

### Building for Linux (via Zig Cross-Compilation)

A Python cross-compilation script is included so you can compile Linux `.so` shared libraries directly from Windows or Linux using Zig:

```bash
python scripts/build_linux.py
```

This compiles:
* `build64/Release/linux/` $\rightarrow$ `qagame.mp.x86_64.so`, `cgame.mp.x86_64.so`, `ui.mp.x86_64.so`, `liblua5.1.so`, `sqlite3.so`
* `build32/Release/linux/` $\rightarrow$ `qagame.mp.i386.so`, `cgame.mp.i386.so`, `ui.mp.i386.so`, `liblua5.1.so`, `sqlite3.so`

---

### Packaging PK3s

Create standard zip files (without any leading folder paths) containing the binaries and assets, then rename the extension to `.pk3` (or run `python scripts/package_release.py`):

* `nq_b_v1.3.1b6.pk3`: Pack the client files (`cgame.mp.x86_64.dll`, `ui.mp.x86_64.dll`, `cgame.mp.x86_64.so`, `ui.mp.x86_64.so`, `cgame_mp_x86.dll`, `ui_mp_x86.dll`, `cgame.mp.i386.so`, `ui.mp.i386.so`).
* `nq_v1.3.1b6.pk3`: Pack your assets (scripts, shaders, textures, and UI menudefs).

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
