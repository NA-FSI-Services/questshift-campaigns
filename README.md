# QuestShift campaigns

Authored 60-minute adventures. The engine mounts this repo (or copies a file) and treats YAML rooms as the puzzle source of truth. Granite narrates; it does not invent win conditions.

## Files

| File | Purpose |
| --- | --- |
| [campaigns/campaign-devops-dungeon.yaml](campaigns/campaign-devops-dungeon.yaml) | First 1-hour run: five rooms |

## Room contract

Each room provides:

- `puzzle_type`: `linux` \| `ansible` \| `openshift` \| `java`
- `narrative` / `success_narrative` / `hint` for LLM fallback
- `expected_command_pattern`: Java regex scored by `CommandEvaluator`
- `forbidden_patterns`: optional known-wrong answers
- `loot` and `canvas_event` granted on success

Seats (Guardian, Automancer, Cluster Ranger, Artificer) are cosmetic. Any player may submit the solving command.

## Authoring

Keep the whole file under a 60-minute arc: ~10 minutes of framing, ~8–10 minutes per room, ~5 minutes of boss + debrief. Prefer one obvious intended command plus a regex that still accepts reasonable aliases (`oc` vs `kubectl`, `grep -i` vs `grep`).

## Quality gates

Python 3.11+.

```bash
python3 -m pip install -r requirements-dev.txt
./verify.sh              # yamllint, ruff, pytest-cov ≥ 80% on tools/
```

Pre-commit (once per clone): `./.githooks/install`. PRs to `main` run **Quality** / **Lint, ruff, coverage**. Dependabot opens weekly GitHub Actions update PRs.
