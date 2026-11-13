"""Lua 5.1 gameplay and mocked client integration checks."""
from pathlib import Path
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / 'RaynnaRuneballs'

def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT / 'tests/wow_mock.lua').read_text())
    lua.execute("""
        local create=CreateFrame
        function CreateFrame(...)
            local f=create(...)
            f.SetBackdrop=function(self,data) self.backdrop=data end
            f.CreateTexture=function(self,name,layer)
                local t=create('Texture',name,self);t.drawLayer=layer;return t
            end
            return f
        end
    """)
    lua.execute('FLYING=false; function UnitOnTaxi() return FLYING end; function InCombatLockdown() return false end; UISpecialFrames={}')
    for line in (ADDON / 'RaynnaRuneballs.toc').read_text().splitlines():
        if line and not line.startswith('#'):
            lua.execute('assert(loadstring(...))("RaynnaRuneballs",A)', (ADDON / line).read_text())
    return lua

lua = runtime()
lua.execute('''
local E=A.Engine
local db={options={scale=1.1,autoFlight=false},best=40}
E.Init(db)
assert(db.options.scale==1.1 and not db.options.autoFlight and db.best==40)
local r=E.NewRun(db)
assert(r.paused and #r.balls==22 and r.remaining==62)
local head=r.head
E.Step(db,0.05); assert(r.head==head,'paused simulation is stationary')
r.paused=false
E.Step(db,0.05); assert(r.head>head)
assert(not E.Fire(r,380,250),'zero length aim rejected')
assert(E.Fire(r,100,100) and not E.Fire(r,100,100),'single projectile at a time')
local loaded,nextColor=r.loaded,r.next
E.Swap(r); assert(r.loaded==nextColor and r.next==loaded)
E.Init(db); assert(db.run==r and r.paused and r.shot,'reload retains in-flight shot and pauses')

-- Matches create persistent gaps; matching ends retract before the combo.
r=E.NewRun(db,1);r.remaining=0;r.paused=false
r.balls={{color=2,d=400},{color=2,d=375},{color=1,d=350},{color=1,d=325},{color=2,d=300}}
assert(E.Insert(r,4,1)==1 and #r.balls==3 and r.score==300)
assert(r.balls[1].d==425 and r.balls[3].d==300,'removal does not teleport survivors')
E.Step(db,0.05)
assert(r.balls[1].d<425 and r.balls[3].d>300 and #r.balls==3,'matching front retracts while rear advances')
for i=1,30 do E.Step(db,0.05) end
assert(r.status=='won' and r.score==900 and db.level==2 and db.best==900,'contact triggers delayed x2 combo')

-- Unmatched leading section waits; rear catches it and supplies forward motion.
r=E.NewRun(db,1);r.remaining=0;r.paused=false;r.balls={{color=1,d=400},{color=2,d=350}}
E.Step(db,0.05);assert(r.balls[1].d==400 and r.balls[2].d>350)
for i=1,24 do E.Step(db,0.05) end
assert(r.balls[1].d>400 and math.abs(r.balls[1].d-r.balls[2].d-25)<0.001,'rear pushes front after contact')
assert(E.Speed(r)==26 and E.Speed({level=5})==42 and E.Speed({level=10})==57,'gentle opening ramps into faster later rounds')
r=E.NewRun(db,2);r.paused=false;r.remaining=0;r.balls={{color=1,d=E.Path(2).length-0.01}}
E.Step(db,0.05); assert(r.status=='lost' and not r.paused and r.ending.phase=='drain','defeat starts animated drain')
local drainCount=#r.balls
E.Step(db,0.05);assert(#r.balls<drainCount,'leading ball disappears into portal')
for i=1,70 do E.Step(db,0.05) end
assert(#r.balls==0 and r.ending.done and r.paused,'drain finishes and result settles')

-- Swept collision and specials.
r=E.NewRun(db,1);r.paused=false;r.remaining=0;r.balls={{color=1,d=350}}
local x,y=E.Point(1,350)
r.shot={x=x-35,y=y,vx=1040,vy=0,color=2}
E.Step(db,0.05);assert(not r.shot and #r.balls==2,'fast shot does not tunnel')
r.shot={x=759,y=1,vx=1040,vy=0,color=2}
E.Step(db,0.05);assert(not r.shot)
r=E.NewRun(db,1);r.paused=false;r.remaining=0
local before=#r.balls
E.Special(r,7,'Bomb');assert(#r.balls==before-5 and r.burst.kind=='Explosion')
E.Special(r,7,'Frost');assert(r.slow==4)
local tail=r.balls[#r.balls].d
E.Step(db,0.05);assert(r.balls[#r.balls].d-tail<1,'frost slows rear driver')
E.Special(r,7,'Rewind');assert(r.reverse==2.5)
tail=r.balls[#r.balls].d
E.Step(db,0.05);assert(r.balls[#r.balls].d<tail,'rewind moves backwards, including behind entrance')
for i=1,21 do
    r.shot=nil;r.cooldown=0;assert(E.Fire(r,10,10))
    if i%7==0 then assert(r.nextKind==({'Bomb','Frost','Rewind'})[i/7]) end
end
r.nextKind='Bomb';r.loadedKind=nil;E.Swap(r);assert(r.loadedKind=='Bomb' and not r.nextKind)

-- Saved v1 run migration preserves score/preferences and gains path distances.
local old={best=2000,options={scale=1.1},run={version=1,head=400,balls={{color=1},{color=3}},score=1234}}
E.Init(old);assert(old.run.version==2 and old.run.balls[2].d==375 and old.run.score==1234 and old.best==2000 and old.options.scale==1.1)
local position=old.run.balls[2].d;E.Init(old);assert(old.run.balls[2].d==position,'migration is idempotent')

-- Distinct routes, bounded geometry and increasing complexity.
local seen={}
for level=1,60 do
    local path=E.Path(level)
    assert(path.length>1000)
    local signature=string.format('%.4f:%.4f:%.4f',path.length,path[1].x,path[1].y)
    assert(not seen[signature],'every round has a different route');seen[signature]=true
    for _,p in ipairs(path) do assert(p.x>=-28.01 and p.x<=788.01 and p.y>=-0.01 and p.y<=500.01,'route stays on board') end
end
assert(E.Path(12).length>E.Path(1).length)
-- Unattended runs terminate; simulation keeps all neighbours ordered.
for level=1,8 do
    r=E.NewRun(db,level);r.paused=false
    for step=1,3000 do
        E.Step(db,0.05)
        for i=2,#r.balls do assert(r.balls[i-1].d-r.balls[i].d>=24.99) end
        if r.status~='playing' then break end
    end
    assert(r.status=='lost')
end
function UnitFactionGroup() return 'Horde' end
assert(A.Faction()=='Horde')
function UnitFactionGroup() return 'Alliance' end
assert(A.Faction()=='Alliance')
UnitFactionGroup=nil;assert(A.Faction()=='Alliance')
assert(A.Number(1234567)=='1,234,567')

-- Actual module wiring, pause/resume, saving, settings and flight ownership.
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs')
A.events.OnEvent(A.events,'PLAYER_LOGIN')
assert(not A.frame:IsShown() and RaynnaModsSettingsRegistry.pages.runeballs)
SlashCmdList.RAYNNARUNEBALLS('show');assert(A.frame:IsShown())
A.frame.play.OnClick(); assert(not A.db.run.paused and A.frame.OnUpdate)
A.frame.OnUpdate(A.frame,0.02)
A.Close();assert(A.db.run.paused and not A.frame:IsShown() and not rawget(A.frame,'OnUpdate'))
A.Open(false);assert(A.db.run.paused,'reopening waits for Play')
A.SetScale(9);assert(A.db.options.scale==1.3 and A.db.options.position)
A.SetScale(0);assert(A.db.options.scale==0.55)
SlashCmdList.RAYNNARUNEBALLS('settings');assert(SETTINGS_OPENED==123)
A.Close();FLYING=true;A.CheckFlight();assert(A.frame:IsShown() and A.autoOpened)
FLYING=false;A.CheckFlight();assert(not A.frame:IsShown() and A.db.run.paused)
A.Open(false);FLYING=true;A.CheckFlight();FLYING=false;A.CheckFlight()
assert(A.frame:IsShown(),'manually opened window survives landing')
A.Close();A.db.options.autoFlight=false;FLYING=true;A.CheckFlight()
assert(not A.frame:IsShown(),'flight opt out respected')
FLYING=false;A.CheckFlight();A.db.options.autoFlight=true;A.db.options.closeOnLanding=false
FLYING=true;A.CheckFlight();A.frame.play.OnClick();FLYING=false;A.CheckFlight()
assert(A.frame:IsShown() and A.db.run.paused,'landing may leave window open but paused')
A.events.OnEvent(A.events,'PLAYER_REGEN_DISABLED');assert(not A.frame:IsShown())
SlashCmdList.RAYNNARUNEBALLS('center'); assert(A.frame:IsShown() and not A.db.options.position)
A.SetMinimapVisible(false); assert(not A.minimap:IsShown() and not A.db.options.minimap)
local page=RaynnaModsSettingsRegistry.pages.runeballs
local checks={}
local scaleInput
for _,f in ipairs(Frames) do
    if f.parent==page.frame then
        if f.kind=='CheckButton' then checks[#checks+1]=f end
        if f.kind=='EditBox' then scaleInput=f end
    end
end
assert(#checks==6 and scaleInput,'settings controls are present')
for _,c in ipairs(checks) do c.GetChecked=function() return false end;c.OnClick(c) end
assert(not A.db.options.autoFlight and not A.db.options.closeOnLanding and not A.db.options.minimap and not A.db.options.aimGuide and not A.db.options.sound)
scaleInput:SetText('115%');scaleInput.OnEnterPressed(scaleInput)
assert(A.db.options.scale==1.15 and scaleInput:GetText()=='115%')
scaleInput:SetText('nonsense');scaleInput.OnEnterPressed(scaleInput)
assert(A.db.options.scale==1.15 and scaleInput:GetText()=='115%')
scaleInput:SetText('77');scaleInput.OnEscapePressed(scaleInput)
assert(A.db.options.scale==1.15 and scaleInput:GetText()=='115%')
A.SetScale(0.8);page.refresh();assert(scaleInput:GetText()=='80%','settings refresh after external changes')
local played={}
function PlaySoundFile(path,channel) played[#played+1]={path=path,channel=channel};return true end
function PlaySound(id,channel) played[#played+1]={kit=id,channel=channel};return true end
A.GameSound('Shoot');assert(#played==0,'mute disables audio')
A.db.options.sound=true
A.GameSound('Shoot');assert(#played==1 and played[1].channel=='SFX' and played[1].kit==856)
A.GameSound('Shoot');assert(#played==1,'duplicate event sounds throttled')
NOW=NOW+1;A.GameSound('Combo',4);assert(played[2].kit==618)
A.GameSound('Invalid');assert(#played==2)
PlaySoundFile=nil;A.GameSound('Bomb');assert(played[3].kit==3175,'missing file API uses native fallback')
PlaySound=nil;A.GameSound('Frost')
-- Finish effects animate to completion even after a win, then stop updating.
A.db.run.effects={{x=0,y=0,color=1,age=0}};A.db.run.status='won';A.db.run.paused=true
for i=1,20 do E.Step(A.db,0.05) end
assert(#A.db.run.effects==0)

''')

for faction in ('Alliance','Horde'):
    client=runtime()
    client.execute('FACTION=...;function UnitFactionGroup() return FACTION end',faction)
    client.execute('''
        A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs')
        A.events.OnEvent(A.events,'PLAYER_LOGIN')
        assert(A.frame.art.texture==A.media..FACTION..'Frame.tga')
        assert(not A.frame.backdrop.bgFile and A.frame.art.drawLayer=='ARTWORK','no opaque backdrop can cover the faction artwork')
        assert(A.board.launcher.texture==A.media..FACTION..'Launcher.tga')
        local count=#Frames;A.Draw();A.Draw()
        assert(#Frames==count,'render pools reused on unchanged board')
    ''')

# End-to-end result sequences, including a save/reload during the drain.
ending=runtime()
ending.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs')
A.events.OnEvent(A.events,'PLAYER_LOGIN')
A.Open(false)
local r=A.db.run
local total=#r.balls+r.remaining
r.status='lost';A.Engine.BeginEnding(r,false)
assert(#r.balls==total and r.remaining==0)
A.Open(false);A.frame.OnUpdate(A.frame,0.1)
assert(not A.frame.result:IsShown(),'result waits for drain')
local age=r.ending.age
A.Close();A.Engine.Step(A.db,0.05);assert(r.ending.age==age)
A.Engine.Init(A.db);assert(r.paused and r.ending.age==age,'reload preserves cinematic')
A.Open(false)
for i=1,40 do local update=rawget(A.frame,'OnUpdate');if update then update(A.frame,0.1) end end
assert(#r.balls==0 and r.ending.done and A.frame.result:IsShown())
assert(not rawget(A.frame,'OnUpdate'),'finished popup is idle')
A.frame.result.action.OnClick()
r=A.db.run;assert(r.status=='playing' and not r.paused and not A.frame.result:IsShown())
r.balls={};r.remaining=0
A.frame.OnUpdate(A.frame,0.02)
assert(r.status=='won' and r.ending.phase=='celebrate' and not A.frame.result:IsShown())
for i=1,30 do local update=rawget(A.frame,'OnUpdate');if update then update(A.frame,0.1) end end
assert(r.ending.done and A.frame.result:IsShown() and r.paused)
local level=r.level;local score=r.score
A.frame.result.action.OnClick()
assert(A.db.run.level==level+1 and A.db.run.score==score and not A.db.run.paused)
""")

# Registry is deliberately byte-identical; exercise both orders and late registration.
if (ROOT / 'RaynnaTowerDefense/SettingsRegistry.lua').exists():
    assert (ADDON / 'SettingsRegistry.lua').read_bytes() == (ROOT / 'RaynnaTowerDefense/SettingsRegistry.lua').read_bytes()
for first in ('runeballs', 'towerdefense'):
    check = LuaRuntime(unpack_returned_tuples=True)
    check.execute((ROOT / 'tests/wow_mock.lua').read_text())
    check.execute('COUNT=0; local orig=Settings.RegisterAddOnCategory; Settings.RegisterAddOnCategory=function(...) COUNT=COUNT+1;orig(...) end')
    for name in (first, 'towerdefense' if first == 'runeballs' else 'runeballs'):
        check.execute((ADDON / 'SettingsRegistry.lua').read_text())
        check.execute('RaynnaModsSettingsRegistry:Register(..., ..., function() return function() end end)', name, name)
    check.execute("assert(COUNT==1 and RaynnaModsSettingsRegistry.pages.runeballs and RaynnaModsSettingsRegistry.pages.towerdefense)")
print('PASS: Lua 5.1 gap physics, combos, specials, 60 unique routes, migration, faction UI, native sound/mute/fallback, settings and flight lifecycle')


# Edge entrances, paired lanes, bridges and dual-round end states.
lua=runtime()
lua.execute("""
local E=A.Engine
for level=1,60 do
 local p=E.Path(level);local x,y=E.Point(level,0)
 assert(math.min(math.abs(x+28),math.abs(x-788),math.abs(y),math.abs(y-500))<0.01,'edge entrance')
end
local db={};E.Init(db)
local r=E.NewRun(db,6);r.paused=false
assert(r.other and #E.Crossings(6)>0 and E.Remaining(r)>44)
local h,h2=r.head,r.other.head
E.Step(db,0.05);assert(r.head>h and r.other.head>h2,'simultaneous chains')
local cross=E.Crossings(6)[1]
assert(E.Hidden(r.other,cross.under) and not E.Hidden(r,cross.over),'bridge occludes lower lane only')
r.balls={};r.remaining=0
E.Step(db,0.05);assert(r.cleared and r.status=='playing','one clear lane is not a win')
r.other.balls={};r.other.remaining=0
E.Step(db,0.05);assert(r.status=='won' and db.level==7)
for i=1,80 do E.Step(db,0.05) end
assert(r.ending.done)
for _,secondary in ipairs({false,true}) do
 r=E.NewRun(db,6);r.paused=false
 local lane=secondary and r.other or r
 lane.balls={{color=1,d=E.Path(E.Route(lane)).length-0.01}};lane.remaining=0
 E.Step(db,0.05);assert(r.status=='lost' and r.other.status=='lost')
 r.paused=true;local age=r.ending.age
 E.Step(db,0.05);assert(r.paused and r.ending.age==age,'paused dual cinematic stays paused')
 E.Init(db);assert(r.paused and r.other.paused)
 r.paused=false
 for i=1,200 do E.Step(db,0.05) end
 assert(r.ending.done and #r.balls==0 and #r.other.balls==0,'both lanes drain before result')
end
""")
print('PASS: edge entrances, dual chains, bridges, both loss lanes, win and paused cinematic reload')

lua=runtime()
lua.execute("""
local E=A.Engine
for level=6,58,4 do
 local a,b=E.Path(level),E.Path(level+1000)
 assert(math.abs(a.length-b.length)<0.00001,'identical lane lengths')
 local ax,ay=E.Point(level,a.length);local bx,by=E.Point(level+1000,b.length)
 assert((ax-bx)^2+(ay-by)^2>350^2,'widely separated exits')
 local crosses=E.Crossings(level)
 assert(#crosses==2,'two clear crossings with long exposed runs')
 for _,c in ipairs(crosses) do
  assert(math.abs(math.sin(c.angle-c.underAngle))>0.97,'near-right-angle intersection')
  assert(E.Hidden({level=level,route=level+1000},c.under-65))
  assert(E.Hidden({level=level,route=level+1000},c.under+65))
  assert(not E.Hidden({level=level,route=level+1000},c.under+115))
 end
end
local db={};E.Init(db)
local r=E.NewRun(db,6);r.paused=false
local c=E.Crossings(6)[1]
r.balls={{color=1,d=200}};r.remaining=0
r.other.balls={{color=2,d=c.under}};r.other.remaining=0
local x,y=E.Point(E.Route(r.other),c.under)
r.shot={x=x,y=y,vx=1,vy=1,color=1,kind='Bomb'}
E.Step(db,0.01)
assert(r.shot and #r.other.balls==1,'shot cannot hit a ball in the covered tunnel')
r=E.NewRun(db,1);r.paused=false;r.remaining=0;r.balls={{color=1,d=14}}
x,y=E.Point(1,14);r.shot={x=x,y=y,vx=1,vy=1,color=2}
E.Step(db,0.01);assert(#r.balls==1 and r.balls[1].color==1,'edge entrance protects emerging balls')
""")
print('PASS: clear perpendicular crossings and long tunnel hit protection')


lua=runtime()
lua.execute("""
local before=#Frames
local label=A.GoldLabel(UIParent,'',0,0,28,119)
assert(#Frames==before+1 and not label.goldBands,'single score glyph layer')
label.SetFont=function(self,path,size,flags) self.measuredSize=size end
label.GetUnboundedStringWidth=function(self) return #self:GetText()*self.measuredSize*0.65 end
A.FitText(label,'99,999,999',119,28,10)
assert(label:GetText()=='99,999,999' and label:GetHeight()>28)
assert(label:GetUnboundedStringWidth()<=113 and label.fontSize<28)
local button=A.Button(UIParent,'SETTINGS',0,0,150,57,'SettingsIcon',function() end)
assert(button.label:GetText()=='SETTINGS' and button.label:GetHeight()>0)
A.db={options={}}
PlaySoundFile=function() error('ordinary hit must not use a spell file') end
PlaySound=function(id) HIT_SOUND=id end
A.GameSound('Hit');assert(HIT_SOUND==856)
""")
print('PASS: single-layer scores, bounded text fitting and subtle native hit sound')

lua=runtime()
lua.execute("""
local E=A.Engine
for level=6,58,4 do
 for _,route in ipairs({level,level+1000}) do
  local path=E.Path(route)
  local x,y=E.Point(route,path.length)
  for _,other in ipairs({level,level+1000}) do
   local limit=E.Path(other).length-(other==route and 90 or 0)
   for d=0,limit,4 do
    local px,py=E.Point(other,d)
    assert((x-px)^2+((y-py)*0.86)^2>47^2,'compact exit clears nearby roads')
   end
  end
 end
end
""")
print('PASS: compact exit clearance from neighbouring roads on all dual rounds')

lua=runtime()
lua.execute("""
local E=A.Engine
for level=1,60 do
 for _,route in ipairs((level>=6 and level%4==2) and {level,level+1000} or {level}) do
  local path=E.Path(route)
  for d=0,path.length,4 do
   local x,y=E.Point(route,d)
   assert((x-380)^2+((y-250)*0.86)^2>99.5^2,'launcher clearance on every route')
  end
 end
end
""")
print('PASS: launcher and next-ammo clearance across 60 rounds')

lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs')
A.events.OnEvent(A.events,'PLAYER_LOGIN')
local r=A.Engine.NewRun(A.db,6);r.paused=false
A.Open(false);r.paused=false
local hole=A.Visuals.holes[1]
hole.entry.SetAlpha=function(self,value) self.alphaValue=value end
A.Visuals.Tick(0.05,r);A.Draw()
local alpha=hole.entry.alphaValue
assert(hole.swirl[1]:IsShown() and A.Visuals.holes[2].exit:IsShown())
A.Visuals.Tick(0.4,r);A.Draw();assert(hole.entry.alphaValue~=alpha,'entrance pulse advances')
A.db.options.reducedMotion=true;A.Draw()
assert(hole.entry:IsShown() and hole.exit:IsShown() and not hole.swirl[1]:IsShown())
A.Close();assert(not hole.entry:IsShown() and not hole.exit:IsShown())
""")
print('PASS: animated portal interior, entrance pulse, reduced motion and close cleanup')
