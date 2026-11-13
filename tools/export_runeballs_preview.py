"""Export exact Lua runtime paths for offline art/layout review (requires lupa)."""
from pathlib import Path
import json, math
from lupa.lua51 import LuaRuntime
root=Path(__file__).resolve().parents[1]
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('A={}')
lua.execute('assert(loadstring(...))("RaynnaRuneballs",A)',(root/'RaynnaRuneballs/Engine.lua').read_text())
engine=lua.globals().A.Engine
data=[]
for level in range(1,101):
    path=engine.Path(level)
    length=path.length
    data.append({'level':level,'name':engine.MapName(level),'colors':6,'path':[[path[i].x,path[i].y] for i in range(1,len(path)+1)],
        'marbles':[list(engine.Point(level,d)) for d in range(14,min(1150,int(length)),25)],'end':list(engine.Point(level,length))})
for scene in data:
    level=scene['level']
    if engine.IsDualLevel(level):
        path=engine.Path(level+1000)
        scene['other']=[[path[i].x,path[i].y] for i in range(1,len(path)+1)]
        scene['otherMarbles']=[list(engine.Point(level+1000,d)) for d in range(14,1150,25)]
        scene['crossings']=[{'x':c.x,'y':c.y,'angle':c.angle,'bounds':list(engine.CoverBounds(c)),'guide':[[*engine.Point(level+1000,c.under+offset),math.atan2((engine.Point(level+1000,c.under+offset)[1]-engine.Point(level+1000,c.under+offset-4)[1])*.86,engine.Point(level+1000,c.under+offset)[0]-engine.Point(level+1000,c.under+offset-4)[0])] for offset in range(-72,73,26)]} for c in engine.Crossings(level).values()]
(root/'.test-deps').mkdir(exist_ok=True)
(root/'.test-deps/runeballs-scenes.json').write_text(json.dumps(data))
print('Exported 100 exact engine routes.')
