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
