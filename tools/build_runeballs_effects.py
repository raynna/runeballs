"""Procedural light-only effects: supersampled arcs, glow masks and particles."""
from pathlib import Path
import math, random
from PIL import Image,ImageDraw,ImageFilter,ImageChops
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'RaynnaRuneballs/Media'
def save(name,im,size=64):im.resize((size,size) if isinstance(size,int) else size,Image.Resampling.LANCZOS).save(OUT/(name+'.tga'))
def rgba(mask):
 im=Image.new('RGBA',mask.size,'white');im.putalpha(mask);return im
for variant in range(1,4):
 rng=random.Random(5027+variant);mask=Image.new('L',(1024,256));d=ImageDraw.Draw(mask)
 points=[(0,128)]+[(x,128+rng.randrange(-42,43)) for x in range(80,990,80)]+[(1023,128)]
 d.line(points,fill=255,width=8,joint='curve')
 for i in [3,6,9]:
  x,y=points[i];sign=-1 if i%2 else 1
  d.line([(x,y),(x+24,y+sign*36),(x+75,y+sign*63),(x+86,y+sign*98)],fill=190,width=4,joint='curve')
 glow=ImageChops.lighter(mask.filter(ImageFilter.GaussianBlur(12)),mask.filter(ImageFilter.GaussianBlur(4)))
 glow=glow.point(lambda v:min(255,v*4))
 save('LightningBolt'+str(variant),rgba(mask),(256,64));save('LightningBloom'+str(variant),rgba(glow),(256,64))
mask=Image.new('L',(256,256));d=ImageDraw.Draw(mask)
d.polygon([(128,24),(139,105),(215,128),(139,141),(128,230),(115,141),(37,128),(115,113)],fill=255)
d.ellipse((111,111,145,145),fill=255);save('LightningFlash',rgba(mask))
mask=Image.new('L',(256,256));px=mask.load()
for y in range(256):
 for x in range(256):px[x,y]=round(220*math.exp(-((x-128)**2+(y-128)**2)/(2*39**2)))
save('ImpactLight',rgba(mask))
# Abstract physical effects replace the large ability icons used as particles.
for name in ['PaintBurst','PaintDrop','StasisBurst','MagnetBurst','TreasureBurst','WardBurst','FrostShard','CoinGlint','EnergyMote','BombBurst','BombEmber','FrostBurst','RewindBurst','RainbowBurst','StarGlint']:
 mask=Image.new('L',(256,256));d=ImageDraw.Draw(mask)
 if name=='BombBurst':
  d.ellipse((35,35,221,221),outline=255,width=9)
  d.ellipse((44,44,212,212),outline=130,width=3)
  for i in range(12):
   a=i*math.pi/6;d.line((128+math.cos(a)*88,128+math.sin(a)*88,128+math.cos(a)*113,128+math.sin(a)*113),fill=220,width=5)
 elif name=='BombEmber':
  d.polygon([(128,16),(150,128),(128,239),(106,128)],fill=255);d.ellipse((104,99,152,160),fill=255)
 elif name=='FrostBurst':
  for i in range(8):
   a=i*math.pi/4;b=a+.26
   pts=[(128+math.cos(a)*48,128+math.sin(a)*48),(128+math.cos(b)*83,128+math.sin(b)*83),(128+math.cos(a)*112,128+math.sin(a)*112)]
   d.line(pts,fill=245,width=6)
  d.ellipse((55,55,201,201),outline=160,width=3)
 elif name=='RewindBurst':
  for offset in [0,math.pi]:
   points=[]
   for step in range(180):
    t=step/179;a=offset+t*math.pi*3.8;r=105*(1-t)+8
    points.append((128+math.cos(a)*r,128+math.sin(a)*r))
   d.line(points,fill=255,width=5,joint='curve')
 elif name=='RainbowBurst':
  for i in range(6):
   a=i*math.pi/3
   d.line((128+math.cos(a)*40,128+math.sin(a)*40,128+math.cos(a)*108,128+math.sin(a)*108),fill=255,width=6)
  d.ellipse((86,86,170,170),outline=210,width=5)
 elif name=='StarGlint':
  d.polygon([(128,18),(146,108),(232,128),(146,148),(128,238),(110,148),(24,128),(110,108)],fill=255)
 elif name=='PaintBurst':
  d.ellipse((68,68,188,188),fill=240)
  for i in range(9):
   a=i*2.399;x=128+math.cos(a)*80;y=128+math.sin(a)*80;r=10+i%3*5
   d.line((128,128,x,y),fill=210,width=12);d.ellipse((x-r,y-r,x+r,y+r),fill=230)
 elif name=='PaintDrop':
  d.ellipse((71,109,185,218),fill=255);d.polygon([(128,30),(75,128),(181,128)],fill=255)
 elif name=='StasisBurst':
  d.ellipse((27,27,229,229),outline=230,width=5)
  for i in range(12):
   a=i*math.pi/6;d.line((128+math.cos(a)*83,128+math.sin(a)*83,128+math.cos(a)*99,128+math.sin(a)*99),fill=255,width=6)
  d.line([(128,70),(128,128),(167,151)],fill=255,width=8)
 elif name=='MagnetBurst':
  for inset in [28,56,85]:
   d.arc((inset,inset,256-inset,256-inset),20,155,fill=255,width=6)
   d.arc((inset,inset,256-inset,256-inset),200,335,fill=255,width=6)
 elif name=='TreasureBurst':
  for i in range(8):
   a=i*math.pi/4;d.line((128+math.cos(a)*62,128+math.sin(a)*62,128+math.cos(a)*108,128+math.sin(a)*108),fill=245,width=6)
  d.ellipse((85,85,171,171),outline=255,width=7)
 elif name=='WardBurst':
  points=[(128,25),(219,62),(205,150),(175,192),(128,234),(81,192),(51,150),(37,62),(128,25)]
  d.line(points,fill=255,width=7,joint='curve');d.line([(128,47),(196,76),(183,143),(157,179),(128,207)],fill=120,width=4)
 elif name=='FrostShard':d.polygon([(128,22),(170,146),(128,232),(87,146)],fill=255)
 elif name=='CoinGlint':
  d.ellipse((52,30,204,226),outline=255,width=14);d.polygon([(128,71),(155,128),(128,184),(101,128)],fill=255)
 else:
  d.ellipse((70,70,186,186),fill=255);mask=mask.filter(ImageFilter.GaussianBlur(18))
 save(name,rgba(mask))
 if name.endswith('Burst'):save(name+'Glow',rgba(mask.filter(ImageFilter.GaussianBlur(6)).point(lambda v:min(255,v*3))))
print('Built layered lightning and dedicated luminous VFX textures for all ten specials.')
