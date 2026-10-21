"""Add recorded source information to the native About dialog."""
import json
import re
from pathlib import Path
import frappe

METADATA_PATH = Path(__file__).resolve().parents[3] / "release-metadata.json"


def apply_metadata(versions, metadata):
    """Use safe image metadata, retaining native versions and Git branches."""
    if not isinstance(metadata, dict) or not isinstance(metadata.get("apps"), list):
        return versions
    for entry in metadata["apps"]:
        if not isinstance(entry, dict):
            continue
        app = entry.get("app")
        commit = entry.get("commit")
        branch = entry.get("branch")
        if app not in versions or not isinstance(commit, str) or not re.fullmatch(r"[a-f0-9]{40}", commit):
            continue
        if branch is not None and (not isinstance(branch, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,127}", branch)):
            continue
        if "display_branch" in entry:
            label = entry["display_branch"]
            if not isinstance(label, str) or (label and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,127}", label)):
                continue
            if not versions[app].get("branch"):
                versions[app]["branch"] = label
        elif not versions[app].get("branch"):
            versions[app]["branch"] = branch or "pinned commit"
        versions[app]["deployed_commit"] = commit
    return versions


@frappe.whitelist()
def get_versions():
    from frappe.utils.change_log import get_versions as native_get_versions
    versions = native_get_versions()
    try:
        metadata = json.loads(METADATA_PATH.read_text())
    except (OSError, ValueError):
        return versions
    return apply_metadata(versions, metadata)
