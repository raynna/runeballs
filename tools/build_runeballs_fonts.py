"""Rebuild renamed static Baloo 2 weight-800 label font (fontTools required)."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
root=Path(__file__).resolve().parents[1]/'RaynnaRuneballs'
font=instantiateVariableFont(TTFont(root/'ArtSource/Fonts/Baloo2-Variable.ttf'),{'wght':800},inplace=False)
for entry in font['name'].names:
 if entry.nameID in (1,4,6,16):
  value='RuneballsLabels' if entry.nameID==6 else 'Runeballs Labels'
  entry.string=value.encode(entry.getEncoding(),errors='replace')
font.save(root/'Media/Fonts/RuneballsLabels.ttf')
print('Built renamed OFL-licensed label font.')
