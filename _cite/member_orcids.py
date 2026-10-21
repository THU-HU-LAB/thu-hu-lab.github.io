"""Read citation sources from member Markdown front matter."""

import re
from pathlib import Path

import yaml


def load_member_orcid(path):
    """Return zero or one ORCID source; never pass member profile fields on."""
    path = Path(path)
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing YAML front matter")
    end = next(
        (i for i in range(1, len(lines)) if lines[i].strip() == "---"), None
    )
    if end is None:
        raise ValueError(f"{path}: missing closing --- for YAML front matter")
    try:
        profile = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as error:
        raise ValueError(f"{path}: invalid YAML front matter: {error}") from error
    if not isinstance(profile, dict):
        raise ValueError(f"{path}: front matter must be a YAML mapping")
    links = profile.get("links")
    if links is None:
        return []
    if not isinstance(links, dict):
        raise ValueError(f"{path}: links must be a YAML mapping")
    value = links.get("orcid")
    if value is None or value == "":
        return []
    if not isinstance(value, str):
        raise ValueError(f"{path}: links.orcid must be an ORCID string")
    value = value.strip().upper()
    if not value:
        return []
    if not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", value):
        raise ValueError(
            f"{path}: invalid links.orcid {value!r}; "
            "use the 16-character ORCID iD with hyphens, without a URL"
        )
    return [{"orcid": value}]
