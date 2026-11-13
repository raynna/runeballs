"""Slice generated atlas, preserve alpha, and convert runtime assets to WoW TGA."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'RaynnaRuneballs/ArtSource'
out=ROOT/'RaynnaRuneballs/Media'
for faction in ('Alliance','Horde'):
    Image.open(src/(faction+'.png')).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS).save(out/(faction+'Frame.tga'))
atlas=Image.open(src/'SpritesSimple.png').convert('RGBA')
def cuts(image,axis,count):
    alpha=image.getchannel('A')
    size=image.width if axis==0 else image.height
    result=[0]
    for i in range(1,count):
        center=size*i/count
        reach=size/count*.27
        scores=[]
        for n in range(int(center-reach),int(center+reach)):
            band=alpha.crop((n,0,n+1,image.height) if axis==0 else (0,n,image.width,n+1))
            scores.append((sum(band.histogram()[100:]),n))
        best=min(score for score,_ in scores)
        gaps=[n for score,n in scores if score==best]
        result.append(gaps[len(gaps)//2])
    return result+[size]
ys=cuts(atlas,1,4)
names=['Ball1','Ball2','Ball3','Ball4','Ball5','Bomb','Frost','Rewind','AllianceLauncher','HordeLauncher','Portal','Explosion','Spark','Shatter','AllianceButton','HordeButton']
for i,name in enumerate(names):
    x,y=i%4,i//4
    row=atlas.crop((0,ys[y],atlas.width,ys[y+1]))
    xs=cuts(row,0,4)
    tile=row.crop((xs[x],0,xs[x+1],row.height))
    bbox=tile.getchannel('A').point(lambda a:255 if a>24 else 0).getbbox()
    if bbox: tile=tile.crop(bbox)
    size=(256,128) if name.endswith('Button') else (128,128)
    tile.thumbnail((size[0]-8,size[1]-8),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',size)
    canvas.alpha_composite(tile,((size[0]-tile.width)//2,(size[1]-tile.height)//2))
    canvas.save(out/(name+'.tga'))
# Ordinary marbles deliberately carry no ability glyphs.
plain=Image.open(src/'PlainBallsPolished.png').convert('RGBA')
xs=cuts(plain,0,5)
for i in range(5):
    tile=plain.crop((xs[i],0,xs[i+1],plain.height))
    bounds=tile.getchannel('A').point(lambda a:255 if a>24 else 0).getbbox()
    tile=tile.crop(bounds)
    tile.thumbnail((120,120),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(128,128))
    canvas.alpha_composite(tile,((128-tile.width)//2,(128-tile.height)//2))
    canvas.save(out/('Ball'+str(i+1)+'.tga'))
# Sixth ordinary marble: a neutral pearl, distinct from the five saturated hues.
# Procedural sphere keeps the same padded silhouette and bold outline.
import math
pearl=Image.new('RGBA',(128,128))
for y in range(128):
    for x in range(128):
        dx,dy=(x-63.5)/57,(y-63.5)/57
        radius=dx*dx+dy*dy
        if radius<=1:
            if radius>.88:
                color=(15,18,25,255)
            else:
                z=math.sqrt(1-radius)
                light=max(0,-dx*.4-dy*.55+z*.7)
                spec=max(0,1-math.hypot(dx+.32,dy+.42)/.3)**2
                value=min(255,int(95+155*light+100*spec))
                color=(value,value,min(255,value+8),255)
            pearl.putpixel((x,y),color)
pearl.save(out/'Ball6.tga')
# A code-native repeatable road segment: dark groove, bevel and fine gold rails.
track=Image.new('RGBA',(128,32));d=ImageDraw.Draw(track)
for y,color in enumerate([(12,11,13,230)]*2+[(126,94,43,255)]*2+[(51,43,37,255)]*2+[(18,20,25,245)]*20+[(51,43,37,255)]*2+[(126,94,43,255)]*2+[(12,11,13,230)]*2):
    d.line((0,y,127,y),fill=color)
track.save(out/'Track.tga')
dot=Image.new('RGBA',(16,16))
ImageDraw.Draw(dot).ellipse((3,3,12,12),fill=(255,226,139,230),outline=(20,15,10,255),width=1)
dot.save(out/'Dot.tga')
print('Built 20 runtime textures; source alpha preserved.')

# Additional production HUD icons, bevelled controls and faction launchers.
polish=Image.open(src/'PolishUI.png').convert('RGBA')
ys=cuts(polish,1,4)
names=['Trophy','Crown','QuestGem','Marbles','MouseLeft','MouseRight','EscapeKey','AimArrow','PauseIcon','SettingsIcon','PlayIcon','CloseIcon','HordeButton','AllianceButton','HordeLauncher','AllianceLauncher']
for i,name in enumerate(names):
    row=polish.crop((0,ys[i//4],polish.width,ys[i//4+1]))
    xs=cuts(row,0,4)
    tile=row.crop((xs[i%4],0,xs[i%4+1],row.height))
    bbox=tile.getchannel('A').point(lambda a:255 if a>24 else 0).getbbox()
    if bbox:tile=tile.crop(bbox)
    size=(256,128) if name.endswith('Button') else (128,128)
    tile.thumbnail((size[0]-8,size[1]-8),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',size)
    canvas.alpha_composite(tile,((size[0]-tile.width)//2,(size[1]-tile.height)//2))
    canvas.save(out/(name+'.tga'))
# Code-native effects material: a soft radial light, used with vertex tint.
import math
halo=Image.new('RGBA',(128,128));pixels=halo.load()
for y in range(128):
    for x in range(128):
        radius=math.hypot(x-63.5,y-63.5)/63
        pixels[x,y]=(255,255,255,int(150*max(0,1-radius)**2))
halo.save(out/'Halo.tga')
# A small reusable panel tile with clean cartoon outlines and gold bevel.
panel=Image.new('RGBA',(64,64));d=ImageDraw.Draw(panel)
d.rounded_rectangle((0,0,63,63),radius=8,fill=(22,13,18),width=2)
d.rounded_rectangle((3,3,60,60),radius=6,fill=(169,98,22))
d.rounded_rectangle((4,4,59,59),radius=5,fill=(255,200,61))
d.rounded_rectangle((6,7,57,57),radius=4,fill=(41,33,43))
d.line((10,9,53,9),fill=(94,73,68),width=1)
panel.save(out/'HUDPanel.tga')
print('Polished HUD, controls and effects built.')

tunnels=Image.open(src/'Tunnels.png').convert('RGBA')
xs=cuts(tunnels,0,2)
for i,name in enumerate(('Entrance','Bridge')):
    tile=tunnels.crop((xs[i],0,xs[i+1],tunnels.height))
    tile=tile.crop(tile.getchannel('A').point(lambda a:255 if a>24 else 0).getbbox())
    tile.thumbnail((120,120),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(128,128));canvas.alpha_composite(tile,((128-tile.width)//2,(128-tile.height)//2))
    canvas.save(out/(name+'.tga'))

# 0.4.1: flat cartoon covers, unmistakable bridge deck, round losing sinkhole.
simple=Image.open(src/'CrossingsSimple.png').convert('RGBA')
xs=cuts(simple,0,3)
for i,name in enumerate(('Bridge','Entrance','Portal')):
    tile=simple.crop((xs[i],0,xs[i+1],simple.height))
    tile=tile.crop(tile.getchannel('A').point(lambda a:255 if a>24 else 0).getbbox())
    size=(256,256) if name!='Entrance' else (256,128)
    # Fill known runtime dimensions; entrance preserves its long low silhouette.
    if name=='Bridge': tile=tile.resize((248,248),Image.Resampling.LANCZOS)
    elif name=='Portal': tile=tile.resize((248,248),Image.Resampling.LANCZOS)
    else: tile=tile.resize((248,100),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',size)
    canvas.alpha_composite(tile,((size[0]-tile.width)//2,(size[1]-tile.height)//2))
    canvas.save(out/(name+'.tga'))
print('Built simple covered crossings and round sinkhole.')

# Preserve the source canvas center: rotation pivots at the pit, not its road stub.
Image.open(src/'ExitMouth.png').convert('RGBA').resize((256,256),Image.Resampling.LANCZOS).save(out/'Portal.tga')

# Compact 0.4.4 entry and exit: crop fixed source coordinates to keep the
# aperture center on the texture's rotation pivot. Source atlas is 2160x720.
compact=Image.open(src/'CompactHoles.png').convert('RGBA')
compact=compact.resize((2160,720),Image.Resampling.LANCZOS)
compact.crop((90,150,510,570)).resize((128,128),Image.Resampling.LANCZOS).save(out/'Entry.tga')
compact.crop((1428,0,2148,720)).resize((128,128),Image.Resampling.LANCZOS).save(out/'Portal.tga')

# Continuous procedural two-arm energy spiral, rather than a particle outline.
from PIL import ImageFilter
swirl=Image.new('RGBA',(512,512));pen=ImageDraw.Draw(swirl)
for arm in range(2):
    points=[]
    for step in range(181):
        t=step/180
        radius=(5+43*t)*4
        angle=t*math.pi*2.1+arm*math.pi
        points.append((256+math.cos(angle)*radius,256+math.sin(angle)*radius))
    pen.line(points,fill=(110,45,255,235),width=42,joint='curve')
    pen.line(points,fill=(100,200,255,255),width=18,joint='curve')
    pen.line(points,fill=(225,245,255,255),width=7,joint='curve')
glow=swirl.filter(ImageFilter.GaussianBlur(10))
glow.alpha_composite(swirl)
glow.resize((128,128),Image.Resampling.LANCZOS).save(out/'PortalSwirl.tga')

# Reuse the original round rim without a baked road stub. Runtime track geometry
# continues under its center, so curved approaches need no straight overlay.
round_sheet=Image.open(src/'CrossingsSimple.png').convert('RGBA')
round_cuts=cuts(round_sheet,0,3)
round_tile=round_sheet.crop((round_cuts[2],0,round_cuts[3],round_sheet.height))
round_tile=round_tile.crop(round_tile.getchannel('A').point(lambda a:255 if a>24 else 0).getbbox())
round_tile.thumbnail((96,96),Image.Resampling.LANCZOS)
round_canvas=Image.new('RGBA',(128,128))
round_canvas.alpha_composite(round_tile,((128-round_tile.width)//2,(128-round_tile.height)//2))
round_canvas.save(out/'Portal.tga')
