-- Shared optional flight-game chooser. No third-party preferences are modified.
local R = _G.RaynnaFlightGames
if R then
    return
end
R = { providers = {}, flying = false }
_G.RaynnaFlightGames = R
function R:Register(id, provider)
    self.providers[id] = provider
end
function R:Choose(id)
    if self.window then
        self.window:Hide()
    end
    if InCombatLockdown and InCombatLockdown() then
        return
    end
    local p = self.providers[id]
    if p then
        self.selected = id
        p.open()
    end
end
function R:Begin()
    if self.flying then
        return
    end
    self.flying = true
    if InCombatLockdown and InCombatLockdown() then
        return
    end
    local choices, enabled = {}, false
    for id, p in pairs(self.providers) do
        if p.visible() then
            return
        end -- Leave an already-open manual game alone.
        choices[#choices + 1] = id
        enabled = enabled or p.enabled()
    end
    if not enabled then
        return
    end
    table.sort(choices)
    if #choices == 1 then
        self:Choose(choices[1])
        return
    end
    if not self.window then
        local f = CreateFrame(
            'Frame',
            'RaynnaFlightGameChooser',
            UIParent,
            BackdropTemplateMixin and 'BackdropTemplate' or nil
        )
        self.window = f
        f:SetPoint('CENTER')
        f:SetFrameStrata('DIALOG')
        f:EnableMouse(true)
        f:SetBackdrop({
            bgFile = 'Interface\\DialogFrame\\UI-DialogBox-Background',
            edgeFile = 'Interface\\DialogFrame\\UI-DialogBox-Border',
            tile = true,
            tileSize = 32,
            edgeSize = 32,
            insets = { left = 8, right = 8, top = 8, bottom = 8 },
        })
        local title = f:CreateFontString(nil, 'OVERLAY', 'GameFontNormalLarge')
        title:SetPoint('TOP', 0, -22)
        title:SetText('Choose a flight game')
        f.buttons = {}
        if UISpecialFrames then
            table.insert(UISpecialFrames, 'RaynnaFlightGameChooser')
        end
    end
    local f = self.window
    f:SetSize(340, 100 + #choices * 40)
    for _, b in ipairs(f.buttons) do
        b:Hide()
    end
    for i = 1, #choices + 1 do
        local id = choices[i]
        local b = f.buttons[i]
        if not b then
            b = CreateFrame('Button', nil, f, 'UIPanelButtonTemplate')
            f.buttons[i] = b
        end
        b:SetSize(280, 30)
        b:ClearAllPoints()
        b:SetPoint('TOP', 0, -48 - (i - 1) * 40)
        b:SetText(id and self.providers[id].name or 'Not now')
        b:SetScript('OnClick', function()
            if id then
                self:Choose(id)
            else
                f:Hide()
            end
        end)
        b:Show()
    end
    f:Show()
end
function R:DiscoverPeggle()
    local w = _G.PeggleWindow
    if not w or self.providers.peggle then
        return
    end
    self:Register('peggle', {
        name = 'Peggle',
        visible = function()
            return w:IsShown()
        end,
        enabled = function()
            return PeggleData and PeggleData.settings and PeggleData.settings.openFlightStart == true
        end,
        open = function()
            w:Show()
        end,
        land = function()
            if PeggleData and PeggleData.settings and PeggleData.settings.closeFlightEnd then
                w:Hide()
            end
        end,
    })
    w:HookScript('OnShow', function()
        if w.flying and self.selected ~= 'peggle' and not self.peggleAttempt then
            self.peggleAttempt = true
            w:Hide()
            if C_Timer and C_Timer.After then
                C_Timer.After(0, function()
                    self:Begin()
                end)
            else
                self:Begin()
            end
        end
    end)
end
function R:Check()
    self:DiscoverPeggle()
    local flying = UnitOnTaxi and not not UnitOnTaxi('player') or false
    if flying then
        self:Begin()
    elseif self.flying then
        self.flying = false
        if self.window then
            self.window:Hide()
        end
        local p = self.providers[self.selected]
        if p then
            p.land()
        end
        self.selected = nil
        self.peggleAttempt = nil
    end
end
function R:Cancel()
    if self.window then
        self.window:Hide()
    end
end

local discovery = CreateFrame('Frame')
discovery:RegisterEvent('ADDON_LOADED')
discovery:SetScript('OnEvent', function()
    R:DiscoverPeggle()
end)
