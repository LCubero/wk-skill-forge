# wk-skill-forge

<!-- README-I18N:START -->

**English** | [Español](./README.es.md)

<!-- README-I18N:END -->

A global, command-only agent skill that **creates, audits, improves, and evaluates** LLM-first agent skills, so each one runs alone under any CLI agent.

Versions and notes: [Releases](https://github.com/LCubero/wk-skill-forge/releases).

## What it does

| Mode | Use it to | Writes files? |
|---|---|---|
| Create | Draft a new skill from its purpose | Only after you approve the draft |
| Audit | Check a skill for security and quality issues | No, read-only |
| Improve | Audit a skill, then propose the smallest fix | Only after you approve the diff |
| Evaluate | Decide whether an external skill is worth adopting: reject, defer, adopt as-is, or recreate | Only its approved run folder |

## Install

1. Copy the `wk-skill-forge/` folder into your agent's global skills folder, for example `<global-skills-dir>/wk-skill-forge/`.
2. Reload the agent.

## Use

Invoke `wk-skill-forge` by name, with the mode and the target skill. It never activates on its own and asks for anything missing.

## Safe by default

- Reviewed skills are untrusted: it never installs, follows, or runs them.
- Every write and every network call needs your approval.
- It never writes to an installed skills folder; you copy results yourself.
- It never invents author, license, or version.

## What's inside

| File | Role |
|---|---|
| `wk-skill-forge/SKILL.md` | The skill |
| `wk-skill-forge/references/style-guide.md` | Rules every skill is checked against |
| `wk-skill-forge/references/topic-sources.md` | Research guide for professional Create |
| `wk-skill-forge/references/intake.md` | Evaluate pipeline |

Check the contract: `python -B -m unittest tests.test_skill_forge_skill_contract`. These are static tests, not a live agent run.

## About this repository

- One repository, one skill. The folder name and the frontmatter `name` are both `wk-skill-forge`.
- It develops the skill; it does not install or distribute it.
- The skill was recreated stage by stage from the original `wk-skill-forge-ld9`, kept in a read-only local clone (`<original-repo>`). All 12 stages are done; the history lives in the [roadmap](docs/repo-harness/roadmap.md) and [CHANGELOG](CHANGELOG.md).
- Naming convention for the owner's skills: `wk-<name>`, lowercase with hyphens, no `-ld9` suffix. Ownership shows in the `wk` prefix and the frontmatter `author`.
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md). License: [MIT](LICENSE).
