
NOW, MONEY = 100, 10000
function IsControlKeyDown() return CTRL or false end
function SetCursor(value) CURSOR = value end
function ResetCursor() CURSOR = nil; CURSOR_MODE = nil end
Enum = {Cursormode = {NoCursor = 0}, TooltipDataType = {Item = 0}}
TooltipDataProcessor = {AddTooltipPostCall = function(_, fn) ITEM_TOOLTIP_CALLBACK = fn end}
function SetCursorByMode(mode) CURSOR_MODE = mode end
function GetTime() return NOW end
function GetMoney() return MONEY end
function issecretvalue() return false end
C_CurrencyInfo = {GetCoinTextureString = function(n) return tostring(n) end}
function UnitGUID(u) if u == 'player' then return 'Player-1' elseif u == 'pet' then return 'Pet-1' else return 'Creature-0-1-2-3-100-1' end end
ALT_DOWN = false
function IsAltKeyDown() return ALT_DOWN end
function UnitName() return 'Forest Wolf' end
XP, XPMAX, PLAYERLEVEL = 100, 1000, 8
function UnitXP() return XP end
function UnitXPMax() return XPMAX end
function UnitLevel(u) return u == 'player' and PLAYERLEVEL or 8 end
local methods = {}
Frames = {}
function methods:RegisterEvent(e) assert(e ~= 'COMBAT_LOG_EVENT_UNFILTERED' and e ~= 'COMBAT_LOG_EVENT', 'forbidden event registration'); self.events = self.events or {}; self.events[e] = true end
function methods:SetParent(parent) self.parent = parent end
function methods:SetText(t) self.labelText = t end
function methods:GetText() return self.labelText end
function methods:SetSize(w,h) self.width = w; self.height = h end
function methods:SetScale(s) self.scale = s end
function methods:GetEffectiveScale() return self.scale or 1 end
function methods:GetFrameLevel() return 1 end
function methods:GetLeft() return 100 end
function methods:GetTop() return 500 end
function methods:GetRight() return 400 end
function methods:GetWidth() return self.width or 1920 end
function methods:GetHeight() return self.height or 1080 end
function methods:SetWidth(w) self.width = w end
function methods:SetHeight(h) self.height = h end
function methods:IsShown() return self.shown end
function methods:IsMouseOver() return self.hovered end
function methods:SetTexture(t) self.texture = t end
function methods:SetHyperlink(t) self.link = t end
function methods:Hide() self.shown = false; if rawget(self, 'OnHide') then self.OnHide(self) end end
function methods:Show() self.shown = true end
function methods:SetShown(s) if s then self:Show() else self:Hide() end end
function methods:SetPoint(p, ...) self.anchor = p; self.pointArgs = {...} end
CURSOR_X, CURSOR_Y = 100, 100
function GetCursorPosition() return CURSOR_X, CURSOR_Y end
function IsMouseButtonDown() return true end
function methods:SetScript(k, f) self[k] = f end
function methods:GetScript(k) return rawget(self,k) end
function methods:GetPoint() return 'CENTER', nil, 'CENTER', 0, 0 end
function methods:CreateFontString() return CreateFrame() end
function methods:CreateTexture() return CreateFrame() end
function CreateFrame(kind, name, parent)
    local frame = setmetatable({kind = kind, parent = parent}, {__index = function(_, k) if k:match('^[A-Z]') then return methods[k] or function() end end end})
    table.insert(Frames, frame)
    if name then _G[name] = frame end
    return frame
end
C_Timer = {NewTicker = function() end, After = function(_, callback) callback() end}
bit = {band = function(a,b) return a % (b + 1) end}
COMBATLOG_XPGAIN_FIRSTPERSON = '%s dies, you gain %d experience.'
COMBATLOG_XPGAIN_FIRSTPERSON_GROUP = '%s dies, you gain %d experience. (+%d group bonus)'
COMBATLOG_XPGAIN_EXHAUSTION1 = '%s dies, you gain %d experience. (%s exp %s bonus)'
YOU_LOOT_MONEY = 'You loot %s'
LOOT_MONEY_SPLIT = 'Your share of the loot is %s.'
GOLD_AMOUNT, SILVER_AMOUNT, COPPER_AMOUNT = '%d Gold', '%d Silver', '%d Copper'
LOOT_ITEM_SELF = 'You receive loot: %s.'
LOOT_ITEM_SELF_MULTIPLE = 'You receive loot: %sx%d.'
UIParent, Minimap, GameTooltip = CreateFrame(), CreateFrame(), CreateFrame()
StaticPopupDialogs, SlashCmdList = {}, {}
STANDARD_TEXT_FONT = 'font'
Settings = {
    RegisterCanvasLayoutCategory = function(panel, name)
        SETTINGS_PANEL, SETTINGS_NAME = panel, name
        return {GetID = function() return 123 end}
    end,
    RegisterAddOnCategory = function() SETTINGS_REGISTERED = true end,
    OpenToCategory = function(id) SETTINGS_OPENED = id end,
}
A = {}
function GetNumLootItems() return 1 end
SLOT_TYPE = 2
function GetLootSlotType() return SLOT_TYPE end
function GetLootSlotLink() return '|cffffffff|Hitem:123:0|h[Wolf Fur]|h|r' end
function GetLootSourceInfo() return UnitGUID('target'), 3 end
