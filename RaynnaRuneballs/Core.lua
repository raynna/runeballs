-- Client lifecycle and flight detection. Minigame actions never spend WoW gold.
local _, A = ...
function A.OpenSettings()
    A.Pause()
    A.Draw()
    RaynnaModsSettingsRegistry:Open('runeballs')
end
function A.CheckFlight()
    RaynnaFlightGames:Check()
end
function A.SetMinimapVisible(value)
    A.db.options.minimap = value
    if A.minimap then
        A.minimap:SetShown(value)
    end
end
local function buildMinimap()
    local b = CreateFrame('Button', 'RaynnaRuneballsMinimap', Minimap)
    A.minimap = b
    b:SetSize(30, 30)
    b:SetFrameStrata('MEDIUM')
    b:EnableMouse(true)
    b.icon = b:CreateTexture(nil, 'ARTWORK')
    b.icon:SetAllPoints()
    b.icon:SetTexture(A.media .. 'Ball5.tga')
    local border = b:CreateTexture(nil, 'OVERLAY')
    border:SetAllPoints()
    border:SetTexture('Interface\\Minimap\\MiniMap-TrackingBorder')
    border:SetTexCoord(0, 0.6, 0, 0.6)
    local function position()
        local angle = math.rad(A.db.options.minimapAngle or 145)
        b:ClearAllPoints()
        b:SetPoint('CENTER', Minimap, 'CENTER', math.cos(angle) * 82, math.sin(angle) * 82)
    end
    b:RegisterForClicks('LeftButtonUp', 'RightButtonUp')
    b:RegisterForDrag('LeftButton')
    b:SetScript('OnClick', function(_, which)
        if which == 'RightButton' then
            A.OpenSettings()
        else
            A.Toggle()
        end
    end)
    b:SetScript('OnDragStart', function(self)
        self:SetScript('OnUpdate', function()
            local x, y = GetCursorPosition()
            local mx, my = Minimap:GetCenter()
            local s = Minimap:GetEffectiveScale()
            A.db.options.minimapAngle = math.deg(math.atan2(y / s - my, x / s - mx))
            position()
        end)
    end)
    b:SetScript('OnDragStop', function(self)
        self:SetScript('OnUpdate', nil)
    end)
    b:SetScript('OnEnter', function(self)
        GameTooltip:SetOwner(self, 'ANCHOR_LEFT')
        GameTooltip:SetText("Raynna's Runeballs")
        GameTooltip:AddLine('Left-click: play / hide\nRight-click: settings\nDrag: move button', 1, 1, 1)
        GameTooltip:Show()
    end)
    b:SetScript('OnLeave', function()
        GameTooltip:Hide()
    end)
    position()
    A.SetMinimapVisible(A.db.options.minimap ~= false)
end
local events = CreateFrame('Frame')
A.events = events
for _, event in ipairs({
    'ADDON_LOADED',
    'PLAYER_LOGIN',
    'PLAYER_LOGOUT',
    'PLAYER_CONTROL_LOST',
    'PLAYER_CONTROL_GAINED',
    'PLAYER_REGEN_DISABLED',
}) do
    events:RegisterEvent(event)
end
local ready = false
events:SetScript('OnEvent', function(_, event, name)
    if event == 'ADDON_LOADED' and name == 'RaynnaRuneballs' then
        RaynnaRuneballsDB = RaynnaRuneballsDB or {}
        A.db = RaynnaRuneballsDB
        A.Engine.Init(A.db)
        if not A.db.run then
            A.Engine.NewRun(A.db)
        end
        A.db.appearance = A.db.appearance or {}
    elseif event == 'PLAYER_LOGIN' then
        A.BuildUI()
        A.BuildSettings()
        buildMinimap()
        RaynnaFlightGames:Register('runeballs', {
            name = "Raynna's Runeballs",
            visible = function()
                return A.frame:IsShown()
            end,
            enabled = function()
                return A.db.options.autoFlight ~= false
            end,
            open = function()
                A.autoOpened = true
                A.Open(true)
            end,
            land = function()
                if A.autoOpened then
                    A.Pause()
                    if A.db.options.closeOnLanding ~= false then
                        A.Close()
                    else
                        A.Draw()
                    end
                end
                A.autoOpened = false
            end,
        })
        ready = true
        -- A low-frequency transition check catches flights even when a client omits a control event.
        if C_Timer and C_Timer.NewTicker then
            A.flightTicker = C_Timer.NewTicker(1, function()
                A.CheckFlight()
            end)
        end
        if C_Timer and C_Timer.After then
            C_Timer.After(0, A.CheckFlight)
        else
            A.CheckFlight()
        end
    elseif ready and event == 'PLAYER_LOGOUT' then
        A.Pause()
    elseif ready and event == 'PLAYER_REGEN_DISABLED' then
        RaynnaFlightGames:Cancel()
        A.Close()
    elseif ready and (event == 'PLAYER_CONTROL_LOST' or event == 'PLAYER_CONTROL_GAINED') then
        A.CheckFlight()
    end
end)
-- Demo state is session-only; the real SavedVariables table keeps campaign data.
local campaignDB
local function demo(value)
    local name = (UnitName('player') or ''):lower():gsub('%s+', '')
    if name ~= 'itsraynna' then
        print('Runeballs: demo commands are restricted to Its Raynna.')
        return
    end
    if value == 'off' then
        if campaignDB then
            A.Pause()
            A.db = campaignDB
            campaignDB = nil
            A.Open(false)
        end
        print('Runeballs: returned to your saved campaign.')
        return
    end
    local level = tonumber(value)
    if not level or level ~= math.floor(level) or level < 1 or level > A.Engine.MAX_LEVEL then
        print('Runeballs: /rrb demo 1-100 | /rrb demo off')
        return
    end
    A.Pause()
    campaignDB = campaignDB or A.db
    A.db = {
        options = campaignDB.options,
        appearance = campaignDB.appearance,
        best = campaignDB.best,
        level = level,
    }
    A.Engine.NewRun(A.db, level)
    A.Open(false)
    A.frame.play:GetScript('OnClick')(A.frame.play)
    print('Runeballs: DEMO round ' .. level .. '. /rrb demo off restores your campaign.')
end
SLASH_RAYNNARUNEBALLS1 = '/rrb'
SLASH_RAYNNARUNEBALLS2 = '/runeballs'
SLASH_RAYNNARUNEBALLS3 = '//rrb'
SlashCmdList.RAYNNARUNEBALLS = function(message)
    if not ready then
        return
    end
    local command, value = (message or ''):lower():match('^(%S*)%s*(.-)$')
    if command == 'demo' then
        demo(value)
    elseif command == 'settings' then
        A.OpenSettings()
    elseif command == 'hide' then
        A.Close()
    elseif command == 'show' then
        A.Open(false)
    elseif command == 'center' then
        A.frame:ClearAllPoints()
        A.frame:SetPoint('CENTER')
        A.db.options.position = nil
        A.Open(false)
    elseif command == 'scale' and tonumber(value) then
        A.SetScale(tonumber(value) / 100)
    elseif command == '' then
        A.Toggle()
    else
        print("Raynna's Runeballs: /rrb | show | hide | center | scale 55-130 | settings")
    end
end
