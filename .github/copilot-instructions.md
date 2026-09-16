# GitHub Copilot Instructions for NoQuarter 1.3.1 Modernized

When generating or editing code in this repository:
1. Target C99/C89 compatible code that builds cleanly under Visual Studio 2022 (MSVC) and GCC/Clang/Zig.
2. Maintain strict 32-bit (x86) and 64-bit (x86_64) cross-compatibility. Never assume pointer sizes are 4 or 8 bytes.
3. Use `Q_strncpyz` instead of `strcpy`/`strncpy`. Use `Com_sprintf` instead of `sprintf`/`snprintf`.
4. Respect the idTech 3 module boundaries:
   - `src/game/`: Server-side simulation (`gentity_t`, `level_locals_t`).
   - `src/cgame/`: Client-side rendering and prediction (`centity_t`, `cg_t`, `cgs_t`).
   - `src/ui/`: Menu scripts and panel elements.
5. In UI and HUD code, always calculate positions within the virtual 640x480 coordinate space adjusted by `wideXoffset`.
6. Refer to `AGENT.md` and `docs/DEVELOPER_KNOWLEDGE_BASE.md` for architecture details, CVAR lists, and solved bug history.
