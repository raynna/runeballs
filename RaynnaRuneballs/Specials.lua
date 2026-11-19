local _, A = ...
local E = A.Engine
A.Specials = {
    descriptions = {
        Lightning = 'Lightning: match 3\nZap 5 same-colour balls',
        Paint = 'Paint: match 3\nRecolour nearby balls',
        Stasis = 'Stasis: match 3\nStop this lane for 3s',
        Magnet = 'Magnet: match 3\nPull gaps closed for 4s',
        Treasure = 'Treasure: match 3\nDouble match points for 8s',
        Ward = 'Ward: match 3\nOne portal save for 12s',
        Rainbow = 'Rainbow wildcard\nJoins a same-colour pair',
    },
}
local timers = { 'stasis', 'magnet', 'treasure', 'ward' }
local function nearby(run, d, accept)
    local found = {}
    for i, ball in ipairs(run.balls) do
        if not E.Hidden(run, ball.d) and accept(ball) then
            found[#found + 1] = { ball = ball, index = i, distance = math.abs(ball.d - d) }
        end
    end
    table.sort(found, function(a, b)
        if a.distance == b.distance then
            return a.index < b.index
        end
        return a.distance < b.distance
    end)
    return found
end
function E.ApplyExtraSpecial(run, d, kind, combo, color)
    local impact = run.specialImpact
    if kind == 'Lightning' then
        local targets = nearby(run, d, function(ball)
            return ball.color == color
        end)
        local indices = {}
        impact.links = {}
        for i = 1, math.min(5, #targets) do
            local target = targets[i]
            local x, y = E.Point(E.Route(run), target.ball.d)
            impact.links[#impact.links + 1] = { x = x, y = y }
            indices[#indices + 1] = target.index
        end
        table.sort(indices, function(a, b)
            return a > b
        end)
        for _, index in ipairs(indices) do
            E.ClearSpecialBall(run, index, combo)
        end
    elseif kind == 'Paint' then
        local targets = nearby(run, d, function(ball)
            return not ball.kind and math.abs(ball.d - d) <= 180
        end)
        impact.links = {}
        for i = 1, math.min(4, #targets) do
            local ball = targets[i].ball
            ball.color, ball.paintDelay, ball.paintCombo = color, 0.45, combo + 1
            local x, y = E.Point(E.Route(run), ball.d)
            impact.links[#impact.links + 1] = { x = x, y = y }
        end
    elseif kind == 'Stasis' then
        run.stasis = 3
    elseif kind == 'Magnet' then
        run.magnet = 4
    elseif kind == 'Treasure' then
        run.treasure = 8
    elseif kind == 'Ward' then
        run.ward, run.wardColor = 12, color
    end
end
function E.StepExtraSpecials(run, dt)
    for _, timer in ipairs(timers) do
        run[timer] = math.max(0, (run[timer] or 0) - dt)
    end
    if run.streakNotice then
        run.streakNotice.age = run.streakNotice.age + dt
        if run.streakNotice.age >= 1.8 then
            run.streakNotice = nil
        end
    end
    local ready = {}
    for _, ball in ipairs(run.balls) do
        if ball.paintDelay then
            ball.paintDelay = ball.paintDelay - dt
            if ball.paintDelay <= 0 then
                ready[#ready + 1] = { ball = ball, combo = ball.paintCombo or 2 }
                ball.paintDelay, ball.paintCombo = nil, nil
            end
        end
    end
    -- Keep the recolour visible before resolving new matches; references are
    -- transient only, while the saved countdown lives on each marble.
    for _, target in ipairs(ready) do
        for index, ball in ipairs(run.balls) do
            if ball == target.ball then
                E.Match(run, index, target.combo)
                break
            end
        end
    end
end
function E.TryWard(run)
    if (run.ward or 0) <= 0 then
        return false
    end
    local finish = E.Path(E.Route(run)).length
    local shift = math.max(0, run.head - (finish - 20))
    for _, ball in ipairs(run.balls) do
        ball.d = ball.d - shift
    end
    run.head = run.balls[1].d
    run.ward, run.reverse = 0, math.max(run.reverse or 0, 2.5)
    local x, y = E.Point(E.Route(run), finish)
    run.specialImpact = { x = x, y = y, d = finish, kind = 'Ward', color = run.wardColor or 6, age = 0 }
    if A.GameSound then
        A.GameSound('Ward')
    end
    return true
end
function E.RecordShot(run, matched)
    if not matched then
        run.precision = 0
        return
    end
    run.precision = (run.precision or 0) + 1
    if run.precision % 3 == 0 then
        local bonus = math.min(900, run.precision * 100)
        run.score = run.score + bonus
        run.streakNotice = { age = 0, points = bonus }
        if A.GameSound then
            A.GameSound('Treasure')
        end
    end
end
function E.SpecialStatus(run)
    if run.streakNotice then
        return 'PRECISION +' .. run.streakNotice.points
    end
    for i, lane in ipairs(run.other and { run, run.other } or { run }) do
        for _, timer in ipairs(timers) do
            if (lane[timer] or 0) > 0 then
                return (run.other and ('L' .. i .. ' ') or '')
                    .. timer:upper()
                    .. ' '
                    .. math.ceil(lane[timer])
                    .. 's'
            end
        end
    end
end
