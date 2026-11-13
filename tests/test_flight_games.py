"""Shared chooser: registration order, manual ownership, Peggle and landing."""
from pathlib import Path
from lupa.lua51 import LuaRuntime
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'RaynnaRuneballs/GameRegistry.lua').read_text()
other=ROOT/'RaynnaTowerDefense/GameRegistry.lua'
if other.exists(): assert source==other.read_text()
for order in [('runeballs','towerdefense'),('towerdefense','runeballs')]:
 lua=LuaRuntime(unpack_returned_tuples=True)
 lua.execute((ROOT/'tests/wow_mock.lua').read_text())
 lua.execute('FLYING=false;COMBAT=false;function UnitOnTaxi() return FLYING end;function InCombatLockdown() return COMBAT end;UISpecialFrames={}')
 lua.execute(source)
 lua.execute('''
 R=RaynnaFlightGames; opened={};landed={};visible={};enabled={}
 function register(id)
  R:Register(id,{name=id,visible=function() return visible[id] end,enabled=function() return enabled[id]~=false end,
  open=function() opened[id]=(opened[id] or 0)+1;visible[id]=true end,
  land=function() landed[id]=(landed[id] or 0)+1;visible[id]=false end})
 end
 ''')
 for id in order:
  lua.execute(source) # duplicate bootstrap must retain state
  lua.eval('register')(id)
 lua.execute('''
 FLYING=true;R:Check();R:Check()
 assert(R.window:IsShown() and not next(opened))
 R:Choose('runeballs');assert(opened.runeballs==1 and not opened.towerdefense)
 FLYING=false;R:Check();assert(landed.runeballs==1 and not landed.towerdefense)
 visible.towerdefense=true;FLYING=true;R:Check();assert(not R.window:IsShown())
 FLYING=false;R:Check();assert(visible.towerdefense,'manual window is not owned')
 visible.towerdefense=false;COMBAT=true;FLYING=true;R:Check();assert(not R.window:IsShown())
 COMBAT=false;FLYING=false;R:Check()
 enabled.runeballs=false;enabled.towerdefense=false;FLYING=true;R:Check();assert(not R.window:IsShown())
 FLYING=false;R:Check()
 PeggleData={settings={openFlightStart=true,closeFlightEnd=true}}
 PeggleWindow=CreateFrame('Frame');PeggleWindow:Hide()
 PeggleWindow.HookScript=function(self,event,fn) self.hook=fn end
 R:DiscoverPeggle();assert(R.providers.peggle)
 PeggleWindow.flying=true;PeggleWindow:Show();PeggleWindow.hook()
 assert(not PeggleWindow:IsShown() and R.window:IsShown())
 R:Choose('peggle');PeggleWindow.hook();assert(PeggleWindow:IsShown())
 FLYING=false;R:Check();assert(not PeggleWindow:IsShown())
 assert(PeggleData.settings.openFlightStart==true,'third-party preference unchanged')
 ''')
# A standalone game retains direct auto-opening.
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute((ROOT/'tests/wow_mock.lua').read_text());lua.execute(source)
lua.execute("RaynnaFlightGames:Register('only',{name='Only',visible=function() return false end,enabled=function() return true end,open=function() OPENED=true end});RaynnaFlightGames:Begin();assert(OPENED and not RaynnaFlightGames.window)")
print('PASS: shared chooser, both orders, late Peggle, manual ownership, disabled/combat, landing, standalone')

# Runeballs plus Peggle, with Tower Defense entirely absent.
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((ROOT/'tests/wow_mock.lua').read_text())
lua.execute("FLYING=false;function UnitOnTaxi() return FLYING end;function InCombatLockdown() return false end;UISpecialFrames={}")
lua.execute(source)
lua.execute("""
local R=RaynnaFlightGames
local visible=false
R:Register('runeballs',{name="Raynna's Runeballs",visible=function() return visible end,enabled=function() return true end,open=function() visible=true end,land=function() visible=false end})
PeggleData={settings={openFlightStart=true,closeFlightEnd=true}}
PeggleWindow=CreateFrame('Frame');PeggleWindow:Hide()
PeggleWindow.HookScript=function(self,event,fn) self.hook=fn end
R:DiscoverPeggle()
FLYING=true;R:Check()
assert(R.window:IsShown() and not visible and not PeggleWindow:IsShown())
assert(R.providers.runeballs and R.providers.peggle and not R.providers.towerdefense)
R:Choose('runeballs');assert(visible and not PeggleWindow:IsShown())
FLYING=false;R:Check();assert(not visible)
FLYING=true;R:Check();R:Choose('peggle');assert(PeggleWindow:IsShown() and not visible)
FLYING=false;R:Check();assert(not PeggleWindow:IsShown())
""")
print('PASS: Runeballs + Peggle flight selection without Tower Defense')
