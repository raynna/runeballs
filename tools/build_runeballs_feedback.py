from pathlib import Path
from PIL import Image,ImageDraw
out=Path('RaynnaRuneballs/Media')
for name in ['MatchRing','PortalShield']:
 im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im)
 if name=='MatchRing':d.ellipse((20,20,236,236),outline='white',width=7)
 else:
  d.ellipse((15,15,241,241),outline=(100,210,255,200),width=8)
  d.polygon([(128,44),(185,68),(179,139),(155,174),(128,196),(101,174),(77,139),(71,68)],fill=(80,180,255,55),outline='white',width=9)
  d.line([(101,116),(123,139),(159,93)],fill='white',width=11)
 im.resize((128,128),Image.Resampling.LANCZOS).save(out/(name+'.tga'))
