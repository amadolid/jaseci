"""This module provides a FastAPI-based API for managing Kubernetes pods."""

from logging import INFO, basicConfig


from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from .routers.deployment import router

basicConfig(level=INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(default_response_class=ORJSONResponse)
app.include_router(router)
