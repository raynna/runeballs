local _, A = ...
local F = { clears = {}, statuses = {}, chains = {}, pulls = {}, stops = {} }
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
    for _, pool in ipairs({ F.clears, F.statuses, F.chains, F.pulls, F.stops }) do
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
            local time = math.max(0, e.age)
            local frame = math.min(3, time / 0.12)
            local stage = reduced and 2 or math.floor(frame) + 1
            local mix = reduced and 0 or frame - math.floor(frame)
            mix = mix * mix * (3 - 2 * mix)
            local travel = reduced and 0 or (1 - math.exp(-time * 4)) / 4
            local x, y = e.x + (e.vx or 0) * travel, e.y + (e.vy or 0) * travel
            if reduced then
                x, y = e.restX or e.x, e.restY or e.y
            end
            local size = reduced and 36 or 36 + 6 * (1 - math.exp(-time * 5))
            local alpha = math.min(1, (1 - p) * 2)
            item[1]:SetTexture(A.media .. 'Break' .. (e.color or 6) .. '_' .. stage .. '.tga')
            item[1]:SetBlendMode('BLEND')
            draw(item[1], x, y, size, { 1, 1, 1 }, alpha * (1 - mix))
            if mix > 0 and stage < 4 then
                item[3]:SetTexture(A.media .. 'Break' .. (e.color or 6) .. '_' .. (stage + 1) .. '.tga')
                item[3]:SetBlendMode('BLEND')
                draw(item[3], x, y, size, { 1, 1, 1 }, alpha * mix)
            end
            draw(item[2], x, y, radius * 1.5, color, (1 - p) ^ 2 * 0.45)
        else
            item[1]:SetTexture(A.media .. 'MatchRing.tga')
            item[1]:SetBlendMode('ADD')
        end

        if not reduced and firework then
            local count = 8
            for j = 1, count do
                item[j + 2]:SetBlendMode('ADD')
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
    local count, chainCount, pullCount, stopCount = 0, 0, 0, 0
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
                    local dx, dy = nx - x, (ny - y) * 0.86
                    local length = math.max(0.001, math.sqrt(dx * dx + dy * dy))
                    -- Bind alongside the train, leaving every matching colour exposed.
                    x, y = x - dy / length * 17, y + dx / length * 17 / 0.86
                    link:SetBlendMode('BLEND')
                    if x >= 10 and x <= 750 and y >= 12 and y <= 488 then
                        draw(link, x, y, 20, { 1, 1, 1 }, 1 - release, -math.atan2(dy, dx))
                    end
                    link:SetSize(20, reduced and 15 or 15 + release * 5)
                end
            end
            if not A.Engine.Hidden(lane, last) then
                stopCount = stopCount + 1
                local item = F.stops[stopCount]
                if not item then
                    item = { texture(board, 'EffectStasis') }
                    F.stops[stopCount] = item
                end
                local x, y = A.Engine.Point(route, last)
                local px, py = A.Engine.Point(route, last - 4)
                local dx, dy = x - px, (y - py) * 0.86
                local length = math.max(0.001, math.sqrt(dx * dx + dy * dy))
                item[1]:SetBlendMode('BLEND')
                draw(
                    item[1],
                    x - dy / length * 29,
                    y + dx / length * 29 / 0.86,
                    19,
                    { 0.9, 0.78, 1 },
                    1 - release
                )
            end
        end
        -- Draw the pull along the actual road, from the leading group back
        -- toward the rear group. Other powers that stop/rewind supersede Magnet.
        if
            run.status == 'playing'
            and (lane.magnet or 0) > 0
            and (lane.stasis or 0) <= 0
            and (lane.reverse or 0) <= 0
        then
            local route = A.Engine.Route(lane)
            for i = 1, #lane.balls - 1 do
                local front, rear = lane.balls[i], lane.balls[i + 1]
                local gap = front.d - rear.d
                if gap > 40 and front.d >= 38 and pullCount < 96 then
                    local low, high = math.max(24, rear.d + 13), front.d - 13
                    if high > low then
                        for j = 1, 3 do
                            local phase = reduced and j / 4 or (clock * 85 / (high - low) + j / 3) % 1
                            local distance = high - phase * (high - low)
                            if
                                not A.Engine.Hidden(lane, distance)
                                and not A.Engine.Hidden(lane, distance - 7)
                                and not A.Engine.Hidden(lane, distance + 7)
                            then
                                pullCount = pullCount + 1
                                local item = F.pulls[pullCount]
                                if not item then
                                    item = { texture(board, 'MagnetPull'), texture(board, 'ImpactLight') }
                                    F.pulls[pullCount] = item
                                end
                                local x, y = A.Engine.Point(route, distance)
                                local tx, ty = A.Engine.Point(route, distance - 4)
                                local alpha = reduced and 0.7 or 0.45 + math.sin(phase * math.pi) * 0.5
                                draw(item[2], x, y, 23, { 0.25, 0.8, 1 }, alpha * 0.28)
                                draw(
                                    item[1],
                                    x,
                                    y,
                                    17,
                                    { 0.45, 0.9, 1 },
                                    alpha,
                                    -math.atan2((ty - y) * 0.86, tx - x)
                                )
                            end
                        end
                    end
                end
            end
        end
        local states = {}
        local function add(name, alpha, size, rotation)
            states[#states + 1] = { name = name, alpha = alpha, size = size, rotation = rotation or 0 }
        end
        if run.status == 'playing' then
            if (lane.reverse or 0) > 0 then
                add('RewindWrap', math.min(0.8, lane.reverse / 0.4), 35, reduced and 0 or clock * 2)
            end
            if (lane.slow or 0) > 0 then
                local stage = math.max(1, math.min(6, math.ceil(lane.slow * 1.5)))
                add('IceShell' .. stage, math.min(0.85, lane.slow / 0.35), 35)
            end
            if (lane.magnet or 0) > 0 then
                add('MatchRing', math.min(0.4, lane.magnet / 0.5), 34)
                states[#states].color = { 0.4, 0.85, 1 }
            end
            if (lane.treasure or 0) > 0 then
                add('TreasureWrap', math.min(0.75, lane.treasure / 0.5), 34)
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
                    draw(
                        item[j + 1],
                        x,
                        y,
                        state.size,
                        state.color or { 1, 1, 1 },
                        state.alpha,
                        state.rotation
                    )
                end
            end
        end
    end
end
