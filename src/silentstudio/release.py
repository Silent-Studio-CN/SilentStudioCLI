"""Release helpers for the SilentStudio CLI."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .i18n import tr
from .utils import get_system_language

CONFIG_NAME = ".ss.json"
USER_CONFIG = Path.home() / ".silentstudio" / "releases.json"

DEFAULT_PROJECT = {
    "repo": "Silent-Studio-CN/SilentCraft-Launcher",
    "workflow": "silentcraft-release.yml",
    "ref": "main",
    "tag": "v${version}",
}


def find_config(start: Optional[Path] = None) -> Optional[Path]:
    current = (start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        candidate = directory / CONFIG_NAME
        if candidate.is_file():
            return candidate
    return None


def load_projects() -> Dict[str, Any]:
    config_path = find_config()
    if config_path:
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            return data.get("projects", {})
        except Exception as exc:
            raise SystemExit(f"Cannot read {config_path}: {exc}")

    if USER_CONFIG.is_file():
        try:
            return json.loads(USER_CONFIG.read_text(encoding="utf-8")).get("projects", {})
        except Exception as exc:
            raise SystemExit(f"Cannot read {USER_CONFIG}: {exc}")
    return {}


def save_project(project: str, data: Dict[str, Any]) -> Path:
    config_path = find_config() or Path.cwd() / CONFIG_NAME
    try:
        config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
    except Exception:
        config = {}
    config.setdefault("projects", {})[project] = data
    config["defaultProject"] = project
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return config_path


def normalize_tag(template: str, version: str, commit: str) -> str:
    return (template.replace("${version}", version)
            .replace("${commit}", commit[:7] if commit else ""))


def require_gh() -> str:
    gh = shutil.which("gh")
    if not gh:
        raise SystemExit("gh CLI not found. Install it from https://cli.github.com/")
    probe = subprocess.run([gh, "auth", "status"], capture_output=True, text=True)
    if probe.returncode != 0:
        raise SystemExit("gh is not authenticated. Run: gh auth login")
    return gh


def latest_run_id(gh: str, repo: str, workflow: str) -> Optional[int]:
    result = subprocess.run(
        [gh, "run", "list", "--repo", repo, "--workflow", workflow,
         "--limit", "1", "--json", "databaseId"],
        capture_output=True, text=True, check=True,
    )
    runs = json.loads(result.stdout or "[]")
    return runs[0]["databaseId"] if runs else None


def handle_release(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="ss release", description="Publish a SilentStudio release")
    parser.add_argument("project", nargs="?", help="project name")
    parser.add_argument("version", nargs="?", help="version, e.g. 3.18")
    parser.add_argument("commit", nargs="?", help="commit/revision to verify")
    parser.add_argument("--notes", default=None, help="release notes")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config", action="store_true", help="configure a project")
    parser.add_argument("--list", action="store_true", help="list configured projects")
    args = parser.parse_args(argv)
    if args.project == "config" and not args.version:
        args.config = True
        args.project = None
    lang = get_system_language()
    projects = load_projects()

    if args.list:
        if not projects:
            print(tr("no_projects", lang))
        for name, data in projects.items():
            print(f"{name}\t{data.get('repo')}\t{data.get('workflow')}")
        return 0

    if args.config:
        project = args.project or input(f"{tr('project', lang)} [silentcraft]: ").strip() or "silentcraft"
        defaults = projects.get(project, DEFAULT_PROJECT)
        repo = input(f"{tr('repository', lang)} [{defaults.get('repo')}]: ").strip() or defaults.get("repo")
        if not re.fullmatch(r"[^/\s]+/[^/\s]+", repo):
            print(tr("invalid_repo", lang, repo=repo))
            return 1
        workflow = input(f"{tr('workflow', lang)} [{defaults.get('workflow')}]: ").strip() or defaults.get("workflow")
        ref = input(f"{tr('ref', lang)} [{defaults.get('ref')}]: ").strip() or defaults.get("ref")
        tag = input(f"{tr('tag', lang)} [{defaults.get('tag')}]: ").strip() or defaults.get("tag")
        path = save_project(project, {"repo": repo, "workflow": workflow, "ref": ref, "tag": tag})
        print(tr("saved", lang, project=project, path=path))
        return 0

    if not args.project:
        if projects:
            print(tr("configured", lang))
            for name, data in projects.items():
                print(f"  {name}\t{data.get('repo')}")
            print("\n" + tr("usage", lang))
        else:
            print(tr("no_projects", lang))
        return 0

    if not args.version:
        parser.error(tr("version_required", lang))

    data = projects.get(args.project)
    if not data:
        raise SystemExit(tr("unknown_project", lang, project=args.project))

    repo = data["repo"]
    workflow = data["workflow"]
    ref = data.get("ref", "main")
    tag = normalize_tag(data.get("tag", "v${version}"), args.version, args.commit or "")

    if args.commit:
        probe = subprocess.run(["git", "rev-parse", "--verify", args.commit],
                               capture_output=True, text=True)
        if probe.returncode != 0:
            raise SystemExit(f"Unknown commit: {args.commit}")
        commit = probe.stdout.strip()
    else:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True, check=True).stdout.strip()

    print(f"Project:  {args.project}")
    print(f"Repo:     {repo}")
    print(f"Workflow: {workflow}")
    print(f"Ref:      {ref}")
    print(f"Commit:   {commit[:12]}")
    print(f"Tag:      {tag}")

    if args.dry_run:
        return 0

    gh = require_gh()
    subprocess.run([gh, "workflow", "run", workflow, "--repo", repo, "--ref", ref], check=True)

    run_id = None
    for _ in range(10):
        run_id = latest_run_id(gh, repo, workflow)
        if run_id:
            break
        time.sleep(1)
    if not run_id:
        raise SystemExit("Could not find the triggered workflow run")

    print(f"Watching run {run_id}...")
    subprocess.run([gh, "run", "watch", str(run_id), "--repo", repo,
                    "--interval", "10", "--exit-status"], check=True)

    result = subprocess.run([gh, "release", "view", tag, "--repo", repo,
                             "--json", "url", "--jq", ".url"],
                            capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Release: {result.stdout.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(handle_release(sys.argv[1:]))
