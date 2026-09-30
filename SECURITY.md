# Security Policy

## Supported versions

| Version | Supported |
| :--- | :--- |
| 1.3.1b7 (latest release) | Yes |
| 1.3.0 and older (including 1.2.9) | No. These have known crash bugs that are fixed in 1.3.1. Please upgrade. |

## Reporting a vulnerability

If you find a way to crash a NoQuarter server, run code on a server or client, bypass admin or referee permissions, or corrupt player data (XP saves, shrubbot or WolfAdmin files), please **report it privately** so it can be fixed before it's widely known:

1. **GitHub (preferred):** go to the **Security** tab of this repository and click **Report a vulnerability**. Only the maintainer can see the report.
2. **Discord:** send a direct message to the maintainer on the NoQuarter Discord (https://discord.gg/c5yREDTt5). Please don't post details in public channels.

Please don't open a public issue, post in public Discord channels, or share working exploits until a fix has been released.

### What to include

- NoQuarter version, engine (ET:Legacy version or ET 2.60b) and platform (Windows or Linux, 32-bit or 64-bit)
- What happens and how to reproduce it: the command, map, cvar values or client action that triggers it
- Server console output or a crash log (`nq/crash.log`, `etconsole.log`) if you have one

### What to expect

- An acknowledgement within about a week. This is a volunteer project, so response times can vary.
- Updates while a fix is being worked on, and credit in the release notes when it ships (unless you'd rather stay anonymous).

## Out of scope

- Bugs in the ET:Legacy engine itself: report those to the ET:Legacy project (https://github.com/etlegacy/etlegacy).
- Bugs in Omni-Bot or upstream WolfAdmin, unless they are caused by how NoQuarter uses them.
- Admin impersonation through a stolen `cl_guid`. Admins are identified by GUID, which the player's client sends and the server cannot verify. Keep admin GUIDs private, and use referee passwords or rcon for sensitive commands.
- Problems that need rcon access or access to the server's files.
