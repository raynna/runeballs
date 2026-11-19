"""Slice approved generated sprite atlases; preserve their alpha and cell alignment."""
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'RaynnaRuneballs/ArtSource';OUT=ROOT/'RaynnaRuneballs/Media'
def cells(file,columns,rows):
 im=Image.open(SRC/file).convert('RGBA');w,h=im.size
 return [im.crop((round(c*w/columns),round(r*h/rows),round((c+1)*w/columns),round((r+1)*h/rows))) for r in range(rows) for c in range(columns)]
def save(name,im):im.resize((128,128),Image.Resampling.LANCZOS).save(OUT/(name+'.tga'))
for i,im in enumerate(cells('IceMeltAtlas.png',3,2)):save('IceShell'+str(6-i),im)
for name,im in zip(['TimeChainLink','FireBlast','FireTongue','RewindWrap','MagnetWrap','TreasureWrap'],cells('EffectMaterialsAtlas.png',3,2)):
 save(name,im)
 if name in ['FireBlast','FireTongue']:save(name+'Glow',im)
for i,im in enumerate(cells('MarbleBreakAtlas.png',4,6)):save('Break'+str(i//4+1)+'_'+str(i%4+1),im)
print('Sliced 38 alpha-preserving ice, effect and marble-break sprites.')
