"""Export exact Lua runtime paths for offline art/layout review (requires lupa)."""
from pathlib import Path
import json
from lupa.lua51 import LuaRuntime
root=Path(__file__).resolve().parents[1]
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('A={}')
lua.execute('assert(loadstring(...))("RaynnaRuneballs",A)',(root/'RaynnaRuneballs/Engine.lua').read_text())
engine=lua.globals().A.Engine
data=[]
for level in range(1,13):
    path=engine.Path(level)
    length=path.length
    data.append({'level':level,'name':engine.MapName(level),'path':[[path[i].x,path[i].y] for i in range(1,len(path)+1)],
        'marbles':[list(engine.Point(level,d)) for d in range(0,min(1150,int(length)),25)],'end':list(engine.Point(level,length))})
for scene in data:
    level=scene['level']
    if level>=6 and level%4==2:
        path=engine.Path(level+1000)
        scene['other']=[[path[i].x,path[i].y] for i in range(1,len(path)+1)]
        scene['otherMarbles']=[list(engine.Point(level+1000,d)) for d in range(0,1150,25)]
        scene['crossings']=[{'x':c.x,'y':c.y,'angle':c.angle} for c in engine.Crossings(level).values()]
(root/'.test-deps').mkdir(exist_ok=True)
(root/'.test-deps/runeballs-scenes.json').write_text(json.dumps(data))
print('Exported twelve exact engine routes.')
