import os
import sys
import shutil
import zipfile
import ctypes

def check_dll_exports(dll_path, expected_exports):
    print(f"Checking {dll_path}...")
    try:
        lib = ctypes.CDLL(dll_path)
        for sym in expected_exports:
            has_sym = hasattr(lib, sym)
            print(f"  Export '{sym}': {'OK' if has_sym else 'MISSING'}")
            if not has_sym:
                return False
        return True
    except Exception as e:
        print(f"  Failed to load DLL {dll_path}: {e}")
        return False

# Paths
TRUNK_DIR = r"C:\Users\Dylan\Documents\ETFiles\WET-NoQuarter-master\NQV1.3.0dev\trunk"
BUILD64_DIR = os.path.join(TRUNK_DIR, "build64", "Release")
BUILD32_DIR = os.path.join(TRUNK_DIR, "build32", "Release")
LINUX64_DIR = os.path.join(BUILD64_DIR, "linux")
LINUX32_DIR = os.path.join(BUILD32_DIR, "linux")

RELEASE_DIR = r"C:\Users\Dylan\Documents\NQ_1.3.1_Mod"
ET64_NQ_DIR = r"C:\ETLegacy64\nq"
CLIENT_NQ_DIR = r"C:\Users\Dylan\Documents\ETLegacy\nq"

# 1. Verify 64-bit DLL exports
cgame64 = os.path.join(BUILD64_DIR, "cgame_mp_x64.dll")
ui64 = os.path.join(BUILD64_DIR, "ui_mp_x64.dll")
qagame64 = os.path.join(BUILD64_DIR, "qagame_mp_x64.dll")

cgame32 = os.path.join(BUILD32_DIR, "cgame_mp_x86.dll")
ui32 = os.path.join(BUILD32_DIR, "ui_mp_x86.dll")
qagame32 = os.path.join(BUILD32_DIR, "qagame_mp_x86.dll")

assert check_dll_exports(cgame64, ["vmMain", "dllEntry"]), "cgame_mp_x64.dll exports missing!"
assert check_dll_exports(ui64, ["vmMain", "dllEntry"]), "ui_mp_x64.dll exports missing!"
assert check_dll_exports(qagame64, ["vmMain", "dllEntry"]), "qagame_mp_x64.dll exports missing!"

# Helper to build Universal (Multi-Architecture) Binary PK3
def build_universal_binary_pk3(pk3_path):
    print(f"\nBuilding Universal Multi-Architecture PK3: {pk3_path}...")
    os.makedirs(os.path.dirname(pk3_path), exist_ok=True)
    with zipfile.ZipFile(pk3_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        # Windows 64-bit Client DLLs
        z.write(cgame64, "cgame_mp_x64.dll")
        z.write(ui64, "ui_mp_x64.dll")
        z.write(cgame64, "cgame.mp.x86_64.dll")
        z.write(ui64, "ui.mp.x86_64.dll")

        # Windows 32-bit Client DLLs
        z.write(cgame32, "cgame_mp_x86.dll")
        z.write(ui32, "ui_mp_x86.dll")
        z.write(cgame32, "cgame.mp.i386.dll")
        z.write(ui32, "ui.mp.i386.dll")

        # Linux 64-bit Client SOs
        cgame64_so = os.path.join(LINUX64_DIR, "cgame.mp.x86_64.so")
        ui64_so = os.path.join(LINUX64_DIR, "ui.mp.x86_64.so")
        if os.path.exists(cgame64_so):
            z.write(cgame64_so, "cgame.mp.x86_64.so")
            z.write(cgame64_so, "cgame_mp_x64.so")
        if os.path.exists(ui64_so):
            z.write(ui64_so, "ui.mp.x86_64.so")
            z.write(ui64_so, "ui_mp_x64.so")

        # Linux 32-bit Client SOs
        cgame32_so = os.path.join(LINUX32_DIR, "cgame.mp.i386.so")
        ui32_so = os.path.join(LINUX32_DIR, "ui.mp.i386.so")
        if os.path.exists(cgame32_so):
            z.write(cgame32_so, "cgame.mp.i386.so")
            z.write(cgame32_so, "cgame_mp_x86.so")
        if os.path.exists(ui32_so):
            z.write(ui32_so, "ui.mp.i386.so")
            z.write(ui32_so, "ui_mp_x86.so")
    print(f"Built {pk3_path} successfully.")

# 2. Build Universal nq_b_v1.3.1_64.pk3
pk3_64_path = os.path.join(RELEASE_DIR, "nq_b_v1.3.1_64.pk3")
build_universal_binary_pk3(pk3_64_path)

# 3. Build Universal nq_b_v1.3.1_32.pk3
pk3_32_path = os.path.join(RELEASE_DIR, "DLL's", "Windows", "32 Bit", "nq_b_v1.3.1_32.pk3")
build_universal_binary_pk3(pk3_32_path)

# Copy to Linux 32-Bit folder
shutil.copy2(pk3_32_path, os.path.join(RELEASE_DIR, "DLL's", "Linux", "32 Bit", "nq_b_v1.3.1_32.pk3"))


# 4. Update menudef files and menus in nq_v1.3.1_b.pk3
nq_v131_b = os.path.join(RELEASE_DIR, "nq_v1.3.1_b.pk3")
menudef_h = os.path.join(TRUNK_DIR, "etmain", "ui", "menudef.h")
menudef2_h = os.path.join(TRUNK_DIR, "etmain", "ui", "menudef2.h")
vote_map_menu = os.path.join(TRUNK_DIR, "assets", "ui", "ingame_vote_map.menu")

print(f"\nUpdating {nq_v131_b} with new menudef headers and fixed menus...")
temp_pk3 = nq_v131_b + ".tmp"
with zipfile.ZipFile(nq_v131_b, 'r') as zin, zipfile.ZipFile(temp_pk3, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == "ui/menudef.h":
            zout.write(menudef_h, "ui/menudef.h")
        elif item.filename == "ui/menudef2.h":
            zout.write(menudef2_h, "ui/menudef2.h")
        elif item.filename == "ui/ingame_vote_map.menu":
            zout.write(vote_map_menu, "ui/ingame_vote_map.menu")
        else:
            buffer = zin.read(item.filename)
            zout.writestr(item, buffer)

os.replace(temp_pk3, nq_v131_b)
print("Updated nq_v1.3.1_b.pk3 successfully.")

# 5. Copy release binaries to DLL's subfolders
win64_dir = os.path.join(RELEASE_DIR, "DLL's", "Windows", "64 Bit")
win32_dir = os.path.join(RELEASE_DIR, "DLL's", "Windows", "32 Bit")
lin64_dir = os.path.join(RELEASE_DIR, "DLL's", "Linux", "64 Bit")
lin32_dir = os.path.join(RELEASE_DIR, "DLL's", "Linux", "32 Bit")

shutil.copy2(qagame64, os.path.join(RELEASE_DIR, "qagame_mp_x64.dll"))
shutil.copy2(qagame64, os.path.join(win64_dir, "qagame_mp_x64.dll"))
shutil.copy2(pk3_64_path, os.path.join(win64_dir, "nq_b_v1.3.1_64.pk3"))

shutil.copy2(qagame32, os.path.join(win32_dir, "qagame_mp_x86.dll"))

if os.path.exists(os.path.join(LINUX64_DIR, "qagame.mp.x86_64.so")):
    shutil.copy2(os.path.join(LINUX64_DIR, "qagame.mp.x86_64.so"), os.path.join(lin64_dir, "qagame_mp_x64.so"))
shutil.copy2(pk3_64_path, os.path.join(lin64_dir, "nq_b_v1.3.1_64.pk3"))

if os.path.exists(os.path.join(LINUX32_DIR, "qagame.mp.i386.so")):
    shutil.copy2(os.path.join(LINUX32_DIR, "qagame.mp.i386.so"), os.path.join(lin32_dir, "qagame_mp_x86.so"))

def safe_copy(src, dst):
    try:
        shutil.copy2(src, dst)
        print(f"  Copied {os.path.basename(src)} -> {dst}")
    except PermissionError:
        print(f"  [NOTICE] Could not copy {os.path.basename(src)} to {dst} (game/server is currently running). Restart game/server to apply.")
    except Exception as e:
        print(f"  [WARN] Copy failed: {e}")

# 6. Copy to active test game directories
if os.path.exists(ET64_NQ_DIR):
    print(f"\nUpdating {ET64_NQ_DIR}...")
    safe_copy(pk3_64_path, os.path.join(ET64_NQ_DIR, "nq_b_v1.3.1_64.pk3"))
    safe_copy(nq_v131_b, os.path.join(ET64_NQ_DIR, "nq_v1.3.1_b.pk3"))
    safe_copy(qagame64, os.path.join(ET64_NQ_DIR, "qagame_mp_x64.dll"))

if os.path.exists(CLIENT_NQ_DIR):
    print(f"\nUpdating {CLIENT_NQ_DIR}...")
    safe_copy(pk3_64_path, os.path.join(CLIENT_NQ_DIR, "nq_b_v1.3.1_64.pk3"))
    safe_copy(nq_v131_b, os.path.join(CLIENT_NQ_DIR, "nq_v1.3.1_b.pk3"))
    safe_copy(cgame64, os.path.join(CLIENT_NQ_DIR, "cgame_mp_x64.dll"))
    safe_copy(ui64, os.path.join(CLIENT_NQ_DIR, "ui_mp_x64.dll"))
    safe_copy(cgame32, os.path.join(CLIENT_NQ_DIR, "cgame_mp_x86.dll"))
    safe_copy(ui32, os.path.join(CLIENT_NQ_DIR, "ui_mp_x86.dll"))
    safe_copy(qagame64, os.path.join(CLIENT_NQ_DIR, "qagame_mp_x64.dll"))

ET32_NQ_DIR = r"C:\Enemy Territory - Legacy\nq"
if os.path.exists(ET32_NQ_DIR):
    print(f"\nUpdating {ET32_NQ_DIR}...")
    safe_copy(pk3_64_path, os.path.join(ET32_NQ_DIR, "nq_b_v1.3.1_64.pk3"))
    safe_copy(pk3_32_path, os.path.join(ET32_NQ_DIR, "nq_b_v1.3.1_32.pk3"))
    safe_copy(nq_v131_b, os.path.join(ET32_NQ_DIR, "nq_v1.3.1_b.pk3"))
    safe_copy(cgame32, os.path.join(ET32_NQ_DIR, "cgame_mp_x86.dll"))
    safe_copy(ui32, os.path.join(ET32_NQ_DIR, "ui_mp_x86.dll"))
    safe_copy(qagame32, os.path.join(ET32_NQ_DIR, "qagame_mp_x86.dll"))

print("\nAll packaging and deployments completed successfully!")
