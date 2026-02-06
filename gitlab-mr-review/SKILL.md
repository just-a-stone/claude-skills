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

## Usage

```bash
python scripts/fetch_mr_diff.py <mr_url>
```

Example:
```bash
python scripts/fetch_mr_diff.py http://10.13.29.154/iflorens/iflorens-bill-ap-core/merge_requests/19
```

## Output Format

The script outputs:
- MR overview (title, author, branches, state, description)
- Changed files list with status markers: `[NEW]`, `[DEL]`, `[REN]`, `[MOD]`
- Full diff for each changed file

## Post Review Comment (Optional)

After review, post summary to MR as a comment:

```bash
python scripts/post_mr_comment.py <mr_url> "<comment>"
```

Before posting, ask user for confirmation. Format the review summary in Markdown.

## Code Review Guidelines

When reviewing the diff, focus on:

1. **Correctness**: Logic errors, edge cases, null checks
2. **Security**: Input validation, SQL injection, XSS, sensitive data exposure
3. **Performance**: N+1 queries, unnecessary loops, memory leaks
4. **Maintainability**: Code clarity, naming, duplication
5. **Best Practices**: Error handling, logging, testing coverage
