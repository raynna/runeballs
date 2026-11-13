# Raynna's Runeballs

A standalone coloured-marble shooter for WoW Forever (Interface 16001), version 0.5.17.
Aim an arcane launcher into a winding chain and match three or more marbles
before its leading ball reaches the void portal. Joining matching groups creates
chain reactions and score multipliers. Every round has a distinct route: a grove
spiral, serpentine bends, clover and switchbacks introduce the mechanics, followed
by generated routes with increasing turns and lobes. The campaign has 100 rounds with a gentler progression. Round one starts with
12 balls in the chain, 54 total marbles and a speed of 40 path pixels/second, increasing by 0.5 each round.
Six colours are available from round one: red, blue, green, yellow, purple and pearl. Speed and total marble count rise gradually across the campaign.

Rounds 1-29 are single-path. Dual paths appear at rounds 30, 40 and 50, then every
five rounds from 60 through 100. Each lane runs at 50% of the equivalent single
lane's speed and starts with a shorter chain. Both paths have exactly equal
lengths. Clearing round 100 completes the campaign; Play Again restarts round one
while retaining your personal best.

Alliance and Horde characters automatically receive different illustrated frames,
launcher bases and buttons. Marbles, controls and effects use simple cartoon
sprites with thick outlines. Ordinary balls are plain colours; only special shots
carry ability icons.

## Chain movement and specials

Marbles have independent path positions. A match leaves a visible gap: the leading
section stops, while the rear section advances and eventually pushes it. Matching
colours across a gap pull the front section backwards; a chain combo scores only
when the sections actually touch. Combo multipliers reward successive joins.

Each fired shot has an independent 3% chance to award special next-ammo.
The type is chosen randomly with equal chances:

- **Bomb:** clears up to three neighbouring balls ahead and three behind its position, plus the matching group.
- **Frost:** slows the chain for four seconds.
- **Rewind:** reverses the chain for up to 2.5 seconds.

Specials retain one of the six normal colours and activate only in a touching
match of at least three same-colour balls (special plus two others). Incoming
chain balls also have an independent 3% chance of a random special. Unmatched
special shots stay in the chain; blast collateral does not trigger their abilities.
Specials can be swapped just like normal balls. Explosions, shards, spark bursts,
portal rotation and danger pulses animate during play. Sounds reference native
WoW spell and UI assets, respect the game's SFX volume, and can be disabled in
Runeballs settings. Missing client sound references safely fall back to a UI ping.

## Playing

- `/rrb` or `/runeballs`: open/close. Minimap left-click also opens the game.
- Click **Play**, aim with your mouse, and left-click the board to fire.
- Right-click the board to exchange the loaded and next marble.
- Match at least three adjacent balls of the same colour. Only special ammunition carries icons. The small ball beside the launcher is next.
- Click **Pause**, close the window, or press Escape to pause. Reopening does
  not resume until Play is clicked. Combat closes and pauses the game.
- Clear the entire incoming chain to advance. Try again restarts the failed
  round with zero score; your personal best is retained.
- Drag the title bar to move the window.

`/rrb settings` opens **Settings → AddOns → Raynna's mods → Runeballs**.
Choose automatic flight opening, close on landing, minimap visibility and scale.
Minimap right-click opens settings; drag the minimap icon to reposition it.
`/rrb center`, `/rrb show`, `/rrb hide`, `/rrb scale 90` are also available.
Opening automatically on a flight waits for Play. Landing pauses only a window
opened automatically. Runs, scores, window position and preferences save per
character on normal logout/reload. This game uses no real gold or items.

## Install

Extract the ZIP's `RaynnaRuneballs` folder into the client's `Interface/AddOns`
directory. Enable it in the addon list. Restart the client if a new addon is not
discovered by reload. No other Raynna addon is required.

## Development

Engine.lua owns serializable simulation state; UI.lua renders pooled textures
and advances a fixed-step simulation only while playing. Theme.lua centralizes
styling. Core.lua handles persistence, commands, launcher and flight events.
The unchanged version-2 settings registry is shared with the other packages.
Version-1 saves migrate once to independent marble positions without resetting
scores, round progress, or preferences. Closing or reloading always pauses.
Audio.lua handles native sound selection, throttling and optional-API fallback.
Generated art sources and prompts are retained in `ArtSource` (development only).
Build runtime art with `python tools/build_runeballs_faction_art.py` (Pillow).
Export exact routes with `python tools/export_runeballs_preview.py` (lupa), then
render offline previews with `python tools/preview_runeballs.py` (Pillow).
Tests: `python tests/test_runeballs.py` (lupa required).
Package: `python tools/package_runeballs.py`.

Automated mock checks do not replace
verification of rendering, input and flight events in the actual client.

Version 0.2.2 removes the opaque backdrop that obscured the faction artwork and
removes decorative road characters. The interface adds cleaner typography,
button hover/press feedback, floating match scores and a portal-threat meter.

Version 0.3.0 adds saved, interruptible end-of-round animations. Defeat pulls the
entire remaining chain into the portal in about two seconds. Victory seals the
portal with a sparkle celebration. An animated result card then shows the score,
best score and Retry/Next round and Close controls. Result animations lock shots;
closing/reloading pauses them and reopening resumes them. Early rounds are slower.

Version 0.3.1 removes icons from ordinary marbles, separates score labels and values,
and cleans up text size, shadows, spacing, footer help and button typography.

## Version 0.4.0

New outlined cartoon typography, gold score displays, illustrated controls and
faction launchers, brighter plain marbles, recoil/trails and reduced-motion mode.
The shoot sound is a quiet native UI tick. Roads enter through edge tunnels;
rounds 6, 10, 14 and every fourth round thereafter have two simultaneous chains
and bridges. Balls beneath bridges cannot be hit until they emerge.
A shared flight chooser supports Tower Defense 0.4.3+ and PeggleForever without
changing Peggle settings. Manual opening stays independent.

Every released update increments the TOC version, builds a matching player ZIP,
and receives a matching vVERSION GitHub tag/release. See RELEASE.md.

## Version 0.4.1

Crossings use the actual stone background as a foreground cover: the lower road
and balls pass beneath it, while the upper road stays continuous. Covered balls
cannot be hit. Dual routes are exact mirrored paths of equal length, with two clear crossings and exits
over 450 board units apart. Larger circular sinkholes have subtle rim effects and an
inward pull during defeat. Single-layer gold text replaces clipped gradient bands;
labels have explicit bounds and buttons scale text to fit. Ordinary hits now use
a subtle native UI click, like shooting.

## Version 0.4.2

Compact starting holes sit at the board edges and face into each road. Exit holes
have a marble-sized opening and stone rim, aligned with the final road segment.
Dual lanes keep more space between parallel roads and around the exits; their
buried sections have directional arrow markers. Equal path lengths and widely
separated exits are retained. This version supersedes the large-hole previews.

Version 0.4.3 moves the next-ball preview beside the launcher to keep the
dual-path road and its label clear of each other.

## Version 0.4.4

Distinct teal stone entry openings are built into the outer board border. Compact
round exit pits use an aligned road-width mouth and a warm rim. Every route keeps
a 100-pixel clearance radius around the launcher center, also protecting the next
ammunition display. Dual routes retain exact equal lengths, clear perpendicular
crossings, underground arrows and widely separated exits. Entrance coordinates
extend to the illustrated border; covered entry balls remain protected.

Version 0.4.5 adds a rotating two-arm portal swirl inside each exit and a soft
teal pulse inside each entrance during play. Reduced motion uses steady glows.
Effects use preallocated textures and stop on pause/close.

## Version 0.5.0

The 100-round difficulty curve replaces the previous early dual-path schedule.
Old saved dual rounds below the new threshold become single-lane runs, preserving
score and remaining marbles. Runs stay paused after reload.

Balls now fade into view inside the entrance light, above its floor artwork.
The exit uses a plain round rim with the actual curved track underneath, plus a
continuous rotating energy spiral. Header values fit the different faction
plaques; footer icons/text have larger insets. The close control is an icon,
not a fitted text label.

Version 0.5.1 raises the base speed from 18 to 24 path pixels/second. Each
dual-path lane runs at exactly half the normal speed for its level. The existing
100-level progression and late introduction of dual paths are retained.

Version 0.5.2 fixes gap-contact matching and shot insertion locality, prevents
successful matches from pushing surviving sections forward, caps rewind at a
visible leading ball, and places combat effects and floating text above roads.

Version 0.5.4 uses continuous antialiased road textures, generated from the exact
engine routes, and advances movement on every render frame. Launcher artwork is
aligned to the loaded marble. The bundled flight chooser supports Runeballs and
Peggle together without Tower Defense.

To regenerate roads after route changes, run tools/export_runeballs_preview.py
with Lua 5.1/lupa, then tools/build_runeballs_roads.py with Pillow. All 112 route
textures are bundled; only the active one or two lanes are displayed.

Developer testing (Its-Raynna / Itsraynna character only): `/rrb demo N` starts
any round 1–100 immediately with its normal speed and lanes. `/rrb demo off`
returns to the paused campaign. Demo progress and scores are session-only;
reloading also restores the saved campaign. `//rrb` is an additional alias.

Version 0.5.9 gives every dual round a distinct visible route through mirrored
orientations and new detours. Lane lengths match, exits remain separated, and
tunnels cover at most 128 path units with at least 180 open units before exits.
Losing ends the run; New Game restarts round one. Share Result previews your
round and score, with selectable chat destinations and a separate Send button.
Matching sections retract more slowly so chain combos are easier to follow.
