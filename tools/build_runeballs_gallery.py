"""Render labelled promotional demo scenes using shipped roads, sprites and effect formulas.
These are offline previews, not live client captures. No player saves are read.
"""
from pathlib import Path
import bisect, copy, json, math, zipfile
from PIL import Image, ImageDraw, ImageFont
from preview_runeballs import preview, ROOT, MEDIA, scenes

OUT=ROOT/'dist/Runeballs-0.5.24-previews'
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
    (1,'Alliance','Rainbow','A longer opening spiral','Plain six-colour marbles, coloured special glows and rainbow ammunition.'),
    (3,'Horde','Rewind','Broad switchbacks','Long exposed corridors and colour-matched Rewind special balls.'),
    (10,'Alliance','Bomb','Winding bends and a bomb match','A matched bomb clears three neighbours ahead and behind; particles follow the road.'),
    (30,'Horde','Frost','Two lanes and short tunnels','Equal-length paths, covered crossings and a blue Frost activation.'),
    (61,'Alliance','Rainbow','Rainbow matches and chain combos','A wildcard match and a visible gap during a chain reaction.'),
    (100,'Horde','Rewind','The final dual-path round','Widely separated exits, directional underground guides and a Rewind activation.'),
]
images=[]
for level,faction,kind,title,caption in specs:
    scene=copy.deepcopy(scenes[level-1]);scene.update(loadedKind=kind,loadedColor={'Rainbow':6,'Rewind':5,'Bomb':1,'Frost':2}[kind],nextColor=3,score=f'{level*1400:,}',best=f'{max(32200,level*1600):,}')
    point,length=sampler(scene['path'])
    dual='other' in scene
    head=min(length-200,length*(.73 if dual else .67))
    count=36 if dual else min(60,54+(level-1))
    distances=[head-i*25 for i in range(count-1,-1,-1) if head-i*25>=25]
    scene['distances']=distances;scene['marbles']=[point(d) for d in distances]
    scene['kinds']={len(distances)//3:('Frost',2),len(distances)*3//4:('Rewind',4)}
    if level==61:scene['kinds'][len(distances)//3]=('Rainbow',6)
    scene['remaining']=54+int((level-1)*1.4)
    if dual:
        other,otherlength=sampler(scene['other'])
        scene['otherDistances']=distances
        scene['otherMarbles']=[other(d) for d in distances]
        scene['otherKinds']={len(distances)//2:('Bomb',1)}
    if level in (10,30,61,100):
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
        scene['impacts']=[impact]
        radius=3 if kind=='Bomb' else 1
        scene['removed']=list(range(index-radius,index+radius+1))
        if level==61:
            scene['combo']={'point':pos,'count':3,'score':900}
            scene['removed']+=list(range(max(0,index-6),max(0,index-3)))
    scene['remaining']-=len(scene.get('removed',[]))
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
html='<!doctype html><meta charset="utf-8"><title>Runeballs preview gallery</title><style>body{background:#18141c;color:#ffe6b2;font:18px system-ui;max-width:1100px;margin:32px auto}img{width:100%;border-radius:8px}p{color:#cbbecf}article{margin-bottom:40px}</style><h1>Raynna’s Runeballs — preview gallery</h1><p>Version 0.5.24. Offline, staged gameplay previews built from the shipped game assets and exact map geometry. These are not live WoW screenshots; effects show one animation frame.</p>'
for _,name,title,caption in images:html+=f'<article><h2>{title}</h2><p>{caption}</p><a href="{name}"><img src="{name}" alt="{title}"></a></article>'
(OUT/'index.html').write_text(html,encoding='utf-8')
(OUT/'README.txt').write_text('Raynna\'s Runeballs 0.5.24 preview gallery\n\nOpen index.html or overview.png. Six individual PNGs show both factions, rounds 1, 3, 10, 30, 61 and 100, all four special types, activation particles and a combo.\n\nThese are labelled offline, staged previews using shipped art and exact route geometry, not screenshots captured in WoW. Animated effects are represented by a single frame. No player saved data is used.\n')
with zipfile.ZipFile(ROOT/'dist/RaynnaRuneballs-0.5.24-previews.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(OUT.iterdir()):archive.write(file,file.name)
print('Created six labelled previews, overview, HTML gallery and separate preview ZIP:',OUT)
