#!/usr/bin/env python3
"""
Post a comment to GitLab Merge Request.

Usage:
    python post_mr_comment.py <mr_url> <comment>

Example:
    python post_mr_comment.py http://10.13.29.154/group/project/merge_requests/19 "LGTM!"

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
    """
    parsed = urlparse(mr_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    match = re.match(r'^(.+?)(?:/-)?/merge_requests/(\d+)$', parsed.path)
    if not match:
        raise ValueError(f"Invalid MR URL format: {mr_url}")

    project_path = match.group(1).strip('/')
    mr_iid = match.group(2)

    return base_url, project_path, mr_iid


def post_comment(base_url: str, project_path: str, mr_iid: str, token: str, comment: str) -> dict:
    """Post a note (comment) to the merge request."""
    encoded_path = quote(project_path, safe='')
    url = f"{base_url}/api/v4/projects/{encoded_path}/merge_requests/{mr_iid}/notes"

    data = json.dumps({"body": comment}).encode('utf-8')

    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('PRIVATE-TOKEN', token)
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        raise RuntimeError(f"GitLab API error {e.code}: {error_body}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python post_mr_comment.py <mr_url> <comment>")
        print('Example: python post_mr_comment.py http://gitlab.example.com/group/project/merge_requests/123 "LGTM!"')
        sys.exit(1)

    mr_url = sys.argv[1]
    comment = sys.argv[2]
    token = os.environ.get('GITLAB_TOKEN')

    if not token:
        print("Error: GITLAB_TOKEN environment variable is not set")
        sys.exit(1)

    if not comment.strip():
        print("Error: Comment cannot be empty")
        sys.exit(1)

    try:
        base_url, project_path, mr_iid = parse_mr_url(mr_url)
        result = post_comment(base_url, project_path, mr_iid, token, comment)
        print(f"Comment posted successfully!")
        print(f"Comment ID: {result.get('id')}")
        print(f"URL: {mr_url}#note_{result.get('id')}")

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
