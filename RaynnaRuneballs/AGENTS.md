# Runeballs release rules

Target Lua 5.1 and WoW Forever Interface 16001. Ordinary balls remain plain;
ability icons appear only on special ammunition. Keep saves serializable.
Preserve both faction themes and reduced-motion behavior. Shared GameRegistry
and SettingsRegistry bootstraps must stay identical across Raynna packages.

Every shipped update requires a new TOC version, matching versioned player ZIP,
and matching vVERSION GitHub release/tag. Follow RELEASE.md. Run tests and inspect
both faction previews before deployment; never overwrite WTF saved variables.
