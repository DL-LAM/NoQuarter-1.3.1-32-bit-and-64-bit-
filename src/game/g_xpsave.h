#ifndef _G_XPSAVE_H
#define _G_XPSAVE_H

// Lucel: XP save structure. We read/write this directly to disk.
//
// We don't care about padding issues as the structure will be padded
// consistently on the same machine - if we want to share these across different
// platforms then we might need to deal with padding.

#define XP_SAVE_SIGNATURE 		0x0ACED00D
#define XP_SAVE_CUR_VER			0
#define XP_SAVE_FILE_EXT		".xp"
#define MAX_GUID_LENGTH			32

// [NQ 1.3.1 - Audit M5]: 32/64-bit portable XP save files.
// This struct used to be written to disk raw and contained a time_t, which is
// 4 bytes on 32-bit Linux but 8 bytes on 64-bit Linux and on Windows (MSVC).
// The file layout therefore changed when a server moved from the 32-bit to the
// 64-bit build, every read failed the exact-size check and all saved XP was
// "lost". The in-memory timestamp is now always 64-bit, and the file is read
// and written field by field at fixed byte offsets (see g_xpsave.c
// G_xpsave_to_disk / G_xpsave_read):
//
//   offset  size  field
//   0       4     signature
//   4       4     version
//   8       8     timestamp (int64)
//   16      36    netname  (MAX_NETNAME)
//   52      28    skillpoints (SK_NUM_SKILLS floats)
//   80            total = XP_SAVE_DISK_SIZE (padded to a multiple of 8)
//
// That is byte-for-byte the layout the old code produced on 64-bit Linux and
// on Windows (32 and 64-bit), so those existing files keep loading unchanged.
// Files written by the old 32-bit Linux build (4-byte time_t, 76 bytes =
// XP_SAVE_DISK_SIZE_LEGACY32) are still read and are rewritten in the new
// layout the next time that player's XP is saved.
typedef struct {
	int			signature;					// Check it's a valid save file
	int			version;					// Check file version. Allow for backwards compatibility later on.
	int64_t		timestamp;					// Timestamp of xp save file ([NQ 1.3.1 - Audit M5]: was time_t)
	char		netname[MAX_NETNAME];		// Store the player name
	float		skillpoints[SK_NUM_SKILLS];	// skillpoints
} g_xpsave_t;

#define XP_SAVE_DISK_OFS_NAME			16
#define XP_SAVE_DISK_OFS_SKILLS			(XP_SAVE_DISK_OFS_NAME + MAX_NETNAME)
#define XP_SAVE_DISK_SIZE				((XP_SAVE_DISK_OFS_SKILLS + (int)sizeof(float) * SK_NUM_SKILLS + 7) & ~7)
#define XP_SAVE_LEGACY32_OFS_NAME		12
#define XP_SAVE_LEGACY32_OFS_SKILLS		(XP_SAVE_LEGACY32_OFS_NAME + MAX_NETNAME)
#define XP_SAVE_DISK_SIZE_LEGACY32		(XP_SAVE_LEGACY32_OFS_SKILLS + (int)sizeof(float) * SK_NUM_SKILLS)

void		G_xpsave_writestats();
qboolean	G_xpsave_add(gentity_t *ent);
qboolean	G_xpsave_load(gentity_t *ent);
void		G_xpsave_resetxp();
void		G_xpsave_init_game();

#endif /* ifndef _G_XPSAVE_H */
