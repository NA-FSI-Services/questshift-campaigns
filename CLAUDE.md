# Claude / Cursor — questshift-campaigns

Read `AGENTS.md` first (this repo), then the docs-repo map.

- GitHub: https://github.com/NA-FSI-Services/questshift/blob/main/AGENTS.md
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/AGENTS.md`

## Hard rules (v1 freeze)

- Campaign YAML wins. LLM narrates only. Do not hide win conditions only in prompts.
- Two campaigns: `devops-dungeon` (*The Cluster That Forgot Its Name*) and `ansible-bastion` (*The Bastion That Lost Its Runbook*). Five rooms each. Default remains devops-dungeon.
- Seats are cosmetic; any player may solve any puzzle.
- Regex + `accepted_examples` are the scorer. Keep `forbidden_patterns` for cursed forms.
- Each challenge room: locked north door with a YAML `guardian` until solved; always-open south lobby door. After a pass, the open north door enters the next room.
- No open-ended campaign library, TTS copy, or Ollama-specific prompts. Never execute Ansible or call AWS from YAML text.
- Sync engine classpath and gitops copies when these files change.
- Quality: `./verify.sh` (yamllint, ruff, pytest-cov). Pre-commit: `./.githooks/install`.
