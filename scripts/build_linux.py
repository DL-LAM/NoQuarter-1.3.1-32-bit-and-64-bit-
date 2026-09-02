import os
import sys
import glob
import subprocess
import shutil

ROOT_DIR = r"C:\Users\Dylan\Documents\ETFiles\WET-NoQuarter-master\NQV1.3.0dev\trunk"
SRC_DIR = os.path.join(ROOT_DIR, "src")
ZIG_EXE = None

for candidate in [
    r"C:\Users\Dylan\zig\zig-windows-x86_64-0.13.0\zig.exe",
    r"C:\Users\Dylan\zig\zig.exe",
    shutil.which("zig")
]:
    if candidate and os.path.isfile(candidate):
        ZIG_EXE = candidate
        break

if not ZIG_EXE:
    matches = glob.glob(r"C:\Users\Dylan\zig\**\zig.exe", recursive=True)
    if matches:
        ZIG_EXE = matches[0]

if not ZIG_EXE:
    print("ERROR: zig.exe not found!")
    sys.exit(1)

print(f"Using Zig compiler: {ZIG_EXE}")

# Include directories
INCLUDES = [
    os.path.join(SRC_DIR, "game"),
    os.path.join(SRC_DIR, "cgame"),
    os.path.join(SRC_DIR, "ui"),
    os.path.join(SRC_DIR, "sha-1"),
    os.path.join(ROOT_DIR, "Omnibot", "Common"),
    os.path.join(ROOT_DIR, "Omnibot", "ET"),
    os.path.join(SRC_DIR, "lua", "lua-5.1.5", "src"),
    os.path.join(SRC_DIR, "luasql"),
    os.path.join(SRC_DIR, "sqlite3"),
]

BG_SRC = [
    "game/bg_animation.c",
    "game/bg_animgroup.c",
    "game/bg_campaign.c",
    "game/bg_character.c",
    "game/bg_classes.c",
    "game/bg_misc.c",
    "game/bg_pmove.c",
    "game/bg_slidemove.c",
    "game/bg_sscript.c",
    "game/bg_stats.c",
    "game/bg_tracemap.c",
    "game/bg_weapons.c",
    "game/q_math.c",
    "game/q_shared.c",
]

LUA_SRC = [
    "lua/lua-5.1.5/src/lapi.c",
    "lua/lua-5.1.5/src/lauxlib.c",
    "lua/lua-5.1.5/src/lbaselib.c",
    "lua/lua-5.1.5/src/lcode.c",
    "lua/lua-5.1.5/src/ldblib.c",
    "lua/lua-5.1.5/src/ldebug.c",
    "lua/lua-5.1.5/src/ldo.c",
    "lua/lua-5.1.5/src/ldump.c",
    "lua/lua-5.1.5/src/lfunc.c",
    "lua/lua-5.1.5/src/lgc.c",
    "lua/lua-5.1.5/src/linit.c",
    "lua/lua-5.1.5/src/liolib.c",
    "lua/lua-5.1.5/src/llex.c",
    "lua/lua-5.1.5/src/lmathlib.c",
    "lua/lua-5.1.5/src/lmem.c",
    "lua/lua-5.1.5/src/loadlib.c",
    "lua/lua-5.1.5/src/lobject.c",
    "lua/lua-5.1.5/src/lopcodes.c",
    "lua/lua-5.1.5/src/loslib.c",
    "lua/lua-5.1.5/src/lparser.c",
    "lua/lua-5.1.5/src/lstate.c",
    "lua/lua-5.1.5/src/lstring.c",
    "lua/lua-5.1.5/src/lstrlib.c",
    "lua/lua-5.1.5/src/ltable.c",
    "lua/lua-5.1.5/src/ltablib.c",
    "lua/lua-5.1.5/src/ltm.c",
    "lua/lua-5.1.5/src/lundump.c",
    "lua/lua-5.1.5/src/lvm.c",
    "lua/lua-5.1.5/src/lzio.c",
    "lua/lua-5.1.5/src/print.c",
]

LUASQL_SRC = [
    "luasql/luasql.c",
    "luasql/ls_sqlite3.c",
    "sqlite3/sqlite3.c",
]

QAGAME_SRC = BG_SRC + [
    "game/bg_profiler_hook.c",
    "game/etpro_mdx.c",
    "game/et-antiwarp.c",
    "game/g_active.c",
    "game/g_alarm.c",
    "game/g_antilag.c",
    "game/g_buddy_list.c",
    "game/g_character.c",
    "game/g_client.c",
    "game/g_cmds.c",
    "game/g_cmds_ext.c",
    "game/g_combat.c",
    "game/g_config.c",
    "game/g_crash.c",
    "game/g_fireteams.c",
    "game/g_items.c",
    "game/g_main.c",
    "game/g_match.c",
    "game/g_match_tokens.c",
    "game/g_mem.c",
    "game/g_misc.c",
    "game/g_missile.c",
    "game/g_mover.c",
    "game/g_multiview.c",
    "game/g_osfile.c",
    "game/g_props.c",
    "game/g_referee.c",
    "game/g_script.c",
    "game/g_script_actions.c",
    "game/g_session.c",
    "game/g_sha1.c",
    "game/g_shrubbot.c",
    "game/g_spawn.c",
    "game/g_stats.c",
    "game/g_strparse.c",
    "game/g_svcmds.c",
    "game/g_syscalls.c",
    "game/g_systemmsg.c",
    "game/g_target.c",
    "game/g_team.c",
    "game/g_teammapdata.c",
    "game/g_time.c",
    "game/g_trigger.c",
    "game/g_utils.c",
    "game/g_vote.c",
    "game/g_weapon.c",
    "game/g_xpsave.c",
    "game/geoip.c",
    "sha-1/sha.c",
    "sha-1/sha1.c",
    "game/g_lua.c",
    "game/g_etbot_interface.cpp",
    "../Omnibot/Common/BotLoadLibrary.cpp",
]

CGAME_SRC = BG_SRC + [
    "game/g_match_tokens.c",
    "game/g_strparse.c",
    "ui/ui_shared.c",
    "cgame/cg_atmospheric.c",
    "cgame/cg_character.c",
    "cgame/cg_commandmap.c",
    "cgame/cg_consolecmds.c",
    "cgame/cg_crash.c",
    "cgame/cg_debriefing.c",
    "cgame/cg_draw.c",
    "cgame/cg_drawtools.c",
    "cgame/cg_effects.c",
    "cgame/cg_ents.c",
    "cgame/cg_event.c",
    "cgame/cg_fireteamoverlay.c",
    "cgame/cg_fireteams.c",
    "cgame/cg_flamethrower.c",
    "cgame/cg_info.c",
    "cgame/cg_limbopanel.c",
    "cgame/cg_loadpanel.c",
    "cgame/cg_localents.c",
    "cgame/cg_main.c",
    "cgame/cg_marks.c",
    "cgame/cg_missionbriefing.c",
    "cgame/cg_missionmessages.c",
    "cgame/cg_multiview.c",
    "cgame/cg_newDraw.c",
    "cgame/cg_particles.c",
    "cgame/cg_players.c",
    "cgame/cg_playerstate.c",
    "cgame/cg_polybus.c",
    "cgame/cg_popupmessages.c",
    "cgame/cg_predict.c",
    "cgame/cg_scoreboard.c",
    "cgame/cg_servercmds.c",
    "cgame/cg_snapshot.c",
    "cgame/cg_sound.c",
    "cgame/cg_spawn.c",
    "cgame/cg_statsranksmedals.c",
    "cgame/cg_syscalls.c",
    "cgame/cg_trails.c",
    "cgame/cg_view.c",
    "cgame/cg_weapons.c",
    "cgame/cg_window.c",
]

UI_SRC = [
    "game/bg_campaign.c",
    "game/bg_classes.c",
    "game/bg_misc.c",
    "game/q_math.c",
    "game/q_shared.c",
    "ui/ui_atoms.c",
    "ui/ui_gameinfo.c",
    "ui/ui_loadpanel.c",
    "ui/ui_main.c",
    "ui/ui_shared.c",
    "ui/ui_syscalls.c",
]

def build_target(arch, target_triple, out_dir):
    print(f"\n==========================================")
    print(f"Building NoQuarter Linux ({arch}) -> {out_dir}")
    print(f"==========================================")
    os.makedirs(out_dir, exist_ok=True)

    common_flags = [
        "-target", target_triple,
        "-shared",
        "-fPIC",
        "-fcommon",
        "-O2",
        "-Wall",
        "-Wno-unused-function",
        "-Wno-unused-variable",
        "-Wno-deprecated-declarations",
        "-Wno-incompatible-pointer-types",
        "-Wno-format-security",
        "-Wno-macro-redefined",
        "-fvisibility=hidden",
        "-D_GNU_SOURCE",
    ]
    for inc in INCLUDES:
        common_flags.extend(["-I", inc])

    # 1. Build liblua5.1.so
    lua_out = os.path.join(out_dir, "liblua5.1.so")
    lua_sources = [os.path.join(SRC_DIR, f) for f in LUA_SRC]
    print(f"Compiling {lua_out}...")
    cmd = [ZIG_EXE, "cc"] + common_flags + ["-DLUA_USE_LINUX", "-o", lua_out] + lua_sources + ["-lm", "-ldl"]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Failed to build {lua_out}")
        return False
    # also copy as lua5.1.so
    shutil.copyfile(lua_out, os.path.join(out_dir, "lua5.1.so"))

    # 2. Build sqlite3.so
    sqlite_out = os.path.join(out_dir, "sqlite3.so")
    sqlite_sources = [os.path.join(SRC_DIR, f) for f in LUASQL_SRC]
    print(f"Compiling {sqlite_out}...")
    cmd = [ZIG_EXE, "cc"] + common_flags + [
        "-DSQLITE_ENABLE_COLUMN_METADATA", "-DSQLITE_ENABLE_FTS3",
        "-L" + out_dir, "-llua5.1",
        "-o", sqlite_out
    ] + sqlite_sources + ["-lm", "-ldl", "-lpthread"]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Failed to build {sqlite_out}")
        return False

    # 3. Build qagame
    if arch == "x86_64":
        qagame_name = "qagame.mp.x86_64.so"
    else:
        qagame_name = "qagame.mp.i386.so"
    qagame_out = os.path.join(out_dir, qagame_name)
    qagame_sources = [os.path.normpath(os.path.join(SRC_DIR, f)) for f in QAGAME_SRC]
    print(f"Compiling {qagame_out}...")
    cmd = [ZIG_EXE, "c++"] + common_flags + [
        "-DGAMEDLL", "-DNEW_ANIMS", "-DET_LUA", "-DOMNIBOTS",
        "-L" + out_dir, "-llua5.1",
        "-o", qagame_out
    ] + qagame_sources + ["-lm", "-ldl"]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Failed to build {qagame_out}")
        return False
    if arch != "x86_64":
        shutil.copyfile(qagame_out, os.path.join(out_dir, "qagame_mp_x86.so"))

    # 4. Build cgame
    if arch == "x86_64":
        cgame_name = "cgame.mp.x86_64.so"
    else:
        cgame_name = "cgame.mp.i386.so"
    cgame_out = os.path.join(out_dir, cgame_name)
    cgame_sources = [os.path.normpath(os.path.join(SRC_DIR, f)) for f in CGAME_SRC]
    print(f"Compiling {cgame_out}...")
    cmd = [ZIG_EXE, "cc"] + common_flags + [
        "-DCGAMEDLL", "-DNEW_ANIMS",
        "-o", cgame_out
    ] + cgame_sources + ["-lm", "-ldl"]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Failed to build {cgame_out}")
        return False
    if arch != "x86_64":
        shutil.copyfile(cgame_out, os.path.join(out_dir, "cgame_mp_x86.so"))

    # 5. Build ui
    if arch == "x86_64":
        ui_name = "ui.mp.x86_64.so"
    else:
        ui_name = "ui.mp.i386.so"
    ui_out = os.path.join(out_dir, ui_name)
    ui_sources = [os.path.normpath(os.path.join(SRC_DIR, f)) for f in UI_SRC]
    print(f"Compiling {ui_out}...")
    cmd = [ZIG_EXE, "cc"] + common_flags + [
        "-DUIDLL", "-DNEW_ANIMS",
        "-o", ui_out
    ] + ui_sources + ["-lm", "-ldl"]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Failed to build {ui_out}")
        return False
    if arch != "x86_64":
        shutil.copyfile(ui_out, os.path.join(out_dir, "ui_mp_x86.so"))

    print(f"Successfully built all Linux {arch} binaries in {out_dir}")
    return True

if __name__ == "__main__":
    out64 = os.path.join(ROOT_DIR, "build64", "Release", "linux")
    out32 = os.path.join(ROOT_DIR, "build32", "Release", "linux")

    ok64 = build_target("x86_64", "x86_64-linux-gnu", out64)
    ok32 = build_target("x86", "x86-linux-gnu", out32)

    if ok64 and ok32:
        print("\nAll Linux 64-bit and 32-bit .so binaries compiled successfully!")
    else:
        sys.exit(1)
