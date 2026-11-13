local _, A = ...
A.Theme = {
    gold = { 1, 0.784, 0.239 },
    cream = { 1, 0.945, 0.788 },
    muted = { 0.80, 0.76, 0.70 },
    panel = { 0.161, 0.129, 0.169 },
    outline = { 0.086, 0.051, 0.071 },
    blue = { 0.153, 0.749, 1 },
    amber = { 1, 0.67, 0.16 },
    red = { 1, 0.27, 0.21 },
    heading = A.media .. 'Fonts\\LilitaOne.ttf',
    body = A.media .. 'Fonts\\RuneballsLabels.ttf',
    buttonDuration = 0.14,
}
function A.MotionReduced()
    return A.db and A.db.options.reducedMotion == true
end
function A.Label(parent, text, x, y, size, style)
    local label = parent:CreateFontString(nil, 'OVERLAY', 'GameFontNormal')
    label.fontPath = style == 'body' and A.Theme.body or A.Theme.heading
    label.fontFlags = style == 'body' and 'OUTLINE' or 'THICKOUTLINE'
    label.fontSize = size or 16
    if label:SetFont(label.fontPath, label.fontSize, label.fontFlags) == false then
        label.fontPath = 'Fonts\\FRIZQT__.TTF'
        label:SetFont(label.fontPath, label.fontSize, label.fontFlags)
    end
    label:SetShadowColor(0.04, 0.015, 0.025, 0.85)
    label:SetShadowOffset(1.5, -2)
    label:SetPoint('TOPLEFT', x, y)
    label:SetTextColor(unpack(A.Theme.cream))
    label:SetText(text)
    return label
end
-- Gold highlights are live font glyphs in clipped bands, never rasterized text.
-- The base glyph supplies its dark outline and shadow below the highlight bands.
function A.GoldLabel(parent, text, x, y, size, width)
    local label = A.Label(parent, text, x, y, size)
    label:SetWidth(width)
    label:SetJustifyH('CENTER')
    label:SetTextColor(unpack(A.Theme.gold))
    label.goldBands = {}
    local colors = { { 1, 0.96, 0.67 }, { 1, 0.88, 0.38 }, { 1, 0.79, 0.19 }, { 0.97, 0.64, 0.09 } }
    for i, color in ipairs(colors) do
        local clip = CreateFrame('Frame', nil, parent)
        clip:EnableMouse(false)
        clip:SetClipsChildren(true)
        clip:SetPoint('TOPLEFT', label, 'TOPLEFT', 0, -(i - 1) * size / 4)
        clip:SetPoint('TOPRIGHT', label, 'TOPRIGHT', 0, -(i - 1) * size / 4)
        clip:SetHeight(size / 4)
        local ink = clip:CreateFontString(nil, 'OVERLAY')
        ink:SetAllPoints(label)
        ink:SetFont(label.fontPath, size, label.fontFlags)
        ink:SetJustifyH('CENTER')
        ink:SetTextColor(unpack(color))
        ink:SetText(text)
        label.goldBands[i] = { clip = clip, ink = ink }
    end
    local setText = label.SetText
    label.SetText = function(self, value)
        setText(self, value)
        for _, band in ipairs(self.goldBands) do
            band.ink:SetText(value)
        end
    end
    return label
end
function A.FitText(label, text, width, size, minimum)
    if label.lastFitText == text then
        return
    end
    label.lastFitText = text
    label:SetWidth(0)
    label:SetWordWrap(false)
    label:SetText(text)
    local chosen = size
    label:SetFont(label.fontPath, chosen, label.fontFlags)
    local measured = label:GetStringWidth()
    while type(measured) == 'number' and measured > width and chosen > (minimum or 12) do
        chosen = chosen - 1
        label:SetFont(label.fontPath, chosen, label.fontFlags)
        measured = label:GetStringWidth()
    end
    if type(measured) == 'number' and measured > width then
        local shortened = text
        while #shortened > 3 and measured > width do
            shortened = shortened:sub(1, -2)
            label:SetText(shortened .. '...')
            measured = label:GetStringWidth()
        end
    end
    label:SetWidth(width)
    label.fontSize = chosen
    if label.goldBands then
        for i, band in ipairs(label.goldBands) do
            band.clip:ClearAllPoints()
            band.clip:SetPoint('TOPLEFT', label, 'TOPLEFT', 0, -(i - 1) * chosen / 4)
            band.clip:SetPoint('TOPRIGHT', label, 'TOPRIGHT', 0, -(i - 1) * chosen / 4)
            band.clip:SetHeight(chosen / 4)
            band.ink:SetFont(label.fontPath, chosen, label.fontFlags)
        end
    end
end
function A.Art(parent, name, x, y, w, h, layer)
    local texture = parent:CreateTexture(nil, layer or 'ARTWORK')
    texture:SetTexture(A.media .. name .. '.tga')
    texture:SetPoint('CENTER', parent, 'TOPLEFT', x, -y)
    texture:SetSize(w, h)
    return texture
end
-- Nine-slice panel artwork keeps the same edge thickness at every panel size.
function A.Panel(parent, x, y, width, height)
    local frame = CreateFrame('Frame', nil, parent)
    frame:SetPoint('TOPLEFT', x, -y)
    frame:SetSize(width, height)
    local uv = { 0, 0.18, 0.82, 1 }
    local xs = { 0, 10, width - 10, width }
    local ys = { 0, 10, height - 10, height }
    for row = 1, 3 do
        for col = 1, 3 do
            local t = frame:CreateTexture(nil, 'BACKGROUND')
            t:SetTexture(A.media .. 'HUDPanel.tga')
            t:SetTexCoord(uv[col], uv[col + 1], uv[row], uv[row + 1])
            t:SetPoint('TOPLEFT', xs[col], -ys[row])
            t:SetSize(xs[col + 1] - xs[col], ys[row + 1] - ys[row])
        end
    end
    return frame
end
function A.Button(parent, text, x, y, width, height, icon, callback)
    local b = CreateFrame('Button', nil, parent)
    b:SetPoint('TOPLEFT', x, -y)
    b:SetSize(width, height)
    local visual = CreateFrame('Frame', nil, b)
    visual:SetAllPoints()
    visual:EnableMouse(false)
    b.visual = visual
    local art = A.Art(visual, A.Faction() .. 'Button', width / 2, height / 2, width, height)
    local glyph = icon and A.Art(visual, icon, 25, height / 2, 24, 24, 'OVERLAY')
    local label = A.Label(visual, text, icon and 43 or 12, 0, 20)
    label:ClearAllPoints()
    label:SetPoint('LEFT', icon and 43 or 12, 0)
    label:SetJustifyH('CENTER')
    label:SetWidth(width - (icon and 54 or 24))
    b.SetText = function(_, value)
        A.FitText(label, value, width - (icon and 54 or 24), 20, 14)
    end
    b.SetIcon = function(_, name)
        if glyph then
            glyph:SetTexture(A.media .. name .. '.tga')
        end
    end
    b:SetText(text)
    local hover, pressed, amount = false, false, 0
    local function paint()
        visual:ClearAllPoints()
        visual:SetPoint('CENTER', b, 'CENTER', 0, pressed and not A.MotionReduced() and -2 or 0)
        visual:SetSize(width, height)
        visual:SetScale(A.MotionReduced() and 1 or (1 + amount * 0.035))
        art:SetVertexColor(
            pressed and 0.78 or 0.92 + amount * 0.08,
            pressed and 0.78 or 0.92 + amount * 0.08,
            pressed and 0.78 or 0.92 + amount * 0.08
        )
    end
    local function transition()
        if A.MotionReduced() then
            amount = hover and 1 or 0
            paint()
            b:SetScript('OnUpdate', nil)
            return
        end
        b:SetScript('OnUpdate', function(_, dt)
            local target = hover and 1 or 0
            local step = dt / A.Theme.buttonDuration
            amount = target > amount and math.min(target, amount + step) or math.max(target, amount - step)
            paint()
            if amount == target then
                b:SetScript('OnUpdate', nil)
            end
        end)
    end
    b:SetScript('OnEnter', function()
        hover = true
        transition()
    end)
    b:SetScript('OnLeave', function()
        hover = false
        pressed = false
        transition()
    end)
    b:SetScript('OnMouseDown', function()
        pressed = true
        paint()
    end)
    b:SetScript('OnMouseUp', function()
        pressed = false
        paint()
    end)
    b:SetScript('OnHide', function()
        hover = false
        pressed = false
        amount = 0
        b:SetScript('OnUpdate', nil)
        paint()
    end)
    b:SetScript('OnClick', callback)
    paint()
    return b
end
function A.ApplyAppearance()
    if A.frame and A.frame.art then
        A.frame.art:SetAlpha(A.db.appearance.opacity or 0.97)
        A.frame.art:SetVertexColor(1, 1, 1)
    end
end
function A.Skin(frame)
    frame:SetBackdrop({
        edgeFile = 'Interface\\Tooltips\\UI-Tooltip-Border',
        edgeSize = 12,
        insets = { left = 4, right = 4, top = 4, bottom = 4 },
    })
    frame:SetBackdropBorderColor(0.74, 0.55, 0.22)
end
function A.Faction()
    return UnitFactionGroup and UnitFactionGroup('player') == 'Horde' and 'Horde' or 'Alliance'
end
function A.Number(value)
    local formatted = tostring(math.floor(value))
    while true do
        local n
        formatted, n = formatted:gsub('^(-?%d+)(%d%d%d)', '%1,%2')
        if n == 0 then
            return formatted
        end
    end
end
