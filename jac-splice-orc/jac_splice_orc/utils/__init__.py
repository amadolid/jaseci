"""Importing required modules and classes."""

from datetime import UTC, datetime, timedelta
from logging import StreamHandler, getLogger
from os import getenv, listdir, makedirs
from pathlib import Path
from re import compile
from shutil import rmtree
from subprocess import CompletedProcess, run
from sys import stdout
from typing import Any

from orjson import loads

PLACEHOLDERS = compile(r"\$j{([^\^:}]+)(?:\:([^\}]+))?}")


def utc_datetime(**addons: int) -> datetime:
    """Get current datetime with option to add additional timedelta."""
    return datetime.now(tz=UTC) + timedelta(**addons)


def utc_timestamp(**addons: int) -> int:
    """Get current timestamp with option to add additional timedelta."""
    return int(utc_datetime(**addons).timestamp())


def apply_manifests(
    path: Path, config: dict[str, Any]
) -> tuple[CompletedProcess[str], dict[str, Any]]:
    """Apply Manifests."""
    tmp = Path(f"{path}/tmp-{utc_timestamp()}")
    makedirs(tmp, exist_ok=True)

    parsed_config: dict[str, Any] = {}

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

                current = config.get(prefix, default)
                raw = raw.replace(f"$j{{{prefix}{suffix}}}", str(current))
                parsed_config[prefix] = current

            with open(f"{tmp}/{manifest}", "w") as stream:
                stream.write(raw)

    output = run(
        ["kubectl", "apply", "-f", tmp],
        capture_output=True,
        text=True,
    )

    rmtree(tmp)

    return output, parsed_config


def view_manifests(
    path: Path, config: dict[str, Any]
) -> tuple[dict[str, str], dict[str, dict[str, dict[str, Any]]]]:
    """View Manifests."""
    manifests: dict[str, str] = {}
    placeholders: dict[str, dict[str, dict[str, Any]]] = {}

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

                current = config.get(prefix, default)
                raw = raw.replace(f"$j{{{prefix}{suffix}}}", str(current))
                placeholders[prefix] = {"current": current, "default": default}
            manifests[manifest] = raw
    return manifests, placeholders


logger = getLogger(__name__)
logger.setLevel(getenv("LOGGER_LEVEL", "DEBUG"))
logger.addHandler(StreamHandler(stdout))
