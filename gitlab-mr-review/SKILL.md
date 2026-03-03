---
name: gitlab-mr-review
description: Fetch and review GitLab Merge Request code changes. Use when user provides a GitLab MR URL (containing /merge_requests/) and wants to review code, analyze changes, or get feedback on the merge request. Supports self-hosted GitLab instances. Requires GITLAB_TOKEN environment variable.
---

# GitLab MR Review

Fetch merge request diffs from self-hosted GitLab for code review.

## Prerequisites

Ensure `GITLAB_TOKEN` environment variable is set with a personal access token that has `api` scope.

## Workflow

1. User provides MR URL (e.g., `http://gitlab.example.com/group/project/merge_requests/123`)
2. Run `scripts/fetch_mr_diff.py` to fetch MR info and diffs
3. Review the code changes and provide feedback
4. If diff context is insufficient, use `scripts/fetch_file.py` to fetch full file content for deeper understanding

## Usage

```bash
python3 scripts/fetch_mr_diff.py <mr_url>
```

Example:
```bash
python3 scripts/fetch_mr_diff.py http://10.13.29.154/iflorens/iflorens-bill-ap-core/merge_requests/19
```

## Output Format

The script outputs:
- MR overview (title, author, branches, state, description)
- Changed files list with status markers: `[NEW]`, `[DEL]`, `[REN]`, `[MOD]`
- Full diff for each changed file

## Fetch Full File Content (Optional, 当前工作目录没有review的项目时)

**约束：仅在确认存在 P0 级别问题（如严重安全漏洞、数据丢失风险、核心逻辑错误）且 diff 上下文确实不足以判断时，才使用此脚本拉取完整文件。** 避免随意拉取文件导致上下文无限膨胀，每次拉取前应明确说明理由。

When diff context is not enough to understand the full logic, fetch complete file content:

```bash
python3 scripts/fetch_file.py <mr_url> <file_path> [file_path2 ...] [--ref source|target|<branch>]
```

- Default `--ref source`: fetch from MR source branch (the changed version)
- `--ref target`: fetch from MR target branch (the original version)
- `--ref <branch>`: fetch from any branch/tag/commit

Examples:
```bash
# Fetch single file from source branch
python3 scripts/fetch_file.py http://gitlab.example.com/group/project/merge_requests/123 src/main/App.java

# Fetch original version from target branch
python3 scripts/fetch_file.py http://gitlab.example.com/group/project/merge_requests/123 src/main/App.java --ref target

# Fetch multiple files
python3 scripts/fetch_file.py http://gitlab.example.com/group/project/merge_requests/123 src/App.java src/Utils.java
```

## Post Review Comment (Optional)

After review, post summary to MR as a comment:
(Do not mention AI names like 'by Claude Code' in the comments)

```bash
python3 scripts/post_mr_comment.py <mr_url> "<comment>"
```

Before posting, ask user for confirmation. Format the review summary in Markdown.

## Code Review Guidelines

When reviewing the diff, focus on:

1. **Correctness**: Logic errors, edge cases, null checks
2. **Security**: Input validation, SQL injection, XSS, sensitive data exposure
3. **Performance**: N+1 queries, unnecessary loops, memory leaks
4. **Maintainability**: Code clarity, naming, duplication
5. **Best Practices**: Error handling, logging, testing coverage
