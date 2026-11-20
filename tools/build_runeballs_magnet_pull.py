"""A clean directional chevron for Magnet's moving gap indicators."""
from pathlib import Path
from PIL import Image,ImageDraw
im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im)
for shift in [-40,40]:
 pts=[(76+shift,57),(143+shift,128),(76+shift,199)]
 d.line(pts,fill=(255,255,255,255),width=19,joint='curve')
 for x,y in pts:d.ellipse((x-9,y-9,x+9,y+9),fill='white')
im.resize((64,64),Image.Resampling.LANCZOS).save(Path(__file__).resolve().parents[1]/'RaynnaRuneballs/Media/MagnetPull.tga')
