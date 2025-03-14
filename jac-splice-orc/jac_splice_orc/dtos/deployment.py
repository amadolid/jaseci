"""Jac Orc DTOs."""

from subprocess import CompletedProcess
from typing import Any

from pydantic import BaseModel, Field


class Deployment(BaseModel):
    """Deployment DTO."""

    module: str
    config: dict = Field(default_factory=dict)


class DeploymentResponse(BaseModel):
    """DeploymentResponse DTO."""

    results: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    def push(self, output: CompletedProcess[str]) -> None:
        """Push results and errors."""
        if results := output.stdout.strip():
            self.results += results.split("\n")

        if errors := output.stderr.strip():
            self.errors.append(errors)


class Placeholder(BaseModel):
    """Placeholder DTO."""

    default: Any
    current: Any


class DryRunResponse(BaseModel):
    """DeploymentResponse DTO."""

    placeholders: dict[str, Placeholder] = Field(default_factory=dict)
    dependencies: dict[str, str] = Field(default=None)
    modules: dict[str, str] = Field(default=None)
