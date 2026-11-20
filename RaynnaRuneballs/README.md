# Raynna's Runeballs

A standalone coloured-marble shooter for WoW Forever (Interface 16001), version 0.5.32.
Aim an arcane launcher into a winding chain and match three or more marbles
before its leading ball reaches the void portal. Joining matching groups creates
chain reactions and score multipliers. The 100-round campaign alternates twelve
single-path shape families: a circular opening spiral, broad switchbacks, angular
coils, folded corridors, sweeping bends and winding loops. Later editions change
orientation and proportions; dual rounds add short covered crossings. Single paths
have at least 2,500 path units of travel, with round one about 20% longer than in
0.5.23. Round one starts with
12 balls in the chain, 54 total marbles and a speed of 40 path pixels/second, increasing by 0.5 each round.
Six colours are available from round one: red, blue, green, yellow, purple and pearl. Speed and total marble count rise gradually across the campaign.

Rounds 1-29 are single-path. Dual paths appear at rounds 30, 40 and 50, then every
five rounds from 60 through 100. Each lane runs at 50% of the equivalent single
lane's speed and starts with a shorter chain. Both paths have exactly equal
lengths. Clearing round 100 completes the campaign; Play Again restarts round one
while retaining your personal best.

Alliance and Horde characters automatically receive different illustrated frames,
launcher bases and buttons. Marbles, controls and effects use simple cartoon
sprites with thick outlines. Ordinary balls are plain colours; only special balls
carry ability icons.

## Chain movement and specials

Marbles have independent path positions. A match leaves a visible gap: the leading
section stops, while the rear section advances and eventually pushes it. Matching
colours across a gap pull the front section backwards; a chain combo scores only
when the sections actually touch. Combo multipliers reward successive joins.

Each fired shot has an independent 3% chance to award special next-ammo.
Ten types share that chance equally (0.3% per type overall):

- **Bomb:** blasts a circular 120-unit screen-space radius, including nearby bends and the other lane; tunnel-hidden balls remain protected.
- **Frost:** slows the chain for four seconds.
- **Rewind:** reverses the chain for up to 2.5 seconds.
- **Rainbow:** completes every valid colour group touching it. Two whites + Rainbow + two blues clears all five; one white + Rainbow + one blue does not qualify.
- **Lightning:** zaps up to five exposed same-colour balls, nearest first.
- **Paint:** recolours up to four nearby ordinary balls within 180 path units; new touching matches resolve after 0.45 seconds as chain combos.
- **Stasis:** stops lane movement for three seconds; shooting remains available.
- **Magnet:** pulls separated groups together for six seconds, including unlike colours, and halves forward lane speed.
- **Treasure:** doubles subsequent match/clear points on that lane for eight seconds.
- **Ward:** protects that lane for twelve seconds; one portal breach consumes it and starts a 2.5-second rewind.

Coloured specials retain one of the six normal colours and activate in a touching
match of at least three same-colour balls (special plus two others). Incoming
chain balls also have an independent 3% chance of a random special. Unmatched
special shots stay in the chain. Bomb blasts and lightning also activate caught
specials; each physical ball can activate only once per reaction. Lane effects
do not spill into the other lane. Timers pause with the game and survive reloads.
Every third consecutive shot that directly makes a match earns a precision bonus:
+300 at three, +600 at six, then +900 at nine and every third match beyond it.
A miss or non-matching insertion resets the streak, without removing earned points.
Delayed Paint/gap combos still score normally but do not count as direct shots.
The HUD shows loaded-special help, active timers and precision rewards.

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
“Close game when flight is done” defaults to off: an automatically opened game
stays visible and pauses after landing. Enable it to close automatically instead.
Manually opened games remain open; explicit saved choices are preserved.
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

Rainbow shares the existing 3% total special rate equally with the other nine
abilities (0.3% per type overall). Its light cycles through the six colours,
with a steady pearl glow under reduced motion.

Version 0.5.24 replaces the repeated single-path spiral formula with twelve route
families and visibly distinct editions throughout the campaign. Single paths are
about 37% longer on average than 0.5.23. Their roads retain at least 32 screen pixels
of centreline separation outside adjacent bends, clear portals and launcher space.
Speed and the half-speed dual-lane rule are unchanged. Saved runs retain score,
marbles and preferences, pause on reload and discard transient effects/projectiles
from the old geometry. The release includes six individual, labelled offline
preview PNGs showing both factions, different rounds and special effects; these
are staged previews, not live WoW screenshots.

Version 0.5.26 adds six coloured specials, a precision-shot streak mechanic and
36 new ball sprites with six distinct activation glyphs and lightning arcs.
Rainbow now clears valid groups on both sides, and powered clears chain into
caught specials. Regenerate the new sprites with tools/build_runeballs_specials.py.

Version 0.5.27 replaces the activation graphics with luminous 2D VFX for all ten
specials. Lightning uses sequential branched arcs, bright cores, colour-matched
bloom and illuminated hit points; its animation survives secondary bomb effects.
Other powers use glowing shockwaves, icy shards, rewind vortices, prismatic
sparks, paint splashes, clock rings, magnetic waves, treasure glints and shield
pulses. The existing idle marble glow and gameplay balance are unchanged.
Reduced motion removes jumping arcs and flying particles. These are additive UI
light effects on the board, not 3D world lighting. Rebuild the materials with
tools/build_runeballs_effects.py; tools/preview_runeballs_effects.py renders the
all-effects review sheet. The release includes six PNGs and an animated Lightning
preview, all labelled offline renders rather than live client screenshots.


Version 0.5.28 adds colour-matched match rings and light fragments, stronger combo
feedback, multicolour victory fireworks, and a cyan shield around warded exits.
Active Rewind, Frost, Stasis, Magnet and Treasure have small per-ball indicators,
including simultaneous buffs; tunnel-hidden marbles remain hidden. Reduced motion
uses steady indicators and disables flying fragments. Magnet now lasts six seconds,
pulls unlike gaps at 110 units/sec and halves forward lane speed while active.


Version 0.5.29 replaces orbiting buff icons with material overlays on affected
marbles. Frost encases them in translucent faceted ice; six melting stages follow
the remaining four-second timer. Time Stop binds them with crossed chains that
release during its final 0.45 seconds. Rewind wraps, magnetic bands and treasure
rims also sit on the balls themselves. Matching colours remain visible, tunnel
occlusion and insertion easing are preserved, and reduced motion keeps static
materials. Bomb detonations use warm orange flame lobes, a hot yellow core and
rising flame particles; idle special-ball glows still use their matching colour.


Version 0.5.30 replaces the flat ice and effect materials with approved generated
artwork: six thaw frames, polished interlocking chain links, fire/ember textures,
and Rewind/Magnet/Treasure wraps. Time Stop uses one continuous chain from tail
to head, following curves and hiding in tunnels, rather than binding each ball.
Each marble colour now has four breaking frames: cracked, split, scattered and
fading fragments. Reduced motion keeps a static split frame. Lightning jumps
are spaced 0.18 seconds apart with 0.10-second travel and a 1.55-second lifetime.
Bombs use a 120-unit circular blast that reaches nearby road sections and both
lanes, activates caught specials once, and preserves out-of-radius/hidden balls.
Explosion visuals persist when another caught special activates.


Version 0.5.31 smooths the existing four breaking frames with eased crossfades
and continuous expansion. Breaks begin at the actual eased marble position,
inherit forward/reverse/gap-closing motion, then gradually slow through drag.
Stationary chains stay stationary; reduced motion uses a static frame. No new
sprites are added, and the blend reuses existing pooled textures.


Version 0.5.32 makes active powers clearer without obscuring matching colours.
Magnet sends cyan directional pulses backward through open gaps along the road;
its cue pauses under Time Stop/Rewind and stays hidden in tunnels. Treasure now
has a gold ×2 symbol on every colour, including loaded/next ammunition. Time Stop
has a thicker continuous chain beside the train and an endpoint hourglass. Frost,
Rewind and Treasure sit farther out on the rim, and Magnet uses a subtle outer
ring instead of crossing the ball centre. Reduced motion keeps static arrows.
