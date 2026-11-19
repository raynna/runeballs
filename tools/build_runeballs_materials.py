"""Original supersampled materials for visible ball transformations and fire VFX."""
from pathlib import Path
import math
from PIL import Image,ImageDraw,ImageFilter
OUT=Path(__file__).resolve().parents[1]/'RaynnaRuneballs/Media'
def save(name,im):im.resize((128,128),Image.Resampling.LANCZOS).save(OUT/(name+'.tga'))
# A transparent centre retains the underlying matching colour. Six silhouettes
# progressively lose their upper ice facets, then their last lower chips.
for stage in range(1,7):
 im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im)
 points=[(41,62),(96,22),(171,31),(224,88),(217,171),(164,231),(77,219),(24,145)]
 d.polygon(points,fill=(105,211,255,48),outline=(195,245,255,245),width=9)
 d.polygon([(41,62),(96,22),(108,72),(66,100)],fill=(202,248,255,180))
 d.polygon([(171,31),(224,88),(188,112),(163,75)],fill=(117,211,255,135))
 d.polygon([(217,171),(164,231),(150,187),(184,162)],fill=(157,226,255,165))
 d.polygon([(77,219),(24,145),(65,147),(99,183)],fill=(175,238,255,150))
 for pts in [[(45,65),(66,100),(94,106)],[(215,169),(184,162),(164,139)],[(78,216),(99,183),(112,171)]]:d.line(pts,fill=(228,253,255,230),width=5)
 if stage<6:
  px=im.load();threshold=(6-stage)*36
  for y in range(256):
   for x in range(256):
    # Irregular melt edge rather than a rectangular texture crop.
    if y<threshold+12*math.sin(x*.075)+7*math.sin(x*.16):px[x,y]=(0,0,0,0)
 save('IceShell'+str(stage),im)
# Linked restraints wrap across the marble rather than orbiting as an icon.
im=Image.new('RGBA',(256,256))
for diagonal in [-1,1]:
 row=Image.new('RGBA',(256,256));d=ImageDraw.Draw(row)
 for i in range(4):
  x=53+i*50;y=128
  d.rounded_rectangle((x-32,y-17,x+32,y+17),radius=15,outline=(26,19,43,255),width=12)
  d.rounded_rectangle((x-30,y-15,x+30,y+15),radius=13,outline=(213,184,255,255),width=7)
  d.line((x-12,y-10,x+12,y-10),fill=(255,240,255,255),width=3)
 im.alpha_composite(row.rotate(diagonal*35,resample=Image.Resampling.BICUBIC))
save('TimeChains',im)
for name in ['RewindWrap','MagnetWrap','TreasureWrap']:
 im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im)
 if name=='RewindWrap':
  for start in [15,195]:
   d.arc((20,20,236,236),start,start+110,fill=(221,198,255,230),width=11)
   a=math.radians(start);x=128+108*math.cos(a);y=128+108*math.sin(a)
   d.polygon([(x-17,y-15),(x+9,y),(x-17,y+15)],fill=(245,228,255,255))
 elif name=='MagnetWrap':
  for box in [(19,55,237,201),(55,19,201,237)]:d.ellipse(box,outline=(127,220,255,210),width=8)
 else:
  d.ellipse((23,23,233,233),outline=(255,198,50,230),width=9)
  for x,y in [(48,64),(197,171)]:d.polygon([(x,y-19),(x+5,y-5),(x+19,y),(x+5,y+5),(x,y+19),(x-5,y+5),(x-19,y),(x-5,y-5)],fill=(255,241,161,255))
 save(name,im)
# Irregular rising flame lobes, with softer bloom and separate ember tongues.
for name in ['FireBlast','FireTongue']:
 im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im)
 if name=='FireBlast':
  pts=[]
  for i in range(96):
   a=i*math.pi/48;r=82+21*math.sin(a*7)+9*math.sin(a*13)
   pts.append((128+math.cos(a)*r,139+math.sin(a)*r*.9))
  d.polygon(pts,fill='white');d.polygon([(64,155),(62,52),(99,87),(120,14),(151,72),(184,38),(187,159)],fill='white')
 else:d.polygon([(124,15),(142,74),(176,57),(160,122),(193,146),(164,214),(124,240),(86,216),(65,168),(97,120),(86,73)],fill='white')
 save(name,im)
 glow=im.filter(ImageFilter.GaussianBlur(13));save(name+'Glow',glow)
