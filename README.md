# Claude Code Skills

A collection of custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Skills

| Skill | Description |
|-------|-------------|
| [gitlab-mr-review](./gitlab-mr-review/) | Fetch and review GitLab Merge Request code changes |

## Installation

### Method 1: Add skill directory to Claude settings

Add the skill path to your Claude settings file (`~/.claude/settings.json`):

```json
{
  "skills": [
    "/path/to/claude-skills/gitlab-mr-review"
  ]
}
```

### Method 2: Pack and install .skill file

```bash
# Pack the skill
cd gitlab-mr-review
zip -r ../dist/gitlab-mr-review.skill SKILL.md scripts/

# Then add the .skill file path to settings
```

## Creating New Skills

Each skill should follow this structure:

```
skill-name/
├── SKILL.md           # Required: Skill config with frontmatter
└── scripts/           # Optional: Helper scripts
    └── ...
```

### SKILL.md Format

```markdown
---
name: skill-name
description: Brief description for when to invoke this skill
---

# Skill Title

Instructions and documentation for the skill...
```

## License

MIT
