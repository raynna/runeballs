local _, A = ...
function A.BuildSettings()
    local registry = RaynnaModsSettingsRegistry
    registry:RegisterAppearance('runeballs', function()
        return A.db.appearance
    end, function(key, value)
        A.db.appearance[key] = value
        A.ApplyAppearance()
    end)
    registry:Register('runeballs', 'Runeballs', function(panel)
        local refreshers = {}
        local function label(value, x, y)
            local t = panel:CreateFontString(nil, 'OVERLAY', 'GameFontNormal')
            t:SetPoint('TOPLEFT', x, y)
            t:SetText(value)
        end
        local function check(value, y, get, set)
            local c = CreateFrame('CheckButton', nil, panel, 'UICheckButtonTemplate')
            c:SetPoint('TOPLEFT', 24, y)
            c:SetSize(26, 26)
            label(value, 54, y - 6)
            c:SetScript('OnClick', function(self)
                set(not not self:GetChecked())
            end)
            refreshers[#refreshers + 1] = function()
                c:SetChecked(get())
            end
        end
        local function button(value, x, y, w, callback)
            local b = CreateFrame('Button', nil, panel, 'UIPanelButtonTemplate')
            b:SetPoint('TOPLEFT', x, y)
            b:SetSize(w, 25)
            b:SetText(value)
            b:SetScript('OnClick', callback)
        end
        label("Raynna's Runeballs", 24, -22)
        label('Match three coloured marbles to stop the chain reaching the void.', 24, -52)
        check('Open automatically when a flight path begins', -90, function()
            return A.db.options.autoFlight ~= false
        end, function(v)
            A.db.options.autoFlight = v
        end)
        check('Close game when flight is done (automatic opens)', -125, function()
            return A.db.options.closeOnLanding == true
        end, function(v)
            A.db.options.closeOnLanding = v
        end)
        check('Show minimap button', -160, function()
            return A.db.options.minimap ~= false
        end, A.SetMinimapVisible)
        label('Window scale (55-130%)', 24, -207)
        local input = CreateFrame('EditBox', nil, panel, 'InputBoxTemplate')
        input:SetPoint('TOPLEFT', 255, -200)
        input:SetSize(65, 25)
        input:SetAutoFocus(false)
        input:SetMaxLetters(5)
        local function refreshScale()
            input:SetText(math.floor((A.db.options.scale or 0.9) * 100 + 0.5) .. '%')
        end
        input:SetScript('OnEnterPressed', function(self)
            local value = tonumber((self:GetText() or ''):match('^%s*(%d+)%s*%%?%s*$'))
            if value then
                A.SetScale(value / 100)
            end
            refreshScale()
            self:ClearFocus()
        end)
        input:SetScript('OnEscapePressed', function(self)
            refreshScale()
            self:ClearFocus()
        end)
        input:SetScript('OnEditFocusLost', refreshScale)
        button('-', 220, -200, 25, function()
            A.SetScale((A.db.options.scale or 0.9) - 0.05)
            refreshScale()
        end)
        button('+', 330, -200, 25, function()
            A.SetScale((A.db.options.scale or 0.9) + 0.05)
            refreshScale()
        end)
        refreshers[#refreshers + 1] = refreshScale
        button('Open game', 24, -250, 145, function()
            A.Open(false)
        end)
        button('Center and show', 190, -250, 145, function()
            SlashCmdList.RAYNNARUNEBALLS('center')
        end)
        check('Show dotted aiming guide', -300, function()
            return A.db.options.aimGuide ~= false
        end, function(value)
            A.db.options.aimGuide = value
        end)
        check('Play game sounds (uses WoW sound effects volume)', -337, function()
            return A.db.options.sound ~= false
        end, function(value)
            A.db.options.sound = value
        end)
        check('Reduced motion (no shake, ambient particles or recoil)', -372, function()
            return A.db.options.reducedMotion == true
        end, function(value)
            A.db.options.reducedMotion = value
            A.Visuals.Reset()
            A.Draw()
        end)
        label(
            'Automatic faction artwork: ' .. A.Faction() .. '. Left-click shoots; right-click swaps.',
            24,
            -415
        )
        label(
            'Run, best score and preferences save per character. Closing pauses.\n/rrb opens the game; /rrb settings opens this page.\nSpecial shots: Bomb explodes, Frost slows, Rewind reverses the chain.',
            24,
            -450
        )
        return function()
            for _, refresh in ipairs(refreshers) do
                refresh()
            end
        end
    end)
end
