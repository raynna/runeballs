"""Render labelled promotional demo scenes using shipped roads, sprites and effect formulas.
These are offline previews, not live client captures. No player saves are read.
"""
from pathlib import Path
import bisect, copy, json, math, zipfile
from PIL import Image, ImageDraw, ImageFont
from preview_runeballs import preview, ROOT, MEDIA, scenes

OUT=ROOT/'dist/Runeballs-0.5.28-previews'
OUT.mkdir(parents=True,exist_ok=True)

def sampler(path):
    distances=[0]
    for a,b in zip(path,path[1:]):distances.append(distances[-1]+math.dist(a,b))
    def point(distance):
        distance=max(0,min(distances[-1],distance))
        i=max(1,min(len(path)-1,bisect.bisect_left(distances,distance)))
        f=(distance-distances[i-1])/(distances[i]-distances[i-1])
        return [a+(b-a)*f for a,b in zip(path[i-1],path[i])]
    return point,distances[-1]

specs=[
    (1,'Alliance','Lightning','Lightning arcs','Matched lightning jumps to exposed balls of the same colour.'),
    (3,'Horde','Paint','Paint a chain reaction','Nearby ordinary balls recolour before delayed matches resolve.'),
    (10,'Alliance','Stasis','Stop time on your lane','Three seconds to aim while the lane stands still.'),
    (30,'Horde','Magnet','Pull the gaps together','Magnetic attraction closes gaps between unlike colours too.'),
    (61,'Alliance','Treasure','Double the match points','An eight-second treasure window rewards fast matching and combos.'),
    (100,'Horde','Ward','Protect the portal','A twelve-second ward saves one portal breach and rewinds the lane.'),
]
images=[]
lightning_scene=None
for level,faction,kind,title,caption in specs:
    scene=copy.deepcopy(scenes[level-1]);scene.update(loadedKind=kind,loadedColor={'Lightning':2,'Paint':5,'Stasis':6,'Magnet':1,'Treasure':4,'Ward':3}[kind],nextColor=3,score=f'{level*1400:,}',best=f'{max(32200,level*1600):,}')
    point,length=sampler(scene['path'])
    dual='other' in scene
    head=min(length-200,length*(.73 if dual else .67))
    count=36 if dual else min(60,54+(level-1))
    distances=[head-i*25 for i in range(count-1,-1,-1) if head-i*25>=25]
    scene['distances']=distances;scene['marbles']=[point(d) for d in distances]
    scene['kinds']={len(distances)//3:(kind,scene['loadedColor']),len(distances)*3//4:('Rewind',4)}
    scene['status']={'Lightning':'PRECISION +300','Paint':'PAINT CHAIN','Stasis':'STASIS 3s','Magnet':'L1 MAGNET 4s','Treasure':'TREASURE 8s','Ward':'L1 WARD 12s'}[kind]
    scene['hint']=kind+' - match 3 to activate'
    scene['ward']=kind=='Ward'
    scene['remaining']=54+int((level-1)*1.4)
    if dual:
        other,otherlength=sampler(scene['other'])
        scene['otherDistances']=distances
        scene['otherMarbles']=[other(d) for d in distances]
        scene['otherKinds']={len(distances)//2:('Bomb',1)}
    if True:
        candidates=[i for i,(x,y) in enumerate(scene['marbles']) if 85<x<675 and 155<y<420 and 4<i<len(distances)-5]
        index=candidates[len(candidates)//2] if candidates else len(distances)//2
        distance=distances[index];pos=point(distance)
        progress=.4
        impact={'point':pos,'kind':kind,'color':scene['loadedColor'],'progress':progress}
        if kind=='Bomb':
            particles=[]
            for i in range(1,13):
                angle=i*math.pi/6
                x,y=point(distance+(-1 if i<=6 else 1)*progress*90*(.5+(i%6)/10))
                particles.append([x+math.cos(angle)*8,y+math.sin(angle)*8])
            impact['particles']=particles
        if kind in ('Lightning','Paint'):
            indices=([max(0,index-13),max(0,index-7),min(len(distances)-1,index+4),min(len(distances)-1,index+10),min(len(distances)-1,index+16)] if kind=='Lightning' else [max(0,index-7),max(0,index-4),min(len(distances)-1,index+4),min(len(distances)-1,index+7)])
            impact['links']=[scene['marbles'][i] for i in indices]
            scene['ballColors']={i:scene['loadedColor'] for i in indices}
            if kind=='Lightning':
                pending=impact['links'];ordered=[];previous=pos
                while pending:
                    target=min(pending,key=lambda p:(p[0]-previous[0])**2+((p[1]-previous[1])*.86)**2)
                    ordered.append(target);pending.remove(target);previous=target
                impact['links']=ordered;impact['progress']=.34
        scene['impacts']=[impact]
        radius=3 if kind=='Bomb' else 1
        scene['removed']=list(range(index-radius,index+radius+1))
        if kind=='Lightning':scene['removed']+=indices
        if level==61:
            scene['combo']={'point':pos,'count':3,'score':900}
            scene['removed']+=list(range(max(0,index-6),max(0,index-3)))
    scene['remaining']-=len(scene.get('removed',[]))
    if kind=='Lightning':lightning_scene=copy.deepcopy(scene)
    if level in (3,61):
        scene['clears']=[dict(x=pos[0]+offset,y=pos[1],color=3,combo=3 if level==61 else 1,age=.22) for offset in (-25,0,25)]
    if level==10:scene['buff']='EffectStasis'
    if level==30:scene['buff']='EffectMagnet'
    if level==100:
        scene['ward']=True
    image=preview(faction,scene).convert('RGB')
    labelled=Image.new('RGB',(1024,772),(24,20,28));labelled.paste(image,(0,0))
    draw=ImageDraw.Draw(labelled)
    font=ImageFont.truetype(str(MEDIA/'Fonts/LilitaOne.ttf'),18)
    small=ImageFont.truetype(str(MEDIA/'Fonts/LilitaOne.ttf'),13)
    draw.text((16,727),f'Round {level} | {faction} | {title}',font=font,fill='#ffe6b2')
    draw.text((16,752),'Rendered gameplay preview - staged scene using addon assets; not a live client screenshot.',font=small,fill='#baaebd')
    name=f'{level:03d}-{faction.lower()}-{kind.lower()}.png'
    labelled.save(OUT/name);images.append((labelled,name,title,caption))

sheet=Image.new('RGB',(1280,1536),(24,20,28))
for i,(im,*_) in enumerate(images):sheet.paste(im.resize((640,483),Image.Resampling.LANCZOS),((i%2)*640,(i//2)*512))
sheet.save(OUT/'overview.png')
html='<!doctype html><meta charset="utf-8"><title>Runeballs preview gallery</title><style>body{background:#18141c;color:#ffe6b2;font:18px system-ui;max-width:1100px;margin:32px auto}img{width:100%;border-radius:8px}p{color:#cbbecf}article{margin-bottom:40px}</style><h1>Raynna’s Runeballs — preview gallery</h1><p>Version 0.5.28. Offline, staged gameplay previews built from the shipped game assets and exact map geometry. These are not live WoW screenshots; effects show one animation frame.</p>'
for _,name,title,caption in images:html+=f'<article><h2>{title}</h2><p>{caption}</p><a href="{name}"><img src="{name}" alt="{title}"></a></article>'
(OUT/'index.html').write_text(html,encoding='utf-8')
(OUT/'README.txt').write_text('Raynna\'s Runeballs 0.5.28 preview gallery\n\nOpen index.html or overview.png. Six individual PNGs show both factions, rounds 1, 3, 10, 30, 61 and 100, six new special types, activation effects and a combo.\n\nThese are labelled offline, staged previews using shipped art and exact route geometry, not screenshots captured in WoW. Animated effects are represented by a single frame. No player saved data is used.\n')
print('Created six labelled previews, overview, HTML gallery and separate preview ZIP:',OUT)

# A labelled animated preview makes the hop timing and light falloff reviewable.
frames=[]
for frame in range(36):
    scene=copy.deepcopy(lightning_scene)
    if frame<23:scene['impacts'][0]['progress']=frame*.05/1.1
    else:scene['impacts']=[]
    im=preview('Alliance',scene).convert('RGB').resize((768,540),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(768,568),(24,20,28));canvas.paste(im,(0,0))
    ImageDraw.Draw(canvas).text((12,545),'Chain lightning - rendered animation preview (not a live WoW capture)',font=ImageFont.truetype(str(MEDIA/'Fonts/LilitaOne.ttf'),14),fill='#ffe6b2')
    frames.append(canvas)
palette=frames[8].quantize(colors=256)
indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
indexed[0].save(OUT/'Lightning-VFX-preview.gif',save_all=True,append_images=indexed[1:],duration=50,loop=0,optimize=False)
print('Rendered animated chain-lightning VFX preview.')

with zipfile.ZipFile(ROOT/'dist/RaynnaRuneballs-0.5.28-previews.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(OUT.iterdir()):archive.write(file,file.name)
