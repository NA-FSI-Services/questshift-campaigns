# Agent notes — questshift-campaigns

Canonical map:

- GitHub: https://github.com/NA-FSI-Services/questshift/blob/main/AGENTS.md
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/AGENTS.md`

Authoring contract:

- GitHub: https://github.com/NA-FSI-Services/questshift/blob/main/docs/CAMPAIGN-AUTHORING.md
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift/docs/CAMPAIGN-AUTHORING.md`

Adventure YAMLs:

- GitHub: https://github.com/NA-FSI-Services/questshift-campaigns/blob/main/campaigns/campaign-devops-dungeon.yaml
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-campaigns/campaigns/campaign-devops-dungeon.yaml`
- GitHub: https://github.com/NA-FSI-Services/questshift-campaigns/blob/main/campaigns/campaign-ansible-bastion.yaml
- Local: `/Users/dtorresf/Documents/GitHub/na-fsi-services/questshift/questshift-campaigns/campaigns/campaign-ansible-bastion.yaml`

## This repo

YAML is the puzzle source of truth. Ships **two** campaigns (`devops-dungeon` default, `ansible-bastion`), five rooms each, 60 minutes.

- Every room needs `expected_command_pattern`, `accepted_examples`, `hint`, fallback `narrative`, and a `guardian` (`id`, `title`, `sprite`) for the locked north challenge door.
- Each room also has an always-open south lobby door back to the overworld. Do not put the guardian on that door. After a pass, the open north door enters the next room (`order + 1`).
- `forbidden_patterns` catch the known-broken command. Do not hide wins only in `system_prompt`.
- Seats stay cosmetic. No `required_seat`.
- Keep engine classpath copy and gitops ConfigMap copy in sync when you edit.
- Engine restart required after YAML changes (no reload endpoint).
- Do not paste Hugging Face tokens, kubeconfigs, or API keys into campaign YAML.
- Quality: `./verify.sh` (yamllint, ruff, pytest-cov ≥ 80% on `tools/`). Pre-commit: `./.githooks/install`. CI: `.github/workflows/quality.yml`. Dependabot: `.github/dependabot.yml` (weekly GitHub Actions).
