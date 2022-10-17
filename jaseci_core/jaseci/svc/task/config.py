DEFAULT_MSG = "Skipping scheduled walker!"

TASK_CONFIG = {
    "enabled": True,
    "quiet": True,
    "broker_url": "redis://localhost:6379/1",
    "result_backend": "redis://localhost:6379/1",
    "broker_connection_retry_on_startup": True,
    "task_track_started": True,
    "kube": {},
}
