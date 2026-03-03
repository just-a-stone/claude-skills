#!/usr/bin/env python3
"""
Fetch file content from GitLab repository for MR review context.

Usage:
    python fetch_file.py <mr_url> <file_path> [file_path2 ...] [--ref source|target|<branch>]

Example:
    python fetch_file.py http://10.13.29.154/group/project/merge_requests/19 src/main/App.java
    python fetch_file.py http://10.13.29.154/group/project/merge_requests/19 src/App.java --ref target

Environment:
    GITLAB_TOKEN: GitLab personal access token with api scope
"""

import os
import sys
import re
import json
import base64
import urllib.request
import urllib.error
from urllib.parse import urlparse, quote
from typing import Tuple


def parse_mr_url(mr_url):
    # type: (str) -> Tuple[str, str, str]
    """
    Parse MR URL to extract base_url, project_path, and mr_iid.

    Example:
        http://10.13.29.154/iflorens/iflorens-bill-ap-core/merge_requests/19
        -> ('http://10.13.29.154', 'iflorens/iflorens-bill-ap-core', '19')
    """
    parsed = urlparse(mr_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    match = re.match(r'^(.+?)(?:/-)?/merge_requests/(\d+)$', parsed.path)
    if not match:
        raise ValueError(f"Invalid MR URL format: {mr_url}")

    project_path = match.group(1).strip('/')
    mr_iid = match.group(2)

    return base_url, project_path, mr_iid


def gitlab_api_request(base_url, endpoint, token):
    # type: (str, str, str) -> dict
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


def fetch_mr_info(base_url, project_path, mr_iid, token):
    # type: (str, str, str, str) -> dict
    """Fetch MR basic information."""
    encoded_path = quote(project_path, safe='')
    endpoint = f"/projects/{encoded_path}/merge_requests/{mr_iid}"
    return gitlab_api_request(base_url, endpoint, token)


def fetch_file_content(base_url, project_path, file_path, ref, token):
    # type: (str, str, str, str, str) -> dict
    """Fetch file content from GitLab repository."""
    encoded_project = quote(project_path, safe='')
    encoded_file = quote(file_path, safe='')
    endpoint = f"/projects/{encoded_project}/repository/files/{encoded_file}?ref={quote(ref, safe='')}"
    return gitlab_api_request(base_url, endpoint, token)


def format_file_output(file_info, file_path, ref):
    # type: (dict, str, str) -> str
    """Format file content for output."""
    output = []
    output.append("=" * 60)
    output.append(f"File: {file_path}")
    output.append(f"Ref: {ref}")
    output.append(f"Size: {file_info.get('size', 'unknown')} bytes")
    output.append("=" * 60)

    content = file_info.get('content', '')
    encoding = file_info.get('encoding', '')

    if encoding == 'base64':
        try:
            decoded = base64.b64decode(content).decode('utf-8')
            output.append(decoded)
        except UnicodeDecodeError:
            output.append("(binary file, cannot display as text)")
    elif content:
        output.append(content)
    else:
        output.append("(empty file)")

    return '\n'.join(output)


def parse_args(argv):
    # type: (list) -> Tuple[str, list, str]
    """Parse command line arguments. Returns (mr_url, file_paths, ref)."""
    if len(argv) < 3:
        return None, [], ''

    mr_url = argv[1]
    file_paths = []
    ref = 'source'

    i = 2
    while i < len(argv):
        if argv[i] == '--ref':
            if i + 1 < len(argv):
                ref = argv[i + 1]
                i += 2
            else:
                raise ValueError("--ref requires a value (source, target, or branch name)")
        else:
            file_paths.append(argv[i])
            i += 1

    return mr_url, file_paths, ref


def main():
    try:
        mr_url, file_paths, ref = parse_args(sys.argv)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not mr_url or not file_paths:
        print("Usage: python fetch_file.py <mr_url> <file_path> [file_path2 ...] [--ref source|target|<branch>]")
        print()
        print("Options:")
        print("  --ref source   Fetch from MR source branch (default)")
        print("  --ref target   Fetch from MR target branch")
        print("  --ref <name>   Fetch from specified branch/tag/commit")
        print()
        print("Example:")
        print("  python fetch_file.py http://gitlab.example.com/group/project/merge_requests/123 src/App.java")
        print("  python fetch_file.py http://gitlab.example.com/group/project/merge_requests/123 src/App.java --ref target")
        sys.exit(1)

    token = os.environ.get('GITLAB_TOKEN')
    if not token:
        print("Error: GITLAB_TOKEN environment variable is not set")
        print("Please set it with: export GITLAB_TOKEN=<your_token>")
        sys.exit(1)

    try:
        base_url, project_path, mr_iid = parse_mr_url(mr_url)

        # Resolve ref from MR info
        if ref in ('source', 'target'):
            mr_info = fetch_mr_info(base_url, project_path, mr_iid, token)
            if ref == 'source':
                resolved_ref = mr_info['source_branch']
            else:
                resolved_ref = mr_info['target_branch']
        else:
            resolved_ref = ref

        # Fetch each file
        results = []
        errors = []
        for fp in file_paths:
            try:
                file_info = fetch_file_content(base_url, project_path, fp, resolved_ref, token)
                results.append(format_file_output(file_info, fp, resolved_ref))
            except RuntimeError as e:
                errors.append(f"Failed to fetch {fp}: {e}")

        # Output results
        print('\n\n'.join(results))

        if errors:
            print("\n" + "=" * 60)
            print("Errors:")
            for err in errors:
                print(f"  - {err}")
            if not results:
                sys.exit(1)

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
