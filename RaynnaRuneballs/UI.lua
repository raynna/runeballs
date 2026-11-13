local _, A = ...
local E = A.Engine
local frame, board
local balls, aimDots, tracks, effects, fragments = {}, {}, {}, {}, {}
local active = {}
local clock = 0
local entrances, bridges = {}, {}
local covers, upperRoad, entryCovers
local guides = {}
local guideCount = 0
local roadLevel
local YS = 0.86
local update
local function move(texture, x, y)
    texture:ClearAllPoints()
    texture:SetPoint('CENTER', board, 'TOPLEFT', x, -y * YS)
end
local function ball(index)
    if not balls[index] then
        balls[index] = A.Art(board, 'Ball1', 0, 0, 27, 27)
    end
    return balls[index]
end
local function cursor()
    local x, y = GetCursorPosition()
    local scale = board:GetEffectiveScale()
    return A.CursorToBoard(x, y, scale, board:GetLeft(), board:GetTop())
end
function A.CursorToBoard(x, y, scale, left, top)
    return x / scale - left, (top - y / scale) / YS
end
function A.Pause()
    if A.db.run then
        A.db.run.paused = true
    end
    if frame then
        frame:SetScript('OnUpdate', nil)
    end
    for _, dot in ipairs(aimDots) do
        dot:Hide()
    end
    if A.Visuals then
        A.Visuals.Reset()
    end
end
-- Copy the exact background UV region over the lower lane. The upper road
-- has its own draw frame, so crossing geometry stays continuous above it.
local function cover(pool, index, parent, left, top, width, height)
    local patch = pool[index]
    if not patch then
        patch = parent:CreateTexture(nil, 'ARTWORK')
        pool[index] = patch
    end
    patch:SetTexture(A.media .. A.Faction() .. 'Frame.tga')
    patch:ClearAllPoints()
    patch:SetPoint('TOPLEFT', board, 'TOPLEFT', left, -top)
    patch:SetSize(width, height)
    patch:SetTexCoord(
        (132 + left) / 1024,
        (132 + left + width) / 1024,
        (155 + top) / (2048 / 3),
        (155 + top + height) / (2048 / 3)
    )
    patch:SetVertexColor(1, 1, 1, 1)
    patch:Show()
end
local function coveredGuide(route, from, to, parent)
    for distance = from, to, 26 do
        local x, y = E.Point(route, distance)
        local px, py = E.Point(route, distance - 4)
        local angle = math.atan2((y - py) * YS, x - px)
        -- Two short strokes form a forward chevron, not a font glyph.
        for side = -1, 1, 2 do
            guideCount = guideCount + 1
            local arrow = guides[guideCount]
            if not arrow then
                arrow = parent:CreateTexture(nil, 'OVERLAY')
                arrow:SetTexture('Interface\\Buttons\\WHITE8X8')
                guides[guideCount] = arrow
            end
            arrow:SetParent(parent)
            local wing = angle + side * 0.65
            move(arrow, x - math.cos(wing) * 3, y - math.sin(wing) * 3 / YS)
            arrow:SetSize(7, 2)
            arrow:SetRotation(-wing)
            arrow:SetVertexColor(0.74, 0.61, 0.41, 0.7)
            arrow:Show()
        end
    end
end
local function exitAngle(lane)
    local length = E.Path(E.Route(lane)).length
    local x, y = E.Point(E.Route(lane), length)
    local px, py = E.Point(E.Route(lane), length - 10)
    return -math.atan2((y - py) * YS, x - px)
end
local function drawRoad(level)
    if roadLevel == level then
        return
    end
    roadLevel = level
    local index = 0
    guideCount = 0
    local routes = { level }
    if A.db.run.other then
        routes[2] = E.Route(A.db.run.other)
    end
    for lane, route in ipairs(routes) do
        local path = E.Path(route)
        index = index + 1
        if not tracks[index] then
            tracks[index] = A.Art(board, 'Road' .. route, 380, 215, 816, 430, 'BACKGROUND')
        end
        local road = tracks[index]
        road:SetParent(lane == 1 and upperRoad or board)
        road:SetTexture(A.media .. 'Road' .. route .. '.tga')
        move(road, 380, 250)
        road:SetSize(816, 430)
        road:Show()
        if not entrances[lane] then
            entrances[lane] = A.Art(lane == 1 and upperRoad or board, 'Entry', 0, 0, 60, 60, 'BORDER')
        end
        local sx, sy = E.Point(route, 14)
        local tx, ty = E.Point(route, 24)
        move(entrances[lane], sx, sy)
        entrances[lane]:SetRotation(-math.atan2((ty - sy) * YS, tx - sx))
        entrances[lane]:SetVertexColor(0.8, 0.9, 1, 1)
        entrances[lane]:Show()
    end
    for i = #routes + 1, #entrances do
        entrances[i]:Hide()
    end
    for i = index + 1, #tracks do
        tracks[i]:Hide()
    end
    local crossing = A.db.run.other and E.Crossings(level) or {}
    for i, cross in ipairs(crossing) do
        -- Lower-road gaps are baked along the route, never rectangular background masks.
        coveredGuide(
            level + 1000,
            cross.under - E.TunnelHalf(cross),
            cross.under + E.TunnelHalf(cross),
            covers
        )
    end
    for i = guideCount + 1, #guides do
        guides[i]:Hide()
    end
    for i = #crossing + 1, #bridges do
        bridges[i]:Hide()
    end
end
local function shotArt(color, kind)
    return A.media .. (kind or 'Ball' .. color) .. '.tga'
end
function A.Draw()
    if not frame then
        return
    end
    local r = A.db.run
    local burst = r.burst
    if r.other and r.other.burst and (not burst or r.other.burst.age < burst.age) then
        burst = r.other.burst
    end
    drawRoad(r.level)
    frame.art:SetTexture(A.media .. A.Faction() .. 'Frame.tga')
    frame.footer:SetTexture(A.media .. A.Faction() .. 'Frame.tga')
    board.launcher:SetTexture(A.media .. A.Faction() .. 'Launcher.tga')
    local visualIndex = 0
    for _, lane in ipairs(r.other and { r, r.other } or { r }) do
        for _, b in ipairs(lane.balls) do
            visualIndex = visualIndex + 1
            local texture = ball(visualIndex)
            texture:SetParent(lane == r and upperRoad or board)
            texture:SetTexture(shotArt(b.color))
            move(texture, E.Point(E.Route(lane), b.d))
            texture:SetShown(b.d >= 8 and (b.d < 24 or not E.Hidden(lane, b.d)))
            local shrink = 1
            if lane.ending and lane.ending.phase == 'drain' then
                shrink = math.max(0.05, math.min(1, (E.Path(E.Route(lane)).length + 18 - b.d) / 38))
            end
            texture:SetSize(27 * shrink, 27 * shrink)
            texture:SetAlpha(shrink * math.max(0, math.min(1, (b.d - 8) / 12)))
        end
    end
    for i = visualIndex + 1, #balls do
        balls[i]:Hide()
    end
    board.otherExit:SetShown(r.other ~= nil)
    if r.other then
        move(board.otherExit, E.Point(E.Route(r.other), E.Path(E.Route(r.other)).length))
        board.otherExit:SetRotation(exitAngle(r.other))
        board.otherExit:SetSize(60, 60)
        board.otherExit:SetAlpha(1)
        if r.ending and r.ending.won then
            local seal = math.max(0, 1 - r.ending.age / 1.1)
            board.otherExit:SetSize(math.max(1, 60 * seal), math.max(1, 60 * seal))
            board.otherExit:SetAlpha(seal)
        elseif r.ending and r.ending.phase == 'drain' then
            board.otherExit:SetSize(66, 66)
        end
    end
    board.loaded:SetTexture(shotArt(r.loaded, r.loadedKind))
    board.next:SetTexture(shotArt(r.next, r.nextKind))
    board.shot:SetShown(r.shot ~= nil)
    if r.shot then
        move(board.shot, r.shot.x, r.shot.y)
        board.shot:SetTexture(shotArt(r.shot.color, r.shot.kind))
    end
    local ex, ey = E.Point(r.level, E.Path(r.level).length)
    move(board.exit, ex, ey)
    local danger = r.head > E.Path(r.level).length - 240
    board.exit:SetVertexColor(1, danger and 0.35 or 1, danger and 0.35 or 1)
    board.exit:SetRotation(exitAngle(r))
    board.exit:SetSize(
        60 + (A.MotionReduced() and 0 or math.sin(clock * (danger and 10 or 3)) * 4),
        60 + (A.MotionReduced() and 0 or math.sin(clock * (danger and 10 or 3)) * 4)
    )
    board.exit:SetAlpha(1)
    if r.ending then
        if r.ending.won then
            local seal = math.max(0, 1 - r.ending.age / 1.1)
            board.exit:SetSize(math.max(1, 60 * seal), math.max(1, 60 * seal))
            board.exit:SetAlpha(seal)
        elseif r.ending.phase == 'drain' then
            board.exit:SetRotation(exitAngle(r))
            board.exit:SetSize(66, 66)
        end
    end
    A.FitText(frame.stats, 'ROUND ' .. r.level, 155, 25, 16)
    A.FitText(frame.mapName, E.MapName(r.level), 165, 14, 10)
    A.FitText(frame.score, A.Number(r.score), frame.scoreWidth, 24, 12)
    A.FitText(frame.best, A.Number(A.db.best), frame.scoreWidth, 24, 12)
    frame.progress:SetText(tostring(E.Remaining(r)))
    local pressure = E.Pressure(r)
    frame.pressure:SetValue(A.Visuals.Pressure(pressure))
    local tint = pressure < 0.55 and A.Theme.blue or pressure < 0.8 and A.Theme.amber or A.Theme.red
    frame.pressure:SetStatusBarColor(unpack(tint))
    frame.pressure:SetAlpha(
        pressure > 0.92 and not A.MotionReduced() and (0.8 + math.sin(clock * 8) * 0.2) or 1
    )
    frame.pressureLabel:SetText(danger and 'PORTAL DANGER' or 'PORTAL THREAT')
    board.combo:SetShown(burst ~= nil)
    if burst then
        board.combo:ClearAllPoints()
        board.combo:SetPoint(
            'CENTER',
            board,
            'TOPLEFT',
            burst.x,
            -burst.y * YS + 28 + (A.MotionReduced() and 0 or burst.age * 35)
        )
        board.combo:SetText(
            (
                burst.combo >= 3 and 'CHAIN REACTION! x' .. burst.combo .. '\n'
                or burst.combo == 2 and 'COMBO! x2\n'
                or ''
            )
                .. '+'
                .. A.Number(burst.count * 100 * burst.combo)
        )
        board.combo:SetAlpha(math.max(0, 1 - burst.age / (burst.combo > 1 and 0.9 or 0.55)))
    end
    local message = 'Seal the portal'
    if r.status == 'won' then
        message = 'Portal sealed'
    elseif r.status == 'lost' then
        message = 'Round over'
    elseif r.paused then
        message = 'Paused'
    elseif (r.reverse or 0) > 0 then
        message = 'Rewinding'
    elseif (r.slow or 0) > 0 then
        message = 'Frozen'
    elseif burst then
        message = (
            burst.combo > 1 and 'CHAIN x' .. burst.combo .. '!  '
            or burst.kind == 'Explosion' and 'BOOM!  '
            or 'MATCH!  '
        )
            .. '+'
            .. A.Number(burst.count * 100 * burst.combo)
    elseif danger then
        message = 'Portal danger'
    end
    if r.ending and not r.ending.done then
        if r.ending.phase == 'drain' then
            message = 'Into the void...'
        elseif r.ending.phase == 'celebrate' then
            message = 'Portal sealed'
        end
    end
    A.FitText(frame.message, message:upper(), 213, 18, 12)
    local resultVisible = r.status ~= 'playing' and (not r.ending or r.ending.phase == 'result')
    frame.result:SetShown(resultVisible)
    if not resultVisible and frame.share then
        frame.share:Hide()
    end
    if resultVisible then
        local won = r.status == 'won'
        local t = (not A.MotionReduced() and r.ending) and math.min(1, r.ending.popupAge / 0.35) or 1
        frame.result:SetAlpha(t)
        frame.result:SetScale(0.82 + 0.18 * (1 - (1 - t) ^ 3))
        A.FitText(
            frame.result.title,
            won and (r.level >= E.MAX_LEVEL and 'CAMPAIGN CLEARED!' or 'VICTORY!') or 'THE VOID WINS',
            360,
            30,
            20
        )

        frame.result.title:SetTextColor(won and 1 or 1, won and 0.84 or 0.35, won and 0.25 or 0.25)
        frame.result.detail:SetText(
            'Round '
                .. r.level
                .. '  |  '
                .. E.MapName(r.level)
                .. '\n\nScore  '
                .. A.Number(r.score)
                .. '    Best  '
                .. A.Number(A.db.best)
        )
        frame.result.action:SetText(
            won and (r.level >= E.MAX_LEVEL and 'PLAY AGAIN' or 'NEXT ROUND') or 'NEW GAME'
        )
        frame.result.action:SetEnabled(not r.ending or r.ending.done)
    end
    frame.special:SetText(
        r.loadedKind and (r.loadedKind .. ' ready  -  Click to fire') or 'Match 3 or more coloured balls!'
    )
    frame.play:SetIcon(r.status == 'playing' and not r.paused and 'PauseIcon' or 'PlayIcon')
    frame.play:SetText(
        r.status == 'won' and (r.level >= E.MAX_LEVEL and 'PLAY AGAIN' or 'NEXT ROUND')
            or r.status == 'lost' and 'NEW GAME'
            or r.paused and 'PLAY'
            or 'PAUSE'
    )
    for i = #active, 1, -1 do
        active[i] = nil
    end
    for _, e in ipairs(r.effects) do
        active[#active + 1] = e
    end
    if r.other then
        for _, e in ipairs(r.other.effects) do
            if #active < 32 then
                active[#active + 1] = e
            end
        end
    end
    A.Visuals.Draw(r, active)
    for i, e in ipairs(active) do
        if not effects[i] then
            effects[i] = A.Art(board.effectLayer, 'Spark', 0, 0, 1, 1, 'OVERLAY')
        end
        local t = effects[i]
        t:SetTexture(A.media .. (e.kind or 'Spark') .. '.tga')
        move(t, e.x, e.y)
        local size = (e.kind == 'Explosion' and 65 or 24) + e.age * (e.kind == 'Explosion' and 180 or 100)
        if A.MotionReduced() then
            size = e.kind == 'Explosion' and 65 or 24
        end
        t:SetSize(size, size)
        t:SetAlpha(math.max(0, 1 - e.age / 0.6))
        t:SetRotation(A.MotionReduced() and 0 or e.age * 2)
        t:Show()
        for j = 1, 3 do
            local k = (i - 1) * 3 + j
            if not fragments[k] then
                fragments[k] = A.Art(board.effectLayer, 'Ball1', 0, 0, 9, 9, 'OVERLAY')
            end
            local shard = fragments[k]
            local angle = j * 2.094 + i
            shard:SetTexture(shotArt(e.color))
            move(
                shard,
                e.x + math.cos(angle) * e.age * 115,
                e.y + math.sin(angle) * e.age * 115 + e.age * e.age * 70
            )
            shard:SetAlpha(math.max(0, 1 - e.age / 0.6))
            shard:SetShown(not A.MotionReduced())
        end
    end
    for i = #active + 1, #effects do
        effects[i]:Hide()
    end
    for i = #active * 3 + 1, #fragments do
        fragments[i]:Hide()
    end
end
update = function(_, elapsed)
    clock = clock + math.min(elapsed, 0.1)
    -- Consume the whole render interval, subdividing for swept collision safety.
    -- No leftover accumulator means high-refresh frames do not repeat positions.
    local remaining = math.min(elapsed, 0.1)
    while remaining > 0 do
        local step = math.min(remaining, 1 / 120)
        E.Step(A.db, step)
        remaining = remaining - step
    end
    local x, y = cursor()
    local dx, dy = x - 380, y - 250
    local length = math.sqrt(dx * dx + dy * dy)
    for i, dot in ipairs(aimDots) do
        dot:SetShown(
            A.db.options.aimGuide ~= false and length > 20 and x >= 0 and x <= 760 and y >= 0 and y <= 500
        )
        if length > 20 then
            move(dot, 380 + dx / length * (35 + i * 12), 250 + dy / length * (35 + i * 12))
        end
    end
    A.Visuals.Tick(math.min(elapsed, 0.1), A.db.run)
    A.Draw()
    if A.db.run.paused and (A.db.run.status == 'playing' or #A.db.run.effects == 0) then
        A.Pause()
    end
end
function A.Close()
    A.Pause()
    if frame.share then
        frame.share:Hide()
    end
    A.autoOpened = false
    if frame then
        frame:Hide()
    end
end
function A.Open(automatic)
    if not automatic then
        A.autoOpened = false
    end
    frame:Show()
    local r = A.db.run
    if r.ending and not r.ending.done then
        r.paused = false
        frame:SetScript('OnUpdate', update)
    end
    A.Draw()
end
function A.Toggle()
    if frame:IsShown() then
        A.Close()
    else
        A.Open(false)
    end
end
function A.SetScale(value)
    A.db.options.scale = math.max(0.55, math.min(1.3, value))
    if frame then
        local old = frame:GetEffectiveScale()
        local x, y = frame:GetLeft() * old, frame:GetTop() * old
        frame:SetScale(A.db.options.scale)
        local scale = frame:GetEffectiveScale()
        frame:ClearAllPoints()
        frame:SetPoint('TOPLEFT', UIParent, 'BOTTOMLEFT', x / scale, y / scale)
        A.db.options.position = { point = 'TOPLEFT', relative = 'BOTTOMLEFT', x = x / scale, y = y / scale }
    end
end
function A.BuildUI()
    frame = CreateFrame(
        'Frame',
        'RaynnaRuneballsFrame',
        UIParent,
        BackdropTemplateMixin and 'BackdropTemplate' or nil
    )
    A.frame = frame
    frame:SetSize(1024, 720)
    frame:SetFrameStrata('DIALOG')
    frame:SetClampedToScreen(true)
    frame:SetMovable(true)
    frame:EnableMouse(true)
    frame:SetScale(A.db.options.scale or 0.9)
    local pos = A.db.options.position
    if pos then
        frame:SetPoint(pos.point, UIParent, pos.relative, pos.x, pos.y)
    else
        frame:SetPoint('CENTER')
    end
    A.Skin(frame)
    -- An opaque stone footer fills the area below the 3:2 illustration.
    local backing = frame:CreateTexture(nil, 'BACKGROUND')
    backing:SetAllPoints(frame)
    backing:SetTexture('Interface\\Buttons\\WHITE8X8')
    backing:SetVertexColor(0.10, 0.08, 0.09, 1)
    frame.footer = A.Art(frame, A.Faction() .. 'Frame', 512, 665, 1024, 110, 'BORDER')
    frame.footer:SetTexCoord(132 / 1024, 892 / 1024, 400 / (2048 / 3), 510 / (2048 / 3))
    -- Keep the main illustration's aspect ratio and board coordinates unchanged.
    frame.art = A.Art(frame, A.Faction() .. 'Frame', 512, 1024 / 3, 1024, 2048 / 3, 'ARTWORK')
    A.ApplyAppearance()
    local shade = frame:CreateTexture(nil, 'OVERLAY')
    shade:SetPoint('TOPLEFT', 132, -155)
    shade:SetSize(760, 430)
    shade:SetTexture('Interface\\Buttons\\WHITE8X8')
    shade:SetVertexColor(0.07, 0.04, 0.08, 0.08)
    local title = CreateFrame('Frame', nil, frame)
    title:SetPoint('TOPLEFT', 5, -5)
    title:SetSize(960, 122)
    title:EnableMouse(true)
    title:RegisterForDrag('LeftButton')
    title:SetScript('OnDragStart', function()
        frame:StartMoving()
    end)
    title:SetScript('OnDragStop', function()
        frame:StopMovingOrSizing()
        local point, _, relative, x, y = frame:GetPoint()
        A.db.options.position = { point = point, relative = relative, x = x, y = y }
    end)
    local close = CreateFrame('Button', nil, frame)
    close:SetPoint('TOPRIGHT', -15, -12)
    close:SetSize(30, 30)
    close:SetNormalTexture(A.media .. 'CloseIcon.tga')
    close:SetHighlightTexture('Interface\\Buttons\\UI-Common-MouseHilight', 'ADD')
    close:SetScript('OnClick', A.Close)
    frame.closeButton = close
    frame.stats = A.GoldLabel(frame, '', 181, -68, 25, 155)
    frame.mapName = A.Label(frame, '', 177, -101, 14, 'body')
    frame.mapName:SetWidth(165)
    frame.mapName:SetJustifyH('CENTER')
    frame.mapName:SetHeight(24)
    local alliance = A.Faction() == 'Alliance'
    local scoreLeft, bestLeft = alliance and 690 or 689, alliance and 784 or 818
    local width = alliance and 84 or 109
    frame.scoreWidth = width
    for _, entry in ipairs({ { scoreLeft, 'Trophy', 'SCORE' }, { bestLeft, 'Crown', 'BEST' } }) do
        local center = entry[1] + width / 2
        A.Art(frame, entry[2], center - 30, 82, 14, 14, 'OVERLAY')
        local heading = A.Label(frame, entry[3], center - 18, -71, 12)
        heading:SetWidth(60)
        heading:SetJustifyH('CENTER')
    end
    frame.score = A.GoldLabel(frame, '', scoreLeft, -94, 24, width)
    frame.best = A.GoldLabel(frame, '', bestLeft, -94, 24, width)
    board = CreateFrame('Frame', nil, frame)
    A.board = board
    board:SetPoint('TOPLEFT', 132, -155)
    board:SetSize(760, 430)
    board:EnableMouse(true)
    local stone = board:CreateTexture(nil, 'BACKGROUND')
    stone:SetAllPoints(board)
    stone:SetTexture(A.media .. A.Faction() .. 'Frame.tga')
    stone:SetTexCoord(132 / 1024, 892 / 1024, 155 / (2048 / 3), 585 / (2048 / 3))
    covers = CreateFrame('Frame', nil, board)
    covers:SetAllPoints(board)
    covers:SetFrameLevel(board:GetFrameLevel() + 1)
    covers:EnableMouse(false)
    upperRoad = CreateFrame('Frame', nil, board)
    upperRoad:SetAllPoints(board)
    upperRoad:SetFrameLevel(board:GetFrameLevel() + 2)
    upperRoad:EnableMouse(false)
    entryCovers = CreateFrame('Frame', nil, board)
    entryCovers:SetAllPoints(board)
    entryCovers:SetFrameLevel(board:GetFrameLevel() + 3)
    entryCovers:EnableMouse(false)
    board.effectLayer = CreateFrame('Frame', nil, board)
    board.effectLayer:SetAllPoints(board)
    board.effectLayer:SetFrameLevel(board:GetFrameLevel() + 5)
    board.effectLayer:EnableMouse(false)
    board.exit = A.Art(upperRoad, 'Portal', 0, 0, 60, 60, 'BORDER')
    board.otherExit = A.Art(upperRoad, 'Portal', 0, 0, 60, 60, 'BORDER')
    board.launcher = A.Art(board, A.Faction() .. 'Launcher', 380, 250 * YS - 5, 104, 104, 'BORDER')
    for i = 1, 8 do
        aimDots[i] = A.Art(board, 'Dot', 0, 0, 5, 5, 'OVERLAY')
        aimDots[i]:Hide()
    end
    board.loaded = A.Art(board, 'Ball1', 380, 250 * YS, 34, 34, 'OVERLAY')
    board.next = A.Art(board, 'Ball1', 448, 250 * YS, 28, 28, 'OVERLAY')
    local nextLabel = A.Label(board, 'NEXT', 0, 0, 14)
    nextLabel:ClearAllPoints()
    nextLabel:SetPoint('TOP', board.next, 'BOTTOM', 0, -3)
    board.shot = A.Art(board.effectLayer, 'Ball1', 0, 0, 27, 27, 'OVERLAY')
    board.combo = A.Label(board.effectLayer, '', 0, 0, 25)
    board.combo:SetHeight(66)
    board.combo:SetWidth(360)
    board.combo:SetJustifyH('CENTER')
    board.combo:SetWordWrap(true)
    board.combo:SetTextColor(unpack(A.Theme.gold))
    board:SetScript('OnMouseDown', function(_, which)
        if which == 'RightButton' then
            E.Swap(A.db.run)
        elseif which == 'LeftButton' then
            E.Fire(A.db.run, cursor())
        end
        A.Draw()
    end)
    local threat = A.Panel(frame, 132, 590, 760, 27)
    frame.pressureLabel = A.Label(threat, 'PORTAL THREAT', 12, -2, 13)
    frame.pressure = CreateFrame('StatusBar', nil, threat)
    frame.pressure:SetPoint('TOPLEFT', 160, -8)
    frame.pressure:SetSize(585, 11)
    frame.pressure:SetStatusBarTexture('Interface\\Buttons\\WHITE8X8')
    frame.pressure:SetMinMaxValues(0, 1)
    local rail = frame.pressure:CreateTexture(nil, 'BACKGROUND')
    rail:SetAllPoints()
    rail:SetTexture('Interface\\Buttons\\WHITE8X8')
    rail:SetVertexColor(0.05, 0.03, 0.06, 1)
    local quest = A.Panel(frame, 35, 625, 290, 83)
    A.Art(quest, 'QuestGem', 31, 41, 38, 48, 'ARTWORK')
    frame.message = A.Label(quest, '', 62, -12, 18)
    frame.message:SetWidth(213)
    frame.message:SetJustifyH('CENTER')
    frame.special = A.Label(quest, '', 62, -40, 14, 'body')
    frame.special:SetWidth(213)
    frame.special:SetHeight(32)
    frame.special:SetWordWrap(true)
    frame.special:SetJustifyH('CENTER')
    local count = A.Panel(frame, 335, 625, 110, 83)
    A.Art(count, 'Marbles', 20, 22, 16, 16, 'ARTWORK')
    local countHeading = A.Label(count, 'MARBLES', 32, -12, 11)
    countHeading:SetWidth(66)
    countHeading:SetJustifyH('CENTER')
    frame.progress = A.GoldLabel(count, '', 12, -34, 28, 86)
    local controls = A.Panel(frame, 455, 625, 220, 83)
    for i, entry in ipairs({
        { 'MouseLeft', 'Left-click: shoot' },
        { 'MouseRight', 'Right-click: swap' },
        { 'EscapeKey', 'Esc: pause' },
    }) do
        A.Art(controls, entry[1], 24, 21 + (i - 1) * 21, 16, 18, 'ARTWORK')
        A.Label(controls, entry[2], 44, -11 - (i - 1) * 21, 13, 'body')
    end
    frame.play = A.Button(frame, 'PLAY', 685, 637, 145, 57, 'PlayIcon', function()
        local r = A.db.run
        if r.ending and not r.ending.done then
            r.paused = false
            frame:SetScript('OnUpdate', update)
            return
        end
        if r.status == 'won' then
            r = E.NewRun(
                A.db,
                r.level >= E.MAX_LEVEL and 1 or r.level + 1,
                r.level >= E.MAX_LEVEL and 0 or r.score
            )
        elseif r.status == 'lost' then
            A.db.level = 1
            r = E.NewRun(A.db, 1, 0)
        end
        r.paused = not r.paused
        if r.paused then
            A.Pause()
        else
            frame:SetScript('OnUpdate', update)
        end
        A.Draw()
    end)
    A.Button(frame, 'SETTINGS', 840, 637, 150, 57, 'SettingsIcon', A.OpenSettings)
    local result = A.Panel(board, 180, 100, 400, 285)
    frame.result = result
    result:ClearAllPoints()
    result:SetPoint('CENTER', board, 'CENTER')
    result:SetFrameLevel(board:GetFrameLevel() + 20)
    result:EnableMouse(true)
    result.title = A.Label(result, '', 0, 0, 34)
    result.title:ClearAllPoints()
    result.title:SetPoint('TOP', 0, -24)
    result.title:SetJustifyH('CENTER')
    result.detail = A.Label(result, '', 0, 0, 17, 'body')
    result.detail:ClearAllPoints()
    result.detail:SetPoint('TOP', 0, -79)
    result.detail:SetWidth(360)
    result.detail:SetHeight(72)
    result.detail:SetWordWrap(true)
    result.detail:SetJustifyH('CENTER')
    result.action = A.Button(result, 'NEXT ROUND', 21, 172, 178, 43, 'PlayIcon', function()
        local r = A.db.run
        if not r.ending or r.ending.done then
            frame.play:GetScript('OnClick')()
        end
    end)
    A.Button(result, 'CLOSE', 211, 172, 168, 43, 'CloseIcon', A.Close)
    A.Button(result, 'SHARE RESULT', 100, 226, 200, 43, nil, function()
        A.OpenShare()
    end)
    A.BuildShare(frame, board)
    result:Hide()
    A.Visuals.Build(frame, board)
    frame:SetScript('OnHide', function()
        A.Pause()
        A.Visuals.Reset()
    end)
    if UISpecialFrames then
        table.insert(UISpecialFrames, 'RaynnaRuneballsFrame')
    end
    frame:Hide()
    A.Draw()
end
