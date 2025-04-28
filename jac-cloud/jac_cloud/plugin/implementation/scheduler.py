"""Jaseci Scheduler Implementations."""

from dataclasses import MISSING
from datetime import UTC
from enum import StrEnum
from os import getenv
from typing import Any, Callable

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.util import _Undefined, undefined

from jaclang.runtimelib.machine import JacMachine as Jac

from ...core.architype import NodeAnchor, WalkerArchitype
from ...core.context import JaseciContext
from ...jaseci.datasources.redis import ScheduleRedis
from ...jaseci.utils import utc_timestamp


class Trigger(StrEnum):
    """Trigger Type."""

    DATE = "date"
    INTERVAL = "interval"
    CRON = "cron"


class Executor(StrEnum):
    """Executor Type."""

    THREAD = "thread"
    PROCESS = "process"


scheduler = BackgroundScheduler(
    executors={
        Executor.THREAD: ThreadPoolExecutor(int(getenv("SCHEDULER_MAX_THREAD", "10"))),
        Executor.PROCESS: ProcessPoolExecutor(
            int(getenv("SCHEDULER_MAX_PROCESS", "5"))
        ),
    },
    timezone=UTC,
)


def scheduled_job(
    trigger: Trigger,
    node: str | None = None,
    args: Any | None = None,
    kwargs: Any | None = None,
    misfire_grace_time: int = 1,
    coalesce: bool = True,
    max_instances: int = 1,
    next_run_time: _Undefined | Any = undefined,
    executor: Executor = Executor.THREAD,
    propagate: bool = False,
    **trigger_args: Any,  # noqa: ANN401
) -> Callable:
    """Override schedule_job to trigger it once across workers and replicas."""

    def wrapper(walker: type[WalkerArchitype]) -> None:
        @scheduler.scheduled_job(
            trigger=trigger,
            args=args,
            kwargs=kwargs,
            name=walker.__name__,
            misfire_grace_time=misfire_grace_time,
            coalesce=coalesce,
            max_instances=max_instances,
            next_run_time=next_run_time,
            executor=executor,
            **trigger_args,
        )
        def process(*args: Any, **kwargs: Any) -> None:  # noqa: ANN401
            if propagate or ScheduleRedis.hsetnx(
                f"{walker.__name__}-{utc_timestamp()}", True
            ):
                jctx = JaseciContext.create(
                    None, NodeAnchor.ref(node) if node else None
                )
                warch = walker(*args, **kwargs)
                wanch = warch.__jac__
                Jac.spawn(warch, jctx.entry_node.architype)
                jctx.close()

                resp = jctx.response(wanch.returns)
                if jctx.custom is not MISSING:
                    resp["custom"] = jctx.custom

    return wrapper
