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
            f.CreateFontString=function(self) return create('FontString',nil,self) end
            f.SetBackdrop=function(self,data) self.backdrop=data end
            f.CreateTexture=function(self,name,layer)
                local t=create('Texture',name,self);t.SetVertexColor=function(self,...) self.tint={...} end;t.drawLayer=layer;t.SetBlendMode=function(self,value) self.blendMode=value end;t.SetAlpha=function(self,v) self.alpha=v end;return t
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
assert(r.paused and #r.balls==12 and r.remaining==42)
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
assert(r.balls[1].d==400 and r.balls[3].d==300,'removal does not teleport survivors')
E.Step(db,0.05)
assert(r.balls[1].d<400 and r.balls[3].d>300 and #r.balls==3,'matching front retracts while rear advances')
for i=1,30 do E.Step(db,0.05) end
assert(r.status=='won' and r.score==900 and db.level==2 and db.best==900,'contact triggers delayed x2 combo')

-- Unmatched leading section waits; rear catches it and supplies forward motion.
r=E.NewRun(db,1);r.remaining=0;r.paused=false;r.balls={{color=1,d=400},{color=2,d=350}}
E.Step(db,0.05);assert(r.balls[1].d==400 and r.balls[2].d>350)
for i=1,40 do E.Step(db,0.05) end
assert(r.balls[1].d>400 and math.abs(r.balls[1].d-r.balls[2].d-25)<0.001,'rear pushes front after contact')
assert(E.Speed(r)==40 and E.Speed({level=5})==42 and E.Speed({level=10})==44.5,'moderate opening and linear level ramp')
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
local expected=0;local bx,by=E.Point(1,r.balls[7].d)
for _,ball in ipairs(r.balls) do local x,y=E.Point(1,ball.d);if ball.d>=24 and not E.Hidden(r,ball.d) and (x-bx)^2+((y-by)*.86)^2<=E.BOMB_RADIUS^2 then expected=expected+1 end end
E.Special(r,7,'Bomb');assert(#r.balls==before-expected and r.burst.kind=='Explosion')
r=E.NewRun(db,1);r.paused=false;r.remaining=0;E.Special(r,math.min(7,#r.balls),'Frost');assert(r.slow==4)
local tail=r.balls[#r.balls].d
E.Step(db,0.05);assert(r.balls[#r.balls].d-tail<1,'frost slows rear driver')
E.Special(r,#r.balls,'Rewind');assert(r.reverse==2.5)
tail=r.balls[#r.balls].d
E.Step(db,0.05);assert(r.balls[#r.balls].d<tail,'rewind moves backwards, including behind entrance')
local random=math.random
for _,case in ipairs({{roll=3,kind=1,expected='Bomb'},{roll=4},{roll=1,kind=3,expected='Rewind'},{roll=100},{roll=2,kind=2,expected='Frost'}}) do
 math.random=function(n)
  if n==100 then return case.roll end
  if n==10 then return case.kind or 1 end
  return 1
 end
 r.shot=nil;r.cooldown=0;assert(E.Fire(r,10,10))
 assert(r.nextKind==case.expected,'independent chance and random ability type')
end
math.random=random
r.nextKind='Bomb';r.loadedKind=nil;E.Swap(r);assert(r.loadedKind=='Bomb' and not r.nextKind)

-- Saved v1 run migration preserves score/preferences and gains path distances.
local old={best=2000,options={scale=1.1},run={version=1,head=400,balls={{color=1},{color=3}},score=1234}}
E.Init(old);assert(old.run.version==2 and old.run.balls[2].d==375 and old.run.score==1234 and old.best==2000 and old.options.scale==1.1)
local position=old.run.balls[2].d;E.Init(old);assert(old.run.balls[2].d==position,'migration is idempotent')

-- Distinct routes, bounded geometry and increasing complexity.
local seen={}
for level=1,100 do
    local path=E.Path(level)
    assert(path.length>1000)
    local signature=string.format('%.4f:%.4f:%.4f',path.length,path[1].x,path[1].y)
    assert(not seen[signature],'every round has a different route');seen[signature]=true
    for _,p in ipairs(path) do assert(p.x>=-28.01 and p.x<=788.01 and p.y>=-0.01 and p.y<=500.01,'route stays on board') end
end
assert(E.Path(99).length>E.Path(1).length)
-- Unattended runs terminate; simulation keeps all neighbours ordered.
for level=1,8 do
    r=E.NewRun(db,level);r.paused=false
    for step=1,6000 do
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
FLYING=false;A.CheckFlight();assert(A.frame:IsShown() and A.db.run.paused,'default leaves automatic game open and paused')
A.Close();A.db.options.closeOnLanding=true
FLYING=true;A.CheckFlight();FLYING=false;A.CheckFlight()
assert(not A.frame:IsShown() and A.db.run.paused,'explicit close on landing closes automatic game')
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
print('PASS: Lua 5.1 gap physics, combos, specials, 100 unique routes, migration, faction UI, native sound/mute/fallback, settings and flight lifecycle')


# Edge entrances, paired lanes, bridges and dual-round end states.
lua=runtime()
lua.execute("""
local E=A.Engine
for level=1,100 do
 local p=E.Path(level);local x,y=E.Point(level,0)
 assert(math.min(math.abs(x+28),math.abs(x-788),math.abs(y),math.abs(y-500))<0.01,'edge entrance')
end
local db={};E.Init(db)
local r=E.NewRun(db,30);r.paused=false
assert(r.other and #E.Crossings(30)>0 and E.Remaining(r)>44)
local h,h2=r.head,r.other.head
E.Step(db,0.05);assert(r.head>h and r.other.head>h2,'simultaneous chains')
local cross=E.Crossings(30)[1]
assert(E.Hidden(r.other,cross.under) and not E.Hidden(r,cross.over),'bridge occludes lower lane only')
r.balls={};r.remaining=0
E.Step(db,0.05);assert(r.cleared and r.status=='playing','one clear lane is not a win')
r.other.balls={};r.other.remaining=0
E.Step(db,0.05);assert(r.status=='won' and db.level==31)
for i=1,80 do E.Step(db,0.05) end
assert(r.ending.done)
for _,secondary in ipairs({false,true}) do
 r=E.NewRun(db,30);r.paused=false
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
for _,level in ipairs({30,40,50,60,65,70,75,80,85,90,95,100}) do
 local a,b=E.Path(level),E.Path(level+1000)
 assert(math.abs(a.length-b.length)<0.00001,'identical lane lengths')
 local ax,ay=E.Point(level,a.length);local bx,by=E.Point(level+1000,b.length)
 assert((ax-bx)^2+(ay-by)^2>350^2,'widely separated exits')
 local crosses=E.Crossings(level)
 assert(#crosses==2,'two clear crossings with long exposed runs')
 for _,c in ipairs(crosses) do
  assert(math.abs(math.sin(c.angle-c.underAngle))>0.97,'near-right-angle intersection')
  assert(E.Hidden({level=level,route=level+1000},c.under-E.TunnelHalf(c)*.8))
  assert(E.Hidden({level=level,route=level+1000},c.under+E.TunnelHalf(c)*.8))
  assert(not E.Hidden({level=level,route=level+1000},c.under+E.TunnelHalf(c)+25))
 end
end
local db={};E.Init(db)
local r=E.NewRun(db,30);r.paused=false
local c=E.Crossings(30)[1]
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
for _,level in ipairs({30,40,50,60,65,70,75,80,85,90,95,100}) do
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
for level=1,100 do
 for _,route in ipairs(E.IsDualLevel(level) and {level,level+1000} or {level}) do
  local path=E.Path(route)
  for d=0,path.length,4 do
   local x,y=E.Point(route,d)
   assert((x-380)^2+((y-250)*0.86)^2>99.5^2,'launcher clearance on every route')
  end
 end
end
""")
print('PASS: launcher and next-ammo clearance across 100 rounds')

lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs')
A.events.OnEvent(A.events,'PLAYER_LOGIN')
local r=A.Engine.NewRun(A.db,30);r.paused=false
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


lua=runtime()
lua.execute("""
local E=A.Engine
local db={};E.Init(db)
local previous=0
for level=1,100 do
 local r=E.NewRun(db,level)
 assert((r.other~=nil)==E.IsDualLevel(level))
 if level<30 then assert(not r.other) end
 local base=E.Speed({level=level});assert(base>previous);previous=base
 if r.other then assert(E.Speed(r)==base/2 and E.Speed(r.other)==base/2 and #r.balls<=12) end
 assert(E.Remaining(r)==E.MarbleCount(level))
end
local r=E.NewRun(db,100);r.paused=false;r.balls={};r.remaining=0;r.other.balls={};r.other.remaining=0
E.Step(db,0.05);assert(r.status=='won' and r.campaignComplete and db.level==100)
assert(E.NewRun(db,101).level==100)
-- Earlier saved dual rounds become a manageable single lane without losing score or marbles.
r=E.NewRun(db,30);r.level=6;r.other.level=6;r.score=500;r.other.score=100
local count=E.Remaining(r)
E.Init(db);assert(not r.other and not r.dual and r.score==600 and E.Remaining(r)==count and r.paused)
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs')
A.events.OnEvent(A.events,'PLAYER_LOGIN')
r=E.NewRun(A.db,1);r.balls={{color=1,d=14}};r.head=14;r.remaining=1
A.Draw()
local entry,emerging
for _,f in ipairs(Frames) do
 if rawget(f,'texture')==A.media..'Entry.tga' and f:IsShown() then entry=f end
 if rawget(f,'texture')==A.media..'Ball1.tga' and f:IsShown() and f.alpha==0.5 then emerging=f end
end
assert(entry and emerging and entry.parent==emerging.parent)
assert(entry.drawLayer=='BORDER' and emerging.drawLayer=='ARTWORK','marble emerges visibly inside entrance light')
assert(A.frame.closeButton:GetScript('OnClick')==A.Close and A.frame.closeButton:GetWidth()==30)
""")
print('PASS: 100-level progression, delayed dual lanes, campaign ending, save migration, entrance reveal and icon close button')

lua.execute("""
local r=A.Engine.NewRun(A.db,100);r.paused=false
r.balls={};r.remaining=0;r.other.balls={};r.other.remaining=0
for i=1,100 do A.Engine.Step(A.db,0.05) end
A.Draw()
assert(A.frame.result.action.label:GetText()=='PLAY AGAIN')
A.frame.result.action.OnClick()
assert(A.db.run.level==1 and A.db.run.score==0,'campaign replay never creates level 101')
""")

# Regression coverage for gap insertion, contact matching and rewind limits.
lua.execute("""
local E=A.Engine
local db={};E.Init(db)
local function run(balls)
 local r=E.NewRun(db,1);r.paused=false;r.remaining=0;r.balls=balls;return r
end
local r=run({{color=1,d=400},{color=1,d=350}})
assert(E.Insert(r,2,1,375)==1 and #r.balls==0,'shot fills a one-ball gap and matches both ends')
r=run({{color=1,d=400},{color=1,d=325}})
E.Insert(r,2,1,375)
for i=1,20 do E.Step(db,.02) end
assert(#r.balls==0 and r.score==300,'unmarked gap contact still matches three')
r=run({{color=2,d=600},{color=1,d=300}})
E.Insert(r,2,3,575)
assert(r.balls[2].d==575 and r.balls[1].d==600,'gap insertion stays at impact boundary')
r=run({{color=2,d=400},{color=1,d=375},{color=1,d=350},{color=3,d=325}})
E.Insert(r,3,1)
assert(r.balls[1].d==400 and r.balls[2].d==325,'successful shot cannot push survivors forward')
r=run({{color=1,d=50},{color=2,d=25},{color=3,d=0}});r.reverse=2.5
for i=1,2 do E.Step(db,.05) end
assert(r.balls[1].d==38 and r.reverse==0 and not E.Hidden(r,38),'rewind stops with visible leading marble')
E.Step(db,.05);assert(r.balls[1].d>38,'chain resumes forward after rewind limit')
for trial=1,200 do
 r=run({{color=1,d=400},{color=2,d=375},{color=3,d=350},{color=4,d=325}})
 local index=math.random(1,5);E.Insert(r,index,5)
 for i=1,#r.balls-1 do assert(r.balls[i].d-r.balls[i+1].d>=24.999) end
 assert(r.head<=425,'one insertion advances front by at most one marble')
end
""")
print('PASS: gap shot matching, local insertion, no match shove, capped rewind')

lua.execute("""
local E=A.Engine;local db={};E.Init(db)
local r=E.NewRun(db,1);r.remaining=0;r.paused=false
r.balls={{color=1,d=400},{color=1,d=350.05}}
E.Insert(r,2,1,375)
for i=1,3 do E.Step(db,.001) end
assert(#r.balls==0,'subpixel gap cannot become touching without checking match')
A.Open()
assert(A.board.combo.parent==A.board.effectLayer and A.board.shot.parent==A.board.effectLayer,'text and projectiles render above road frames')
""")

lua.execute("""
local E=A.Engine;local db={};E.Init(db)
for level=1,100 do
 local r=E.NewRun(db,level);assert(r.colorCount==6)
 if r.other then assert(r.other.colorCount==6) end
end
local r=E.NewRun(db,1);r.colorCount=3;local score=r.score;E.Init(db)
assert(r.colorCount==6 and r.score==score,'saved runs gain sixth colour without resetting')
r.remaining=0;r.balls={{color=6,d=100}};r.paused=false;r.cooldown=0
E.Fire(r,100,100);assert(r.next==6,'ammo picker includes pearl and excludes exhausted colours')
""")
assert((ADDON/'Media/Ball6.tga').exists())

# Render intervals smaller than a physics tick still advance visible positions.
lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN');A.Open();A.frame.play.OnClick()
local r=A.db.run;r.remaining=0;r.balls={{color=1,d=200}};r.head=200
local start=r.head
for i=1,24 do
 local previous=r.head
 A.frame.OnUpdate(A.frame,1/240)
 assert(r.head>previous,'every high-refresh frame advances the chain')
end
assert(math.abs(r.head-start-A.Engine.Speed(r)*.1)<.000001,'render subdivision retains original speed')
local launcher=A.board.launcher.pointArgs
local loaded=A.board.loaded.pointArgs
assert(math.abs(launcher[4]-loaded[4]-5)<.001,'launcher socket aligns with loaded ball')
local roads=0
for _,f in ipairs(Frames) do
 if type(f.texture)=='string' and f.texture:match('Road%d+%.tga$') then roads=roads+1 end
end
assert(roads==1,'single lane uses one continuous road texture')
""")
for level in range(1,101):
    assert((ADDON/f'Media/Road{level}.tga').exists())
print('PASS: high-refresh movement, unchanged speed, launcher alignment and continuous roads')

lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN')
local saved=A.db;local campaign=saved.run;local best=saved.best;local level=saved.level
SlashCmdList.RAYNNARUNEBALLS('demo 100');assert(A.db==saved,'non-developer cannot jump rounds')
function UnitName() return 'Its Raynna' end
for n=1,100 do
 SlashCmdList.RAYNNARUNEBALLS('demo '..n)
 assert(A.db~=saved and A.db.run.level==n and not A.db.run.paused)
 assert((A.db.run.other~=nil)==A.Engine.IsDualLevel(n))
 assert(RaynnaRuneballsDB==saved and saved.run==campaign and saved.best==best and saved.level==level)
end
local demo=A.db
for _,v in ipairs({'0','101','2.5','nope',''}) do SlashCmdList.RAYNNARUNEBALLS('demo '..v);assert(A.db==demo) end
A.db.best=999999;A.db.level=100
SlashCmdList.RAYNNARUNEBALLS('demo off')
assert(A.db==saved and A.db.run==campaign and saved.best==best and saved.level==level and campaign.paused)
function UnitName() return 'Its-Raynna' end
SlashCmdList.RAYNNARUNEBALLS('demo 42');assert(A.db.run.level==42)
SlashCmdList.RAYNNARUNEBALLS('demo off')
""")
print('PASS: developer demo all 100 rounds, name restriction, validation and campaign isolation')

lua.execute("""
for _,name in ipairs({'Its Raynna','Its-Raynna','ITS RAYNNA','Its'..string.char(194,160)..'Raynna'}) do
 UnitName=function() return name end
 SlashCmdList.RAYNNARUNEBALLS('demo 7');assert(A.db.run.level==7)
 SlashCmdList.RAYNNARUNEBALLS('demo off')
end
UnitName=function() return 'Its','Raynna' end
SlashCmdList.RAYNNARUNEBALLS('demo 8');assert(A.db.run.level==8)
SlashCmdList.RAYNNARUNEBALLS('demo off')
UnitName=function() return 'Its' end
CharacterFrameTitleText=CreateFrame('FontString');CharacterFrameTitleText:SetText('Its Raynna')
SlashCmdList.RAYNNARUNEBALLS('demo 9');assert(A.db.run.level==9)
SlashCmdList.RAYNNARUNEBALLS('demo off')
CharacterFrameTitleText=nil
local saved=A.db
UnitName=function() return 'Someone Else' end
SlashCmdList.RAYNNARUNEBALLS('demo 10');assert(A.db==saved)
""")

lua.execute("""
local E=A.Engine
local signatures={}
for level=1,100 do
 local cells={}
 for _,route in ipairs(E.IsDualLevel(level) and {level,level+1000} or {level}) do
  for d=0,E.Path(route).length,5 do
   local x,y=E.Point(route,d);cells[math.floor(x/20)..':'..math.floor(y/20)]=true
  end
 end
 local keys={};for k in pairs(cells) do keys[#keys+1]=k end;table.sort(keys)
 local signature=table.concat(keys,',');assert(not signatures[signature],'rounds must differ at visible map scale');signatures[signature]=level
 if E.IsDualLevel(level) then
  for _,cross in ipairs(E.Crossings(level)) do
   local half=E.TunnelHalf(cross)
   assert(half<=64 and half>=0)
   assert(E.Path(level+1000).length-cross.under-half>=180)
  end
  for d=E.Path(level+1000).length-179,E.Path(level+1000).length,3 do
   assert(not E.Hidden({level=level,route=level+1000},d),'exit approach stays shootable')
  end
 end
end
local db={};E.Init(db);local r=E.NewRun(db,100)
r.layoutVersion=nil;r.other.layoutVersion=nil;r.head=9999;r.balls={{color=1,d=9999},{color=2,d=9974}}
r.score=1234;E.Init(db)
assert(r.score==1234 and #r.balls==2 and r.balls[1].d-r.balls[2].d==25 and r.paused)
assert(r.head<=E.Path(100).length-180+0.000001 and r.layoutVersion==3)
""")
print('PASS: 100 visible route signatures, capped tunnels, exposed exits and saved-layout migration')

lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN')
local E=A.Engine
for _,level in ipairs({15,30,100}) do
 local r=E.NewRun(A.db,level);r.paused=false;r.remaining=0;r.score=1234
 local lane=r.other or r
 lane.remaining=0;lane.balls={{color=1,d=E.Path(E.Route(lane)).length-.001}}
 E.Step(A.db,.05)
 assert(r.status=='lost' and A.db.level==1 and r.level==level and r.score==1234)
 r.ending.done=true
 A.frame.play:GetScript('OnClick')()
 assert(A.db.run.level==1 and A.db.run.score==0)
end
local r=E.NewRun(A.db,1);r.paused=false;r.remaining=0;r.balls={{color=1,d=400},{color=1,d=300}}
E.Step(A.db,.05);assert(math.abs(r.balls[1].d-395.5)<.001,'visible 90px/sec combo retraction')
r.burst={age=0,combo=2};E.Animate(r,.7);assert(r.burst);E.Animate(r,.21);assert(not r.burst)
r.status='lost';r.level=42;r.score=12345
GetChannelList=function() return 1,'General',false end
local sent={};SendChatMessage=function(...) sent[#sent+1]={...} end
A.OpenShare();assert(#sent==0)
local p=A.frame.share
assert(p.preview:GetText():find('42/100') and p.preview:GetText():find('12,345'))
p.send:GetScript('OnClick')();assert(sent[1][2]=='SAY')
A.OpenShare();for i=1,7 do p.choose:GetScript('OnClick')() end
p.send:GetScript('OnClick')();assert(#sent==1,'empty whisper recipient rejected')
p.target:SetText('A Friend');p.send:GetScript('OnClick')();assert(sent[2][2]=='WHISPER' and sent[2][4]=='A Friend')
p.choose:GetScript('OnClick')();p.send:GetScript('OnClick')();assert(sent[3][2]=='CHANNEL' and sent[3][4]==1)
A.db.demo=true;assert(A.ShareMessage(r):find('[Demo]',1,true)==1)
""")
print('PASS: loss restarts round one, slower combos, result preview and explicit chat sharing')

lua.execute("""
local E=A.Engine
A.db.demo=nil
for _,kind in ipairs({'Bomb','Frost','Rewind'}) do
 local r=E.NewRun(A.db,30);r.paused=false
 E.Special(r.other,3,kind)
 assert(r.other.specialImpact.kind==kind and r.other.specialImpact.age==0)
 A.Draw()
 local fx=A.Visuals.specialBursts[2]
 assert(fx.core:IsShown() and fx.particles[1]:IsShown())
 assert(fx.core.parent==A.board.effectLayer)
 E.Animate(r.other,.4);A.Draw();assert(fx.core.alpha>0 and fx.core.alpha<.65)
 A.db.options.reducedMotion=true;A.Draw()
 assert(fx.core:IsShown() and not fx.particles[1]:IsShown())
 A.db.options.reducedMotion=false
 E.Animate(r.other,.71);A.Draw();assert(not r.other.specialImpact and not fx.core:IsShown())
end
local r=A.db.run;E.Special(r,2,'Bomb');A.Draw();A.Close()
for _,fx in ipairs(A.Visuals.specialBursts) do
 assert(not fx.core:IsShown());for _,p in ipairs(fx.particles) do assert(not p:IsShown()) end
end
""")
print('PASS: distinct special impacts, dual-lane drawing, lifetime, reduced motion and close cleanup')

lua.execute("""
local E=A.Engine;local db={};E.Init(db);local r=E.NewRun(db,1);r.paused=false
local random=math.random;local count=0
for roll=1,100 do
 math.random=function(n) return n==100 and roll or 1 end
 r.shot=nil;r.cooldown=0;E.Fire(r,100,100)
 if r.nextKind then count=count+1 end
end
math.random=random
assert(count==3,'exactly 3 of 100 equally likely rolls award any special')
""")

lua.execute("""
local E=A.Engine
local previousGain=0
for level=1,100 do
 local speed=E.Speed({level=level})
 assert(E.Speed({level=level,dual=true})==speed/2)
 if level>1 then
  local gain=speed-E.Speed({level=level-1})
  assert(gain==0.5,'each round adds exactly 0.5');previousGain=gain
 end
end
assert(math.abs(E.Speed({level=100})-89.5)<.000001)
""")

lua.execute("""
local E=A.Engine;local db={};E.Init(db)
for color=1,6 do
 for _,kind in ipairs({'Bomb','Frost','Rewind'}) do
  local r=E.NewRun(db,1);r.remaining=0;r.balls={{color=color,d=300}}
  E.Insert(r,1,color,325,kind)
  assert(#r.balls==2 and r.balls[1].kind==kind and not r.specialImpact,'two matching balls cannot activate')
  E.Insert(r,1,color,350)
  assert(#r.balls==0 and r.specialImpact.kind==kind,'three matching balls activate any coloured special')
 end
end
local r=E.NewRun(db,1);r.remaining=0;r.balls={}
for i=1,11 do r.balls[i]={color=i%2+2,d=600-i*25} end
r.balls[5].color=1;r.balls[6].color=1;r.balls[7].color=1;r.balls[6].kind='Bomb';r.balls[4].kind='Frost'
local expected=0;local bx,by=E.Point(1,r.balls[6].d)
for _,ball in ipairs(r.balls) do local x,y=E.Point(1,ball.d);if (x-bx)^2+((y-by)*.86)^2<=E.BOMB_RADIUS^2 then expected=expected+1 end end
assert(E.Match(r,6)==1 and #r.balls==11-expected and r.score==expected*100)
assert(r.slow==4,'bomb blast activates a caught Frost ball')
r=E.NewRun(db,1);r.remaining=0;r.paused=false;r.balls={{color=2,d=350}}
local x,y=E.Point(1,350);r.shot={x=x-35,y=y,vx=1040,vy=0,color=1,kind='Rewind'}
E.Step(db,.05)
assert(#r.balls==2 and not r.specialImpact and (r.balls[1].kind=='Rewind' or r.balls[2].kind=='Rewind'),'unmatched special projectile inserts instead of triggering')
local original=math.random
math.random=function(n) return n==100 and 3 or 1 end
r=E.NewRun(db,1);assert(r.balls[1].kind=='Bomb')
r.balls={};r.remaining=1;r.paused=false;E.Step(db,.01)
assert(r.balls[1].kind=='Bomb','incoming tunnel ball can carry special')
local ball=r.balls[1];E.Init(db);assert(r.balls[1]==ball and ball.kind=='Bomb','reload retains coloured chain specials')
math.random=original
""")
for kind in ['Bomb','Frost','Rewind']:
 for color in range(1,7): assert((ADDON/f'Media/{kind}{color}.tga').exists())
print('PASS: all 18 coloured specials, match-only activation, incoming specials and three-neighbour bomb blast')

lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN')
local E=A.Engine;local r=E.NewRun(A.db,30);r.paused=false;r.remaining=0;r.other.remaining=0
r.balls={{color=1,d=300,kind='Bomb'},{color=2,d=275,kind='Frost'},{color=3,d=250,kind='Rewind'}}
local cross=E.Crossings(30)[1]
r.other.balls={{color=4,d=cross.under,kind='Bomb'}}
A.Draw();assert(#A.Visuals.chainAuras==3,'hidden tunnel special has no leaking aura')
local aura=A.Visuals.chainAuras[1];assert(aura.glow:IsShown() and aura.sparks[1]:IsShown())
local alpha=aura.ring.alpha;A.Visuals.Tick(.1,r);A.Draw();assert(alpha~=aura.ring.alpha,'chain special pulses')
A.db.options.reducedMotion=true;A.Draw();alpha=aura.ring.alpha
A.Visuals.Tick(.1,r);A.Draw();assert(alpha==aura.ring.alpha and not aura.sparks[1]:IsShown(),'reduced motion uses steady glow')
r.balls={};A.Draw();assert(not aura.glow:IsShown() and not aura.ring:IsShown(),'removed specials release visuals')
r.balls={{color=1,d=300,kind='Bomb'}};A.Draw();A.Close();assert(not aura.glow:IsShown())
""")
print('PASS: chain ability auras pulse, respect tunnels/reduced motion and clean up')

lua.execute("""
local E=A.Engine
local r=E.NewRun(A.db,1);r.paused=false;r.remaining=0
r.balls={{color=1,d=400},{color=2,d=375}}
A.db.options.reducedMotion=false
local fx,fy=E.Point(1,400);local hx,hy=E.Point(1,390)
E.Insert(r,2,3,nil,'Frost',hx+8,hy+12)
assert(r.balls[1].d==425 and r.balls[2].d==400,'physics resolves insertion immediately')
local x,y=A.BallPosition(r,r.balls[1]);assert(math.abs(x-fx)<.001 and math.abs(y-fy)<.001,'pushed neighbour starts from previous visual position')
x,y=A.BallPosition(r,r.balls[2]);assert(math.abs(x-hx-8)<.001 and math.abs(y-hy-12)<.001,'inserted ball starts at shot contact')
E.Animate(r,.08)
local nx,ny=E.Point(1,425);x,y=A.BallPosition(r,r.balls[1]);assert((x-nx)^2+(y-ny)^2<(fx-nx)^2+(fy-ny)^2)
E.Animate(r,.09);assert(not r.balls[1].slideAge and not r.balls[2].slideAge)
for color=1,6 do
 for _,kind in ipairs({'Bomb','Frost','Rewind'}) do
  r.balls={{color=color,d=300,kind=kind}};A.Draw()
  local tint=A.Visuals.chainAuras[1].ring.tint
  for channel=1,3 do assert(tint[channel]==A.colors[color][channel],'aura uses matching marble colour') end
  E.Special(r,1,kind);assert(r.specialImpact.color==color)
  A.Draw();tint=A.Visuals.specialBursts[1].core.tint
  if kind=='Bomb' then assert(tint[1]==1 and tint[3]==1,'detonation is fire while idle aura retains ball colour')
  else for channel=1,3 do assert(tint[channel]==A.colors[color][channel]) end end
 end
end
""")
print('PASS: matching-colour auras and impacts, eased insertion with immediate physics')

lua.execute("""
local r=A.Engine.NewRun(A.db,1);r.paused=false;r.loaded=5;r.loadedKind='Frost'
A.Draw();local light=A.Visuals.ammoLight
assert(light:IsShown() and light.texture==A.media..'SpecialLight.tga')
for i=1,3 do assert(light.tint[i]==A.colors[5][i]) end
r.loadedKind=nil;A.Draw();assert(not light:IsShown(),'ordinary loaded ball has no special light')
r.loadedKind='Bomb';A.Draw();A.Close();assert(not light:IsShown())
""")

lua.execute("""
local E=A.Engine;local db={};E.Init(db)
local function chain(balls)
 local r=E.NewRun(db,1);r.remaining=0;r.balls=balls;r.paused=false;return r
end
for color=1,6 do
 local r=chain({{color=color,d=350},{color=6,kind='Rainbow',d=325},{color=color,d=300}})
 assert(E.Match(r,2)==1 and #r.balls==0,'rainbow bridges any same-colour pair')
end
local r=chain({{color=1,d=350},{color=6,kind='Rainbow',d=325},{color=2,d=300}})
assert(E.Match(r,2)==0 and #r.balls==3,'rainbow does not mix different colours')
r=chain({{color=1,d=350},{color=6,kind='Rainbow',d=325},{color=1,d=250}})
assert(E.Match(r,2)==0,'wildcard respects gaps')
for i=1,100 do E.Step(db,.01) end
assert(#r.balls==0,'wildcard closes a matching gap and triggers the contact match')
r=chain({{color=1,d=400},{color=1,d=375},{color=6,kind='Rainbow',d=350},{color=2,d=325},{color=2,d=300},{color=2,d=275}})
assert(E.Match(r,3)==1 and #r.balls==0 and r.score==600,'wildcard clears both independently valid colour groups once')
local random=math.random
math.random=function(n) return n==100 and 3 or 4 end
assert(E.RollSpecial()=='Rainbow','fourth special within existing probability gate')
math.random=random
""")
assert((ADDON/'Media/Rainbow.tga').exists())
print('PASS: rainbow wildcard colours, mixed-colour rejection, gaps and shared rarity')

# Longer corridors must remain readable, with a visible gap around each exit.
lua=runtime()
lua.execute("""
local E=A.Engine
for level=1,100 do
 if not E.IsDualLevel(level) then
  local path=E.Path(level)
  assert(path.length>=2500,'single routes offer at least 2500 units of travel')
  local ex,ey=E.Point(level,path.length)
  for distance=0,path.length-100,8 do
   local x,y=E.Point(level,distance)
   assert((x-ex)^2+((y-ey)*0.86)^2>=39^2,'exit does not overlap earlier road')
   for other=distance+104,path.length,8 do
    local ox,oy=E.Point(level,other)
    assert((x-ox)^2+((y-oy)*0.86)^2>=32^2,'non-crossing corridors retain visible separation')
   end
  end
 end
end
local db={best=9876,options={sound=false},run={version=2,pathVersion=1,layoutVersion=2,level=2,head=9999,score=321,remaining=20,balls={{color=2,d=9999,slideAge=0.1},{color=4,d=9974}},shot={x=0,y=0},specialImpact={x=0,y=0}}}
E.Init(db)
local r=db.run
assert(r.layoutVersion==3 and r.paused and r.score==321 and db.best==9876 and db.options.sound==false)
assert(r.head<=E.Path(2).length-180+0.000001 and r.balls[1].d-r.balls[2].d==25)
assert(not r.shot and not r.specialImpact and not r.balls[1].slideAge)
local head=r.head;E.Init(db);assert(r.head==head,'route migration happens only once')
""")
print('PASS: longer single routes, separated corridors, portal clearance and v3 layout migration')

# Landing toggle defaults, UI refresh, callbacks and saved choices agree.
landing=runtime()
landing.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs')
A.events.OnEvent(A.events,'PLAYER_LOGIN')
local page=RaynnaModsSettingsRegistry.pages.runeballs
local checks={}
for _,f in ipairs(Frames) do if f.parent==page.frame and f.kind=='CheckButton' then checks[#checks+1]=f end end
local toggle=checks[2]
toggle.SetChecked=function(self,value) self.checked=value end
page.refresh();assert(toggle.checked==false,'unset preference displays off')
for _,value in ipairs({true,false}) do
 toggle.GetChecked=function() return value end
 toggle.OnClick(toggle);assert(A.db.options.closeOnLanding==value)
 A.Engine.Init(A.db);page.refresh();assert(toggle.checked==value,'explicit choice survives initialization and refresh')
 A.Close();FLYING=true;A.CheckFlight();A.frame.play.OnClick();FLYING=false;A.CheckFlight()
 assert(A.db.run.paused and A.frame:IsShown()==not value,'landing follows selected preference')
end
""")
print('PASS: close-after-flight defaults off, settings callbacks and saved preferences')

# New specials, protected tunnels, timer persistence and reaction chains.
new=runtime()
new.execute("""
local E=A.Engine;local db={};E.Init(db)
local kinds={'Lightning','Paint','Stasis','Magnet','Treasure','Ward'}
local function fresh(level)
 local r=E.NewRun(db,level or 1);r.paused=false;r.remaining=0;r.balls={};return r
end
for _,kind in ipairs(kinds) do
 for color=1,6 do
  local r=fresh();r.balls={{color=color,d=400,kind=kind},{color=color,d=375}}
  assert(E.Match(r,1)==0 and not r.specialImpact,'two alone never activate')
  r.balls[3]={color=color,d=350};assert(E.Match(r,1)==1 and r.specialImpact.kind==kind)
 end
end
local random=math.random;local counts={}
for roll=1,100 do for choice=1,10 do
 math.random=function(n) return n==100 and roll or choice end
 local kind=E.RollSpecial();if kind then counts[kind]=(counts[kind] or 0)+1 end
end end
math.random=random
local total=0;for _,count in pairs(counts) do assert(count==3);total=total+count end
assert(total==30,'ten specials share exactly 3 percent total, not 3 percent each')
-- Lightning prioritizes nearest same-colour balls and ignores covered targets.
local r=fresh(30);local lane=r.other;lane.paused=false;lane.remaining=0
local covered=E.Crossings(30)[1].under
lane.balls={{color=2,d=covered,kind='Frost'}}
for i=1,7 do lane.balls[#lane.balls+1]={color=2,d=E.Path(1030).length-200-i*25} end
lane.balls[#lane.balls+1]={color=3,d=50}
table.sort(lane.balls,function(a,b)return a.d>b.d end)
lane.specialImpact={};E.ApplyExtraSpecial(lane,100,'Lightning',1,2)
assert(#lane.balls==4 and #lane.specialImpact.links==5)
local hidden=false;for _,b in ipairs(lane.balls) do if b.d==covered then hidden=true end end
assert(hidden,'hidden matching special survives lightning')
-- Paint shows the new colour, then awards a delayed x2 match without painting specials.
r=fresh();r.stasis=1;r.balls={{color=1,d=400},{color=2,d=375},{color=3,d=350},{color=4,d=325},{color=6,d=300,kind='Ward'}}
r.specialImpact={age=0};E.ApplyExtraSpecial(r,425,'Paint',1,5)
assert(#r.balls==5 and r.balls[1].color==5 and r.balls[4].color==5 and r.balls[5].color==6)
E.Step(db,.05);assert(#r.balls==5,'paint does not clear instantly')
local countdown=r.balls[1].paintDelay;E.Init(db);E.Step(db,.05);assert(r.balls[1].paintDelay==countdown,'paint countdown pauses on reload')
r.paused=false;for i=1,9 do E.Step(db,.05) end
assert(#r.balls==1 and r.balls[1].kind=='Ward' and r.score==800,'paint resolves delayed combo and preserves other specials')
-- Stasis stops travel, keeps shots available and resumes after its duration.
r=fresh();r.balls={{color=1,d=400},{color=2,d=375}};r.stasis=3;r.reverse=1
local d=r.balls[1].d;E.Step(db,.05);assert(r.balls[1].d==d and r.reverse==1)
assert(E.Fire(r,0,0));r.shot=nil;r.reverse=0
E.Init(db);local t=r.stasis;E.Step(db,.05);assert(r.stasis==t)
r.paused=false;for i=1,61 do E.Step(db,.05) end;assert(r.balls[1].d>d)
-- Magnet pulls unlike groups together, retaining ordered spacing and entry visibility.
r=fresh();r.balls={{color=1,d=400},{color=2,d=300}};r.magnet=4
E.Step(db,.05);assert(r.balls[1].d<400 and r.balls[2].d>300)
for i=1,80 do E.Step(db,.05);assert(r.balls[1].d-r.balls[2].d>=24.999) end
r=fresh();r.balls={{color=1,d=38},{color=2,d=-30}};r.magnet=4
E.Step(db,.05);assert(r.balls[1].d>=38)
-- Treasure doubles subsequent match points, while timers remain lane-local.
r=fresh();r.treasure=8;r.balls={{color=2,d=400},{color=2,d=375},{color=2,d=350}}
E.Match(r,1);assert(r.score==600 and r.burst.points==600)
r=fresh(30);r.treasure=8;assert(not r.other.treasure)
-- Ward catches precisely one breach; a second unprotected breach loses the run.
r=fresh();local length=E.Path(1).length;r.balls={{color=1,d=length-.01},{color=2,d=length-25.01}};r.ward=12;r.wardColor=2
E.Step(db,.05);assert(r.status=='playing' and r.ward==0 and r.reverse==2.5 and r.head<length)
assert(math.abs(r.balls[1].d-r.balls[2].d-25)<.000001)
r.reverse=0;r.balls={{color=1,d=length-.01}};E.Step(db,.05);assert(r.status=='lost')
-- Shared rainbow qualifies each side separately and does not double-count itself.
r=fresh();r.balls={{color=6,d=400},{color=6,d=375},{color=1,kind='Rainbow',d=350},{color=2,d=325},{color=2,d=300}}
assert(E.Match(r,3)==1 and #r.balls==0 and r.score==500)
r=fresh();r.balls={{color=6,d=400},{color=6,d=375},{color=1,kind='Rainbow',d=350},{color=2,d=325}}
E.Match(r,3);assert(#r.balls==1 and r.balls[1].color==2,'one blue alone does not qualify')
r=fresh();r.balls={{color=6,d=400},{color=6,d=375},{color=1,kind='Rainbow',d=350},{color=2,d=300},{color=2,d=275}}
E.Match(r,3);assert(#r.balls==2,'rainbow cannot match across a gap')
-- Dense bomb chain terminates, with every caught special activating once.
r=fresh();for i=1,35 do r.balls[i]={color=(i%6)+1,d=1100-i*25,kind='Bomb'} end
r.balls[1].color=1;r.balls[2].color=1;r.balls[3].color=1
local triggered=0;local sound=A.GameSound;A.GameSound=function(kind)if kind=='Bomb' then triggered=triggered+1 end end
E.Match(r,2);A.GameSound=sound
assert(#r.balls==0 and triggered==35 and r.score==3500,'each chained bomb resolves once')
for _,kind in ipairs({'Frost','Rewind','Lightning','Paint','Stasis','Magnet','Treasure','Ward'}) do
 r=fresh();r.balls={{color=1,d=400},{color=1,d=375,kind='Bomb'},{color=1,d=350},{color=2,d=325,kind=kind}}
 E.Match(r,2);assert(r.specialImpact.kind==kind,'blast activates caught '..kind)
end
-- Precision rewards only consecutive matching shots; misses reset the sequence.
r=fresh();for i=1,3 do E.RecordShot(r,true) end;assert(r.score==300 and r.precision==3)
E.RecordShot(r,false);assert(r.precision==0)
for i=1,12 do E.RecordShot(r,true) end;assert(r.score==300+300+600+900+900)
E.Init(db);assert(r.precision==12 and r.streakNotice)
""")
for kind in ('Lightning','Paint','Stasis','Magnet','Treasure','Ward'):
 for color in range(1,7):assert((ADDON/f'Media/{kind}{color}.tga').exists())
print('PASS: six specials, rarity, targeting, delayed paint, lane-local timers, ward, wildcard union, bounded cascades and precision bonuses')

visual=runtime()
visual.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN');A.Open(false)
local E=A.Engine
for _,kind in ipairs({'Lightning','Paint','Stasis','Magnet','Treasure','Ward'}) do
 local r=E.NewRun(A.db,30);r.paused=false;r.loadedKind=kind;r.loaded=3
 r.balls={{color=3,kind=kind,d=400},{color=2,d=375},{color=3,d=350},{color=3,d=325}}
 E.Special(r,1,kind);A.Draw()
 local fx=A.Visuals.specialBursts[1]
 assert(fx.core.texture==A.media..A.Visuals.impactTextures[kind]..'.tga' and fx.core:IsShown())
 assert(A.Visuals.ammoLight:IsShown() and A.Visuals.ammoLight.tint[2]==A.colors[3][2])
 if kind=='Lightning' then assert(fx.arcs[1]:IsShown()) end
 A.db.options.reducedMotion=true;A.Draw()
 for _,arc in ipairs(fx.arcs) do assert(not arc:IsShown()) end
 for _,particle in ipairs(fx.particles) do assert(not particle:IsShown()) end
 A.db.options.reducedMotion=false;A.Close()
 for _,arc in ipairs(fx.arcs) do assert(not arc:IsShown()) end
 assert(not fx.core:IsShown());A.Open(false)
end
""")
print('PASS: new coloured sprites, distinct impact art, lightning links, reduced motion and pooled cleanup')

new.execute("""
local E=A.Engine;local db={};E.Init(db)
local r=E.NewRun(db,1);r.remaining=0
r.balls={{color=6,d=400},{color=6,d=375},{color=2,d=325},{color=2,d=300}}
assert(E.Insert(r,3,1,350,'Rainbow')==1 and #r.balls==0 and r.score==500,'inserted wildcard clears white pair and blue pair')
r=E.NewRun(db,30);r.paused=false;r.remaining=0;r.balls={{color=1,d=300}};local lane=r.other
lane.remaining=0;lane.ward=12;local length=E.Path(1030).length;lane.balls={{color=1,d=length-.01},{color=2,d=length-25.01}}
E.Step(db,.05);assert(r.status=='playing' and lane.status=='playing' and lane.reverse==2.5 and (r.reverse or 0)==0,'secondary ward saves only its own lane')
-- Wire the precision counter through a real projectile hit and miss.
r=E.NewRun(db,1);r.paused=false;r.remaining=0;r.precision=2;r.stasis=3;r.balls={{color=2,d=400},{color=2,d=375},{color=1,d=300}}
local x,y=E.Point(1,400);r.shot={x=x,y=y,vx=1040,vy=0,color=2}
E.Step(db,.01);assert(r.precision==3 and r.score==600 and r.streakNotice.points==300)
r.shot={x=759,y=1,vx=1040,vy=0,color=1};E.Step(db,.01);assert(r.precision==0)
""")
print('PASS: wildcard insertion, secondary ward and projectile-driven precision rewards')

# Layered lightning progresses between targets without losing the visual to cascades.
vfx=runtime()
vfx.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN');A.Open(false)
local E=A.Engine;local r=E.NewRun(A.db,1);r.paused=false
local impact={kind='Lightning',color=2,x=100,y=100,age=0,links={}}
for i=1,5 do impact.links[i]={x=100+i*70,y=100+i%2*50} end
r.specialImpact=impact;r.lightningImpact=impact;A.Draw()
local fx=A.Visuals.specialBursts[1]
assert(fx.arcs[1]:IsShown() and not fx.arcs[2]:IsShown(),'lightning begins with one hop')
assert(fx.arcBlooms[1].blendMode=='ADD' and fx.arcCores[1].blendMode=='ADD')
assert(fx.arcBlooms[1].parent==A.board.effectLayer and fx.hitLights[1].parent==A.board.effectLayer)
E.Animate(r,.38);A.Draw()
assert(math.abs(impact.age-.38)<.000001,'shared visual record advances once')
assert(fx.arcs[3]:IsShown() and not fx.arcs[4]:IsShown(),'hops reveal in sequence')
assert(fx.hitLights[1].alpha>0 and fx.hitFlashes[1].alpha>0,'arrival illuminates the hit point')
assert(fx.arcBlooms[1].tint[2]==A.colors[2][2] and fx.arcCores[1].tint[1]>A.colors[2][1],'colour bloom and bright core stay separate')
local count=#Frames;A.Draw();assert(#Frames==count,'effect pools are reused')
r.specialImpact={kind='Bomb',color=1,x=200,y=100,age=0};E.Animate(r,.4);A.Draw()
assert(fx.arcs[5]:IsShown() and r.lightningImpact==impact,'later special does not erase chain lightning')
local age=impact.age;r.paused=true;E.Step(A.db,.05);assert(impact.age==age,'pause freezes lightning')
E.Init(A.db);assert(r.paused and r.lightningImpact==impact and impact.age==age,'reload preserves and pauses the lightning record')
A.db.options.reducedMotion=true;A.Draw()
assert(not fx.sourceLight:IsShown())
for _,key in ipairs({'arcs','arcBlooms','arcCores','hitLights','hitFlashes'}) do
 for _,texture in ipairs(fx[key]) do assert(not texture:IsShown(),'reduced motion removes jumping lights') end
end
A.db.options.reducedMotion=false;r.paused=false;E.Animate(r,1.2);A.Draw()
assert(not r.lightningImpact and not fx.arcs[1]:IsShown() and not fx.impactLight:IsShown())
r=E.NewRun(A.db,1);r.paused=false;r.remaining=0
r.balls={{color=2,d=500},{color=2,d=475,kind='Lightning'},{color=2,d=450},{color=1,d=425},{color=2,d=400,kind='Bomb'},{color=1,d=375}}
E.Match(r,2);assert(r.lightningImpact and r.specialImpact.kind=='Bomb','real bomb cascade retains lightning record')
A.Draw();assert(fx.arcs[1]:IsShown());A.Close()
assert(not fx.sourceLight:IsShown() and not fx.impactLight:IsShown())
for _,key in ipairs({'arcs','arcBlooms','arcCores','hitLights','hitFlashes'}) do
 for _,texture in ipairs(fx[key]) do assert(not texture:IsShown(),'close clears every light layer') end
end
""")
print('PASS: additive chain lightning, sequential hops, hit illumination, cascade retention, pause, reduced motion and cleanup')

vfx.execute("""
A.Open(false);A.db.options.reducedMotion=false
for _,kind in ipairs({'Bomb','Frost','Rewind','Rainbow','Paint','Stasis','Magnet','Treasure','Ward'}) do
 local r=A.Engine.NewRun(A.db,30);r.paused=false
 r.other.specialImpact={x=350,y=150,kind=kind,color=3,age=.2,links={}}
 A.Draw();local fx=A.Visuals.specialBursts[2]
 assert(fx.core.texture==A.media..A.Visuals.impactTextures[kind]..'.tga')
 assert(fx.coreBloom:IsShown() and fx.coreBloom.blendMode=='ADD')
 assert(fx.coreBloom.texture==A.media..A.Visuals.impactTextures[kind]..'Glow.tga')
 assert(fx.particleLights[1]:IsShown() and fx.particleLights[1].blendMode=='ADD','all specials illuminate particles')
 if kind=='Rainbow' then
  assert(fx.particleLights[1].tint[1]~=fx.particleLights[2].tint[1],'rainbow has multicolour light')
 elseif kind=='Bomb' then assert(fx.particleLights[1].tint[1]==1 and fx.particleLights[1].tint[3]==.04,'bomb emits firelight')
 else assert(fx.particleLights[1].tint[2]==A.colors[3][2],'coloured powers keep matching light') end
 A.db.options.reducedMotion=true;A.Draw()
 for _,light in ipairs(fx.particleLights) do assert(not light:IsShown()) end
 A.Close();assert(not fx.coreBloom:IsShown() and not fx.coreHot:IsShown())
 A.db.options.reducedMotion=false;A.Open(false)
end
""")
print('PASS: all ten dedicated VFX, luminous particles, rainbow colours and cleanup')


lua = runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN');A.Open(false)
local E=A.Engine; local r=A.db.run
r.balls={{d=250,color=2},{d=225,color=2},{d=200,color=2}}
assert(E.Match(r,2,3));A.Draw()
local fx=A.Feedback.clears[1]
assert(fx[1]:IsShown() and fx[1].blendMode=='BLEND')
assert(fx[1].texture==A.media..'Break2_1.tga' and r.effects[1].combo==3)
A.db.options.reducedMotion=true;A.Draw();assert(not fx[3]:IsShown())
r.balls={{d=250,color=2}};r.reverse=2;r.slow=3;r.stasis=2;r.magnet=4;r.treasure=4
A.Draw();local cue=A.Feedback.statuses[1]
for i=1,5 do assert(cue[i]:IsShown()) end
r.ward=12;A.Draw();assert(A.Visuals.holes[1].ward.texture==A.media..'PortalShield.tga')
r.reverse=0;r.slow=0;r.stasis=0;r.magnet=0;r.treasure=0;A.Draw()
for i=1,5 do assert(not cue[i]:IsShown()) end
r.specialImpact={};E.ApplyExtraSpecial(r,250,'Magnet',1,2);assert(r.magnet==6)
A.Close();assert(not fx[1]:IsShown())
""")
for name in ['MatchRing','PortalShield','Rewind','Frost','EffectStasis','EffectMagnet','EffectTreasure']:
 assert (ADDON/'Media'/f'{name}.tga').exists()
print('PASS: clear lighting, simultaneous status cues, ward shield, magnet duration and reduced motion')


lua=runtime()
lua.execute("""
local E=A.Engine;local db={};E.Init(db);local r=E.NewRun(db,1)
r.paused=false;r.balls={{d=400,color=1},{d=375,color=2}};r.head=400;r.magnet=6
local d=r.balls[1].d;E.Step(db,.05)
assert(math.abs(r.balls[1].d-d-E.Speed(r)*.5*.05)<.001,'magnet halves forward speed even without gaps')
r.status='won';E.BeginEnding(r,true);E.Step(db,.05)
assert(r.effects[#r.effects].kind=='Firework','victory emits fireworks')
""")
print('PASS: magnet slows an intact train and wins emit fireworks')


lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN');A.Open(false)
local r=A.db.run;r.balls={{d=400,color=1},{d=375,color=2}};r.slow=4;r.paused=false
A.Draw();local shell=A.Feedback.statuses[1][2]
assert(shell.texture==A.media..'IceShell6.tga' and shell.blendMode=='BLEND')
r.slow=2;A.Draw();assert(shell.texture==A.media..'IceShell3.tga')
r.slow=.2;A.Draw();assert(shell.texture==A.media..'IceShell1.tga' and shell.alpha<.6)
r.slow=0;r.stasis=3;A.Draw();assert(not shell:IsShown());shell=A.Feedback.chains[1][1];assert(shell.texture==A.media..'TimeChainLink.tga' and shell.alpha==1)
r.stasis=.2;A.Draw();assert(shell.alpha<.5)
A.db.options.reducedMotion=true;A.Draw();assert(shell:IsShown(),'reduced motion retains physical state')
r.stasis=0;A.Draw();assert(not shell:IsShown(),'material vanishes at expiry')
""")
for name in ['IceShell'+str(i) for i in range(1,7)]+['TimeChains','RewindWrap','MagnetWrap','TreasureWrap','FireBlast','FireBlastGlow','FireTongue']:
 assert (ADDON/'Media'/f'{name}.tga').exists()
print('PASS: six ice melt stages, chain release, expiry, firelight and reduced-motion materials')


lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN');A.Open(false)
local r=A.db.run;r.balls={{d=600,color=1},{d=200,color=2}};r.stasis=3
A.Draw();local n=0;for _,item in ipairs(A.Feedback.chains) do if item[1]:IsShown() then n=n+1 end end
assert(n>30,'continuous restraint spans the whole train, including gaps')
local hidden=A.Engine.Hidden;A.Engine.Hidden=function() return true end;A.Draw()
for _,item in ipairs(A.Feedback.chains) do assert(not item[1]:IsShown(),'no chain through tunnel cover') end
A.Engine.Hidden=hidden;A.Draw();A.Close()
for _,item in ipairs(A.Feedback.chains) do assert(not item[1]:IsShown()) end
""")
print('PASS: continuous route-following restraint, gap span, tunnel occlusion and close cleanup')


lua=runtime()
lua.execute("""
local E=A.Engine;local db={};E.Init(db);local r=E.NewRun(db,30);local other=r.other
r.balls={{d=400,color=1},{d=300,color=2},{d=200,color=3},{d=100,color=4}}
other.balls={{d=500,color=2,kind='Frost'},{d=450,color=1}}
local oldPoint,oldHidden=E.Point,E.Hidden
E.Point=function(route,d)
 if route==1030 then if d==500 then return 180,100 else return 100,90 end end
 if d==400 then return 100,100 elseif d==300 then return 350,100 elseif d==200 then return 100,190 else return 100,300 end
end
E.Hidden=function(lane,d)return lane==other and d==450 end
E.Special(r,1,'Bomb')
assert(#r.balls==2 and r.balls[1].d==300 and r.balls[2].d==100,'blast clears near bend but preserves far intervening balls')
assert(#other.balls==1 and other.balls[1].d==450,'other lane is hit but tunnel ball is protected')
assert(other.slow==4 and (r.slow or 0)==0,'caught special applies to its own lane')
-- Rebind the transient peer map on saved-state initialization; secondary blasts reach primary.
E.Init(db);r.balls={{d=200,color=1,kind='Frost'},{d=300,color=2}};other.balls={{d=500,color=1,kind='Bomb'}}
E.Special(other,1,'Bomb');assert(r.slow==4 and #r.balls==1 and r.balls[1].d==300)
E.Point,E.Hidden=oldPoint,oldHidden
""")
print('PASS: radial cross-lane bomb, noncontiguous targets, tunnel protection, lane-local cascades and reload peer binding')


lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN');A.Open(false)
local r=A.db.run;local E=A.Engine;r.balls={{d=350,color=1},{d=325,color=1},{d=300,color=1}}
E.Match(r,2);A.Draw();local t=A.Feedback.clears[1][1]
assert(t.texture==A.media..'Break1_1.tga')
E.Animate(r,.13);A.Draw();assert(t.texture==A.media..'Break1_2.tga')
E.Animate(r,.13);A.Draw();assert(t.texture==A.media..'Break1_3.tga')
E.Animate(r,.13);A.Draw();assert(t.texture==A.media..'Break1_4.tga')
A.db.options.reducedMotion=true;A.Draw();assert(t.texture==A.media..'Break1_2.tga')
r.specialImpact={kind='Bomb',color=1,x=200,y=100,age=0,radius=120};r.bombImpact=r.specialImpact
E.Animate(r,.1);assert(math.abs(r.bombImpact.age-.1)<.001,'shared bomb record ages once')
r.specialImpact={kind='Frost',color=2,x=200,y=100,age=0};A.Draw()
assert(A.Visuals.specialBursts[3].core:IsShown(),'explosion survives caught Frost activation')
E.Animate(r,1.1);A.Draw();assert(not r.bombImpact and not A.Visuals.specialBursts[3].core:IsShown())
""")
for colour in range(1,7):
 for frame in range(1,5):assert (ADDON/'Media'/f'Break{colour}_{frame}.tga').exists()
print('PASS: all 24 breaking frames, reduced motion, bomb cascade visibility and shared-record expiry')


lua=runtime()
lua.execute("""
local E=A.Engine;local db={};E.Init(db)
for _,reverse in ipairs({false,true}) do
 local r=E.NewRun(db,1);r.paused=false;r.remaining=0;r.balls={{d=600,color=1},{d=575,color=2},{d=550,color=3}}
 if reverse then r.reverse=2 end
 E.Step(db,.025);assert(reverse and r.balls[1].motionSpeed<0 or not reverse and r.balls[1].motionSpeed>0)
 local x1,y1=E.Point(1,r.balls[1].d);local x0,y0=E.Point(1,r.balls[1].d-1)
 for _,b in ipairs(r.balls) do b.color=1 end
 E.Match(r,2);local e=r.effects[#r.effects]
 assert((e.vx*(x1-x0)+e.vy*(y1-y0))*(reverse and -1 or 1)>0,'break carries forward/reverse tangent momentum')
end
local r=E.NewRun(db,1);r.balls={{d=400,color=1,motionSpeed=100},{d=375,color=1,motionSpeed=100},{d=350,color=1,motionSpeed=100}};r.stasis=2
E.Match(r,2);assert(r.effects[1].vx==0 and r.effects[1].vy==0,'stopped balls do not drift')
r=E.NewRun(db,1);r.balls={{d=400,color=1,slideX=10,slideY=5,slideAge=.08},{d=375,color=1},{d=350,color=1}}
local x,y=E.Point(1,400);E.Match(r,2);local e=r.effects[#r.effects]
assert(math.abs(e.x-x-1.25)<.001 and math.abs(e.y-y-.625)<.001,'break starts at eased visual position')
""")
lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN');A.Open(false)
local r=A.db.run;r.effects={{x=300,y=200,vx=100,vy=-50,age=.06,color=2}};A.Draw()
local fx=A.Feedback.clears[1]
assert(fx[1].texture==A.media..'Break2_1.tga' and fx[3].texture==A.media..'Break2_2.tga')
assert(math.abs(fx[1].alpha-.5)<.001 and math.abs(fx[3].alpha-.5)<.001,'smooth midpoint crossfade')
assert(fx[1].pointArgs[3]>300 and fx[1].pointArgs[4]>-172,'fragments inherit velocity')
local frames=#Frames;A.Draw();assert(#Frames==frames,'blend reuses existing pool slots')
A.db.options.reducedMotion=true;A.Draw()
assert(fx[1].pointArgs[3]==300 and not fx[3]:IsShown(),'reduced motion disables travel and blending')
""")
print('PASS: forward/reverse momentum, stopped chains, eased spawn position, crossfade, pool reuse and reduced motion')


lua=runtime()
lua.execute("""
local E=A.Engine;local db={};E.Init(db)
for _,kind in ipairs({'Bomb','Frost','Rewind','Lightning','Paint','Stasis','Magnet','Treasure','Ward','Rainbow'}) do
 local r=E.NewRun(db,1);r.remaining=0;r.balls={{d=500,color=2},{d=475,color=2,kind='Lightning'},{d=450,color=2},{d=425,color=1},{d=400,color=2,kind=kind}}
 local calls={};local sound=A.GameSound;A.GameSound=function(k)calls[k]=(calls[k] or 0)+1 end
 E.Match(r,2);A.GameSound=sound
 assert(calls[kind]==(kind=='Lightning' and 2 or 1),'lightning activates caught '..kind..' once')
end
local r=E.NewRun(db,1);r.remaining=0
r.balls={{d=500,color=2},{d=475,color=2,kind='Lightning'},{d=450,color=2},{d=425,color=1,kind='Stasis'},{d=400,color=2,kind='Bomb'},{d=375,color=3,kind='Magnet'}}
local calls={};local sound=A.GameSound;A.GameSound=function(k)calls[k]=(calls[k] or 0)+1 end
E.Match(r,2);A.GameSound=sound
assert(calls.Lightning==1 and calls.Bomb==1 and calls.Stasis==1 and calls.Magnet==1,'lightning to bomb to multiple effects resolves once each')
assert(r.stasis==3 and r.magnet==6 and r.bombImpact and r.lightningImpact,'both powers and their blast visuals survive')
""")
print('PASS: lightning activates all ten caught special types and bomb cascades trigger multiple powers once')


lua=runtime()
lua.execute("""
A.events.OnEvent(A.events,'ADDON_LOADED','RaynnaRuneballs');A.events.OnEvent(A.events,'PLAYER_LOGIN');A.Open(false)
local r=A.db.run;r.paused=false;r.balls={{d=500,color=1},{d=300,color=2}};r.magnet=6
local point,hidden=A.Engine.Point,A.Engine.Hidden;A.Engine.Point=function(_,d)return d,100 end;A.Engine.Hidden=function()return false end
A.Feedback.Draw(A.board,r,{},0);local p=A.Feedback.pulls[1][1];local x=p.pointArgs[3];assert(p:IsShown())
A.Feedback.Draw(A.board,r,{},.1);assert(p.pointArgs[3]<x,'gap arrows move toward rear group')
local count=#Frames;A.Feedback.Draw(A.board,r,{},.15);assert(#Frames==count)
A.db.options.reducedMotion=true;A.Feedback.Draw(A.board,r,{},1);x=p.pointArgs[3];A.Feedback.Draw(A.board,r,{},2);assert(p.pointArgs[3]==x)
r.stasis=3;A.Feedback.Draw(A.board,r,{},3);assert(not p:IsShown(),'stasis suppresses misleading pull')
local chain=A.Feedback.chains[1][1];assert(math.abs(chain.pointArgs[4]+86)>15,'chain clears ball centres')
assert(A.Feedback.stops[1][1]:IsShown(),'time stop has one endpoint marker')
r.stasis=0;A.Engine.Hidden=function()return true end;A.Feedback.Draw(A.board,r,{},4);assert(not p:IsShown())
A.Engine.Hidden=hidden;A.Engine.Point=point;r.magnet=0;A.Draw();assert(not p:IsShown())
""")
print('PASS: directional Magnet pulls, stationary reduced motion, tunnel protection, colour clearance and stop marker')
