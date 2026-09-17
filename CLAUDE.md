# Claude / Cursor — questshift-campaigns

Read `AGENTS.md` first (this repo), then the docs-repo map.

- GitHub: https://github.com/NA-FSI-Services/questshift/blob/main/AGENTS.md
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/AGENTS.md`

## Hard rules (v1 freeze)

- Campaign YAML wins. LLM narrates only. Do not hide win conditions only in prompts.
- One campaign: *The Cluster That Forgot Its Name*. Five rooms. Loot runes THORN / ASH / OAK / IRON.
- Seats are cosmetic; any player may solve any puzzle.
- Regex + `accepted_examples` are the scorer. Keep `forbidden_patterns` for cursed forms.
- Each challenge room: locked north door with a YAML `guardian` until solved; always-open south lobby door.
- No extra campaigns, TTS copy, or Ollama-specific prompts.
- Sync engine classpath and gitops copies when this file changes.
- Quality: `./verify.sh` (yamllint, ruff, pytest-cov). Pre-commit: `./.githooks/install`.
