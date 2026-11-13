local _, A = ...
local panel, channels, selected, message
function A.ShareMessage(run)
    return (A.db.demo and '[Demo] ' or '')
        .. "Raynna's Runeballs: "
        .. (run.status == 'won' and 'cleared round ' or 'reached round ')
        .. run.level
        .. '/100 with '
        .. A.Number(run.score)
        .. ' points!'
end
function A.OpenShare()
    local run = A.db.run
    if run.status == 'playing' then
        return
    end
    message = A.ShareMessage(run)
    channels = {
        { 'Say', 'SAY' },
        { 'Yell', 'YELL' },
        { 'Party', 'PARTY' },
        { 'Raid', 'RAID' },
        { 'Guild', 'GUILD' },
        { 'Officer', 'OFFICER' },
        { 'Instance', 'INSTANCE_CHAT' },
        { 'Whisper', 'WHISPER' },
    }
    if GetChannelList then
        local list = { GetChannelList() }
        for i = 1, #list, 3 do
            if type(list[i]) == 'number' and type(list[i + 1]) == 'string' then
                channels[#channels + 1] = { list[i + 1], 'CHANNEL', list[i] }
            end
        end
    end
    selected = 1
    panel.preview:SetText(message)
    panel.target:SetText('')
    panel.error:SetText('')
    panel.choose:SetText('Chat: Say')
    panel.target:Hide()
    panel.targetLabel:Hide()
    panel.send:SetEnabled(true)
    panel:Show()
end
function A.BuildShare(frame, board)
    panel = A.Panel(board, 165, 85, 430, 285)
    frame.share = panel
    panel:ClearAllPoints()
    panel:SetPoint('CENTER', board, 'CENTER')
    panel:SetFrameLevel(board:GetFrameLevel() + 30)
    panel:EnableMouse(true)
    A.Label(panel, 'SHARE YOUR RESULT', 24, -18, 23)
    panel.preview = A.Label(panel, '', 24, -55, 16, 'body')
    panel.preview:SetWidth(382)
    panel.preview:SetHeight(55)
    panel.preview:SetWordWrap(true)
    panel.choose = A.Button(panel, 'Chat: Say', 24, 113, 382, 38, nil, function()
        selected = selected % #channels + 1
        panel.choose:SetText('Chat: ' .. channels[selected][1] .. '  >')
        local whisper = channels[selected][2] == 'WHISPER'
        panel.target:SetShown(whisper)
        panel.targetLabel:SetShown(whisper)
        panel.error:SetText('')
        panel.send:SetEnabled(true)
    end)
    panel.targetLabel = A.Label(panel, 'To:', 24, -163, 15)
    panel.target = CreateFrame('EditBox', nil, panel, 'InputBoxTemplate')
    panel.target:SetPoint('TOPLEFT', 62, -161)
    panel.target:SetSize(330, 26)
    panel.target:SetAutoFocus(false)
    panel.target:SetMaxLetters(80)
    panel.target:SetScript('OnEscapePressed', function(self)
        self:ClearFocus()
    end)
    panel.error = A.Label(panel, '', 24, -198, 14, 'body')
    panel.error:SetWidth(382)
    panel.send = A.Button(panel, 'SEND', 24, 231, 180, 39, nil, function()
        local choice = channels[selected]
        local target = choice[3]
        if choice[2] == 'WHISPER' then
            target = (panel.target:GetText() or ''):match('^%s*(.-)%s*$')
            if target == '' then
                panel.error:SetText('Enter a character name first.')
                return
            end
        end
        local send = C_ChatInfo and C_ChatInfo.SendChatMessage or SendChatMessage
        if not send then
            panel.error:SetText('Chat is unavailable.')
            return
        end
        send(message, choice[2], nil, target)
        panel.send:SetEnabled(false)
        panel.error:SetText('Message submitted to ' .. choice[1] .. '.')
    end)
    A.Button(panel, 'CANCEL', 226, 231, 180, 39, nil, function()
        panel:Hide()
    end)
    panel:Hide()
end
