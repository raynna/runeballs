local _, A = ...
local F = { clears = {}, statuses = {}, chains = {} }
A.Feedback = F
local function texture(board, name)
    local t = A.Art(board.effectLayer, name, 0, 0, 1, 1, 'ARTWORK')
    t:SetBlendMode('ADD')
    return t
end
local function draw(t, x, y, size, color, alpha, angle)
    t:ClearAllPoints()
    t:SetPoint('CENTER', t:GetParent(), 'TOPLEFT', x, -y * 0.86)
    t:SetSize(size, size)
    t:SetVertexColor(unpack(color))
    t:SetAlpha(alpha)
    t:SetRotation(angle or 0)
    t:Show()
end
function F.Reset()
    for _, pool in ipairs({ F.clears, F.statuses, F.chains }) do
        for _, item in ipairs(pool) do
            for _, t in ipairs(item) do
                t:Hide()
            end
        end
    end
end
function F.Draw(board, run, active, clock)
    F.Reset()
    if not run.paused then
        F.clock = clock
    end
    clock = F.clock or clock
    local reduced = A.MotionReduced()
    for i, e in ipairs(active) do
        local item = F.clears[i]
        if not item then
            item = { texture(board, 'MatchRing'), texture(board, 'ImpactLight') }
            for j = 1, 8 do
                item[#item + 1] = texture(board, 'StarGlint')
            end
            F.clears[i] = item
        end
        local p = math.min(1, e.age / 0.6)
        local color = A.colors[e.color] or A.colors[6]
        local firework = e.kind == 'Firework'
        local strength = firework and 2.8 or math.min(1.5, 1 + ((e.combo or 1) - 1) * 0.15)
        local radius = reduced and 25 or (22 + p * 36) * strength
        draw(item[1], e.x, e.y, radius, color, (1 - p) * (firework and 0.28 or 0.75))
        draw(item[2], e.x, e.y, radius * 1.5, color, (1 - p) ^ 2 * 0.45)
        if not firework then
            local stage = reduced and 2 or math.min(4, math.floor(e.age / 0.12) + 1)
            item[1]:SetTexture(A.media .. 'Break' .. (e.color or 6) .. '_' .. stage .. '.tga')
            item[1]:SetBlendMode('BLEND')
            draw(item[1], e.x, e.y, reduced and 36 or 38, { 1, 1, 1 }, math.min(1, (1 - p) * 2))
        else
            item[1]:SetTexture(A.media .. 'MatchRing.tga')
            item[1]:SetBlendMode('ADD')
        end

        if not reduced and firework then
            local count = 8
            for j = 1, count do
                item[j + 2]:SetTexture(A.media .. (firework and 'BombEmber' or 'StarGlint') .. '.tga')
                local angle = j * math.pi * 2 / count + (e.phase or e.x * 0.013)
                local distance = (1 - (1 - p) ^ 2) * 34 * strength
                draw(
                    item[j + 2],
                    e.x + math.cos(angle) * distance,
                    e.y + math.sin(angle) * distance + p * p * 18,
                    (firework and 26 or 10) * (1 - p * 0.75),
                    color,
                    1 - p,
                    angle
                )
            end
        end
    end
    local count, chainCount = 0, 0
    -- Material overlays follow simulation timers, so pausing and saved runs
    -- preserve the visible thaw/release stage without a second animation clock.
    for _, lane in ipairs(run.other and { run, run.other } or { run }) do
        -- One linked restraint follows the route from tail to head, including
        -- gaps. Sampling the road avoids straight shortcuts across curved maps.
        if run.status == 'playing' and (lane.stasis or 0) > 0 and #lane.balls > 0 then
            local route = A.Engine.Route(lane)
            local first = math.max(24, lane.balls[#lane.balls].d - 5)
            local last = math.min(A.Engine.Path(route).length, lane.balls[1].d + 5)
            local release = math.max(0, 1 - lane.stasis / 0.45)
            for distance = first, last, 12 do
                if
                    not A.Engine.Hidden(lane, distance)
                    and not A.Engine.Hidden(lane, distance - 7)
                    and not A.Engine.Hidden(lane, distance + 7)
                then
                    chainCount = chainCount + 1
                    local item = F.chains[chainCount]
                    if not item then
                        item = { texture(board, 'TimeChainLink') }
                        F.chains[chainCount] = item
                    end
                    local link = item[1]
                    local x, y = A.Engine.Point(route, distance)
                    local nx, ny = A.Engine.Point(route, math.min(last + 1, distance + 5))
                    link:SetBlendMode('BLEND')
                    draw(link, x, y, 18, { 1, 1, 1 }, 1 - release, -math.atan2((ny - y) * 0.86, nx - x))
                    link:SetSize(18, reduced and 13 or 13 + release * 5)
                end
            end
        end
        local states = {}
        local function add(name, alpha, size, rotation)
            states[#states + 1] = { name = name, alpha = alpha, size = size, rotation = rotation or 0 }
        end
        if run.status == 'playing' then
            if (lane.reverse or 0) > 0 then
                add('RewindWrap', math.min(1, lane.reverse / 0.4), 31, reduced and 0 or clock * 2)
            end
            if (lane.slow or 0) > 0 then
                local stage = math.max(1, math.min(6, math.ceil(lane.slow * 1.5)))
                add('IceShell' .. stage, math.min(1, lane.slow / 0.35), 31)
            end
            if (lane.magnet or 0) > 0 then
                add('MagnetWrap', math.min(0.65, lane.magnet / 0.5), 30, reduced and 0 or -clock)
            end
            if (lane.treasure or 0) > 0 then
                add('TreasureWrap', math.min(0.8, lane.treasure / 0.5), 29)
            end
        end
        for _, ball in ipairs(lane.balls) do
            if #states > 0 and ball.d >= 24 and not A.Engine.Hidden(lane, ball.d) then
                count = count + 1
                local item = F.statuses[count]
                if not item then
                    item = { texture(board, 'MatchRing') }
                    F.statuses[count] = item
                end
                local x, y = A.BallPosition(lane, ball)
                local color = A.colors[ball.color] or A.colors[6]
                draw(item[1], x, y, 29, color, 0.15)
                for j, state in ipairs(states) do
                    if not item[j + 1] then
                        item[j + 1] = texture(board, state.name)
                    end
                    item[j + 1]:SetTexture(A.media .. state.name .. '.tga')
                    item[j + 1]:SetBlendMode('BLEND')
                    draw(item[j + 1], x, y, state.size, { 1, 1, 1 }, state.alpha, state.rotation)
                end
            end
        end
    end
end
