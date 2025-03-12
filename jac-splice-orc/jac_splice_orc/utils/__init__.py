"""Importing required modules and classes."""

from datetime import UTC, datetime, timedelta
from os import listdir, makedirs
from pathlib import Path
from re import compile
from subprocess import CompletedProcess, run
from typing import Any

from orjson import dumps, loads

PLACEHOLDERS = compile(r"\$j{([^\^:}]+)(?:\:([^\}]+))?}")


def utc_datetime(**addons: int) -> datetime:
    """Get current datetime with option to add additional timedelta."""
    return datetime.now(tz=UTC) + timedelta(**addons)


def utc_timestamp(**addons: int) -> int:
    """Get current timestamp with option to add additional timedelta."""
    return int(utc_datetime(**addons).timestamp())


def apply_manifests(
    path: Path, config: dict[str, str | int | float | bool | list]
) -> CompletedProcess[str]:
    """Apply Manifests."""
    tmp = Path(f"{path}/tmp-{utc_timestamp()}")
    makedirs(tmp, exist_ok=True)

    for manifest in listdir(path):
        if manifest.endswith(".yaml") or manifest.endswith(".yml"):
            with open(f"{path}/{manifest}", "r") as stream:
                raw = stream.read()

            for placeholder in set(PLACEHOLDERS.findall(raw)):
                prefix = placeholder[0]
                suffix = ""
                if default := placeholder[1]:
                    suffix = f":{default}"
                    default = loads(default.encode())

                raw = raw.replace(
                    f"$j{{{prefix}{suffix}}}",
                    dumps(config.get(prefix, default)).decode(),
                )

            with open(f"{tmp}/{manifest}", "w") as stream:
                stream.write(raw)

    output = run(
        ["kubectl", "apply", "-f", tmp],
        capture_output=True,
        text=True,
    )

    tmp.unlink()

    return output


def view_manifests(
    path: Path, config: dict[str, str | int | float | bool | list]
) -> dict[str, Any]:
    """View Manifests."""
    manifests: dict[str, Any] = {}

    for manifest in listdir(path):
        if manifest.endswith(".yaml") or manifest.endswith(".yml"):
            with open(f"{path}/{manifest}", "r") as stream:
                raw = stream.read()

            placeholders: dict[str, dict[str, Any]] = {}
            for placeholder in set(PLACEHOLDERS.findall(raw)):
                prefix = placeholder[0]
                suffix = ""
                if default := placeholder[1]:
                    suffix = f":{default}"
                    default = loads(default.encode())

                current = config.get(prefix, default)
                raw = raw.replace(f"$j{{{prefix}{suffix}}}", dumps(current).decode())
                placeholders[prefix] = {"current": current, "default": default}
            manifests[manifest] = {"placeholders": placeholders, "manifest": raw}
    return manifests
