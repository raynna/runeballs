"""Bake continuous antialiased roads from exact Lua routes (Lua 5.1 + Pillow)."""
from pathlib import Path
import sys
from PIL import Image, ImageDraw
import json
ROOT=Path(__file__).resolve().parents[1]
scenes=json.loads((ROOT/'.test-deps/runeballs-scenes.json').read_text())
routes={scene['level']:scene['path'] for scene in scenes}
routes.update({scene['level']+1000:scene['other'] for scene in scenes if 'other' in scene})
# Include 28px margins matching entry coordinates outside the inner board.
# Draw isotropically in screen pixels before scaling to a power-of-two texture.
scale=3
for route,path in routes.items():
    points=[((x+28)*scale,y*.86*scale) for x,y in path]
    road=Image.new('RGBA',(816*scale,430*scale));draw=ImageDraw.Draw(road)
    for width,color in [(30,(10,11,15,255)),(27,(145,110,53,255)),(24,(48,43,38,255)),(22,(18,21,27,255))]:
        draw.line(points,fill=color,width=width*scale,joint='curve')
        radius=width*scale/2
        for x,y in points:
            draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color)
    road.resize((1024,512),Image.Resampling.LANCZOS).save(ROOT/f'RaynnaRuneballs/Media/Road{route}.tga')
print(f'Built {len(routes)} continuous route textures.')
