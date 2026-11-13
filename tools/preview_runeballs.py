"""Offline layout/art review with exact engine routes; not an in-game capture."""
from pathlib import Path
import json, math, random
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
MEDIA=ROOT/'RaynnaRuneballs/Media'
scenes=json.loads((ROOT/'.test-deps/runeballs-scenes.json').read_text())
def preview(faction,scene):
 im=Image.new('RGBA',(1024,720),(25,20,27,255))
 im.alpha_composite(Image.open(MEDIA/(faction+'Frame.tga')).resize((1024,683)))
 d=ImageDraw.Draw(im)
 def text(value,x,y,size=20,gold=False,width=None):
  font=ImageFont.truetype(str(MEDIA/'Fonts/LilitaOne.ttf'),size)
  while width and font.getlength(value)>width and size>12:
   size-=1;font=ImageFont.truetype(str(MEDIA/'Fonts/LilitaOne.ttf'),size)
  d.text((x,y),value,anchor='mt',font=font,fill=(255,207,65) if gold else (255,241,201),stroke_width=2,stroke_fill=(22,13,18))
 def sprite(name,x,y,w,h,angle=0):
  art=Image.open(MEDIA/(name+'.tga')).resize((w,h),Image.Resampling.LANCZOS)
  if angle: art=art.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
  im.alpha_composite(art,(round(x-art.width/2),round(y-art.height/2)))
 def panel(x,y,w,h):
  d.rounded_rectangle((x,y,x+w,y+h),radius=8,fill=(41,33,43),outline=(209,155,59),width=3)
 background=im.copy()
 routes=[scene['path']]+([scene['other']] if 'other' in scene else [])
 rng=random.Random(scene['level'])
 def road(route):
  path=[(132+x,155+y*.86) for x,y in route]
  for width,color in [(31,(9,10,14)),(28,(139,102,45)),(25,(37,34,35)),(22,(17,20,26))]:d.line(path,fill=color,width=width,joint='curve')
 def marbles(points):
  for x,y in points:sprite('Ball'+str(rng.randrange(1,6)),132+x,155+y*.86,27,27)
 def coverbox(left,top,right,bottom):
  box=tuple(round(v) for v in (left,top,right,bottom))
  im.paste(background.crop(box),box)
 if 'other' in scene:
  road(scene['other']);marbles(scene.get('otherMarbles',[]))
  for c in scene['crossings']:
   x,y,w,h=c['bounds'];coverbox(132+x,155+y,132+x+w,155+y+h)
   for gx,gy,angle in c['guide']:
    d.line((132+gx-3*math.cos(angle),155+gy*.86-3*math.sin(angle),132+gx+3*math.cos(angle),155+gy*.86+3*math.sin(angle)),fill=(120,103,76),width=2)
 for route in routes:
  sx,sy=route[0];distance=0;tx,ty=sx,sy
  for x,y in route[1:]:
   distance+=math.hypot(x-tx,y-ty);tx,ty=x,y
   if distance>=88:break
  coverbox(132+min(sx,tx)-18,155+min(sy,ty)*.86-18,132+max(sx,tx)+18,155+max(sy,ty)*.86+18)
 road(scene['path']);marbles(scene['marbles'])
 route=scene['path'];sx,sy=route[0];tx,ty=route[1]
 # Main entrance cover sits above its own road; secondary cover stays below it.
 angle=math.atan2(ty-sy,tx-sx);tx=sx+math.cos(angle)*88;ty=sy+math.sin(angle)*88
 coverbox(132+min(sx,tx)-18,155+min(sy,ty)*.86-18,132+max(sx,tx)+18,155+max(sy,ty)*.86+18)
 for route in routes:
  ex,ey=route[-1];px,py=route[-2];angle=-math.degrees(math.atan2((ey-py)*.86,ex-px))
  sprite('Portal',132+ex,155+ey*.86,112,112,angle)
 sprite(faction+'Launcher',512,370,104,104);sprite('Ball2',512,370,34,34)
 sprite('Bomb',512,427,28,28);text('NEXT',512,446,14)
 text('ROUND '+str(scene['level']),258,72,25,True,155);text(scene['name'],259,105,14,False,165)
 for x,label,value in [(744,'SCORE','9,200'),(873,'BEST','32,200')]:
  text(label,x,72,16);text(value,x,96,28,True,119)
 sprite('Trophy',706,82,22,22);sprite('Crown',835,82,22,22)
 panel(132,590,760,27);text('PORTAL THREAT',207,596,14)
 d.rectangle((292,598,877,609),fill=(13,8,15));d.rectangle((292,598,540,609),fill=(39,191,255))
 panel(35,625,290,83);sprite('QuestGem',68,666,47,55)
 text('SEAL THE PORTAL!',203,635,22,False,213);text('Match 3+ to clear the chain',203,664,15,False,213)
 panel(335,625,110,83);sprite('Marbles',355,646,24,24);text('MARBLES',402,635,14);text('74',390,658,38,True)
 panel(455,625,220,83)
 for i,(icon,label) in enumerate([('MouseLeft','Left mouse - Shoot'),('MouseRight','Right mouse - Swap'),('EscapeKey','Esc - Pause')]):
  sprite(icon,478,641+i*24,24,22);text(label,577,631+i*24,15,False,175)
 for x,w,label,icon in [(685,145,'PAUSE','PauseIcon'),(840,150,'SETTINGS','SettingsIcon')]:
  sprite(faction+'Button',x+w/2,665, w,57);sprite(icon,x+25,665,25,25);text(label,x+w*.61,657,16,False,w-54)
 return im
(ROOT/'dist').mkdir(exist_ok=True)
for faction,level in [('Alliance',1),('Horde',6)]:
 preview(faction,scenes[level-1]).convert('RGB').save(ROOT/'dist'/('RaynnaRuneballs-'+faction+'-preview.png'))
print('Rendered 1024x720 Alliance spiral and Horde dual-path layout previews.')
