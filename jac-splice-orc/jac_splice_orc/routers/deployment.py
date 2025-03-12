"""This module provides a FastAPI-based API for managing Kubernetes pods."""

from os.path import dirname, isdir
from pathlib import Path
from re import compile

from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from jac_splice_orc import manifests

from ..dtos.deployment import Deployment, DeploymentResponse
from ..utils import apply_manifests

PLACEHOLDER = compile(r"\$j{([^\^:}]+)(?:\:([^\}]+))?}")

router = APIRouter(prefix="/deployment")


@router.post("")
async def delete_pod(deployment: Deployment) -> DeploymentResponse:
    """Delete the pod and service for the given module and return the result."""
    manifest_path = dirname(manifests.__file__)
    module_path = Path(f"{manifest_path}/{deployment.name}")
    if not isdir(module_path):
        raise HTTPException(
            400, f"Deployment for {deployment.name} is not yet support!"
        )

    dependencies_path = Path(f"{module_path}/dependencies")

    response = DeploymentResponse()
    if isdir(dependencies_path):
        response.push(apply_manifests(dependencies_path, deployment.config))

    response.push(apply_manifests(module_path, deployment.config))

    return response
