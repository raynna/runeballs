# Runeballs 0.2 artwork

Generated with the built-in `image_gen` tool, November 2026. Original outputs
were copied into this folder; alpha is preserved when slicing the atlas.
`Sprites.png` is the earlier detailed study. The final runtime atlas uses
`SpritesSimple.png`, following the user's request for simpler outlined sprites.
The source PNGs are development assets and are excluded from the player ZIP.

## Alliance.png — final prompt

Create a production game UI background texture for Raynna's Runeballs, vivid hand painted Warcraft fantasy cartoon style, thick crisp outlines, polished chunky beveled gold. Landscape 3:2. ALLIANCE variant: blue and gold banners bearing golden lion emblems on side stone towers, night elf female mage portrait medallion upper left, lush ivy and little purple flowers lower corners, distant Stormwind castle and blue sky across top. Layout strictly: top 16% ornate header chrome with central gold title 'RAYNNA’S RUNEBALLS', blank dark plaques to left and right for live stats; middle 72% a large EMPTY flat blue-grey stone slab playfield bounded by a thin gold frame at x=7% to93%, y=18% to86%; lower 12% dark empty stone footer with gold edging for live controls. The entire center is unobstructed uniform flat masonry: NO track, NO marbles, NO shooter, NO buttons, NO numbers, NO score text. Side decoration narrow. Strong rich illustrated style like a premium fantasy casual marble shooter. This is runtime background artwork, not a screenshot.

## Horde.png — final prompt

Create a production game UI background texture for Raynna's Runeballs, vivid hand painted Warcraft fantasy cartoon style, thick crisp outlines, polished chunky beveled gold. Landscape 3:2. HORDE variant: red and black banners with black Horde emblems on narrow spiked iron and red sandstone side towers, fierce green orc shaman portrait gold medallion upper left, dry scrub and glowing embers lower corners, distant Orgrimmar spikes and orange sunset across top. Layout strictly: top 19% ornate header chrome with central gold title 'RAYNNA’S RUNEBALLS', blank dark plaques to left and right for live stats; middle an EMPTY flat dark warm slate stone slab playfield bounded by thin gold frame at x=9% to91%, y=20% to86%; lower 12% dark empty stone footer with gold edging for live controls. Entire center unobstructed uniform flat masonry: NO track, NO marbles, NO shooter, NO buttons, NO numbers, NO score text. Frame similar to polished Alliance game skin but clearly Horde; chunky tusks and iron details contained on narrow sides. Runtime background art, not screenshot.

## SpritesSimple.png — final prompt (transparent background)

Create a SIMPLE CARTOON production sprite atlas on true transparent background, exact 4 columns x 4 rows equal grid, each sprite centered with generous gutters. Visual style: very bold BLACK outlines, simple clean flat colours, just two-tone cel shading and ONE small highlight, charming chunky readable arcade shapes. NO ornate gold rims, NO texture, NO tiny details, NO realistic rendering, NO gradients, NO filigree. Everything clearly readable at 28 pixels. Row1: round bright RED ball with simple yellow flame; round BLUE ball with simple white shield; round GREEN ball with simple pale leaf; round YELLOW ball with simple orange sun. Row2: round PURPLE ball with simple white diamond; round black cartoon BOMB with orange fuse; round CYAN frost ball with simple white snowflake; round orange clock ball with large white backward arrow. Row3: simple round BLUE launcher with chunky yellow rim and white shield; simple round RED launcher with chunky dark iron rim and white Horde-style rune; simple PURPLE oval portal ring with BLACK outline and transparent center; orange-yellow cartoon explosion starburst with BLACK outline. Row4: small yellow four-point cartoon sparkle black outline; simple cyan ice shatter starburst with black outline; wide blank BLUE rounded rectangular cartoon button with thick black outline and simple yellow edge; wide blank RED rounded rectangular cartoon button with thick black outline and simple dark-grey edge. All are separate sprites on genuine transparent background. No labels, no text, no frames around grid cells. Outline thickness consistent. This is a polished simple 2D cartoon game sprite sheet, not ornate fantasy art.

## PlainBalls.png — final replacement ordinary-ball strip (built-in image_gen)

Production sprite strip: exactly FIVE plain circular cartoon marbles in one horizontal row on genuinely transparent background, equal spacing, equal diameter, generous transparent margins around each. Left to right RED, BLUE, GREEN, YELLOW, PURPLE. Simple vivid flat colour, bold smooth black outline, one small white highlight upper-left, subtle two-tone cel shading lower-right. NO icons, NO symbols, NO letters, NO patterns, NO emblems, NO rims or decorations. Perfect round balls readable at 27 pixels. Polished simple 2D arcade cartoon style. Wide landscape strip with five identical-size balls centered in five equal cells. Background transparent.

## Version 0.4.0 asset provenance

The following original outputs were created with the built-in image_gen tool in
this conversation and retained here. These are summaries of the generation
briefs, not verbatim transcripts of the tool prompts.

- PolishUI.png: transparent 4x4 Warcraft cartoon UI atlas with thick outlines,
  gold bevels, trophy/crown/gem/marbles, mouse/keyboard controls, aiming arrow,
  pause/settings/play/close icons, faction buttons and faction launchers.
  Output ID: exec-5634d9b6-57a9-4071-aded-1c69c0d1b474.
- PlainBallsPolished.png: five plain glossy cartoon marbles in red, blue, green,
  yellow and purple, bold dark outlines, readable highlights, no rune symbols.
  Output ID: exec-b1fe439b-5b5e-4937-aacd-600430f264c1.
- Tunnels.png: top-down cartoon stone-and-bronze circular tunnel entrance and
  vertical stone bridge with bronze rails and dark underpasses, transparent.
  Output ID: exec-51e3e64f-019a-4880-beaa-c92941e380d3.

Slicing is reproducible with tools/build_runeballs_faction_art.py. Halo and
nine-slice HUDPanel are procedural artwork generated by that same script.
