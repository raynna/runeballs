local _, A = ...
local lastPlayed = {}
-- Blizzard FileDataIDs from wowdev's verified listfile (202611122246).
-- Reference client assets directly; no extracted audio is bundled.
local files = {
    Match = 568678, -- arcaneexplosion.ogg
    Bomb = 568528, -- smallexplosions_generic_01.ogg
    Frost = 569378, -- frostnova.ogg
    Rewind = 569735, -- teleport.ogg
}
local kits = {
    Hit = { 'IG_MAINMENU_OPTION_CHECKBOX_ON', 856 }, -- small native UI click
    Shoot = { 'IG_MAINMENU_OPTION_CHECKBOX_ON', 856 }, -- quiet native click
    Swap = { 'IG_MAINMENU_OPTION_CHECKBOX_ON', 3175 },
    Win = { 'LEVEL_UP', 618 },
    Lose = { 'IG_MAINMENU_CLOSE', 3175 },
}
function A.GameSound(name, combo)
    if not A.db or A.db.options.sound == false then
        return
    end
    local file = files[name]
    local kit = kits[name]
    if name == 'Combo' then
        kit = (combo or 2) >= 3 and { 'LEVEL_UP', 618 } or { 'UI_QUEST_AUTO_COMPLETE', 8430 }
    end
    if not file and not kit then
        return
    end
    local now = GetTime and GetTime() or 0
    local cooldown = (name == 'Shoot' or name == 'Hit') and 0.10 or 0.18
    if lastPlayed[name] and now - lastPlayed[name] < cooldown then
        return
    end
    lastPlayed[name] = now
    -- SFX respects WoW's effects volume. Older clients may lack a file ID;
    -- gracefully fall back to a native UI ping instead of failing gameplay.
    if file and PlaySoundFile then
        local ok, played = pcall(PlaySoundFile, file, 'SFX')
        if ok and played then
            return
        end
    end
    if PlaySound then
        local id = kit and ((SOUNDKIT and SOUNDKIT[kit[1]]) or kit[2])
            or ((SOUNDKIT and SOUNDKIT.MAP_PING) or 3175)
        pcall(PlaySound, id, 'SFX')
    end
end
