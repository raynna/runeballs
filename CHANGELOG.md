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
