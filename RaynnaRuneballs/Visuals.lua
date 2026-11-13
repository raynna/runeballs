local _, A = ...
local V = {}
A.Visuals = V
local board, frame
local timer = 0
local lastShots, lastRun, lastBurst
local recoil, shake = 0, 0
local aimX, aimY = 0, -1
local pressure
local trail, pops, embers, orbit = {}, {}, {}, {}
local glow, arrow, muzzle, specialGlow
local holeSparks = {}
V.holes = {}
local function move(t, x, y)
    t:ClearAllPoints()
    t:SetPoint('CENTER', board, 'TOPLEFT', x, -y * 0.86)
end
function V.Build(owner, field)
    frame, board = owner, field
    glow = A.Art(board, 'Halo', 380, 250 * 0.86, 125, 125, 'BACKGROUND')
    glow:SetVertexColor(0.71, 0.30, 1)
    glow:SetBlendMode('ADD')
    arrow = A.Art(board, 'AimArrow', 380, 200 * 0.86, 22, 26, 'OVERLAY')
    muzzle = A.Art(board, 'Spark', 380, 250 * 0.86, 35, 35, 'OVERLAY')
    muzzle:Hide()
    specialGlow = A.Art(board.effectLayer, 'Halo', 0, 0, 52, 52, 'OVERLAY')
    specialGlow:SetBlendMode('ADD')
    specialGlow:Hide()
    for i = 1, 6 do
        trail[i] = A.Art(board.effectLayer, 'Halo', 0, 0, 24, 24, 'OVERLAY')
        trail[i]:SetBlendMode('ADD')
        trail[i]:Hide()
        embers[i] = A.Art(board.effectLayer, 'Dot', 0, 0, 4, 4, 'OVERLAY')
        embers[i]:SetVertexColor(1, 0.5, 0.15)
        embers[i]:Hide()
    end
    for i = 1, 3 do
        orbit[i] = A.Art(board.effectLayer, 'Dot', 0, 0, 4, 4, 'BORDER')
        orbit[i]:SetVertexColor(0.7, 0.4, 1)
        orbit[i]:Hide()
    end
    local portalLayer = CreateFrame('Frame', nil, board)
    portalLayer:SetAllPoints(board)
    portalLayer:SetFrameLevel(board:GetFrameLevel() + 4)
    portalLayer:EnableMouse(false)
    for i = 1, 2 do
        local hole = {}
        hole.entry = A.Art(portalLayer, 'Halo', 0, 0, 30, 30, 'OVERLAY')
        hole.entry:SetVertexColor(0.1, 1, 0.65)
        hole.entry:SetBlendMode('ADD')
        hole.exit = A.Art(portalLayer, 'Halo', 0, 0, 28, 28, 'OVERLAY')
        hole.exit:SetVertexColor(0.65, 0.18, 1)
        hole.exit:SetBlendMode('ADD')
        hole.swirl = { A.Art(portalLayer, 'PortalSwirl', 0, 0, 28, 28, 'OVERLAY') }
        hole.swirl[1]:SetBlendMode('ADD')
        V.holes[i] = hole
    end
    for i = 1, 16 do
        holeSparks[i] = A.Art(portalLayer, 'Spark', 0, 0, 10, 10, 'OVERLAY')
        holeSparks[i]:SetBlendMode('ADD')
        holeSparks[i]:Hide()
    end
    for i = 1, 32 do
        pops[i] = A.Art(board.effectLayer, 'Ball1', 0, 0, 27, 27, 'ARTWORK')
        pops[i]:Hide()
    end
end
function V.Reset()
    if not board then
        return
    end
    recoil, shake = 0, 0
    board:ClearAllPoints()
    board:SetPoint('TOPLEFT', 132, -155)
    move(board.launcher, 380, 250)
    move(board.loaded, 380, 250)
    for _, list in ipairs({ trail, pops, embers, orbit, holeSparks }) do
        for _, t in ipairs(list) do
            t:Hide()
        end
    end
    for _, hole in ipairs(V.holes) do
        hole.entry:Hide()
        hole.exit:Hide()
        for _, dot in ipairs(hole.swirl) do
            dot:Hide()
        end
    end
    muzzle:Hide()
    specialGlow:Hide()
    arrow:Hide()
end
function V.Pressure(target)
    if not pressure or A.MotionReduced() or not frame:GetScript('OnUpdate') then
        pressure = target
    end
    return pressure
end
function V.Tick(dt, r)
    timer = timer + dt
    if lastRun ~= r then
        lastRun = r
        lastShots = r.shotsFired
        lastBurst = nil
        pressure = nil
    end
    local x, y = GetCursorPosition()
    x, y = A.CursorToBoard(x, y, board:GetEffectiveScale(), board:GetLeft(), board:GetTop())
    local dx, dy = x - 380, y - 250
    local length = math.sqrt(dx * dx + dy * dy)
    if length > 10 then
        aimX, aimY = dx / length, dy / length
    end
    if lastShots ~= (r.shotsFired or 0) then
        if (r.shotsFired or 0) > (lastShots or 0) then
            recoil = 0.14
        end
        lastShots = r.shotsFired or 0
    end
    if r.burst and r.burst ~= lastBurst then
        lastBurst = r.burst
        if r.burst.combo > 1 then
            shake = 0.15
        end
    end
    recoil = math.max(0, recoil - dt)
    shake = math.max(0, shake - dt)
    local target = A.Engine.Pressure(r)
    pressure = pressure and pressure + (target - pressure) * math.min(1, dt * 10) or target
    local offset = A.MotionReduced() and 0 or math.sin(timer * 80) * math.min(2, shake * 14)
    board:ClearAllPoints()
    board:SetPoint('TOPLEFT', 132 + offset, -155)
end
function V.Draw(r, active)
    local animated = not A.MotionReduced() and not r.paused
    for i, hole in ipairs(V.holes) do
        local lane = i == 1 and r or r.other
        local sealed = r.ending and r.ending.won
        hole.entry:SetShown(lane ~= nil)
        hole.exit:SetShown(lane ~= nil and not sealed)
        if lane then
            local route = A.Engine.Route(lane)
            local ex, ey = A.Engine.Point(route, 14)
            move(hole.entry, ex, ey)
            hole.entry:SetAlpha(animated and (0.4 + math.sin(timer * 2.2 + i) * 0.2) or 0.4)
            local x, y = A.Engine.Point(route, A.Engine.Path(route).length)
            move(hole.exit, x, y)
            hole.exit:SetAlpha(animated and (0.6 + math.sin(timer * 1.7) * 0.12) or 0.55)
            local draining = r.ending and r.ending.phase == 'drain'
            local swirl = hole.swirl[1]
            swirl:SetShown(animated and not sealed)
            move(swirl, x, y)
            swirl:SetRotation(-timer * (draining and 3.5 or 0.8))
            swirl:SetAlpha(0.95)
        else
            for _, dot in ipairs(hole.swirl) do
                dot:Hide()
            end
        end
    end
    for i, spark in ipairs(holeSparks) do
        local lane = i <= 8 and r or r.other
        local visible = lane
            and not r.paused
            and not A.MotionReduced()
            and r.ending
            and r.ending.phase == 'drain'
        spark:SetShown(not not visible)
        if visible then
            local x, y = A.Engine.Point(A.Engine.Route(lane), A.Engine.Path(A.Engine.Route(lane)).length)
            local draining = r.ending and r.ending.phase == 'drain'
            local phase = (timer * (draining and 1.3 or 0.22) + (i % 8) / 8) % 1
            local radius = draining and (24 * (1 - phase)) or 18 + math.sin(timer * 2 + i) * 2
            local angle = phase * math.pi * 2
            move(spark, x + math.cos(angle) * radius, y + math.sin(angle) * radius / 0.86)
            spark:SetAlpha(draining and (1 - phase) * 0.8 or 0.35)
            spark:SetVertexColor(0.45, 0.65, 1)
            spark:SetSize(draining and 12 or 7, draining and 12 or 7)
        end
    end
    local moving = not A.MotionReduced() and not r.paused and r.status == 'playing'
    glow:SetAlpha(moving and (0.5 + math.sin(timer * 2) * 0.15) or 0.45)
    arrow:SetShown(r.status == 'playing')
    move(arrow, 380 + aimX * 49, 250 + aimY * 49)
    arrow:SetRotation(-math.atan2(aimY, aimX) - math.pi / 2)
    local kick = moving and recoil / 0.14 * 4 or 0
    move(board.launcher, 380 - aimX * kick, 250 - aimY * kick)
    move(board.loaded, 380 - aimX * kick, 250 - aimY * kick)
    muzzle:SetShown(moving and recoil > 0)
    if moving and recoil > 0 then
        move(muzzle, 380 + aimX * 28, 250 + aimY * 28)
        muzzle:SetAlpha(recoil / 0.14)
        muzzle:SetSize(20 + recoil * 90, 20 + recoil * 90)
    end
    local shot = r.shot
    specialGlow:SetShown(shot and shot.kind ~= nil or false)
    if shot and shot.kind then
        move(specialGlow, shot.x, shot.y)
        specialGlow:SetVertexColor(
            shot.kind == 'Bomb' and 1 or 0.5,
            shot.kind == 'Frost' and 0.9 or 0.4,
            shot.kind == 'Bomb' and 0.15 or 1
        )
    end
    for i, t in ipairs(trail) do
        local visible = shot ~= nil and moving
        t:SetShown(visible)
        if visible then
            local speed = math.sqrt(shot.vx ^ 2 + shot.vy ^ 2)
            local x, y = shot.x - shot.vx / speed * i * 7, shot.y - shot.vy / speed * i * 7
            move(t, x, y)
            t:SetShown(x >= 0 and x <= 760 and y >= 0 and y <= 500)
            t:SetAlpha((1 - i / 7) * 0.7)
            t:SetSize(24 - i * 2, 24 - i * 2)
            t:SetVertexColor(unpack(A.colors[shot.color]))
        end
    end
    for i, t in ipairs(pops) do
        local e = (active or r.effects)[i]
        local visible = e and e.age < 0.16 and not A.MotionReduced()
        t:SetShown(not not visible)
        if visible then
            t:SetTexture(A.media .. 'Ball' .. e.color .. '.tga')
            move(t, e.x, e.y)
            local size = 27 + math.sin(e.age / 0.16 * math.pi) * 12
            t:SetSize(size, size)
            t:SetAlpha(1 - e.age / 0.16)
        end
    end
    for i, t in ipairs(embers) do
        t:SetShown(moving)
        if moving then
            local f = (timer * 0.18 + i * 0.137) % 1
            move(
                t,
                i % 2 == 0 and 12 + math.sin(timer + i) * 4 or 748 + math.sin(timer + i) * 4,
                470 - f * 400
            )
            t:SetAlpha(math.sin(f * math.pi) * 0.45)
        end
    end
    for i, t in ipairs(orbit) do
        t:SetShown(moving)
        if moving then
            local angle = timer * 0.5 + i * 2.094
            move(t, 380 + math.cos(angle) * 43, 250 + math.sin(angle) * 43)
            t:SetAlpha(0.65)
        end
    end
end
