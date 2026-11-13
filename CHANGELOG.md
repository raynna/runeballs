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
