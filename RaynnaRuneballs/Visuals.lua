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
local glow, arrow, muzzle, specialGlow, ammoLight
local holeSparks = {}
local specialBursts = {}
local chainAuras = {}
V.chainAuras = chainAuras
local specialColors =
    { Bomb = { 1, 0.48, 0.08 }, Frost = { 0.3, 0.85, 1 }, Rewind = { 0.75, 0.35, 1 }, Rainbow = { 1, 1, 1 } }
for _, kind in ipairs({ 'Lightning', 'Paint', 'Stasis', 'Magnet', 'Treasure', 'Ward' }) do
    specialColors[kind] = { 1, 1, 1 }
end
local impactTextures = {
    Bomb = 'BombBurst',
    Frost = 'FrostBurst',
    Rewind = 'RewindBurst',
    Rainbow = 'RainbowBurst',
    Lightning = 'LightningFlash',
    Paint = 'PaintBurst',
    Stasis = 'StasisBurst',
    Magnet = 'MagnetBurst',
    Treasure = 'TreasureBurst',
    Ward = 'WardBurst',
}
local particleTextures = {
    Bomb = 'BombEmber',
    Rewind = 'EnergyMote',
    Rainbow = 'StarGlint',
    Lightning = 'LightningFlash',
    Paint = 'PaintDrop',
    Stasis = 'FrostShard',
    Magnet = 'EnergyMote',
    Treasure = 'CoinGlint',
    Ward = 'StarGlint',
    Frost = 'FrostShard',
}
V.impactTextures = impactTextures
local lightningLists = { 'arcs', 'arcBlooms', 'arcCores', 'hitLights', 'hitFlashes' }
V.specialBursts = specialBursts
V.holes = {}
local function move(t, x, y)
    t:ClearAllPoints()
    t:SetPoint('CENTER', board, 'TOPLEFT', x, -y * 0.86)
end
local function lightColor(color, kind, animated)
    if kind == 'Rainbow' then
        if not animated then
            return A.colors[6]
        end
        local phase = (timer * 1.5) % 6
        local first = math.floor(phase) + 1
        local nextColor = first % 6 + 1
        local fraction = phase - math.floor(phase)
        local tint = {}
        for i = 1, 3 do
            tint[i] = A.colors[first][i] * (1 - fraction) + A.colors[nextColor][i] * fraction
        end
        return tint
    end
    return A.colors[color] or A.colors[6]
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
    ammoLight = A.Art(board.effectLayer, 'SpecialLight', 380, 250 * 0.86, 78, 78, 'OVERLAY')
    ammoLight:SetBlendMode('ADD')
    ammoLight:Hide()
    V.ammoLight = ammoLight
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
        hole.ward = A.Art(portalLayer, 'EffectWard', 0, 0, 46, 46, 'OVERLAY')
        hole.ward:Hide()
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
        local burst = { particles = {}, particleLights = {} }
        for _, key in ipairs(lightningLists) do
            burst[key] = {}
        end
        burst.core = A.Art(board.effectLayer, 'Halo', 0, 0, 80, 80, 'OVERLAY')
        burst.core:SetBlendMode('BLEND')
        burst.core:Hide()
        burst.coreBloom = A.Art(board.effectLayer, 'ImpactLight', 0, 0, 80, 80, 'OVERLAY')
        burst.coreBloom:SetBlendMode('ADD')
        burst.coreBloom:Hide()
        burst.coreHot = A.Art(board.effectLayer, 'ImpactLight', 0, 0, 80, 80, 'OVERLAY')
        burst.coreHot:SetBlendMode('ADD')
        burst.coreHot:Hide()
        burst.impactLight = A.Art(board.effectLayer, 'ImpactLight', 0, 0, 95, 95, 'OVERLAY')
        burst.impactLight:SetBlendMode('ADD')
        burst.impactLight:Hide()
        burst.sourceLight = A.Art(board.effectLayer, 'ImpactLight', 0, 0, 80, 80, 'OVERLAY')
        burst.sourceLight:SetBlendMode('ADD')
        burst.sourceLight:Hide()
        for i = 1, 12 do
            burst.particleLights[i] = A.Art(board.effectLayer, 'ImpactLight', 0, 0, 30, 30, 'OVERLAY')
            burst.particleLights[i]:SetBlendMode('ADD')
            burst.particleLights[i]:Hide()
            burst.particles[i] = A.Art(board.effectLayer, 'Spark', 0, 0, 12, 12, 'OVERLAY')
            burst.particles[i]:Hide()
        end
        for i = 1, 5 do
            for _, key in ipairs(lightningLists) do
                local texture = key == 'arcBlooms' and 'LightningBloom1'
                    or key == 'hitLights' and 'ImpactLight'
                    or key == 'hitFlashes' and 'LightningFlash'
                    or 'LightningBolt1'
                burst[key][i] = A.Art(board.effectLayer, texture, 0, 0, 64, 32, 'OVERLAY')
                burst[key][i]:SetBlendMode('ADD')
                burst[key][i]:Hide()
            end
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
        hole.ward:Hide()
        for _, dot in ipairs(hole.swirl) do
            dot:Hide()
        end
    end
    for _, aura in ipairs(chainAuras) do
        aura.glow:Hide()
        aura.ring:Hide()
        for _, spark in ipairs(aura.sparks) do
            spark:Hide()
        end
    end
    for _, burst in ipairs(specialBursts) do
        burst.core:Hide()
        burst.coreBloom = A.Art(board.effectLayer, 'ImpactLight', 0, 0, 80, 80, 'OVERLAY')
        burst.coreBloom:SetBlendMode('ADD')
        burst.coreBloom:Hide()
        burst.coreHot = A.Art(board.effectLayer, 'ImpactLight', 0, 0, 80, 80, 'OVERLAY')
        burst.coreHot:SetBlendMode('ADD')
        burst.coreHot:Hide()
        burst.impactLight:Hide()
        burst.sourceLight:Hide()
        for _, key in ipairs(lightningLists) do
            for _, texture in ipairs(burst[key]) do
                texture:Hide()
            end
        end
        for _, particle in ipairs(burst.particles) do
            particle:Hide()
        end
    end
    muzzle:Hide()
    specialGlow:Hide()
    ammoLight:Hide()
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
local function drawLightning(burst, impact, reduced)
    local active = impact and not reduced and impact.age < 1.1
    burst.sourceLight:SetShown(not not active)
    local previous = impact and { x = impact.x, y = impact.y }
    local color = impact and (A.colors[impact.color] or A.colors[6])
    if active then
        move(burst.sourceLight, impact.x, impact.y)
        burst.sourceLight:SetVertexColor(unpack(color))
        burst.sourceLight:SetAlpha(math.max(0, 1 - impact.age / 0.3) * 0.7)
    end
    for i = 1, 5 do
        local target = active and impact.links and impact.links[i]
        local age = target and (impact.age - (i - 1) * 0.075) or -1
        local visible = target and age >= 0 and age < 0.72
        for _, key in ipairs(lightningLists) do
            burst[key][i]:SetShown(not not visible)
        end
        if visible then
            local travel = math.min(1, age / 0.045)
            local endX = previous.x + (target.x - previous.x) * travel
            local endY = previous.y + (target.y - previous.y) * travel
            local dx, dy = endX - previous.x, (endY - previous.y) * 0.86
            local length, angle = math.max(1, math.sqrt(dx * dx + dy * dy)), -math.atan2(dy, dx)
            local alpha = math.max(0, 1 - age / 0.72)
            local variant = math.floor(age * 13) % 3 + 1
            for _, key in ipairs({ 'arcBlooms', 'arcs', 'arcCores' }) do
                local texture = burst[key][i]
                move(texture, (previous.x + endX) / 2, (previous.y + endY) / 2)
                texture:SetSize(length, 32)
                texture:SetRotation(angle)
                texture:SetTexture(
                    A.media
                        .. (key == 'arcBlooms' and 'LightningBloom' or 'LightningBolt')
                        .. variant
                        .. '.tga'
                )
                if key == 'arcCores' then
                    texture:SetVertexColor(
                        0.75 + color[1] * 0.25,
                        0.75 + color[2] * 0.25,
                        0.75 + color[3] * 0.25
                    )
                else
                    texture:SetVertexColor(unpack(color))
                end
                texture:SetAlpha(alpha * (key == 'arcBlooms' and 0.85 or key == 'arcs' and 0.9 or 0.75))
            end
            local arrival = math.max(0, math.min(1, (age - 0.035) / 0.055)) * alpha
            local light, flash = burst.hitLights[i], burst.hitFlashes[i]
            move(light, target.x, target.y)
            move(flash, target.x, target.y)
            light:SetSize(45 + arrival * 22, 45 + arrival * 22)
            light:SetVertexColor(unpack(color))
            light:SetAlpha(arrival * 0.65)
            flash:SetSize(13 + arrival * 10, 13 + arrival * 10)
            flash:SetVertexColor(0.7 + color[1] * 0.3, 0.7 + color[2] * 0.3, 0.7 + color[3] * 0.3)
            flash:SetAlpha(arrival)
        end
        if target then
            previous = target
        end
    end
end
function V.Draw(r, active)
    local auraCount = 0
    local animateAuras = not A.MotionReduced() and not r.paused and r.status == 'playing'
    for _, lane in ipairs(r.other and { r, r.other } or { r }) do
        for _, ball in ipairs(lane.balls) do
            if
                ball.kind
                and specialColors[ball.kind]
                and r.status == 'playing'
                and ball.d >= 24
                and not A.Engine.Hidden(lane, ball.d)
                and auraCount < 32
            then
                auraCount = auraCount + 1
                local aura = chainAuras[auraCount]
                if not aura then
                    aura = { sparks = {} }
                    aura.glow = A.Art(board.effectLayer, 'SpecialLight', 0, 0, 64, 64, 'OVERLAY')
                    aura.glow:SetBlendMode('ADD')
                    aura.ring = A.Art(board.effectLayer, 'SpecialRing', 0, 0, 31, 31, 'OVERLAY')
                    for i = 1, 2 do
                        aura.sparks[i] = A.Art(board.effectLayer, 'SpecialSpark', 0, 0, 7, 7, 'OVERLAY')
                    end
                    chainAuras[auraCount] = aura
                end
                local x, y = A.BallPosition(lane, ball)
                local phase = timer * (ball.kind == 'Bomb' and 5 or 3) + auraCount * 1.7
                local pulse = animateAuras and (0.5 + math.sin(phase) * 0.5) or 0.5
                local color = lightColor(ball.color, ball.kind, animateAuras)
                move(aura.glow, x, y)
                move(aura.ring, x, y)
                aura.glow:SetVertexColor(unpack(color))
                aura.ring:SetVertexColor(unpack(color))
                aura.glow:SetSize(54 + pulse * 4, 54 + pulse * 4)
                aura.glow:SetAlpha(0.38 + pulse * 0.17)
                aura.ring:SetAlpha(0.3 + pulse * 0.2)
                aura.glow:Show()
                aura.ring:Show()
                for i, spark in ipairs(aura.sparks) do
                    spark:SetShown(animateAuras)
                    if animateAuras then
                        local angle = (ball.kind == 'Rewind' and -phase or phase * 0.35) + i * math.pi
                        local sx, sy = x + math.cos(angle) * 15, y + math.sin(angle) * 15 / 0.86
                        if ball.kind == 'Bomb' then
                            local rise = (timer * 1.3 + i * 0.5) % 1
                            sx, sy = x + (i == 1 and -6 or 6), y - 8 - rise * 17
                        end
                        move(spark, sx, sy)
                        spark:SetTexture(A.media .. (particleTextures[ball.kind] or 'SpecialSpark') .. '.tga')
                        spark:SetVertexColor(unpack(color))
                        spark:SetRotation(-angle)
                        spark:SetAlpha(0.45 + pulse * 0.5)
                    end
                end
            end
        end
    end
    for i = auraCount + 1, #chainAuras do
        local aura = chainAuras[i]
        aura.glow:Hide()
        aura.ring:Hide()
        for _, spark in ipairs(aura.sparks) do
            spark:Hide()
        end
    end
    for lane, burst in ipairs(specialBursts) do
        local state = lane == 1 and r or r.other
        local impact = state and state.specialImpact
        drawLightning(
            burst,
            state and (state.lightningImpact or (impact and impact.kind == 'Lightning' and impact)),
            A.MotionReduced()
        )
        burst.coreBloom:SetShown(
            impact ~= nil and impactTextures[impact.kind] ~= nil and impact.kind ~= 'Lightning'
        )
        burst.coreHot:SetShown(
            impact ~= nil
                and impactTextures[impact.kind] ~= nil
                and impact.kind ~= 'Lightning'
                and impact.kind ~= 'Paint'
        )
        burst.impactLight:SetShown(impact ~= nil)
        burst.core:SetShown(impact ~= nil)
        if impact then
            local progress = math.min(1, impact.age / 1.1)
            local reduced = A.MotionReduced()
            local color = impact.kind == 'Rainbow' and lightColor(impact.color, 'Rainbow', not reduced)
                or A.colors[impact.color]
                or A.colors[6]
            local rewind = impact.kind == 'Rewind'
            local extra = impactTextures[impact.kind] ~= nil
            burst.core:SetTexture(
                A.media
                    .. (impactTextures[impact.kind] or (rewind and 'PortalSwirl' or 'SpecialRing'))
                    .. '.tga'
            )
            burst.core:SetBlendMode(extra and 'ADD' or 'BLEND')
            burst.core:SetVertexColor(unpack(color))
            move(burst.impactLight, impact.x, impact.y)
            burst.impactLight:SetVertexColor(unpack(color))
            burst.impactLight:SetAlpha((1 - progress) ^ 2 * (reduced and 0.15 or 0.35))
            move(burst.core, impact.x, impact.y)
            local size = reduced and 55 or rewind and (85 - progress * 45) or (40 + progress * 100)
            if impact.kind == 'Lightning' then
                size = reduced and 32 or 26 + progress * 16
            end
            burst.core:SetSize(size, size)
            burst.core:SetAlpha((1 - progress) * 0.95)
            burst.core:SetRotation(not reduced and (rewind or impact.kind == 'Magnet') and -progress * 5 or 0)
            if impact.kind ~= 'Lightning' and impactTextures[impact.kind] then
                local rotation = not reduced and (rewind or impact.kind == 'Magnet') and -progress * 5 or 0
                for _, layer in ipairs({ burst.coreBloom, burst.coreHot }) do
                    move(layer, impact.x, impact.y)
                    layer:SetSize(size, size)
                    layer:SetRotation(rotation)
                end
                burst.coreBloom:SetTexture(A.media .. impactTextures[impact.kind] .. 'Glow.tga')
                burst.coreBloom:SetVertexColor(unpack(color))
                burst.coreBloom:SetAlpha((1 - progress) * 0.7)
                burst.coreHot:SetTexture(A.media .. impactTextures[impact.kind] .. '.tga')
                burst.coreHot:SetVertexColor(
                    0.65 + color[1] * 0.35,
                    0.65 + color[2] * 0.35,
                    0.65 + color[3] * 0.35
                )
                burst.coreHot:SetAlpha((1 - progress) * 0.35)
            end
            for i, particle in ipairs(burst.particles) do
                local light = burst.particleLights[i]
                local visible = not reduced and impact.kind ~= 'Lightning'
                particle:SetShown(visible)
                light:SetShown(visible)
                if visible then
                    local angle = i * math.pi / 6 + (rewind and -progress * 4 or 0)
                    local radius = rewind and 65 * (1 - progress) or 10 + progress * (i % 2 == 0 and 70 or 45)
                    local px = impact.x + math.cos(angle) * radius
                    local py = impact.y
                        + math.sin(angle) * radius
                        + (impact.kind == 'Bomb' and progress * progress * 35 or 0)
                    if impact.kind == 'Bomb' and impact.d then
                        local direction = i <= 6 and -1 or 1
                        px, py = A.Engine.Point(
                            impact.route or A.Engine.Route(state),
                            impact.d + direction * progress * 90 * (0.5 + (i % 6) / 10)
                        )
                        px, py = px + math.cos(angle) * 8, py + math.sin(angle) * 8
                    elseif impact.kind == 'Paint' and impact.links and impact.links[i] then
                        local target = impact.links[i]
                        px = impact.x + (target.x - impact.x) * math.min(1, progress * 2.5)
                        py = impact.y + (target.y - impact.y) * math.min(1, progress * 2.5)
                    elseif impact.kind == 'Treasure' then
                        px, py = impact.x + math.cos(angle) * 35, impact.y - progress * 90 + i % 3 * 12
                    elseif impact.kind == 'Magnet' then
                        px, py =
                            impact.x + math.cos(angle) * 70 * (1 - progress),
                            impact.y + math.sin(angle) * 70 * (1 - progress)
                    elseif impact.kind == 'Stasis' then
                        px, py = impact.x + math.cos(angle) * 45, impact.y + math.sin(angle) * 45
                    end
                    local tint = impact.kind == 'Rainbow' and A.colors[(i - 1) % 6 + 1] or color
                    move(particle, px, py)
                    move(light, px, py)
                    particle:SetTexture(
                        A.media .. (particleTextures[impact.kind] or 'SpecialSpark') .. '.tga'
                    )
                    particle:SetBlendMode(impact.kind == 'Paint' and 'BLEND' or 'ADD')
                    particle:SetVertexColor(unpack(tint))
                    particle:SetSize(
                        (impact.kind == 'Frost' and 22 or 18) * (1 - progress * 0.6),
                        18 * (1 - progress * 0.6)
                    )
                    particle:SetRotation(angle + progress * (rewind and -4 or 2))
                    particle:SetAlpha((1 - progress) * 0.9)
                    light:SetVertexColor(unpack(tint))
                    light:SetSize(28, 28)
                    light:SetAlpha((1 - progress) * 0.4)
                end
            end
        else
            for _, light in ipairs(burst.particleLights) do
                light:Hide()
            end
            for _, particle in ipairs(burst.particles) do
                particle:Hide()
            end
        end
    end
    local animated = not A.MotionReduced() and not r.paused
    for i, hole in ipairs(V.holes) do
        local lane = i == 1 and r or r.other
        local warded = lane and (lane.ward or 0) > 0 and r.status == 'playing'
        hole.ward:SetShown(not not warded)
        if warded then
            local x, y = A.Engine.Point(A.Engine.Route(lane), A.Engine.Path(A.Engine.Route(lane)).length)
            move(hole.ward, x, y)
            hole.ward:SetVertexColor(unpack(A.colors[lane.wardColor or 6]))
            hole.ward:SetAlpha(A.MotionReduced() and 0.65 or 0.55 + math.sin(timer * 2) * 0.12)
        end
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
    ammoLight:SetShown(r.loadedKind ~= nil and r.status == 'playing')
    if r.loadedKind then
        move(ammoLight, 380 - aimX * kick, 250 - aimY * kick)
        ammoLight:SetVertexColor(unpack(lightColor(r.loaded, r.loadedKind, moving)))
        local pulse = moving and (0.5 + math.sin(timer * 3) * 0.5) or 0.5
        ammoLight:SetSize(66 + pulse * 4, 66 + pulse * 4)
        ammoLight:SetAlpha(0.38 + pulse * 0.17)
    end
    local ability = shot and shot.kind or r.loadedKind
    specialGlow:SetShown(ability ~= nil)
    if ability then
        move(specialGlow, shot and shot.kind and shot.x or 380, shot and shot.kind and shot.y or 250)
        specialGlow:SetTexture(A.media .. 'SpecialRing.tga')
        specialGlow:SetBlendMode('BLEND')
        specialGlow:SetVertexColor(
            unpack(lightColor(shot and shot.kind and shot.color or r.loaded, ability, moving))
        )
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
            t:SetVertexColor(unpack(lightColor(shot.color, shot.kind, moving)))
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
