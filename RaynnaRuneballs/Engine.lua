local _, A = ...
local E = {}
A.Engine = E
E.MAX_LEVEL = 100
function E.IsDualLevel(level)
    return level >= 30 and level <= 100 and (level % 10 == 0 or (level >= 60 and level % 5 == 0))
end
function E.MarbleCount(level)
    return 54 + math.floor((math.min(level, 100) - 1) * 1.4)
end
A.media = 'Interface\\AddOns\\RaynnaRuneballs\\Media\\'
A.colors = {
    { 1, 0.19, 0.15 },
    { 0.15, 0.65, 1 },
    { 0.28, 0.9, 0.22 },
    { 1, 0.8, 0.12 },
    { 0.8, 0.28, 1 },
    { 0.95, 0.95, 1 },
}
A.runes = { 'I', 'II', 'III', 'IV', 'V' }
A.realms = { 'The Emerald Grove', 'The Sunken Archive', 'The Violet Sanctum' }
local spacing = 25
local paths = {}
-- Early rounds introduce distinct layouts; later rounds gain turns and lobes.
-- Cache only the active round so an endless run cannot accumulate path tables.
local earlyRoutes = {
    [2] = {
        { 55, 60 },
        { 270, 40 },
        { 620, 50 },
        { 700, 130 },
        { 590, 180 },
        { 210, 130 },
        { 70, 220 },
        { 110, 400 },
        { 360, 450 },
        { 660, 400 },
        { 690, 300 },
        { 560, 280 },
        { 490, 365 },
        { 300, 360 },
        { 250, 300 },
    },
    [3] = {
        { 55, 420 },
        { 80, 100 },
        { 240, 50 },
        { 370, 110 },
        { 530, 55 },
        { 700, 120 },
        { 650, 240 },
        { 710, 380 },
        { 560, 440 },
        { 400, 390 },
        { 220, 440 },
        { 130, 320 },
        { 190, 215 },
        { 275, 170 },
        { 410, 135 },
        { 530, 190 },
    },
    [4] = {
        { 55, 70 },
        { 660, 70 },
        { 670, 170 },
        { 540, 155 },
        { 520, 340 },
        { 660, 330 },
        { 660, 430 },
        { 90, 430 },
        { 65, 320 },
        { 235, 335 },
        { 245, 160 },
        { 160, 160 },
        { 150, 250 },
    },
}
function E.Path(level)
    if paths[level] then
        return paths[level]
    end
    if level < 1000 and not paths[level + 1000] then
        paths = {}
    end
    local p = { length = 0 }
    local function add(x, y)
        -- Keep every route outside the launcher/ammunition clearance circle.
        local cx, cy = x - 380, (y - 250) * 0.86
        local radius = math.sqrt(cx * cx + cy * cy)
        if radius < 100 then
            if radius < 0.001 then
                cx, cy, radius = 1, 0, 1
            end
            x, y = 380 + cx * 100 / radius, 250 + cy * 100 / radius / 0.86
        end
        if #p > 0 then
            local prev = p[#p]
            p.length = p.length + math.sqrt((x - prev.x) ^ 2 + (y - prev.y) ^ 2)
        end
        p[#p + 1] = { x = x, y = y, d = p.length }
    end
    local controls = earlyRoutes[level]
    if level >= 1000 or E.IsDualLevel(level) then
        -- A rigid half-turn preserves every segment length exactly. The exits
        -- are on opposite sides of the launcher, not beside one another.
        local round = level % 1000
        local rounds = { 30, 40, 50, 60, 65, 70, 75, 80, 85, 90, 95, 100 }
        local variant = 1
        for i, candidate in ipairs(rounds) do
            if candidate == round then
                variant = i
                break
            end
        end
        local family = math.floor((variant - 1) / 4)
        if family == 0 then
            controls = { { 0, 130 }, { 620, 130 }, { 620, 450 }, { 90, 450 }, { 90, 400 } }
        elseif family == 1 then
            controls = {
                { 0, 130 },
                { 620, 130 },
                { 620, 290 },
                { 700, 290 },
                { 700, 450 },
                { 90, 450 },
                { 90, 400 },
            }
        else
            controls = {
                { 0, 80 },
                { 300, 80 },
                { 300, 130 },
                { 620, 130 },
                { 620, 480 },
                { 50, 480 },
                { 50, 240 },
            }
        end
        -- Rotate the complete layout around the board, then mirror its partner.
        -- Each later family adds a visible detour; paired lengths stay identical.
        for _, point in ipairs(controls) do
            if (variant - 1) % 4 >= 2 then
                point[1] = 760 - point[1]
            end
            for turn = 1, (variant - 1) % 2 do
                point[1], point[2] = 380 + (point[2] - 250) * 760 / 500, 250 - (point[1] - 380) * 500 / 760
            end
        end
        if level >= 1000 then
            for _, point in ipairs(controls) do
                point[1], point[2] = 760 - point[1], 500 - point[2]
            end
        end
    end
    if level >= 1000 or E.IsDualLevel(level) then
        local function lineTo(x, y)
            local last = p[#p]
            local count = math.max(1, math.ceil(math.sqrt((x - last.x) ^ 2 + (y - last.y) ^ 2) / 4))
            local sx, sy = last.x, last.y
            for i = 1, count do
                add(sx + (x - sx) * i / count, sy + (y - sy) * i / count)
            end
        end
        add(controls[1][1], controls[1][2])
        for i = 2, #controls - 1 do
            local a, b, c = controls[i - 1], controls[i], controls[i + 1]
            local dx, dy = b[1] - a[1], b[2] - a[2]
            local len = math.sqrt(dx * dx + dy * dy)
            local ex, ey = c[1] - b[1], c[2] - b[2]
            local out = math.sqrt(ex * ex + ey * ey)
            local radius = math.min(16, len * 0.4, out * 0.4)
            local px, py = b[1] - dx / len * radius, b[2] - dy / len * radius
            local qx, qy = b[1] + ex / out * radius, b[2] + ey / out * radius
            lineTo(px, py)
            for step = 1, 12 do
                local t = step / 12
                local u = 1 - t
                add(u * u * px + 2 * u * t * b[1] + t * t * qx, u * u * py + 2 * u * t * b[2] + t * t * qy)
            end
        end
        lineTo(controls[#controls][1], controls[#controls][2])
    elseif level == 1 then
        -- Compensate for the board's 0.86 vertical display scale: this is a
        -- circular inward spiral on screen, rather than an elliptical loop.
        for i = 0, 900 do
            local t = i / 900
            local radius = 190 - 86 * t
            local angle = -math.pi * 0.8 + t * math.pi * 3.6
            add(380 + radius * math.cos(angle), 250 + radius * math.sin(angle) / 0.86)
        end
    elseif controls then
        for segment = 1, #controls - 1 do
            local a = controls[math.max(1, segment - 1)]
            local b = controls[segment]
            local c = controls[segment + 1]
            local d = controls[math.min(#controls, segment + 2)]
            for step = 0, 30 do
                if segment == 1 or step > 0 then
                    local t = step / 30
                    local function axis(k)
                        return 0.5
                            * (
                                (2 * b[k])
                                + (-a[k] + c[k]) * t
                                + (2 * a[k] - 5 * b[k] + 4 * c[k] - d[k]) * t * t
                                + (-a[k] + 3 * b[k] - 3 * c[k] + d[k]) * t * t * t
                            )
                    end
                    add(axis(1), axis(2))
                end
            end
        end
    else
        local turns = level == 1 and 1.215 or math.min(2.05, 1.25 + level * 0.009)
        local phase = level == 1 and -math.pi * 0.8 or level * 0.73
        local lobes = 2 + math.floor(level / 20)
        for i = 0, 900 do
            local t = i / 900
            local angle = phase + t * math.pi * 2 * turns
            local ripple = level == 1 and 0
                or math.sin(angle * lobes + level) * math.min(18, level * 0.18) * math.sin(t * math.pi)
            add(
                380 + (330 - t * 205 + ripple) * math.cos(angle),
                250 + (210 - t * 120 + ripple * 0.6) * math.sin(angle)
            )
        end
    end
    -- Extend backwards along the entry tangent to the board boundary.
    local first, second = p[1], p[2]
    if first.x > -27.9 and first.x < 787.9 and first.y > 0.1 and first.y < 499.9 then
        local dx, dy = first.x - second.x, first.y - second.y
        local length = math.sqrt(dx * dx + dy * dy)
        dx, dy = dx / length, dy / length
        local reach = math.huge
        if dx < 0 then
            reach = math.min(reach, (-28 - first.x) / dx)
        elseif dx > 0 then
            reach = math.min(reach, (788 - first.x) / dx)
        end
        if dy < 0 then
            reach = math.min(reach, -first.y / dy)
        elseif dy > 0 then
            reach = math.min(reach, (500 - first.y) / dy)
        end
        local extended = { length = p.length + reach, entryLength = reach }
        local count = math.ceil(reach / 4)
        for i = 0, count - 1 do
            local distance = i * reach / count
            extended[#extended + 1] =
                { x = first.x + dx * (reach - distance), y = first.y + dy * (reach - distance), d = distance }
        end
        for _, point in ipairs(p) do
            extended[#extended + 1] = { x = point.x, y = point.y, d = point.d + reach }
        end
        p = extended
    else
        p.entryLength = 0
    end
    paths[level] = p
    return p
end
function E.MapName(level)
    local names = {
        'The Emerald Grove',
        'Serpents of the Barrens',
        'The Shattered Clover',
        'Blackrock Switchbacks',
        'The Coiled Sanctum',
        'Felwood Thorns',
        'The Sunwell Labyrinth',
        'The Twisting Nether',
    }
    return names[(level - 1) % #names + 1] .. (level > #names and ' ' .. math.ceil(level / #names) or '')
end
function E.Point(level, distance)
    local p = E.Path(level)
    distance = math.max(0, math.min(p.length, distance))
    local lo, hi = 1, #p
    while hi - lo > 1 do
        local mid = math.floor((lo + hi) / 2)
        if p[mid].d < distance then
            lo = mid
        else
            hi = mid
        end
    end
    local a, b = p[lo], p[hi]
    local f = (distance - a.d) / (b.d - a.d)
    return a.x + (b.x - a.x) * f, a.y + (b.y - a.y) * f
end
function E.Init(db)
    db.options = db.options or {}
    db.appearance = db.appearance or {}
    db.best = db.best or 0
    db.level = math.max(1, math.min(E.MAX_LEVEL, db.level or 1))
    local r = db.run
    if r then
        if not r.level then
            r.pathVersion = 1
        end
        r.level = math.max(1, math.min(E.MAX_LEVEL, r.level or 1))
        if r.route then
            r.route = r.level + 1000
        end
        if r.other and not E.IsDualLevel(r.level) then
            r.remaining = r.remaining + r.other.remaining + #r.other.balls
            r.score = r.score + (r.other.score or 0)
            r.other = nil
            r.dual = nil
            local shift = math.max(0, (r.head or 0) - E.Path(r.level).length * 0.25)
            for _, ball in ipairs(r.balls) do
                ball.d = ball.d - shift
            end
            r.head = (r.head or 0) - shift
        end
        if (r.version or 1) < 2 then
            for i, ball in ipairs(r.balls) do
                ball.d = r.head - (i - 1) * spacing
            end
            r.version = 2
        end
        if not r.pathVersion and r.level then
            local offset = E.Path(r.route or r.level).entryLength or 0
            for _, ball in ipairs(r.balls) do
                ball.d = ball.d + offset
            end
            r.head = (r.head or 0) + offset
            r.pathVersion = 1
        end
        if r.layoutVersion ~= 2 and E.IsDualLevel(r.level) then
            -- Preserve chain spacing/counts on changed maps and leave reaction room.
            local shift = math.max(0, (r.head or 0) - (E.Path(E.Route(r)).length - 180))
            for _, ball in ipairs(r.balls) do
                ball.d = ball.d - shift
            end
            r.head = r.balls[1] and r.balls[1].d or 0
            r.shot = nil
        end
        r.layoutVersion = 2
        if r.other then
            E.Init({ run = r.other })
        end
        r.colorCount = 6
        r.effects = r.effects or {}
        r.shotsFired = r.shotsFired or 0
        r.paused = true
    end
end
function E.Distance(run, index)
    return run.balls[index].d
end
function E.Speed(run)
    local progress = math.max(0, math.min(100, run.level) - 1)
    local speed = 32 + progress * 0.22 + progress * progress * 0.0015
    return speed * (run.dual and 0.5 or 1)
end
local function pick(run)
    local available = {}
    if run.remaining > 0 or (run.other and run.other.remaining > 0) then
        for i = 1, run.colorCount do
            available[i] = i
        end
    else
        local seen = {}
        for _, ball in ipairs(run.balls) do
            if not seen[ball.color] then
                available[#available + 1] = ball.color
                seen[ball.color] = true
            end
        end
        if run.other then
            for _, ball in ipairs(run.other.balls) do
                if not seen[ball.color] then
                    available[#available + 1] = ball.color
                    seen[ball.color] = true
                end
            end
        end
    end
    return available[math.random(math.max(1, #available))] or 1
end
local function newLane(db, level, score)
    level = math.max(1, math.min(E.MAX_LEVEL, level or db.level))
    local initial = E.IsDualLevel(level) and (8 + math.floor(level / 25))
        or (12 + math.floor((level - 1) / 20))
    local run = {
        version = 2,
        pathVersion = 1,
        layoutVersion = 2,
        level = level,
        score = score or 0,
        balls = {},
        remaining = E.MarbleCount(level),
        colorCount = 6,
        head = spacing * (initial - 1),
        effects = {},
        shotsFired = 0,
        status = 'playing',
        paused = true,
        cooldown = 0,
    }
    db.run = run
    for i = 1, initial do
        run.balls[i] = { color = math.random(run.colorCount), d = run.head - (i - 1) * spacing }
        run.remaining = run.remaining - 1
    end
    run.loaded, run.next = pick(run), pick(run)
    return run
end
function E.NewRun(db, level, score)
    local r = newLane(db, level, score)
    if E.IsDualLevel(r.level) then
        local holder = { level = r.level }
        local other = newLane(holder, r.level, 0)
        other.route = r.level + 1000
        r.dual, other.dual = true, true
        local total = E.MarbleCount(r.level)
        r.remaining = math.floor(total / 2) - #r.balls
        other.remaining = total - math.floor(total / 2) - #other.balls
        r.other = other
    end
    return r
end
function E.Route(run)
    return run.route or run.level
end
-- Every marble owns its path distance. Removing a group leaves its neighbours
-- untouched; contact physics, rather than index renumbering, closes the gap.
local function touching(a, b)
    return a and b and a.d - b.d <= spacing + 0.000001
end
local function removeGroup(run, first, last, combo, kind)
    combo = combo or 1
    local count = last - first + 1
    local center = run.balls[math.floor((first + last) / 2)]
    local x, y = E.Point(E.Route(run), center.d)
    run.burst = { x = x, y = y, age = 0, count = count, combo = combo, kind = kind }
    for i = last, first, -1 do
        local b = run.balls[i]
        local bx, by = E.Point(E.Route(run), b.d)
        if #run.effects >= 32 then
            table.remove(run.effects, 1)
        end
        run.effects[#run.effects + 1] =
            { x = bx, y = by, age = 0, color = b.color, kind = b == center and (kind or 'Spark') or 'Spark' }
        table.remove(run.balls, i)
    end
    if run.balls[first] and first > 1 then
        run.balls[first].joinCombo = combo + 1
    end
    run.score = run.score + count * 100 * combo
    run.head = run.balls[1] and run.balls[1].d or 0
end
function E.Match(run, index, combo)
    local b = run.balls[index]
    if not b then
        return 0
    end
    local first, last = index, index
    while
        first > 1
        and touching(run.balls[first - 1], run.balls[first])
        and run.balls[first - 1].color == b.color
    do
        first = first - 1
    end
    while
        run.balls[last + 1]
        and touching(run.balls[last], run.balls[last + 1])
        and run.balls[last + 1].color == b.color
    do
        last = last + 1
    end
    if last - first + 1 < 3 then
        return 0
    end
    removeGroup(run, first, last, combo or 1)
    if A.GameSound then
        A.GameSound((combo or 1) > 1 and 'Combo' or 'Match', combo)
    end
    return combo or 1
end
function E.Insert(run, index, color, target)
    local rear = run.balls[index]
    local front = run.balls[index - 1]
    local d = rear and rear.d + spacing or (front and front.d - spacing or 0)
    if target and front and rear and front.d - rear.d >= spacing * 2 then
        d = math.max(rear.d + spacing, math.min(front.d - spacing, target))
    end
    local shifted = {}
    table.insert(run.balls, index, { color = color, d = d })
    for i = index - 1, 1, -1 do
        local ball = run.balls[i]
        local needed = run.balls[i + 1].d + spacing
        if ball.d >= needed then
            break
        end
        shifted[#shifted + 1] = { ball = ball, d = ball.d }
        ball.d = needed
    end
    local matched = E.Match(run, index)
    -- A consumed shot must not ratchet the surviving front section forward.
    if matched > 0 then
        for _, old in ipairs(shifted) do
            old.ball.d = old.d
        end
    end
    run.head = run.balls[1] and run.balls[1].d or 0
    return matched
end
function E.Special(run, index, kind)
    local x, y = E.Point(E.Route(run), run.balls[index].d)
    run.specialImpact = { x = x, y = y, kind = kind, age = 0 }
    if A.GameSound then
        A.GameSound(kind)
    end
    local first, last = index, index
    if kind == 'Bomb' then
        local d = run.balls[index].d
        while first > 1 and run.balls[first - 1].d - d <= 70 do
            first = first - 1
        end
        while run.balls[last + 1] and d - run.balls[last + 1].d <= 70 do
            last = last + 1
        end
    elseif kind == 'Frost' then
        run.slow = 4
    elseif kind == 'Rewind' then
        run.reverse = 2.5
    end
    removeGroup(
        run,
        first,
        last,
        1,
        kind == 'Bomb' and 'Explosion' or kind == 'Frost' and 'Shatter' or 'Portal'
    )
end
local function advanceChain(run, dt)
    local balls = run.balls
    if #balls == 0 then
        return
    end
    local speed = E.Speed(run) * (run.slow > 0 and 0.28 or 1)
    if run.reverse > 0 then
        local delta = math.min(135 * dt, math.max(0, balls[1].d - 38))
        if balls[1].d - delta <= 38 then
            run.reverse = 0
        end
        for _, b in ipairs(balls) do
            b.d = b.d - delta
        end
        return
    end
    -- Work from the entrance towards the portal. Only the rearmost section
    -- drives itself; other sections wait for a push or retract to matching ends.
    local groups = {}
    local first = 1
    for i = 1, #balls do
        if not touching(balls[i], balls[i + 1]) then
            groups[#groups + 1] = { first = first, last = i }
            first = i + 1
        end
    end
    local contacts = {}
    for g = #groups, 1, -1 do
        local group = groups[g]
        local delta = speed * dt
        if g < #groups then
            local rear = balls[group.last + 1]
            local front = balls[group.last]
            local same = front.color == rear.color
            delta = same and -90 * dt or 0
            local minimum = rear.d + spacing - front.d
            if delta <= minimum + 0.000001 then
                delta = minimum
                contacts[#contacts + 1] = { ball = rear, combo = rear.joinCombo or 1 }
                rear.joinCombo = nil
            end
        end
        for i = group.first, group.last do
            balls[i].d = balls[i].d + delta
        end
    end
    for _, contact in ipairs(contacts) do
        for i, b in ipairs(balls) do
            if b == contact.ball then
                E.Match(run, i, contact.combo)
                break
            end
        end
    end
end
function E.Swap(run)
    if run and run.status == 'playing' and not run.paused then
        run.loaded, run.next = run.next, run.loaded
        run.loadedKind, run.nextKind = run.nextKind, run.loadedKind
        if A.GameSound then
            A.GameSound('Swap')
        end
    end
end
function E.Fire(run, x, y)
    if not run or run.paused or run.status ~= 'playing' or run.shot or run.cooldown > 0 then
        return false
    end
    local dx, dy = x - 380, y - 250
    local length = math.sqrt(dx * dx + dy * dy)
    if length < 15 then
        return false
    end
    run.shot = {
        x = 380,
        y = 250,
        vx = dx / length * 1040,
        vy = dy / length * 1040,
        color = run.loaded,
        kind = run.loadedKind,
    }
    run.loaded, run.next = run.next, pick(run)
    run.loadedKind = run.nextKind
    run.shotsFired = run.shotsFired + 1
    run.nextKind = nil
    if run.shotsFired % 14 == 0 then
        run.nextKind = ({ 'Bomb', 'Frost', 'Rewind' })[(math.floor(run.shotsFired / 14) - 1) % 3 + 1]
    end
    run.cooldown = 0.10
    if A.GameSound then
        A.GameSound('Shoot')
    end
    return true
end
function E.Animate(r, dt)
    if r.specialImpact then
        r.specialImpact.age = r.specialImpact.age + dt
        if r.specialImpact.age >= 0.8 then
            r.specialImpact = nil
        end
    end
    for i = #r.effects, 1, -1 do
        r.effects[i].age = r.effects[i].age + dt
        if r.effects[i].age > 0.6 then
            table.remove(r.effects, i)
        end
    end
    if r.burst then
        r.burst.age = r.burst.age + dt
        if r.burst.age > (r.burst.combo > 1 and 0.9 or 0.55) then
            r.burst = nil
        end
    end
end
-- Endings are saved simulation state: closing pauses the cinematic, reopening
-- resumes it. Input remains locked until the result card has appeared.
function E.BeginEnding(r, won)
    r.paused = false
    r.shot = nil
    r.ending = { age = 0, phase = won and 'celebrate' or 'drain', won = won, popupAge = 0 }
    if not won then
        local tail = r.balls[#r.balls] and r.balls[#r.balls].d or 0
        for i = 1, r.remaining do
            r.balls[#r.balls + 1] = { color = math.random(r.colorCount), d = tail - i * spacing }
        end
        r.remaining = 0
        local last = r.balls[#r.balls]
        r.ending.speed = math.max(700, (E.Path(E.Route(r)).length - (last and last.d or 0) + 35) / 2)
    end
end
function E.EndStep(r, dt)
    local ending = r.ending
    if not ending or ending.done or r.paused then
        return
    end
    E.Animate(r, dt)
    ending.age = ending.age + dt
    if ending.phase == 'drain' then
        local finish = E.Path(E.Route(r)).length
        for i = #r.balls, 1, -1 do
            local b = r.balls[i]
            b.d = b.d + ending.speed * dt
            if b.d >= finish + 18 then
                table.remove(r.balls, i)
            end
        end
        r.head = r.balls[1] and r.balls[1].d or finish
        if #r.balls == 0 then
            ending.phase = 'result'
        end
    elseif ending.phase == 'celebrate' then
        local beat = math.floor(ending.age / 0.12)
        if beat ~= (ending.beat or -1) then
            ending.beat = beat
            local angle = beat * 2.4
            r.effects[#r.effects + 1] = {
                x = 380 + math.cos(angle) * 130,
                y = 250 + math.sin(angle) * 110,
                age = 0,
                color = beat % 5 + 1,
                kind = 'Spark',
            }
        end
        if ending.age >= 1.1 then
            ending.phase = 'result'
        end
    else
        ending.popupAge = math.min(0.5, ending.popupAge + dt)
        if ending.popupAge >= 0.5 and #r.effects == 0 then
            ending.done = true
            r.paused = true
        end
    end
end
local function advance(db, dt)
    local r = db.run
    if not r then
        return
    end
    dt = math.min(dt, 0.05)
    if r.status ~= 'playing' then
        if r.ending then
            E.EndStep(r, dt)
        else
            E.Animate(r, dt)
        end
        return
    end
    if r.paused then
        return
    end
    if r.cleared then
        E.Animate(r, dt)
        return
    end
    E.Animate(r, dt)
    r.cooldown = math.max(0, r.cooldown - dt)
    r.slow = math.max(0, (r.slow or 0) - dt)
    r.reverse = math.max(0, (r.reverse or 0) - dt)
    advanceChain(r, dt)
    while r.remaining > 0 and (#r.balls == 0 or r.balls[#r.balls].d >= spacing) do
        local d = #r.balls == 0 and 0 or r.balls[#r.balls].d - spacing
        r.balls[#r.balls + 1] = { color = math.random(r.colorCount), d = d }
        r.remaining = r.remaining - 1
    end
    r.head = r.balls[1] and r.balls[1].d or 0
end

local function finish(db, r)
    db.best = math.max(db.best, r.score)
    if #r.balls == 0 and r.remaining == 0 then
        if r.dual then
            r.cleared = true
        else
            if A.GameSound then
                A.GameSound('Win')
            end
            r.status = 'won'
            E.BeginEnding(r, true)
            db.level = math.min(E.MAX_LEVEL, math.max(db.level, r.level + 1))
            r.campaignComplete = r.level == E.MAX_LEVEL
        end
    elseif #r.balls > 0 and r.head >= E.Path(E.Route(r)).length then
        if A.GameSound then
            A.GameSound('Lose')
        end
        r.status = 'lost'
        db.level = 1
        E.BeginEnding(r, false)
    end
end

local function shoot(r, dt)
    local shot = r.shot
    if shot then
        -- Swept collision prevents fast shots tunnelling through a 25px marble.
        local dx, dy = shot.vx * dt, shot.vy * dt
        local hit, hitT, hitLane
        for _, lane in ipairs(r.other and { r, r.other } or { r }) do
            for i = 1, #lane.balls do
                local x, y = E.Point(E.Route(lane), lane.balls[i].d)
                local ox, oy = shot.x - x, shot.y - y
                local aa = dx * dx + dy * dy
                local bb = 2 * (ox * dx + oy * dy)
                local cc = ox * ox + oy * oy - 23 * 23
                local disc = bb * bb - 4 * aa * cc
                if lane.balls[i].d >= 0 and not E.Hidden(lane, lane.balls[i].d) and aa > 0 and disc >= 0 then
                    local t = cc <= 0 and 0 or (-bb - math.sqrt(disc)) / (2 * aa)
                    if t >= 0 and t <= 1 and (not hitT or t < hitT) then
                        hit, hitT, hitLane = i, t, lane
                    end
                end
            end
        end
        if hit then
            shot.x, shot.y = shot.x + dx * hitT, shot.y + dy * hitT
            local d = hitLane.balls[hit].d
            local x, y = E.Point(E.Route(hitLane), d)
            local tx, ty = E.Point(E.Route(hitLane), d + 2)
            if d >= E.Path(E.Route(hitLane)).length - 2 then
                local px, py = E.Point(E.Route(hitLane), d - 2)
                tx, ty = x + (x - px), y + (y - py)
            end
            local index = ((shot.x - x) * (tx - x) + (shot.y - y) * (ty - y) >= 0) and hit or hit + 1
            if shot.kind then
                E.Special(hitLane, hit, shot.kind)
            else
                if A.GameSound then
                    A.GameSound('Hit')
                end
                E.Insert(hitLane, index, shot.color, d + (index == hit and spacing or -spacing))
            end
            r.shot = nil
        else
            shot.x, shot.y = shot.x + dx, shot.y + dy
            if shot.x < 0 or shot.x > 760 or shot.y < 0 or shot.y > 500 then
                r.shot = nil
            end
        end
    end
end

function E.Step(db, dt)
    local r = db.run
    if not r or (r.paused and (r.ending or r.status == 'playing')) then
        return
    end
    dt = math.min(dt, 0.05)
    if not r.other then
        advance(db, dt)
        if r.status == 'playing' and not r.paused then
            shoot(r, dt)
            finish(db, r)
        end
        return
    end
    local other = r.other
    other.paused = r.paused
    local holder = { run = other, best = 0, level = r.level }
    advance(holder, dt)
    advance(db, dt)
    if r.status == 'playing' and not r.paused then
        shoot(r, dt)
        r.score = r.score + other.score
        other.score = 0
        finish(holder, other)
        finish(db, r)
        if r.status == 'lost' or other.status == 'lost' then
            db.level = 1
            if r.status ~= 'lost' then
                r.status = 'lost'
                E.BeginEnding(r, false)
            end
            if other.status ~= 'lost' then
                other.status = 'lost'
                E.BeginEnding(other, false)
            end
        elseif r.cleared and other.cleared then
            r.status = 'won'
            E.BeginEnding(r, true)
            other.status = 'won'
            other.ending = { phase = 'result', done = true, won = true, popupAge = 0.5, age = 2 }
            db.level = math.min(E.MAX_LEVEL, math.max(db.level, r.level + 1))
            r.campaignComplete = r.level == E.MAX_LEVEL
            if A.GameSound then
                A.GameSound('Win')
            end
        end
    end
    if r.ending and not r.ending.won and #other.balls > 0 then
        r.ending.phase = 'drain'
        r.ending.popupAge = 0
        r.ending.done = nil
        r.paused = false
    end
end

local crossingLevel, crossings
function E.Crossings(level)
    if crossingLevel == level then
        return crossings
    end
    crossingLevel, crossings = level, {}
    if not E.IsDualLevel(level) then
        return crossings
    end
    local a, b = E.Path(level), E.Path(level + 1000)
    for d1 = 0, a.length - 20, 20 do
        local x1, y1 = E.Point(level, d1)
        local x2, y2 = E.Point(level, d1 + 20)
        local ax, ay = x2 - x1, y2 - y1
        for d2 = 0, b.length - 20, 20 do
            local x3, y3 = E.Point(level + 1000, d2)
            local x4, y4 = E.Point(level + 1000, d2 + 20)
            local bx, by = x4 - x3, y4 - y3
            local determinant = ax * by - ay * bx
            if math.abs(determinant) > 1 then
                local cx, cy = x3 - x1, y3 - y1
                local t = (cx * by - cy * bx) / determinant
                local u = (cx * ay - cy * ax) / determinant
                if t >= 0 and t <= 1 and u >= 0 and u <= 1 then
                    local x, y = x1 + ax * t, y1 + ay * t
                    local unique = true
                    for _, cross in ipairs(crossings) do
                        if (x - cross.x) ^ 2 + (y - cross.y) ^ 2 < 2500 then
                            unique = false
                        end
                    end
                    if unique then
                        crossings[#crossings + 1] = {
                            x = x,
                            y = y,
                            over = d1 + 20 * t,
                            under = d2 + 20 * u,
                            angle = math.atan2(ay * 0.86, ax),
                            underAngle = math.atan2(by * 0.86, bx),
                            level = level,
                        }
                    end
                end
            end
        end
    end
    return crossings
end
function E.TunnelHalf(cross)
    local length = E.Path(cross.level + 1000).length
    return math.max(0, math.min(64, cross.under - 24, length - cross.under - 180))
end
function E.CoverBounds(cross)
    if cross.bounds then
        return unpack(cross.bounds)
    end
    local left, top, right, bottom = math.huge, math.huge, -math.huge, -math.huge
    for offset = -E.TunnelHalf(cross), E.TunnelHalf(cross), 4 do
        local x, y = E.Point(cross.level + 1000, cross.under + offset)
        y = y * 0.86
        left, top, right, bottom =
            math.min(left, x), math.min(top, y), math.max(right, x), math.max(bottom, y)
    end
    cross.bounds = { left - 18, top - 18, right - left + 36, bottom - top + 36 }
    return unpack(cross.bounds)
end
function E.Hidden(run, distance)
    local route = E.Route(run)
    local x, y = E.Point(route, distance)
    if distance < 24 then
        return true
    end
    if not run.route then
        return false
    end
    for _, cross in ipairs(E.Crossings(run.level)) do
        if math.abs(distance - cross.under) <= E.TunnelHalf(cross) then
            return true
        end
    end
    return false
end
function E.Pressure(run)
    local value = run.head / E.Path(E.Route(run)).length
    if run.other then
        value = math.max(value, run.other.head / E.Path(E.Route(run.other)).length)
    end
    return math.max(0, math.min(1, value))
end
function E.Remaining(run)
    return #run.balls + run.remaining + (run.other and (#run.other.balls + run.other.remaining) or 0)
end
