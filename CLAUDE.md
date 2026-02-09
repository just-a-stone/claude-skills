# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 Claude Code Skills 集合项目，用于开发和维护 Claude Code 自定义技能。

**重要**：当用户要求新增或修改技能时，请在当前项目目录中操作，不要修改用户目录（`~/.claude/`）下的文件。

## 技能开发规范

每个技能遵循标准目录结构：
```
skill-name/
├── SKILL.md           # 必需：技能配置（含 YAML frontmatter）和使用文档
└── scripts/           # 可选：辅助脚本
```

SKILL.md frontmatter 格式：
```yaml
---
name: skill-name
description: 何时调用此技能的简要描述
---
```

## 安装技能

方法 1 - 直接路径（在 `~/.claude/settings.json` 中添加）：
```json
{
  "skills": ["/absolute/path/to/skill-directory"]
}
```

方法 2 - 打包 .skill 文件：
```bash
cd skill-name
zip -r ../dist/skill-name.skill SKILL.md scripts/
```

## 当前技能

### gitlab-mr-review

从自托管 GitLab 实例获取并审查合并请求代码变更。

**依赖**：
- 环境变量 `GITLAB_TOKEN`（需要 `api` 权限范围）
- Python 3.8+（仅使用标准库）

**核心脚本**：
- `scripts/fetch_mr_diff.py` - 解析 MR URL，调用 GitLab API v4 获取 MR 信息和差异
- `scripts/post_mr_comment.py` - 向 MR 发布 Markdown 格式审查评论

**支持的 URL 格式**：
- `http://gitlab.example.com/group/project/merge_requests/123`
- `http://gitlab.example.com/-/group/project/-/merge_requests/123`

### cc-nano-banana

使用 Gemini CLI 的 nanobanana 扩展生成和编辑图片。

**功能**：
- 文字生成图片（博客封面、YouTube 缩略图等）
- 图片编辑与修改
- 照片修复
- 图标生成（应用图标、favicon）
- 图表生成（流程图、架构图）
- 无缝纹理/图案生成
- 连续叙事图像

**依赖**：
- Gemini CLI（`npm install -g @anthropic-ai/gemini-cli`）
- 环境变量 `GEMINI_API_KEY`（从 [Google AI Studio](https://aistudio.google.com/) 获取）
- nanobanana 扩展（`gemini extensions install https://github.com/gemini-cli-extensions/nanobanana`）

**常用命令**：
- `/generate` - 文字生成图片
- `/edit` - 编辑现有图片
- `/icon` - 生成应用图标
- `/diagram` - 生成图表
- `/restore` - 修复老照片
- `/pattern` - 生成无缝纹理

**输出目录**：`./nanobanana-output/`

**参考**：[cc-nano-banana GitHub](https://github.com/kkoppenhaver/cc-nano-banana)
