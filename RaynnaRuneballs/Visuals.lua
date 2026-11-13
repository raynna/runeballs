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
    specialGlow = A.Art(board, 'Halo', 0, 0, 52, 52, 'OVERLAY')
    specialGlow:SetBlendMode('ADD')
    specialGlow:Hide()
    for i = 1, 6 do
        trail[i] = A.Art(board, 'Halo', 0, 0, 24, 24, 'OVERLAY')
        trail[i]:SetBlendMode('ADD')
        trail[i]:Hide()
        embers[i] = A.Art(board, 'Dot', 0, 0, 4, 4, 'OVERLAY')
        embers[i]:SetVertexColor(1, 0.5, 0.15)
        embers[i]:Hide()
    end
    for i = 1, 3 do
        orbit[i] = A.Art(board, 'Dot', 0, 0, 4, 4, 'BORDER')
        orbit[i]:SetVertexColor(0.7, 0.4, 1)
        orbit[i]:Hide()
    end
    for i = 1, 32 do
        pops[i] = A.Art(board, 'Ball1', 0, 0, 27, 27, 'ARTWORK')
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
    for _, list in ipairs({ trail, pops, embers, orbit }) do
        for _, t in ipairs(list) do
            t:Hide()
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
