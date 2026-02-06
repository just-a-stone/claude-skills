#!/usr/bin/env python3
"""
Fetch GitLab Merge Request diff for code review.

Usage:
    python fetch_mr_diff.py <mr_url>

Example:
    python fetch_mr_diff.py http://10.13.29.154/iflorens/iflorens-bill-ap-core/merge_requests/19

Environment:
    GITLAB_TOKEN: GitLab personal access token with api scope
"""

import os
import sys
import re
import json
import urllib.request
import urllib.error
from urllib.parse import urlparse, quote


def parse_mr_url(mr_url: str) -> tuple[str, str, str]:
    """
    Parse MR URL to extract base_url, project_path, and mr_iid.

    Example:
        http://10.13.29.154/iflorens/iflorens-bill-ap-core/merge_requests/19
        -> ('http://10.13.29.154', 'iflorens/iflorens-bill-ap-core', '19')
    """
    parsed = urlparse(mr_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # Match pattern: /<project_path>/merge_requests/<iid> or /-/merge_requests/<iid>
    match = re.match(r'^(.+?)(?:/-)?/merge_requests/(\d+)$', parsed.path)
    if not match:
        raise ValueError(f"Invalid MR URL format: {mr_url}")

    project_path = match.group(1).strip('/')
    mr_iid = match.group(2)

    return base_url, project_path, mr_iid


def gitlab_api_request(base_url: str, endpoint: str, token: str) -> dict:
    """Make authenticated request to GitLab API."""
    url = f"{base_url}/api/v4{endpoint}"
    req = urllib.request.Request(url)
    req.add_header('PRIVATE-TOKEN', token)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        raise RuntimeError(f"GitLab API error {e.code}: {error_body}")


def fetch_mr_info(base_url: str, project_path: str, mr_iid: str, token: str) -> dict:
    """Fetch MR basic information."""
    encoded_path = quote(project_path, safe='')
    endpoint = f"/projects/{encoded_path}/merge_requests/{mr_iid}"
    return gitlab_api_request(base_url, endpoint, token)


def fetch_mr_changes(base_url: str, project_path: str, mr_iid: str, token: str) -> dict:
    """Fetch MR changes (diffs)."""
    encoded_path = quote(project_path, safe='')
    endpoint = f"/projects/{encoded_path}/merge_requests/{mr_iid}/changes"
    return gitlab_api_request(base_url, endpoint, token)


def format_diff_output(mr_info: dict, changes: dict) -> str:
    """Format MR info and diffs for code review."""
    output = []

    # MR Overview
    output.append("=" * 60)
    output.append(f"Merge Request: !{mr_info['iid']} - {mr_info['title']}")
    output.append("=" * 60)
    output.append(f"Author: {mr_info['author']['name']} (@{mr_info['author']['username']})")
    output.append(f"Source: {mr_info['source_branch']} -> {mr_info['target_branch']}")
    output.append(f"State: {mr_info['state']}")
    output.append(f"URL: {mr_info['web_url']}")

    if mr_info.get('description'):
        output.append(f"\nDescription:\n{mr_info['description']}")

    output.append("\n" + "=" * 60)
    output.append("Changed Files")
    output.append("=" * 60)

    # List changed files
    file_changes = changes.get('changes', [])
    for i, change in enumerate(file_changes, 1):
        old_path = change.get('old_path', '')
        new_path = change.get('new_path', '')

        if change.get('new_file'):
            status = "[NEW]"
            path = new_path
        elif change.get('deleted_file'):
            status = "[DEL]"
            path = old_path
        elif change.get('renamed_file'):
            status = "[REN]"
            path = f"{old_path} -> {new_path}"
        else:
            status = "[MOD]"
            path = new_path

        output.append(f"{i}. {status} {path}")

    output.append(f"\nTotal: {len(file_changes)} file(s) changed")

    # Detailed diffs
    output.append("\n" + "=" * 60)
    output.append("Detailed Diffs")
    output.append("=" * 60)

    for change in file_changes:
        new_path = change.get('new_path', change.get('old_path', 'unknown'))
        output.append(f"\n--- {new_path} ---")

        diff = change.get('diff', '')
        if diff:
            output.append(diff)
        else:
            output.append("(binary file or no diff available)")

    return '\n'.join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_mr_diff.py <mr_url>")
        print("Example: python fetch_mr_diff.py http://gitlab.example.com/group/project/merge_requests/123")
        sys.exit(1)

    mr_url = sys.argv[1]
    token = os.environ.get('GITLAB_TOKEN')

    if not token:
        print("Error: GITLAB_TOKEN environment variable is not set")
        print("Please set it with: export GITLAB_TOKEN=<your_token>")
        sys.exit(1)

    try:
        base_url, project_path, mr_iid = parse_mr_url(mr_url)

        mr_info = fetch_mr_info(base_url, project_path, mr_iid, token)
        changes = fetch_mr_changes(base_url, project_path, mr_iid, token)

        output = format_diff_output(mr_info, changes)
        print(output)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
