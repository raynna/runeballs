# Release checklist

For every update: increment the TOC version, document changes, run Lua 5.1 tests
and StyLua, build tools/package_runeballs.py, verify the ZIP, commit and tag
vVERSION, then attach RaynnaRuneballs-VERSION.zip to the GitHub release.
The ZIP contains one installable RaynnaRuneballs folder, runtime art/fonts and
license notices. ArtSource, tests and build tools stay out of player downloads.
Deploy to WoW Forever only when authorized. Never modify WTF saved variables.
Mock previews are not in-game testing. CurseForge uploads use the player ZIP and
CURSEFORGE.txt description; the target client is Interface 16001.
