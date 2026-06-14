#!/usr/bin/env python3
"""Resolve the transitive ``uses:`` graph of every action in .github/workflows/.

GitHub's "allowed actions" policy (Settings -> Actions -> General) governs not
only the actions a workflow references directly, but every action they pull in
*transitively*: a composite action runs other actions internally. So an action
you have explicitly allowed can still fail at run time if one of its nested
actions is not also allowed -- which is exactly how a release once broke in this
repo (``sigstore/gh-action-sigstore-python`` calls ``softprops/action-gh-release``
internally, and the latter was not on the allowlist).

This script walks each workflow's ``uses:`` references, fetches each action's
``action.yml`` at its pinned ref, recurses into composite actions, and then
checks every resolved action against this repository's allowed-actions
allowlist. It exits non-zero if any transitive action would be blocked, so it
can be run by hand after bumping an action -- or wired into CI -- to keep the
allowlist provably complete.

Requires the authenticated ``gh`` CLI. Standard library only.

Usage:
    python scripts/resolve_action_uses.py
"""

from __future__ import annotations

import base64
import fnmatch
import json
import re
import subprocess
import sys
from functools import lru_cache

WORKFLOW_DIR = ".github/workflows"
GITHUB_OWNERS = {"actions", "github"}  # treated as "GitHub-owned" by the policy

_USING_RE = re.compile(r"^\s*using:\s*[\"']?([\w.-]+)", re.MULTILINE)
_USES_RE = re.compile(r"""^\s*-?\s*uses:\s*["']?([^"'\s#]+)""", re.MULTILINE)


def _gh(path: str) -> str | None:
    result = subprocess.run(
        ["gh", "api", path], capture_output=True, text=True, check=False
    )
    return result.stdout if result.returncode == 0 else None


def _repo_slug() -> str:
    out = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def _split(use: str) -> tuple[str, str, str]:
    """Split ``owner/repo[/subdir...]@ref`` into (owner/repo, subdir, ref)."""
    path, _, ref = use.partition("@")
    parts = path.split("/")
    return "/".join(parts[:2]), "/".join(parts[2:]), ref or "HEAD"


@lru_cache(maxsize=None)
def _action_yml(owner_repo: str, subdir: str, ref: str) -> str | None:
    prefix = f"{subdir}/" if subdir else ""
    for filename in ("action.yml", "action.yaml"):
        raw = _gh(f"repos/{owner_repo}/contents/{prefix}{filename}?ref={ref}")
        if raw:
            try:
                return base64.b64decode(json.loads(raw)["content"]).decode()
            except (KeyError, ValueError):
                pass
    return None


def walk(use: str, graph: dict[str, dict], seen: set[str]) -> None:
    """Populate ``graph[use]`` with its ``using`` kind and child ``uses``."""
    if use in seen or use.startswith(("docker://", "./", ".github/")):
        return
    seen.add(use)
    text = _action_yml(*_split(use))
    using = None
    children: list[str] = []
    if text:
        match = _USING_RE.search(text)
        using = match.group(1) if match else None
        if using == "composite":
            children = [c for c in _USES_RE.findall(text) if "@" in c or "/" in c]
    graph[use] = {"using": using, "children": children}
    for child in children:
        walk(child, graph, seen)


def top_level_uses() -> list[str]:
    out = subprocess.run(
        ["grep", "-rhoE", r"uses:[[:space:]]*[^[:space:]]+", WORKFLOW_DIR],
        capture_output=True,
        text=True,
        check=False,
    )
    uses = {line.split(":", 1)[1].strip() for line in out.stdout.splitlines()}
    return sorted(u for u in uses if "@" in u)


def covered(use: str, allowlist: dict) -> bool:
    """Whether ``use`` is permitted by the repo's allowed-actions policy."""
    if use.startswith(("./", ".github/")):
        return True  # local actions are not governed by the policy
    owner_repo, _, _ = _split(use)
    owner = owner_repo.split("/")[0]
    if allowlist.get("github_owned_allowed") and owner in GITHUB_OWNERS:
        return True
    for pattern in allowlist.get("patterns_allowed", []):
        pat = pattern.split("@")[0]
        if fnmatch.fnmatch(owner_repo, pat):
            return True
    return (
        False  # may still be allowed if verified_allowed and it is a verified creator
    )


def main() -> int:
    graph: dict[str, dict] = {}
    seen: set[str] = set()
    for use in top_level_uses():
        walk(use, graph, seen)

    print("Transitive action graph:\n")
    for use in sorted(graph):
        info = graph[use]
        print(f"  [{info['using'] or '?':9}] {use}")
        for child in info["children"]:
            print(f"               -> {child}")

    slug = _repo_slug()
    allow_raw = _gh(f"repos/{slug}/actions/permissions/selected-actions")
    print(f"\nAllowed-actions policy for {slug}:")
    if not allow_raw:
        print("  (policy is not 'selected' -- all actions allowed; nothing to check)")
        return 0
    allowlist = json.loads(allow_raw)
    print(
        f"  github_owned_allowed={allowlist.get('github_owned_allowed')} "
        f"verified_allowed={allowlist.get('verified_allowed')}"
    )
    print(f"  patterns: {allowlist.get('patterns_allowed')}")

    gaps = sorted(u for u in graph if not covered(u, allowlist))
    print()
    if gaps:
        print("BLOCKED — transitive actions not covered by the allowlist:")
        for use in gaps:
            print(f"  - {use}")
        if allowlist.get("verified_allowed"):
            print(
                "\n(These are allowed only if they are GitHub Marketplace verified "
                "creators, which this script cannot confirm. Add explicit patterns "
                "to be certain.)"
            )
        return 1
    print(f"OK — all {len(graph)} transitive actions are covered by the allowlist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
