"""Offline layout/art review with exact engine routes; not an in-game capture."""
from pathlib import Path
import json, math, random
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
MEDIA=ROOT/'RaynnaRuneballs/Media'
scenes=json.loads((ROOT/'.test-deps/runeballs-scenes.json').read_text())
def preview(faction,scene):
 im=Image.new('RGBA',(1024,720),(25,20,27,255))
 art=Image.open(MEDIA/(faction+'Frame.tga'))
 footer=art.crop((132,600,892,765)).resize((1024,110),Image.Resampling.LANCZOS)
 im.alpha_composite(footer,(0,610))
 im.alpha_composite(art.resize((1024,683)))
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
  route_id=scene['level']+(1000 if route is scene.get('other') else 0)
  road_art=Image.open(MEDIA/f'Road{route_id}.tga').resize((816,430),Image.Resampling.LANCZOS)
  im.alpha_composite(road_art,(104,155))
 def marbles(points):
  for x,y in points:sprite('Ball'+str(rng.randrange(1,scene['colors']+1)),132+x,155+y*.86,27,27)
 def coverbox(left,top,right,bottom):
  box=tuple(round(v) for v in (left,top,right,bottom))
  im.paste(background.crop(box),box)
 def entrance(route):
  sx,sy=route[0];tx,ty=route[1];a=math.atan2(ty-sy,tx-sx)
  ex,ey=sx+math.cos(a)*14,sy+math.sin(a)*14
  sprite('Entry',132+ex,155+ey*.86,60,60,-math.degrees(math.atan2((ty-sy)*.86,tx-sx)))
 if 'other' in scene:
  road(scene['other']);entrance(scene['other']);marbles(scene.get('otherMarbles',[]))
  for c in scene['crossings']:
   x,y,w,h=c['bounds'];coverbox(132+x,155+y,132+x+w,155+y+h)
   for gx,gy,angle in c['guide']:
    for side in [-1,1]:
     wing=angle+side*.65;d.line((132+gx-6*math.cos(wing),155+gy*.86-6*math.sin(wing),132+gx,155+gy*.86),fill=(145,122,83),width=2)
 road(scene['path']);entrance(scene['path']);marbles(scene['marbles'])
 for route in routes:
  ex,ey=route[-1];px,py=route[-2];angle=-math.degrees(math.atan2((ey-py)*.86,ex-px))
  sprite('Portal',132+ex,155+ey*.86,60,60,angle)
  sprite('PortalSwirl',132+ex,155+ey*.86,28,28)
 sprite(faction+'Launcher',512,365,104,104);sprite('Ball2',512,370,34,34)
 sprite('Bomb',580,370,28,28);text('NEXT',580,390,14)
 text('ROUND '+str(scene['level']),258,72,25,True,155);text(scene['name'],259,105,14,False,165)
 width=84 if faction=='Alliance' else 109
 for left,label,value,icon in [(690 if faction=='Alliance' else 689,'SCORE','9,200','Trophy'),(784 if faction=='Alliance' else 818,'BEST','32,200','Crown')]:
  center=left+width/2
  sprite(icon,center-30,82,14,14);text(label,center+12,76,12);text(value,center,98,24,True,width)
 panel(132,590,760,27);text('PORTAL THREAT',207,596,14)
 d.rectangle((292,598,877,609),fill=(13,8,15));d.rectangle((292,598,540,609),fill=(39,191,255))
 panel(35,625,290,83);sprite('QuestGem',66,666,38,48)
 text('SEAL THE PORTAL!',203,641,18,False,213);text('Match 3+ to clear the chain',203,670,14,False,213)
 panel(335,625,110,83);sprite('Marbles',355,647,16,16);text('MARBLES',400,641,11);text('74',390,665,28,True)
 panel(455,625,220,83)
 for i,(icon,label) in enumerate([('MouseLeft','Left-click: shoot'),('MouseRight','Right-click: swap'),('EscapeKey','Esc: pause')]):
  sprite(icon,479,646+i*21,16,18);text(label,577,641+i*21,13,False,156)
 for x,w,label,icon in [(685,145,'PAUSE','PauseIcon'),(840,150,'SETTINGS','SettingsIcon')]:
  sprite(faction+'Button',x+w/2,665, w,57);sprite(icon,x+32,665,16,16);text(label,x+44+(w-64)/2,658,14,False,w-64)
 sprite('CloseIcon',994,27,30,30)
 return im
(ROOT/'dist').mkdir(exist_ok=True)
for faction,level in [('Alliance',1),('Horde',30)]:
 preview(faction,scenes[level-1]).convert('RGB').save(ROOT/'dist'/('RaynnaRuneballs-'+faction+'-preview.png'))
print('Rendered 1024x720 Alliance spiral and Horde dual-path layout previews.')
