# Raynna's Runeballs

A colourful marble shooter for WoW Forever, with Horde/Alliance artwork, winding
roads, combos and special shots. Open with `/rrb` or `/runeballs`.

Download the versioned player ZIP from [Releases](https://github.com/raynna/runeballs/releases).
Extract its `RaynnaRuneballs` folder into `Interface/AddOns`.

See [features and controls](RaynnaRuneballs/README.md),
[CurseForge description](RaynnaRuneballs/CURSEFORGE.txt),
[asset/font credits](RaynnaRuneballs/ART-CREDITS.txt) and
[release process](RaynnaRuneballs/RELEASE.md).

## Development

Python dependencies: `lupa`, `Pillow`, `fonttools` (art/font rebuild only).

```
python tests/test_runeballs.py
python tests/test_flight_games.py
python tools/package_runeballs.py
```

Lua targets 5.1; format with StyLua using the included configuration.
Every release increments the addon version and includes a matching player ZIP.
Source artwork and tools are excluded from that ZIP. Automated/mock checks and
offline previews do not replace testing in the actual WoW Forever client.
