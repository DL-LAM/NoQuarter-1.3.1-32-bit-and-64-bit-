# NQ-CE Anti-Cheat Design (draft)

Status: design only, nothing implemented yet.
Scope: server-side cheat detection and evidence logging for NoQuarter Community Edition.

---

## 1. Goals and non-goals

**Goals**
- Detect the cheats that actually exist today: wallhack/ESP and aimbot/triggerbot built into modified ET:Legacy clients, and timing (speed) hacks.
- Work entirely on the server, the only part a cheater cannot modify.
- Keep every piece of evidence about a player in one place (`wolfadmin.db`), queryable next to their aliases, IPs, warnings and bans.
- Give admins fast, readable information (`!acinfo`) and live alerts. Humans make the final call.

**Non-goals**
- Client-side scanning, file checksums or "hidden" checks. The client is open source and can be rebuilt; anything it reports about itself can be faked.
- Automatic bans. Detectors log and alert only until they have been tuned on real games (see section 9).
- Replacing `sv_pure`, forced cvars or ET:Legacy's own protections. This builds on top of them.

---

## 2. Threat model

| Cheat | How it works today | Our answer |
|---|---|---|
| Wallhack / ESP | Modified client draws players through walls using positions the server sends | Don't send hidden positions: ET:Legacy engine `wh_active 1` (layer 0) |
| Aimbot | Modified client moves the view onto targets | Server-side aim analysis (snaps, reaction time) |
| Triggerbot | Fires the instant the crosshair covers a target | Reaction-time and first-shot timing analysis |
| Wall tracking (ESP + human aim) | Player follows enemies behind walls | Aim-at-occluded-target analysis |
| Speedhack / timing | Client sends movement commands faster than real time | `commandTime` drift check (extends the existing check in `g_active.c`) |
| Modified pk3 / textures | Old-style see-through textures | Already blocked by `sv_pure 1` |

---

## 3. Layer 0: configuration (no code)

Do this first; it costs nothing and removes the most common cheat.

- `set wh_active 1`: ET:Legacy engine anti-wallhack. The server stops sending the real position of enemies the player has no line of sight to. Tune `wh_bbox_horz` / `wh_bbox_vert` (defaults 30 / 60) if players appear too late around corners. Leave `wh_add_xy 0`.
- `set sv_pure 1`.
- A real `force.cfg` (`g_ForceCvarFile`) locking visual and network cvars that give an advantage.

Verify with the test described in the dev notes: `devmap` with bots, `/r_drawworld 0`, toggle `wh_active`.

---

## 4. Architecture

```
 qagame (C)                                   WolfAdmin (Lua)                     wolfadmin.db (SQLite)
 ─────────────────────────────                ───────────────────────────         ─────────────────────
 ClientThink_real ─► g_anticheat.c            anticheat/anticheat.lua             player, alias, ban,
   per usercmd:      collectors               ├─ on et_ACFlag: store + alert ───► ac_flag
   view angles,      + detectors  ──hook──►   ├─ on map end / disconnect:         ac_stats
   shots, hits,      (thresholds              │   read sess.aWeaponStats ───────► (per player per map)
   visibility,        from g_ac_* cvars)      ├─ !acinfo  !acflags  !acstats ◄─── queries
   timing                                     └─ alerts to online admins
```

- **C (qagame)** sees every movement command (up to the client's frame rate, typically 125 per second). Only C can measure aim snaps and reaction times accurately. Lua runs at the server frame rate (20 per second), which is too coarse.
- **Lua (WolfAdmin module)** stores results, runs the admin commands and sends alerts. Easy to change without rebuilding.
- **SQLite** is the single place for all evidence, joined to WolfAdmin's existing player records.

---

## 5. Detectors (C, `src/game/g_anticheat.c`)

All detectors are off unless enabled in `g_ac_enable` (bitmask), and all thresholds come from cvars so they can be tuned per server.

### 5.1 Aim snap (aimbot)
For each command, compute the view-angle change and the time since the previous command (degrees per millisecond).
Flag when **all** are true:
1. angular speed above `g_ac_snapSpeed` (deg/ms),
2. the view stops within `g_ac_snapLand` degrees of an enemy's head or body within `g_ac_snapSettleMs`,
3. that enemy is visible (trace from eye to target),
4. a shot follows within `g_ac_snapFireMs`.

Humans flick too, so a single snap is weak evidence. The detector scores each snap (0.0 to 1.0) and the Lua side looks at how often it happens per map.

### 5.2 Reaction time (aimbot / triggerbot)
Record the time an enemy first becomes visible to the player (entering the field of view with a clear trace) and the time of the first hit on that enemy.
Human reaction is rarely below ~150 ms. Flag repeated first hits under `g_ac_reactionMinMs`.

### 5.3 Wall tracking (ESP used with human aim)
While an enemy is **not** visible, measure how long the player's crosshair stays within `g_ac_trackDeg` degrees of that enemy while it moves.
Flag sustained tracking longer than `g_ac_trackMs`. With `wh_active 1` this mostly catches hacks that predict positions, so it is lower priority.

### 5.4 Command timing (speedhack)
Compare the sum of the client's `commandTime` advances with real server time over a sliding window.
Flag drift above `g_ac_timeDriftMs` that persists (not just a lag spike).

### 5.5 Events to ignore (false-positive guards)
Reset all per-player state and skip evaluation on: spawn, teleport, death, limbo, spectating, mounting or leaving mounted weapons and tanks, binoculars and mortar/artillery aiming, `setviewpos`, and packet loss or ping spikes above `g_ac_maxPing`.

### 5.6 Performance budget
- Only test enemies inside the player's field of view and within range.
- Cap line-of-sight traces per server frame (`g_ac_maxTraces`), round-robin across players.
- Measure CPU on the 1 GB VPS with a full server before enabling in production.

---

## 6. C to Lua interface

New Lua callback, implemented like the existing `et_Obituary` hook (`G_LuaHook_*` in `g_lua.c`):

```lua
-- called by qagame when a detector fires
function et_ACFlag(clientNum, detector, severity, details)
  -- detector: "aimsnap" | "reaction" | "walltrack" | "timing"
  -- severity: 0.0 - 1.0
  -- details:  short human-readable text, e.g. "171 deg in 8 ms onto head, fired 12 ms later"
end
```

New cvars (server config, not source code, so tuning values are not published in the repo):

| Cvar | Meaning | Starting value |
|---|---|---|
| `g_ac_enable` | bitmask: 1 snap, 2 reaction, 4 walltrack, 8 timing | 0 |
| `g_ac_snapSpeed` | deg/ms to count as a snap | tune |
| `g_ac_snapLand` | deg from target where the snap must stop | tune |
| `g_ac_snapSettleMs` / `g_ac_snapFireMs` | settle / fire windows | tune |
| `g_ac_reactionMinMs` | suspicious first-hit reaction time | 120 |
| `g_ac_trackDeg` / `g_ac_trackMs` | wall-tracking window | tune |
| `g_ac_timeDriftMs` | allowed command-time drift | tune |
| `g_ac_maxPing` / `g_ac_maxTraces` | guards and CPU cap | 250 / 64 |

---

## 7. Database (added to `wolfadmin.db`)

Created by the WolfAdmin anti-cheat module with `CREATE TABLE IF NOT EXISTS`, and added to `database/new/sqlite.sql` plus an upgrade script for existing databases.

```sql
CREATE TABLE IF NOT EXISTS `ac_flag` (
  `id`        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `player_id` INTEGER NOT NULL,          -- WolfAdmin player.id
  `datetime`  INTEGER NOT NULL,          -- unix time
  `map`       TEXT    NOT NULL,
  `detector`  TEXT    NOT NULL,          -- aimsnap / reaction / walltrack / timing
  `severity`  REAL    NOT NULL,          -- 0.0 - 1.0
  `details`   TEXT    NOT NULL,
  `reviewed`  INTEGER NOT NULL DEFAULT 0, -- set by an admin after checking
  CONSTRAINT `ac_flag_player` FOREIGN KEY (`player_id`) REFERENCES `player` (`id`)
);
CREATE INDEX IF NOT EXISTS `ac_flag_player_idx` ON `ac_flag` (`player_id`);
CREATE INDEX IF NOT EXISTS `ac_flag_time_idx`   ON `ac_flag` (`datetime`);

CREATE TABLE IF NOT EXISTS `ac_stats` (
  `id`         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `player_id`  INTEGER NOT NULL,
  `datetime`   INTEGER NOT NULL,         -- end of map / disconnect
  `map`        TEXT    NOT NULL,
  `playtime`   INTEGER NOT NULL,         -- seconds on a team
  `shots`      INTEGER NOT NULL,
  `hits`       INTEGER NOT NULL,
  `headshots`  INTEGER NOT NULL,
  `kills`      INTEGER NOT NULL,
  `deaths`     INTEGER NOT NULL,
  `snaps`      INTEGER NOT NULL DEFAULT 0,   -- from C detectors (phase 2)
  `avg_reaction_ms` INTEGER,                 -- from C detectors (phase 2)
  CONSTRAINT `ac_stats_player` FOREIGN KEY (`player_id`) REFERENCES `player` (`id`)
);
CREATE INDEX IF NOT EXISTS `ac_stats_player_idx` ON `ac_stats` (`player_id`);
```

**Phase 1 stats need no C changes.** Lua can already read `sess.aWeaponStats` through `et.gentity_get`. It is a flat array of `weapon_stat_t` (5 unsigned ints per weapon: `atts, deaths, headshots, hits, kills`), so field `f` of weapon `w` is index `w * 5 + f`, for `w` from 0 to `WS_MAX`. Sum hitscan weapons for shots/hits/headshots; `sess.kills` and `sess.deaths` give totals.

### Example queries

Everything about one player:
```sql
SELECT p.id, p.guid, p.ip, datetime(p.lastseen, 'unixepoch') AS lastseen,
       (SELECT group_concat(a.alias, ', ') FROM alias a WHERE a.player_id = p.id) AS aliases,
       (SELECT count(*) FROM ban b WHERE b.victim_id = p.id)                    AS bans,
       (SELECT count(*) FROM ac_flag f WHERE f.player_id = p.id)                AS flags
FROM player p WHERE p.guid LIKE '%3F9A%';
```

Recent flags, worst first:
```sql
SELECT a.alias, f.map, f.detector, f.severity, f.details,
       datetime(f.datetime, 'unixepoch') AS time
FROM ac_flag f
JOIN alias a ON a.player_id = f.player_id
WHERE f.datetime > strftime('%s','now','-7 days')
GROUP BY f.id ORDER BY f.severity DESC LIMIT 20;
```

Headshot ratio compared with the server average (players with 20+ minutes played):
```sql
SELECT player_id,
       1.0 * sum(headshots) / max(sum(hits), 1) AS hs_ratio,
       1.0 * sum(hits)      / max(sum(shots), 1) AS accuracy
FROM ac_stats GROUP BY player_id HAVING sum(playtime) > 1200
ORDER BY hs_ratio DESC;
```

---

## 8. WolfAdmin module and commands

New module `luascripts/wolfadmin/anticheat/anticheat.lua` (loaded like the other WolfAdmin modules), plus commands in `commands/admin/`.

| Command | Permission | What it shows |
|---|---|---|
| `!acinfo <name\|slot\|guid>` | `acinfo` | Aliases, last IP, warnings/bans, flag count by detector, accuracy and headshot ratio vs server average, last 5 flags |
| `!acflags [count]` | `acinfo` | Latest flags server-wide |
| `!acstats` | `acinfo` | Server averages (accuracy, headshot ratio, reaction time) used as the baseline |
| `!acreview <flag id>` | `acreview` | Marks a flag as checked by an admin |

Alerts: when a flag's severity is at or above `g_ac_alertSeverity`, send a private chat line to every online admin with the `acalert` permission, and write it to `admin.log`.

---

## 9. Rollout and tuning

1. **Phase 0:** layer 0 config (`wh_active`, `force.cfg`). Test on the VPS.
2. **Phase 1:** `ac_stats` from Lua only, plus `!acinfo` / `!acstats`. No detection, just baselines from real players.
3. **Phase 2:** C detectors in **log-only** mode on the public test server. Compare flags against known legit players and bots; adjust thresholds until legit players rarely flag.
4. **Phase 3:** enable admin alerts.
5. **Phase 4 (optional):** automatic actions limited to evidence gathering (for example, start a server demo of a flagged player). Kicks or bans stay manual.

A detector is ready for alerts when, over at least a week of real games, fewer than ~1 in 50 legit regular players ever reach alert severity.

---

## 10. Privacy and retention

- WolfAdmin already stores GUIDs, names and IPs. Anti-cheat adds gameplay statistics and flags.
- Post a short notice on the server (banner or MOTD) that gameplay stats are logged for anti-cheat.
- Only admins with `acinfo` can see the data.
- Retention: delete `ac_stats` rows older than `g_ac_statsRetentionDays` (default 90) and unreviewed low-severity flags older than 180 days, at map start.

---

## 11. License note

NoQuarter is distributed under the No Quarter Mod Team's Modified RPL 1.1. Running a modified server for the public counts as deploying it, so the detector code in qagame must be published with the rest of the source. Threshold values live in server config files, not in the source, which keeps exact tuning private to each server.

---

## 12. Related hardening (found while designing this)

- `et.gentity_get` / `et.gentity_set` with `FIELD_INT_ARRAY` and `FIELD_FLOAT_ARRAY` do not range-check the array index (`g_lua.c`). A script can read or write outside the array. Lua scripts are server-admin code, so the risk is low, but the index should be checked against the field's size before this module relies on it.

---

## 13. Open questions

- Exact cost of per-command visibility traces on a full 1 GB VPS; may need sampling instead of every command.
- Whether ET:Legacy's `wh_active` changes how visibility should be computed for the reaction-time detector (hidden enemies are moved server-side).
- Handling players who change GUID to escape their history (IP and alias correlation in `!acinfo`).
