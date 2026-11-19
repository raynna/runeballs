from pathlib import Path
import sys,copy,math
sys.path.insert(0,'tools')
from preview_runeballs import preview,scenes
from PIL import Image,ImageDraw
out=Path('dist/Runeballs-0.5.28-feedback');out.mkdir(exist_ok=True)
for faction in ['Alliance','Horde']:
 s=copy.deepcopy(scenes[0]);s['marbles']=[];s['distances']=[];s['status']='VICTORY!';s['hint']='Portal sealed';s['remaining']=0
 s['clears']=[dict(x=380+math.cos(i*2.4)*130,y=250+math.sin(i*2.4)*110,color=i%6+1,kind='Firework',age=.12+i*.06,phase=i*2.4) for i in range(6)]
 im=preview(faction,s).convert('RGB');im.save(out/(faction+'-victory.png'))
