"""This module provides a FastAPI-based API for managing Kubernetes pods."""

from os.path import dirname, isdir
from pathlib import Path
from re import compile

from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from jac_splice_orc import manifests

from ..dtos.deployment import (
    Deployment,
    DeploymentResponse,
    DryRunResponse,
    Placeholder,
)
from ..utils import apply_manifests, view_manifests

PLACEHOLDER = compile(r"\$j{([^\^:}]+)(?:\:([^\}]+))?}")

router = APIRouter(prefix="/deployment")


@router.post("")
def deployment(deployment: Deployment) -> DeploymentResponse:
    """Deploy module with configs."""
    manifest_path = dirname(manifests.__file__)
    module_path = Path(f"{manifest_path}/{deployment.module}")
    if not isdir(module_path):
        raise HTTPException(
            400, f"Deployment for {deployment.module} is not yet support!"
        )

    dependencies_path = Path(f"{module_path}/dependencies")

    response = DeploymentResponse()
    if isdir(dependencies_path):
        response.push(apply_manifests(dependencies_path, deployment.config))

    response.push(apply_manifests(module_path, deployment.config))

    return response


@router.post("/dry_run")
def dry_run(deployment: Deployment) -> DryRunResponse:
    """Delete the pod and service for the given module and return the result."""
    manifest_path = dirname(manifests.__file__)
    module_path = Path(f"{manifest_path}/{deployment.module}")
    if not isdir(module_path):
        raise HTTPException(
            400, f"Deployment for {deployment.module} is not yet support!"
        )

    dependencies_path = Path(f"{module_path}/dependencies")

    response = DryRunResponse()
    if isdir(dependencies_path):
        raw_manifests, placeholders = view_manifests(
            dependencies_path, deployment.config
        )
        response.dependencies = raw_manifests
        response.placeholders.update(
            {key: Placeholder(**value) for key, value in placeholders.items()}
        )

    raw_manifests, placeholders = view_manifests(module_path, deployment.config)
    response.modules = raw_manifests
    response.placeholders.update(
        {key: Placeholder(**value) for key, value in placeholders.items()}
    )

    return response
