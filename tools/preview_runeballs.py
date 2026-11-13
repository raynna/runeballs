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
 routes=[scene['path']]+([scene['other']] if 'other' in scene else [])
 for route in routes:
  path=[(132+x,155+y*.86) for x,y in route]
  for width,color in [(31,(9,10,14)),(28,(139,102,45)),(25,(37,34,35)),(22,(17,20,26))]: d.line(path,fill=color,width=width,joint='curve')
 for cross in scene.get('crossings',[]): sprite('Bridge',132+cross['x'],155+cross['y']*.86,64,64,90-math.degrees(cross['angle']))
 for route in routes:
  sprite('Entrance',132+route[0][0],155+route[0][1]*.86,53,53)
  sprite('Portal',132+route[-1][0],155+route[-1][1]*.86,54,54)
 rng=random.Random(scene['level'])
 for x,y in scene['marbles']+scene.get('otherMarbles',[]):
  if any((x-c['x'])**2+(y-c['y'])**2<25**2 for c in scene.get('crossings',[])):continue
  sprite('Ball'+str(rng.randrange(1,6)),132+x,155+y*.86,27,27)
 sprite(faction+'Launcher',512,370,104,104);sprite('Ball2',512,370,34,34)
 sprite('Bomb',512,427,28,28);text('NEXT',512,446,14)
 text('ROUND '+str(scene['level']),258,73,27,True,155);text(scene['name'],259,105,15,False,165)
 for x,label,value in [(744,'SCORE','9,200'),(873,'BEST','32,200')]:
  text(label,x,72,16);text(value,x,96,30,True,119)
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
  sprite(faction+'Button',x+w/2,665, w,57);sprite(icon,x+25,665,25,25);text(label,x+w*.61,655,21,False,w-48)
 return im
(ROOT/'dist').mkdir(exist_ok=True)
for faction,level in [('Alliance',1),('Horde',6)]:
 preview(faction,scenes[level-1]).convert('RGB').save(ROOT/'dist'/('RaynnaRuneballs-'+faction+'-preview.png'))
print('Rendered 1024x720 Alliance spiral and Horde dual-path layout previews.')
