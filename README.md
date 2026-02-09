# Claude Code Skills

A collection of custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Skills

| Skill | Description |
|-------|-------------|
| [gitlab-mr-review](./gitlab-mr-review/) | Fetch and review GitLab Merge Request code changes |
| [cc-nano-banana](./cc-nano-banana/) | Generate and edit images using Gemini CLI's nanobanana extension |

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

```yaml
---
name: skill-name
description: Brief description for when to invoke this skill
---

# Skill Title

Instructions and documentation for the skill...
```

## Skill Details

### gitlab-mr-review

Fetch and review GitLab Merge Request code changes from self-hosted GitLab instances.

**Requirements**:
- Environment variable `GITLAB_TOKEN` (requires `api` scope)
- Python 3.8+ (standard library only)

**Core Scripts**:
- `scripts/fetch_mr_diff.py` - Parse MR URL, call GitLab API v4 to fetch MR info and diff
- `scripts/post_mr_comment.py` - Post Markdown review comments to MR

**Supported URL Formats**:
- `http://gitlab.example.com/group/project/merge_requests/123`
- `http://gitlab.example.com/-/group/project/-/merge_requests/123`

### cc-nano-banana

Generate and edit images using Gemini CLI's nanobanana extension.

**Features**:
- Text-to-image generation (blog covers, YouTube thumbnails, etc.)
- Image editing and modification
- Photo restoration
- Icon generation (app icons, favicons)
- Diagram generation (flowcharts, architecture diagrams)
- Seamless texture/pattern generation
- Sequential narrative images

**Requirements**:
- Gemini CLI (`npm install -g @anthropic-ai/gemini-cli`)
- Environment variable `GEMINI_API_KEY` (get from [Google AI Studio](https://aistudio.google.com/))
- nanobanana extension (`gemini extensions install https://github.com/gemini-cli-extensions/nanobanana`)

**Common Commands**:
- `/generate` - Text-to-image generation
- `/edit` - Edit existing images
- `/icon` - Generate app icons
- `/diagram` - Generate diagrams
- `/restore` - Restore old photos
- `/pattern` - Generate seamless textures

**Output Directory**: `./nanobanana-output/`

**Reference**: [cc-nano-banana GitHub](https://github.com/kkoppenhaver/cc-nano-banana)

## License

MIT
