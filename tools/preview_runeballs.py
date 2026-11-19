"""Offline layout/art review with exact engine routes; not an in-game capture."""
from pathlib import Path
import json, math, random
from PIL import Image, ImageDraw, ImageFont, ImageChops
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
 def tinted(name,x,y,w,h,color,alpha=1,additive=False,angle=0):
  art=Image.open(MEDIA/(name+'.tga')).convert('RGBA').resize((round(w),round(h)),Image.Resampling.LANCZOS)
  tint=Image.new('RGBA',art.size,tuple(round(v*255) for v in color)+(round(alpha*255),))
  art=ImageChops.multiply(art,tint)
  if angle:art=art.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
  pos=(round(x-art.width/2),round(y-art.height/2))
  if additive:
   layer=Image.new('RGBA',im.size);layer.alpha_composite(art,pos)
   rgb=ImageChops.add(im.convert('RGB'),ImageChops.multiply(layer.convert('RGB'),layer.getchannel('A').convert('RGB')))
   im.paste(rgb,(0,0))
  else:im.alpha_composite(art,pos)
 colors=[(1,.19,.15),(.15,.65,1),(.28,.9,.22),(1,.8,.12),(.8,.28,1),(.95,.95,1)]
 auras=[]
 def aura(x,y,color,kind,loaded=False):
  tint=colors[color-1] if kind!='Rainbow' else (.8,.55,1)
  size=68 if loaded else 56
  tinted('SpecialLight',x,y,size,size,tint,.47,True)
  tinted('SpecialRing',x,y,44 if loaded else 31,44 if loaded else 31,tint,.85 if loaded else .4)
  for i in range(2):
   angle=1.2+i*math.pi
   tinted('SpecialSpark',x+math.cos(angle)*16,y+math.sin(angle)*16,7,7,tint,.7)
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
  secondary=points is scene.get('otherMarbles')
  kinds=scene.get('otherKinds' if secondary else 'kinds',{})
  distances=scene.get('otherDistances' if secondary else 'distances',[])
  for index,(x,y) in enumerate(points):
   distance=distances[index] if distances else 14+index*25
   if secondary and any(abs(distance-c['under'])<=c['half'] for c in scene['crossings']):continue
   if index in scene.get('otherRemoved' if secondary else 'removed',[]):continue
   color=scene.get('otherBallColors' if secondary else 'ballColors',{}).get(index,rng.randrange(1,scene['colors']+1))
   kind=None
   if index in kinds:kind,color=kinds[index]
   name=('Rainbow' if kind=='Rainbow' else kind+str(color)) if kind else 'Ball'+str(color)
   sprite(name,132+x,155+y*.86,27,27)
   if kind:auras.append((132+x,155+y*.86,color,kind))
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
   # Underground road gaps are part of the baked lower-lane texture.
   for gx,gy,angle in c['guide']:
    for side in [-1,1]:
     wing=angle+side*.65;d.line((132+gx-6*math.cos(wing),155+gy*.86-6*math.sin(wing),132+gx,155+gy*.86),fill=(145,122,83),width=2)
 road(scene['path']);entrance(scene['path']);marbles(scene['marbles'])
 for route in routes:
  ex,ey=route[-1];px,py=route[-2];angle=-math.degrees(math.atan2((ey-py)*.86,ex-px))
  sprite('Portal',132+ex,155+ey*.86,60,60,angle)
  sprite('PortalSwirl',132+ex,155+ey*.86,28,28)
  if scene.get('ward') and route is scene['path']:tinted('PortalShield',132+ex,155+ey*.86,56,56,(.35,.85,1),.85,True)
 for args in auras:aura(*args)
 sprite(faction+'Launcher',512,365,104,104)
 loaded=scene.get('loadedColor',2);kind=scene.get('loadedKind')
 sprite(('Rainbow' if kind=='Rainbow' else kind+str(loaded)) if kind else 'Ball'+str(loaded),512,370,34,34)
 if kind:aura(512,370,loaded,kind,True)
 sprite('Ball'+str(scene.get('nextColor',4)),580,370,28,28);text('NEXT',580,390,14)
 for impact in scene.get('impacts',[]):
  x,y=impact['point'];x+=132;y=155+y*.86
  progress=impact.get('progress',.35);kind=impact['kind'];tint=colors[impact['color']-1]
  rewind=kind=='Rewind';size=85-progress*45 if rewind else 40+progress*100
  impact_textures={'Bomb':'FireBlast','Frost':'FrostBurst','Rewind':'RewindBurst','Rainbow':'RainbowBurst','Lightning':'LightningFlash','Paint':'PaintBurst','Stasis':'StasisBurst','Magnet':'MagnetBurst','Treasure':'TreasureBurst','Ward':'WardBurst'}
  particles={'Bomb':'FireTongue','Rewind':'EnergyMote','Rainbow':'StarGlint','Paint':'PaintDrop','Stasis':'FrostShard','Magnet':'EnergyMote','Treasure':'CoinGlint','Ward':'StarGlint','Frost':'FrostShard'}
  if kind=='Bomb':tint=(1,.32+(1-progress)*.25,.04)
  extra=kind in impact_textures
  tinted('ImpactLight',x,y,95,95,tint,(1-progress)**2*.35,True)
  if kind=='Lightning':size=26+progress*16
  if kind=='Bomb':size=35+math.sin(min(1,progress*1.4)*math.pi*.5)*100
  tinted(impact_textures.get(kind,'PortalSwirl' if rewind else 'SpecialRing'),x,y,size,size,tint,(1-progress)*.95,extra,angle=math.degrees(-progress*5) if rewind or kind=='Magnet' else 0)
  if kind!='Lightning':
   rotation=math.degrees(-progress*5) if rewind or kind=='Magnet' else 0
   tinted(impact_textures[kind]+'Glow',x,y,size,size,tint,(1-progress)*.7,True,angle=rotation)
   if kind=='Bomb':tinted('FireBlast',x,y,size*.58,size*.58,(1,.85,.3),(1-progress)**2*.95,True)
   elif kind!='Paint':tinted(impact_textures[kind],x,y,size,size,tuple(.65+v*.35 for v in tint),(1-progress)*.35,True,angle=rotation)
  if kind=='Lightning':
   age=progress*1.1
   tinted('ImpactLight',x,y,80,80,tint,max(0,1-age/.3)*.7,True)
   previous=(x,y)
   for index,(tx,ty) in enumerate(impact.get('links',[])):
    target=(132+tx,155+ty*.86);local_age=age-index*.075
    if 0<=local_age<.72:
     travel=min(1,local_age/.045);end=(previous[0]+(target[0]-previous[0])*travel,previous[1]+(target[1]-previous[1])*travel)
     dx,dy=end[0]-previous[0],end[1]-previous[1];alpha=1-local_age/.72;variant=int(local_age*13)%3+1
     center=((end[0]+previous[0])/2,(end[1]+previous[1])/2)
     for texture,color,opacity in [('LightningBloom',tint,.85),('LightningBolt',tint,.9),('LightningBolt',tuple(.75+v*.25 for v in tint),.75)]:
      tinted(texture+str(variant),*center,max(1,math.hypot(dx,dy)),32,color,alpha*opacity,True,angle=-math.degrees(math.atan2(dy,dx)))
     arrival=max(0,min(1,(local_age-.035)/.055))*alpha
     tinted('ImpactLight',*target,45+arrival*22,45+arrival*22,tint,arrival*.65,True)
     tinted('LightningFlash',*target,13+arrival*10,13+arrival*10,tuple(.7+v*.3 for v in tint),arrival,True)
    previous=target
  else:
   for i in range(1,13):
    angle=i*math.pi/6+(-progress*4 if rewind else 0)
    radius=65*(1-progress) if rewind else 10+progress*(70 if i%2==0 else 45)
    px=x+math.cos(angle)*radius;py=y+math.sin(angle)*radius*.86
    if kind=='Bomb' and 'particles' in impact:
     px,py=impact['particles'][i-1];px+=132;py=155+py*.86
    if kind=='Paint' and i<=len(impact.get('links',[])):
     tx,ty=impact['links'][i-1];px=x+(132+tx-x)*min(1,progress*2.5);py=y+(155+ty*.86-y)*min(1,progress*2.5)
    elif kind=='Treasure':px=x+math.cos(angle)*35;py=y+(-progress*90+i%3*12)*.86
    elif kind=='Magnet':px=x+math.cos(angle)*70*(1-progress);py=y+math.sin(angle)*70*(1-progress)*.86
    elif kind=='Stasis':px=x+math.cos(angle)*45;py=y+math.sin(angle)*45*.86
    particle_tint=colors[(i-1)%6] if kind=='Rainbow' else tint
    if kind=='Bomb':py-=progress*25*.86
    tinted('ImpactLight',px,py,28,28,particle_tint,(1-progress)*.4,True)
    tinted(particles.get(kind,'SpecialSpark'),px,py,(22 if kind=='Frost' else 24 if kind=='Bomb' else 18)*(1-progress*.6),(38 if kind=='Bomb' else 18)*(1-progress*.6),particle_tint,(1-progress)*.9,kind!='Paint',angle=math.degrees(angle+progress*(-4 if rewind else 2)))
 for e in scene.get('clears',[]):
  x,y=132+e['x'],155+e['y']*.86;p=e.get('age',.2)/.6;color=colors[e.get('color',2)-1]
  firework=e.get('kind')=='Firework';strength=2.8 if firework else min(1.5,1+(e.get('combo',1)-1)*.15)
  radius=(22+p*36)*strength
  tinted('MatchRing',x,y,radius,radius,color,(1-p)*(.28 if firework else .75),True)
  tinted('ImpactLight',x,y,radius*1.5,radius*1.5,color,(1-p)**2*.45,True)
  count=8 if firework else 3
  for j in range(1,count+1):
   angle=j*math.pi*2/count+e.get('phase',e['x']*.013);distance=(1-(1-p)**2)*34*strength
   size=(26 if firework else 10)*(1-p*.75)
   tinted('BombEmber' if firework else 'StarGlint',x+math.cos(angle)*distance,y+(math.sin(angle)*distance+p*p*18)*.86,size,size,color,1-p,True,angle=math.degrees(angle))
 for index,(x,y) in enumerate(scene.get('marbles',[])):
  if scene.get('buff'):
   x+=132;y=155+y*.86;buff=scene['buff'];remaining=scene.get('buffTime',4)
   name={'Rewind':'RewindWrap','EffectStasis':'TimeChains','EffectMagnet':'MagnetWrap','EffectTreasure':'TreasureWrap'}.get(buff,buff)
   alpha=1;size=31
   if buff=='Frost':name='IceShell'+str(max(1,min(6,math.ceil(remaining*1.5))));alpha=min(1,remaining/.35)
   if name=='TimeChains':release=max(0,1-remaining/.45);alpha=1-release;size=29+release*9
   tinted(name,x,y,size,size,(1,1,1),alpha)
 if scene.get('combo'):
  cx,cy=scene['combo']['point']
  text('COMBO! x'+str(scene['combo']['count']),132+cx,155+cy*.86-46,24,True)
  text('+'+str(scene['combo']['score']),132+cx,155+cy*.86-18,22,True)
 text('ROUND '+str(scene['level']),258,72,25,True,155);text(scene['name'],259,105,14,False,165)
 width=84 if faction=='Alliance' else 109
 for left,label,value,icon in [(690 if faction=='Alliance' else 689,'SCORE',scene.get('score','9,200'),'Trophy'),(784 if faction=='Alliance' else 818,'BEST',scene.get('best','32,200'),'Crown')]:
  center=left+width/2
  sprite(icon,center-30,82,14,14);text(label,center+12,76,12);text(value,center,98,24,True,width)
 panel(132,590,760,27);text('PORTAL THREAT',207,596,14)
 d.rectangle((292,598,877,609),fill=(13,8,15));d.rectangle((292,598,540,609),fill=(39,191,255))
 panel(35,625,290,83);sprite('QuestGem',66,666,38,48)
 text(scene.get('status','SEAL THE PORTAL!'),203,641,18,False,213);text(scene.get('hint','Match 3+ to clear the chain'),203,670,14,False,213)
 panel(335,625,110,83);sprite('Marbles',355,647,16,16);text('MARBLES',400,641,11);text(str(scene.get('remaining',74)),390,665,28,True)
 panel(455,625,220,83)
 for i,(icon,label) in enumerate([('MouseLeft','Left-click: shoot'),('MouseRight','Right-click: swap'),('EscapeKey','Esc: pause')]):
  sprite(icon,479,646+i*21,16,18);text(label,577,641+i*21,13,False,156)
 for x,w,label,icon in [(685,145,'PAUSE','PauseIcon'),(840,150,'SETTINGS','SettingsIcon')]:
  sprite(faction+'Button',x+w/2,665, w,57);sprite(icon,x+32,665,16,16);text(label,x+44+(w-64)/2,658,14,False,w-64)
 sprite('CloseIcon',994,27,30,30)
 return im
if __name__=='__main__':
 (ROOT/'dist').mkdir(exist_ok=True)
 for faction,level in [('Alliance',1),('Horde',30)]:
  preview(faction,scenes[level-1]).convert('RGB').save(ROOT/'dist'/('RaynnaRuneballs-'+faction+'-preview.png'))
 print('Rendered 1024x720 Alliance spiral and Horde dual-path layout previews.')
