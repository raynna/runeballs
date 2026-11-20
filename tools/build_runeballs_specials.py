"""Generate code-native outlined special marbles and matching effect sprites."""
from pathlib import Path
import math, argparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'RaynnaRuneballs/Media'
COLORS=[(240,35,48),(30,115,250),(45,210,45),(255,200,25),(175,45,245),(224,231,244)]
KINDS=['Lightning','Paint','Stasis','Magnet','Treasure','Ward']
parser=argparse.ArgumentParser();parser.add_argument('--kind',choices=KINDS);args=parser.parse_args()
def glyph(kind):
 im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im);white=(255,255,245,255)
 if kind=='Lightning':d.polygon([(143,53),(75,140),(118,140),(102,203),(183,108),(139,108)],fill=white)
 elif kind=='Paint':
  d.polygon([(161,58),(190,85),(121,151),(94,125)],fill=white)
  d.ellipse((69,132,125,183),fill=white);d.polygon([(72,150),(59,194),(107,177)],fill=white)
 elif kind=='Stasis':
  d.line([(77,63),(179,63),(179,78),(144,128),(179,178),(179,193),(77,193),(77,178),(112,128),(77,78),(77,63)],fill=white,width=12)
  d.polygon([(93,83),(163,83),(128,117)],fill=white);d.polygon([(128,145),(96,177),(160,177)],fill=white)
 elif kind=='Magnet':
  d.arc((70,73,186,202),0,180,fill=white,width=26)
  d.rectangle((70,68,96,139),fill=white);d.rectangle((160,68,186,139),fill=white)
  d.line((68,100,99,100),fill=(20,20,30),width=8);d.line((157,100,189,100),fill=(20,20,30),width=8)
 elif kind=='Treasure':
  font=ImageFont.truetype(str(OUT/'Fonts/LilitaOne.ttf'),116)
  d.text((128,132),'×2',font=font,anchor='mm',fill=(255,208,58,255),stroke_width=5,stroke_fill=(70,35,8,255))
 elif kind=='Ward':
  d.polygon([(128,56),(188,82),(179,146),(155,177),(128,202),(101,177),(77,146),(68,82)],fill=white)
  d.polygon([(128,78),(167,96),(161,137),(145,161),(128,179)],fill=(24,26,36,255))
 return im
for kind in ([args.kind] if args.kind else KINDS):
 g=glyph(kind)
 for n,base in enumerate(COLORS,1):
  im=Image.new('RGBA',(256,256));pixels=im.load()
  for y in range(256):
   for x in range(256):
    dx,dy=(x-127.5)/116,(y-127.5)/116;r=math.hypot(dx,dy)
    if r>1:continue
    if r>.91:c=(18,20,29)
    else:
     z=math.sqrt(max(0,1-r*r));light=max(0,min(1,.5+.45*z-.24*dx-.30*dy))
     c=tuple(int(v*(.40+.60*light)) for v in base)
     h=math.exp(-(((dx+.30)/.31)**2+((dy+.38)/.19)**2)*2)*.88
     c=tuple(round(v+(255-v)*h) for v in c)
    pixels[x,y]=c+(255,)
  outline=Image.new('RGBA',im.size,(15,17,24,0));outline.putalpha(g.getchannel('A').filter(ImageFilter.MaxFilter(11)))
  im.alpha_composite(outline);im.alpha_composite(g)
  im.resize((128,128) if kind=='Treasure' else (32,32),Image.Resampling.LANCZOS).save(OUT/f'{kind}{n}.tga')
 g.resize((64,64),Image.Resampling.LANCZOS).save(OUT/f'Effect{kind}.tga')
arc=Image.new('RGBA',(512,128));d=ImageDraw.Draw(arc)
points=[(0,64),(75,48),(137,91),(201,37),(269,82),(333,42),(397,76),(465,53),(511,64)]
d.line(points,fill=(20,23,32,255),width=18,joint='curve');d.line(points,fill=(255,255,245,255),width=9,joint='curve')
if not args.kind:arc.resize((256,64),Image.Resampling.LANCZOS).save(OUT/'LightningArc.tga')
# Large contact sheet for asset review; runtime assets remain 32px.
sheet=Image.new('RGB',(600,6*94),(28,24,32));d=ImageDraw.Draw(sheet)
for row,kind in enumerate(KINDS):
 d.text((8,row*94+5),kind,fill='white')
 for i in range(1,7):
  art=Image.open(OUT/f'{kind}{i}.tga').resize((56,56),Image.Resampling.LANCZOS)
  sheet.paste(art,(90+(i-1)*80,row*94+23),art)
(ROOT/'dist').mkdir(exist_ok=True);sheet.save(ROOT/'dist/Runeballs-new-specials.png')
print('Built 36 coloured special balls, six effect glyphs and a lightning arc.')
