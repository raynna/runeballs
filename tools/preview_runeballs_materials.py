"""Six labelled material previews, plus a timer-driven frost thaw animation."""
from pathlib import Path
import copy,math
from PIL import Image,ImageDraw,ImageFont
from preview_runeballs import preview,scenes,ROOT,MEDIA
OUT=ROOT/'dist/Runeballs-0.5.31-previews';OUT.mkdir(exist_ok=True)
font=ImageFont.truetype(str(MEDIA/'Fonts/LilitaOne.ttf'),18)
def scene_for(kind,time):
 s=copy.deepcopy(scenes[0]);s['buff']=kind;s['buffTime']=time
 s['marbles']=s['marbles'][:45];s['loadedKind']='Frost' if kind=='Frost' else 'Stasis' if kind=='EffectStasis' else 'Bomb'
 s['status']='FROST' if kind=='Frost' else 'TIME STOP' if kind=='EffectStasis' else 'SEAL THE PORTAL!'
 return s
specs=[('Alliance','Frost',4,'Frozen in ice'),('Horde','Frost',1.5,'Ice melting away'),('Alliance','EffectStasis',3,'One continuous Time Stop chain'),('Horde','EffectStasis',.25,'Chain releasing'),('Alliance','Bomb',.1,'Fire explosion'),('Horde','Break',.2,'Coloured shells breaking')]
for i,(faction,kind,t,title) in enumerate(specs,1):
 s=scene_for(kind,t)
 if kind=='Bomb':s.pop('buff');s['impacts']=[dict(point=[550,180],kind='Bomb',color=1,progress=.4)]
 if kind=='Break':
  s.pop('buff');s['loadedKind']=None;s['removed']=list(range(20,26));s['clears']=[dict(x=x,y=y,color=i+1,age=.12+(i%3)*.12,vx=40,vy=-8) for i,(x,y) in enumerate(s['marbles'][20:26])]
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
(OUT/'README.txt').write_text('Runeballs 0.5.31: six individual offline material previews and an animated frost melt. These use addon assets and timer formulas, not live WoW screenshots.\n')
print(OUT)

for mode in ['Break','Lightning']:
 frames=[]
 for i in range(60 if mode=='Break' else 36):
  s=scene_for(mode,0);s.pop('buff');s['loadedKind']=None
  if mode=='Break':
   s['removed']=list(range(20,26));age=i/60
   if age<.6:s['clears']=[dict(x=x,y=y,color=j+1,age=age,vx=40,vy=-8) for j,(x,y) in enumerate(s['marbles'][20:26])]
  else:
   s['impacts']=[dict(point=[490,150],kind='Lightning',color=2,progress=i*.05/1.1,links=[[550,180],[570,230],[530,270],[480,270],[450,220]])] if i*.05<1.55 else []
  im=preview('Horde',s).convert('RGB').resize((768,540),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(768,570),(24,20,28));canvas.paste(im)
  ImageDraw.Draw(canvas).text((12,546),mode+' animation — rendered preview, not a live capture',font=font,fill='#ffe6b2');frames.append(canvas)
 palette=frames[8].quantize(colors=256);frames=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
 frames[0].save(OUT/(mode+'-preview.gif'),save_all=True,append_images=frames[1:],duration=17 if mode=='Break' else 50,loop=0,optimize=False)
