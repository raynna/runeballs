# 0.5.22

- Softened special-ball light spill from 70–100% opacity to 38–55%, with a smaller pulse footprint (54–58px on chain balls).
- Applied the same brightness reduction to the loaded special ball, with a proportionately smaller launcher glow. Softened chain outline rings too.
- Colour matching, pulse motion and ability mechanics are unchanged.

Lua 5.1 regression tests and StyLua passed; unchanged faction layouts reviewed. Use /reload. Saves are untouched; in-game brightness needs user review.

# 0.5.21

- Loaded special ammunition in the central launcher now uses the same coloured light-spill texture and pulse as special chain balls, sized for the larger loaded marble.
- The light follows launcher recoil, matches the ball colour, stays steady with reduced motion and disappears for ordinary ammo or when closing the game.

Lua 5.1 tests and StyLua passed; unchanged faction layout previews reviewed. Use /reload. Actual glow appearance needs in-game confirmation; saves are preserved.

# 0.5.20

- Replaced the faint special-chain glow with a dedicated annular light-spill texture. Its brighter falloff sits outside the ball, illuminating the surrounding road rather than fading out inside the marble.
- Increased pulse footprint to 64–72px and light opacity to 70–100%. The centre stays transparent so the matching colour and ability symbol remain readable.
- Light still uses the ball colour, stays hidden in tunnels and respects reduced motion.

Lua 5.1 regression tests and StyLua passed. Unchanged faction layouts reviewed. Actual glow strength needs in-client confirmation. Use /reload; restart WoW if the new texture does not load. Saves are preserved.

# 0.5.19

- Special-ball auras, loaded/in-flight rings, trails and special impact particles now use the marble's matching colour instead of an ability colour. Symbols still identify Bomb, Frost and Rewind.
- Inserted balls ease from their projectile contact point into the chain over 0.16 seconds; pushed neighbours ease aside from their previous positions.
- Collision and matching resolve immediately. Reduced motion skips the positional animation, and special auras follow the eased positions.

Lua 5.1 regressions cover all six aura/impact colours and insertion start/settle positions alongside existing gameplay checks. StyLua passed; unchanged faction layouts reviewed. Actual animation needs in-game confirmation. Use /reload; saves are preserved.

# 0.5.18

- Special balls travelling in the chain now have a pulsing ability-coloured glow and thin light ring.
- Bombs emit rising orange sparks, Frost has icy shimmer, and Rewind has orbiting violet light. Ball colours and ability symbols remain visible.
- Auras are hidden inside tunnels and entrances, use steady glow with reduced motion, and clean up on removal or close. Pooled visuals are capped for performance.
- Matching rules, 3% special chance and speeds are unchanged.

Lua 5.1 tests cover pulse timing, hidden tunnel balls, reduced motion and cleanup. StyLua passed; unchanged faction layouts reviewed. Actual effects need in-game visual confirmation. Use /reload; saves are untouched.

# 0.5.17

- Specials now retain any of the six ball colours, with 18 matching-colour ability sprites.
- A special activates only in a touching group of at least three same-colour balls: special plus two others. Special shots insert normally and wait for a match instead of triggering on impact.
- Incoming chain balls also have an independent 3% total chance of carrying a random Bomb, Frost or Rewind. Ammo retains its 3% total chance.
- Matching a Bomb clears its matching group and up to three original neighbours ahead and three behind. Orange particles travel both ways along the road. Unmatched specials removed as collateral do not activate.
- Saved chain abilities persist through reload. Normal balls remain plain.

Lua 5.1 tests cover all 18 variants, no activation with only two matches, unmatched projectile insertion, incoming special spawns, persistence and exact three-neighbour bomb bounds. StyLua and both faction previews checked. Use /reload; restart WoW if newly added textures are not loaded. Not tested inside WoW.

# 0.5.16

- Starting speed reduced from 48 to 40: 25% above the former base of 32.
- Replaced the accelerating curve with a steady +0.5 path units/second per round: 40 + 0.5*(round-1).
- Each dual lane remains exactly half the normal speed for that round. Round 100 base speed is 89.5, or 44.75 per dual lane.
- Total special-ammo chance remains 3%.

Lua 5.1 tests verify the start speed, exact +0.5 progression and half-speed lanes across all 100 rounds. StyLua passed; unchanged faction layouts reviewed. Use /reload. Saves are preserved; balance needs in-game playtesting.

# 0.5.15

- Starting speed increased from 32 to 48 path units/second (50% faster).
- Stronger accelerating round curve: 48 + 0.55*(round-1) + 0.004*(round-1)^2. Each round's speed increase is larger than the previous one.
- Each dual-path lane remains exactly half the equivalent round's normal speed.
- Examples: round 1 = 48; round 25 = 63.504; round 50 base = 83.354, each lane = 41.677; round 100 base = 141.654, each lane = 70.827.

Lua 5.1 gameplay tests and StyLua passed. Tests cover increasing speed gains and exact half-speed lanes across all 100 rounds. Unchanged faction layouts reviewed. Use /reload; existing runs keep progress and use the new speeds. In-game balance still needs playtesting.

# 0.5.14

- Reduced total special-ammo probability from 7% to 3% per fired shot. A successful roll then chooses Bomb, Frost or Rewind equally: 1% per type overall.
- Rolls remain independent; three per hundred is an average, not a fixed quota.
- Includes the polished special-ball sprites and clearer effects from 0.5.13.

Lua 5.1 tests verify all 100 possible probability rolls: exactly three award any special. Full gameplay regression tests and StyLua passed. Use /reload; current ammo and saved progress are preserved.

# 0.5.13

- Rebuilt Bomb, Frost and Rewind ammunition with the same smooth small-scale rendering as regular marbles: orange bomb, cyan snowflake and violet rewind arrows.
- Added a clear ability-coloured outline ring around loaded and flying special ammunition.
- Impact effects now use outlined shockwaves and larger bright particles instead of faint glow alone; rewind keeps its inward spiral. Effect duration increased from 0.8 to 1.1 seconds.
- Total special chance remains 7%, with a random type after a successful roll. Reduced-motion and cleanup behavior retained.

Lua 5.1 tests and StyLua passed. Special sprites reviewed at 27px and 34px and both faction previews checked. Actual in-client appearance still needs a playtest. Use /reload; restart the client if old textures remain cached.

# 0.5.12

- Replaced the fixed special-ammo schedule with an independent 7% chance per fired shot.
- Bomb, Frost and Rewind are chosen randomly with equal chances. There is no fixed countdown or repeating type order; lucky streaks and dry spells are possible.
- Includes the new ability-specific particles, trails and reduced-motion effects from 0.5.11.

Lua 5.1 regression tests and StyLua passed, including random-roll boundaries and all three outcomes. Use /reload; current ammunition and saved progress are preserved.

# 0.5.11

- Special ammunition is awarded every 14 shots instead of every 7, halving its frequency while preserving the Bomb/Frost/Rewind rotation.
- Added distinct short impact effects: orange explosive embers, cyan frost shards, and inward-spiralling violet rewind sparks.
- Special projectile trails use their ability colour. Effects render above roads, support both lanes, expire after 0.8 seconds and clean up on close.
- Reduced motion replaces moving particles with a static fading glow.

Lua 5.1 tests cover rarity, impact lifetime, both lanes, layering, reduced motion and cleanup. StyLua passed and unchanged faction layouts reviewed. Use /reload; saves are preserved. Not playtested inside WoW.

# 0.5.10

Includes the distinct late-round layouts, capped tunnels, round-one restart after defeat, chat sharing and slower combo animations from 0.5.9.

Share messages now end with "Available on CurseForge!" Example:
Raynna's Runeballs: reached round 42/100 with 12,345 points! Available on CurseForge!

Gameplay regression tests passed. Use /reload after installation; saved progress is preserved.

# 0.5.9

- Reworked late dual-path rounds into visibly distinct orientations and detours. All 100 rounds have distinct map-scale route signatures; dual lanes retain equal length, separated exits, edge entrances, perpendicular crossings and launcher clearance.
- Tunnels are limited to 128 path units, with at least 180 open units before exits. Lower-lane gaps are baked along the route instead of rectangular background masks that could hide nearby bends. Covered balls remain protected from shots.
- Losing resets progression; New Game starts round one with zero score. The result keeps the finished round and score for sharing.
- Share Result previews a message naming Raynna's Runeballs, round and score. Choose Say, Yell, Party, Raid, Guild, Officer, Instance, Whisper or a joined channel, then click Send. Demo results are labelled.
- Matching sections retract at 90 instead of 210 path units/second, and combo messages remain visible for 0.9 seconds. Normal forward speed is unchanged.
- Existing runs preserve scores and marble counts, pause on reload and gain safe exit clearance if their map became shorter.

Lua 5.1 regression tests cover route uniqueness, geometry, tunnel caps and exit access, save migration, defeat resets, chat callbacks and slower combos. StyLua and both faction previews checked, including rounds 80/90/100. Not playtested inside WoW.
Installed updates take effect with /reload; saves are preserved.

# 0.5.8

- Developer identity matching handles split name/surname returns, UTF-8 spaces and character-panel display names as a fallback.
- If access is rejected, the message includes version and detected names for diagnosis.
- Demo scope remains limited to Its Raynna; campaign isolation is unchanged.

Lua 5.1 tests cover space/hyphen/case variants, split names, nonbreaking spaces, character-panel fallback and rejection of other names. StyLua passed; unchanged faction layouts retain their reviewed previews.
Reload, open the character panel once if needed, then /rrb demo 100.

# 0.5.7

- Added an opaque faction-stone footer behind the full bottom controls, covering the gap below the original illustration.
- Fixed developer demo access for the actual character name Its-Raynna. Name matching now ignores hyphens as well as spaces and case.

Lua 5.1 tests and StyLua passed; both faction footer previews reviewed. Use /reload, then /rrb demo 100 (or any round 1–100). Saves remain untouched.

# 0.5.6

- Developer command `/rrb demo N` starts any round 1–100 immediately with normal round speed and lanes. `//rrb` is also registered as an alias.
- Restricted to character name Itsraynna (case and spaces ignored).
- `/rrb demo off` restores the paused campaign. Demo scores and progress are session-only and never replace the saved campaign; reload also returns to the saved run.

Lua 5.1 tests cover all 100 demo rounds, invalid input, developer restriction and saved-progress isolation. StyLua and faction previews checked. Use /reload after installing.

# 0.5.5

- Increased base chain speed from 24 to 32 path pixels/second: round one is 33% faster.
- Retained the gradual level progression and exactly half-speed movement on each dual-path lane.
- Existing runs use the new speed after /reload without resetting progress.

Lua 5.1 gameplay and speed checks, StyLua and faction preview review passed. Not playtested inside WoW.

# 0.5.4

- Replaced overlapping road strips with continuous antialiased artwork generated from all 100 exact routes, including the 12 second lanes. One road texture per lane removes curve seams and reduces UI texture count.
- Movement now consumes every render interval with small collision-safe steps, avoiding repeated positions above 120 FPS. Optional texture pixel snapping is disabled where supported.
- Shifted launcher artwork so the loaded marble is centered in its socket, including during recoil.
- Verified the bundled flight chooser with Runeballs and Peggle alone, without Tower Defense: only the chosen game opens.

Gameplay, high-refresh timing, launcher alignment and flight-chooser tests passed; StyLua and both faction offline previews checked. Actual client smoothness requires in-game confirmation.
Use /reload after installing; restart WoW if textures remain cached. Saves are preserved.

# 0.5.3

- Rebuilt all six ordinary marble sprites with consistent circular outlines, smooth alpha edges, simpler shading and one soft highlight.
- Supersampled artwork is reduced to 32px runtime textures for cleaner sampling near the normal 27px display size.
- Colours, ball sizes and gameplay remain unchanged.

Lua 5.1 gameplay tests and StyLua passed. Both faction offline previews reviewed; actual client rendering remains to be checked in WoW.
Installed in WoW Forever. Use /reload; if the client retains cached textures, restart it. Saves are untouched.

# 0.5.2

- Fixed missed three-ball matches when separated sections reconnect, including very small gaps.
- Shots inserted into gaps stay beside the ball they hit; successful matches no longer push surviving sections forward.
- Rewind stops with the leading marble fully visible, then forward movement resumes.
- Combo text, projectile and pop effects render above the roads.
- Six plain marble colours from round one: red, blue, green, yellow, purple and pearl. Existing runs retain progress and gain the expanded palette.

Validated with Lua 5.1 gameplay/regression tests, shared flight chooser tests, StyLua and both faction layout previews. These are automated/offline checks, not in-client playtesting.
Installed updates take effect with /reload. Character saves are preserved.

# 0.5.1

- Starting speed increased from 18 to 24 path pixels/second (33% faster).
- Each dual-path lane now runs at exactly half the normal speed for its level.
- The 100-level difficulty curve, shorter starting chains and dual paths from level 30 remain in place.

Validated with Lua 5.1 gameplay tests, exact half-speed checks for both lanes, and StyLua.
Installed updates take effect with /reload. Character saves are preserved.

# 0.5.0

- A 100-level campaign with slower early rounds and gradually increasing speed, ball count and colours.
- Single paths through level 29. Dual paths begin at level 30 and run at 58% per-lane speed, with shorter starting chains.
- Completing level 100 offers Play Again; personal bests are retained.
- Balls appear inside the entrance light instead of being masked until the road.
- Round exit rims use the actual curved road underneath, with no straight baked road stub.
- Continuous rotating portal spiral replaces the dotted swirl.
- Smaller, inset HUD icons and text; faction-specific score widths; a proper icon-only X button.
- Existing early dual-path saves become single-lane runs while retaining score and remaining marbles.

Install the ZIP's RaynnaRuneballs folder into Interface/AddOns. Use /reload, then /rrb.

Validation: Lua 5.1 tests over 100 routes, campaign completion/replay, pacing,
legacy-save conversion, entrance layering, portal animation, close button,
shared flight chooser, StyLua and offline Alliance/Horde previews. Actual WoW
Forever rendering still needs checking in game.

# 0.4.5

- Animated two-arm portal swirls inside the compact exit pits.
- Soft teal pulsing lights inside the distinct border entrances.
- Faster inward motion during defeat; steady glows with reduced motion enabled.
- Effects remain inside the openings, reuse pooled textures and stop on pause/close.

Includes the 0.4.4 border entrances, aligned small exits, launcher clearance,
equal-length dual paths, underground arrows, text fixes and subtle hit sounds.

Use /reload then /rrb. Lua 5.1 tests cover animation, cleanup, reduced motion,
routes, collision and saved runs. Actual client rendering still needs checking.

# 0.4.4

- Distinct teal stone starting openings built into the actual board borders.
- Compact circular exit pits with a clean, road-width entry mouth and warm rim.
- A 100-pixel launcher clearance radius across every route, keeping paths away from the player and next-ammo display.
- Equal-length mirrored dual routes, two clear crossings, underground arrows and widely separated exits.
- Includes earlier text-fitting fixes, subtle shoot/hit sounds and the shared flight-game chooser.

Install the ZIP's RaynnaRuneballs folder into Interface/AddOns. Use /reload, then /rrb.
Character saves are preserved. Tower Defense 0.4.3+ supports the shared chooser.

Validation: Lua 5.1 mock tests over 60 rounds, route length/collision/clearance
checks, flight chooser tests, StyLua and offline faction previews. Check the
actual rendering in WoW Forever after reloading.

# 0.4.3

Moves the next-ball indicator beside the launcher so it no longer overlaps a dual-path road. Includes all 0.4.2 improvements: compact edge holes, aligned exits, better road spacing and underground direction arrows.

Lua 5.1 mock checks and StyLua pass. Use /reload then /rrb for in-game testing.

# 0.4.2

- Restored visible starting holes at every board edge.
- Compact entrance/exit holes sized around a marble with a stone rim and aligned road mouth.
- More spacing between parallel roads and around exits, with automated clearance checks.
- Directional arrow markers show the route beneath background-covered sections.
- Retains equal-length mirrored lanes, two perpendicular crossings, quiet shot/hit sounds and corrected text fitting.

Install the ZIP's RaynnaRuneballs folder into Interface/AddOns. Use /reload and
/rrb to test. Tower Defense 0.4.3+ enables the shared flight chooser alongside
Runeballs; PeggleForever is detected automatically.

Validated with Lua 5.1 mock tests, route/collision/clearance tests, StyLua and
offline faction previews. Actual client rendering still needs an in-game check.

# 0.4.1

- Clear, perpendicular crossings with the lower road and marbles hidden behind matching stone background sections, plus subtle buried-route guides.
- Two mirrored lanes of exactly equal length, with two crossings and exits more than 450 board units apart.
- Covered balls cannot be hit; partial marble silhouettes disappear naturally behind foreground stone.
- Larger simple sinkholes with a road-shaped opening aligned to the path, subtle rim effects and defeat suction.
- Single-layer gold text, explicit text bounds and smaller button labels fix clipped/overlapping typography.
- Ordinary ball hits use a quiet native UI click instead of a spell impact.

Validation: Lua 5.1 gameplay/UI mock tests, tunnel collision/equal-length checks,
shared flight chooser tests, StyLua and offline faction previews. In-game layout
verification is still needed after reload.

# 0.4.0

- Bold cartoon fonts, gold numbers, new control icons, faction launchers and buttons.
- Plain glossy marbles; ability icons only on special shots.
- Recoil, trails, match feedback, ambient effects and reduced-motion setting.
- Subtle native shooting sound.
- Edge tunnel entrances and later dual-path rounds with bridge underpasses.
- Both chains drain on defeat; victory waits for both paths to clear.
- Shared flight chooser for Tower Defense 0.4.3+ and PeggleForever.
- Preserved character saves, manual opening and gentle early-round pace.

Validation: Lua 5.1 mocked gameplay/UI/lifecycle tests, shared chooser tests,
StyLua and offline Alliance/Horde previews. In-client testing remains necessary.
