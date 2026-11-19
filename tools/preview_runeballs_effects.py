"""Render a labelled VFX review sheet from the runtime materials."""
from pathlib import Path
import copy, math
from PIL import Image, ImageDraw, ImageFont
from preview_runeballs import preview,ROOT,MEDIA,scenes
kinds=[('Lightning',2),('Bomb',1),('Frost',2),('Rewind',5),('Rainbow',6),('Paint',3),('Stasis',6),('Magnet',1),('Treasure',4),('Ward',3)]
sheet=Image.new('RGB',(1300,600),(24,20,28));d=ImageDraw.Draw(sheet)
font=ImageFont.truetype(str(MEDIA/'Fonts/LilitaOne.ttf'),22)
small=ImageFont.truetype(str(MEDIA/'Fonts/LilitaOne.ttf'),16)
for i,(kind,color) in enumerate(kinds):
 scene=copy.deepcopy(scenes[0]);scene['marbles']=[];scene['loadedKind']=kind;scene['loadedColor']=color
 links=[[590,280],[500,250],[490,180],[570,140],[650,220]] if kind=='Lightning' else [[520,185],[620,185],[530,260],[610,260]]
 scene['impacts']=[{'point':[570,220],'kind':kind,'color':color,'progress':.34 if kind=='Lightning' else .4,'links':links}]
 im=preview('Alliance' if i%2==0 else 'Horde',scene).convert('RGB')
 x=(i%5)*260;y=(i//5)*280
 sheet.paste(im.crop((572,224,832,464)),(x,y))
 icon=Image.open(MEDIA/(('Rainbow' if kind=='Rainbow' else kind+str(color))+'.tga')).resize((28,28),Image.Resampling.LANCZOS)
 sheet.paste(icon,(x+34,y+245),icon);d.text((x+73,y+245),kind,font=font,fill='#ffe6b2')
d.text((20,576),'Rendered VFX samples from addon materials - not live WoW screenshots.',font=small,fill='#cdbed4')
sheet.save(ROOT/'dist/Runeballs-0.5.27-all-effects.png')
print('Rendered all ten VFX samples.')
