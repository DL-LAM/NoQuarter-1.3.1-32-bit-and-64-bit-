# NoQuarter Modernized (`v1.3.1`)

**NoQuarter Modernized** is an updated, 64-bit and 32-bit compatible fork of the classic **NoQuarter** mod for *Wolfenstein: Enemy Territory* and *ET:Legacy*. 

This release modernizes the user interface, introduces quality-of-life gameplay enhancements, integrates ET:Legacy visual improvements, and provides full cross-platform compilation pipelines for both Windows and Linux on 32-bit and 64-bit architectures.

---

## 🌟 What's New & Key Features

### 1. 🗳️ ET:Legacy-Style Intermission & Map Vote Overhaul
* **Modernized Navigation Panels (`PANELS`)**:
  * Replaced static debriefing buttons with interactive `panel_button_t` elements on the bottom right:
    * **SCOREBOARD** (`cgs.dbMode = 1`) — Live player score list.
    * **AWARDS** (`cgs.dbMode = 2`) — End-game medals, awards, and Roll of Honor.
    * **STATS** (`cgs.dbMode = 3`) — Detailed player weapon and class statistics.
    * **VOTE NOW / MAP VOTE** (`cgs.dbMode = 0`) — Map voting screen with an animated pulsating indicator when votes have not yet been cast.
    * **NEXT** — Smoothly advances to the next available debriefing tab.
  * Features active tab highlighting (gold accent), cursor hover response, and native audio click effects.
* **Side-by-Side Horizontal Chat Panel**:
  * Sits flush to the left of the button panel without overlap (`492x112`).
  * Aligned quick-action buttons: `SAY:` / `TEAM:`, chat edit input, `READY`, and `QUICK CHAT`.
* **Redesigned Map Voting Interface**:
  * **Map List**: Checkbox indicators, aligned multi-column headers (`Name`, `Votes`, `Popularity`), and centered horizontal action buttons (`VOTE #1`, `VOTE #2`, `VOTE #3` / `SEND VOTE`).
  * **Map Statistics Box**: Displays Map Display Name, File, Last Played, Total Votes, and Current Votes.
  * **4:3 Levelshot Preview**: Renders map preview images with multi-format shader support (`.tga`, `.jpg`, unextended shaders), smooth fade-in, dynamic centering, and fallback placeholders.
  * **Widescreen & Ultrawide Support**: All debriefing components are fully calibrated with widescreen offset math (`wideXoffset`), guaranteeing pixel-perfect alignment across 4:3, 16:9, 16:10, and 21:9 displays.

---

### 2. ⚔️ Gameplay & Weaponry Enhancements
* **Soldier Secondary Shotgun**:
  * Soldiers who reach **Heavy Weapons Level 4** can equip the Winchester M97 Shotgun as a secondary weapon option in the Limbo Menu.
  * Configurable via the new server cvar `g_soldierShotgun`.
* **Auto-Select Best Secondary Weapon in Limbo**:
  * When opening the Limbo Menu or switching classes, the menu automatically selects the **best available secondary weapon** for that class and skill level:
    * **Soldier (Heavy Weapons $\ge 4$)**: Automatically pre-selects the SMG (Thompson / MP40).
    * **Any Class (Light Weapons $\ge 4$)**: Automatically pre-selects Akimbo pistols (or Akimbo Silenced for Covert Ops).
    * **Default / Lower Skill Levels**: Standard single pistol.
  * Manual selections in Limbo are remembered.
  * **Spawn State**: When spawning into the game, the player's active held weapon remains their selected **Primary Weapon**, with the secondary weapon holstered and ready for quick-draw.
* **Weapon Icon HUD Glow**:
  * Dynamic weapon icon state glows on the HUD inspired by ET:Legacy.

---

### 3. ⚙️ New Server Cvars

| Cvar | Default | Description | Flags |
| :--- | :---: | :--- | :--- |
| `g_soldierShotgun` | `1` | `1` = Soldier with Heavy Weapons Level 4 can equip the Shotgun as a secondary weapon.<br>`0` = Disables Soldier secondary shotgun (Limbo menu dynamically updates). | `SERVERINFO`<br>`ARCHIVE` |
| `g_infiniteCabinets` | `0` | `1` = Health and ammo cabinets/stands provide unlimited resources without depleting.<br>`0` = Standard cabinet resource depletion and cooldown. | `SERVERINFO`<br>`ARCHIVE` |

---

### 4. 💻 Architecture, 64-Bit Support & PK3 System (`v1.3.1`)
* **Dual-Architecture PK3 Packaging**:
  * Updated version string to `1.3.1`.
  * Enhanced `sv_pakNames` verification to support architecture-tagged binary packages (`nq_b_v1.3.1_64.pk3` and `nq_b_v1.3.1_32.pk3`) alongside unified binary packages (`nq_b_v1.3.1.pk3`, `nq_b_v1.3.0_b.pk3`) and asset packs (`nq_v1.3.1.pk3`, `nq_v1.3.0_b.pk3`).
  * Enables 64-bit and 32-bit clients and servers to connect without PK3 mismatch warnings or missing file errors.
* **Cross-Platform Cross-Compilation**:
  * Native Windows MSVC builds for x64 and x86.
  * Linux cross-compilation pipeline using the Zig compiler to produce `x86_64` and `i386` shared objects (`.so`) with Lua 5.1 and SQLite3.

---

## 📦 File Layout & Binary Identification

```text
nq/
├── nq_v1.3.1.pk3              # Core Assets (textures, models, sounds, scripts)
├── nq_b_v1.3.1_64.pk3         # 64-Bit Binaries (cgame.mp.x86_64, qagame.mp.x86_64, ui.mp.x86_64)
├── nq_b_v1.3.1_32.pk3         # 32-Bit Binaries (cgame_mp_x86, qagame_mp_x86, ui_mp_x86)
├── qagame.mp.x86_64.dll / .so # 64-Bit Server Game Module
├── qagame_mp_x86.dll / .so    # 32-Bit Server Game Module
└── sqlite3.dll / .so          # SQLite3 database engine
```

---

## 🛠️ Building from Source

### Prerequisites
* **Windows**: Visual Studio 2022 / Build Tools with C/C++ support and CMake $\ge 3.20$.
* **Linux / Cross-Compilation**: GCC/Clang or [Zig Compiler](https://ziglang.org/) ($\ge 0.13.0$).
* **Python 3**: For automated packaging and cross-compilation scripts.

---

### Windows Build (MSVC)

#### 1. Generate Build Solutions:
```powershell
# 64-bit Build Solution
cmake -B build64 -S . -A x64

# 32-bit Build Solution
cmake -B build32 -S . -A Win32
```

#### 2. Compile Release Binaries:
```powershell
# Compile 64-bit
msbuild build64/NoQuarter.slnx /p:Configuration=Release /m

# Compile 32-bit
msbuild build32/NoQuarter.slnx /p:Configuration=Release /m
```

---

### Linux Cross-Compilation (via Zig)

A Python cross-compilation script is provided to compile Linux `.so` shared libraries directly on Windows or Linux:

```bash
python scratch/build_linux.py
```

This compiles:
* `build64/Release/linux/` $\rightarrow$ `qagame.mp.x86_64.so`, `cgame.mp.x86_64.so`, `ui.mp.x86_64.so`, `liblua5.1.so`, `sqlite3.so`
* `build32/Release/linux/` $\rightarrow$ `qagame.mp.i386.so`, `cgame.mp.i386.so`, `ui.mp.i386.so`, `liblua5.1.so`, `sqlite3.so`

---

### Packaging PK3 Files

To package your binaries into PK3 archives, create zip files (without root directory prefixes) containing the respective DLL and `.so` files:

* `nq_b_v1.3.1_64.pk3`: Contains 64-bit `cgame.mp.x86_64.dll`, `ui.mp.x86_64.dll`, `cgame.mp.x86_64.so`, `ui.mp.x86_64.so`.
* `nq_b_v1.3.1_32.pk3`: Contains 32-bit `cgame_mp_x86.dll`, `ui_mp_x86.dll`, `cgame.mp.i386.so`, `ui.mp.i386.so`.

---

## 📜 Credits & Acknowledgments

* **NoQuarter Development Team**: IRATA, jaquboss, Meyer, ReyalP, Lucifer, and contributors.
* **ET:Legacy Development Team**: For modern UI designs, weapon HUD concepts, and 64-bit architecture references.
* **Splash Damage & id Software**: Original creators of *Wolfenstein: Enemy Territory*.
* **Omni-Bot Team**: Bot support and interface integration.
* **Community**: All players and server administrators keeping *Enemy Territory* alive!

---

## ⚖️ License
This project is open-source software licensed under the **GNU General Public License v3 (GPLv3)**. See `License.txt` for details.
