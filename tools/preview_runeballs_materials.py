"""Six labelled material previews, plus a timer-driven frost thaw animation."""
from pathlib import Path
import copy,math
from PIL import Image,ImageDraw,ImageFont
from preview_runeballs import preview,scenes,ROOT,MEDIA
OUT=ROOT/'dist/Runeballs-0.5.29-previews';OUT.mkdir(exist_ok=True)
font=ImageFont.truetype(str(MEDIA/'Fonts/LilitaOne.ttf'),18)
def scene_for(kind,time):
 s=copy.deepcopy(scenes[0]);s['buff']=kind;s['buffTime']=time
 s['marbles']=s['marbles'][:45];s['loadedKind']='Frost' if kind=='Frost' else 'Stasis' if kind=='EffectStasis' else 'Bomb'
 s['status']='FROST' if kind=='Frost' else 'TIME STOP' if kind=='EffectStasis' else 'SEAL THE PORTAL!'
 return s
specs=[('Alliance','Frost',4,'Frozen in ice'),('Horde','Frost',1.5,'Ice melting away'),('Alliance','EffectStasis',3,'Time Stop restraints'),('Horde','EffectStasis',.25,'Chains releasing'),('Alliance','Bomb',.1,'Fire explosion'),('Horde','Bomb',.55,'Flames and embers')]
for i,(faction,kind,t,title) in enumerate(specs,1):
 s=scene_for(kind,t)
 if kind=='Bomb':s.pop('buff');s['impacts']=[dict(point=[550,180],kind='Bomb',color=1,progress=t)]
 im=preview(faction,s).convert('RGB');canvas=Image.new('RGB',(1024,772),(24,20,28));canvas.paste(im)
 d=ImageDraw.Draw(canvas);d.text((16,727),title,font=font,fill='#ffe6b2');d.text((16,750),'Rendered preview using addon assets — not a live WoW capture.',font=font,fill='#baaebd')
 canvas.save(OUT/f'{i:03d}-{faction.lower()}-{kind.lower()}.png')
frames=[]
for i in range(41):
 s=scene_for('Frost',max(0,4-i*.1))
 if i==40:s.pop('buff')
 im=preview('Alliance',s).convert('RGB').resize((768,540),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',(768,570),(24,20,28));canvas.paste(im);ImageDraw.Draw(canvas).text((12,546),'Ice melting over 4 seconds — rendered preview',font=font,fill='#ffe6b2');frames.append(canvas)
palette=frames[0].quantize(colors=256);frames=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
frames[0].save(OUT/'Frost-melt-preview.gif',save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=False)
(OUT/'README.txt').write_text('Runeballs 0.5.29: six individual offline material previews and an animated frost melt. These use addon assets and timer formulas, not live WoW screenshots.\n')
print(OUT)
