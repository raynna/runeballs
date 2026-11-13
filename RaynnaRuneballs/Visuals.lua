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
local specialBursts = {}
local specialColors = { Bomb = { 1, 0.48, 0.08 }, Frost = { 0.3, 0.85, 1 }, Rewind = { 0.75, 0.35, 1 } }
V.specialBursts = specialBursts
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
    for lane = 1, 2 do
        local burst = { particles = {} }
        burst.core = A.Art(board.effectLayer, 'Halo', 0, 0, 80, 80, 'OVERLAY')
        burst.core:SetBlendMode('BLEND')
        burst.core:Hide()
        for i = 1, 12 do
            burst.particles[i] = A.Art(board.effectLayer, 'Spark', 0, 0, 12, 12, 'OVERLAY')
            burst.particles[i]:Hide()
        end
        specialBursts[lane] = burst
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
    move(board.launcher, 380, 250 - 5 / 0.86)
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
    for _, burst in ipairs(specialBursts) do
        burst.core:Hide()
        for _, particle in ipairs(burst.particles) do
            particle:Hide()
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
    for lane, burst in ipairs(specialBursts) do
        local state = lane == 1 and r or r.other
        local impact = state and state.specialImpact
        burst.core:SetShown(impact ~= nil)
        if impact then
            local progress = math.min(1, impact.age / 1.1)
            local reduced = A.MotionReduced()
            local color = specialColors[impact.kind]
            local rewind = impact.kind == 'Rewind'
            burst.core:SetTexture(A.media .. (rewind and 'PortalSwirl' or 'SpecialRing') .. '.tga')
            burst.core:SetVertexColor(unpack(color))
            move(burst.core, impact.x, impact.y)
            local size = reduced and 55 or rewind and (85 - progress * 45) or (40 + progress * 100)
            burst.core:SetSize(size, size)
            burst.core:SetAlpha((1 - progress) * 0.95)
            burst.core:SetRotation(not reduced and rewind and -progress * 5 or 0)
            for i, particle in ipairs(burst.particles) do
                particle:SetShown(not reduced)
                if not reduced then
                    local angle = i * math.pi / 6 + (rewind and -progress * 4 or 0)
                    local radius = rewind and (65 * (1 - progress))
                        or (10 + progress * (i % 2 == 0 and 70 or 45))
                    local gravity = impact.kind == 'Bomb' and progress * progress * 35 or 0
                    move(
                        particle,
                        impact.x + math.cos(angle) * radius,
                        impact.y + math.sin(angle) * radius + gravity
                    )
                    if impact.kind == 'Bomb' and impact.d then
                        local direction = i <= 6 and -1 or 1
                        local distance = impact.d + direction * progress * 90 * (0.5 + (i % 6) / 10)
                        local x, y = A.Engine.Point(impact.route or A.Engine.Route(state), distance)
                        move(particle, x + math.cos(angle) * 8, y + math.sin(angle) * 8)
                    end
                    particle:SetTexture(A.media .. 'SpecialSpark' .. '.tga')
                    particle:SetVertexColor(unpack(color))
                    particle:SetSize(
                        (impact.kind == 'Frost' and 22 or 18) * (1 - progress * 0.6),
                        18 * (1 - progress * 0.6)
                    )
                    particle:SetRotation(angle + progress * (rewind and -4 or 2))
                    particle:SetAlpha((1 - progress) * 0.9)
                end
            end
        else
            for _, particle in ipairs(burst.particles) do
                particle:Hide()
            end
        end
    end
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
    move(board.launcher, 380 - aimX * kick, 250 - aimY * kick - 5 / 0.86)
    move(board.loaded, 380 - aimX * kick, 250 - aimY * kick)
    muzzle:SetShown(moving and recoil > 0)
    if moving and recoil > 0 then
        move(muzzle, 380 + aimX * 28, 250 + aimY * 28)
        muzzle:SetAlpha(recoil / 0.14)
        muzzle:SetSize(20 + recoil * 90, 20 + recoil * 90)
    end
    local shot = r.shot
    local ability = shot and shot.kind or r.loadedKind
    specialGlow:SetShown(ability ~= nil)
    if ability then
        move(specialGlow, shot and shot.kind and shot.x or 380, shot and shot.kind and shot.y or 250)
        specialGlow:SetTexture(A.media .. 'SpecialRing.tga')
        specialGlow:SetBlendMode('BLEND')
        specialGlow:SetVertexColor(unpack(specialColors[ability]))
        local size = shot and shot.kind and 37 or 44
        local pulse = moving and math.sin(timer * 5) * 2 or 0
        specialGlow:SetSize(size + pulse, size + pulse)
        specialGlow:SetAlpha(0.85)
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
            t:SetVertexColor(unpack(shot.kind and specialColors[shot.kind] or A.colors[shot.color]))
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
