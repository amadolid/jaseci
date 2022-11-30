import os

REDIS_CONFIG = {
    "enabled": os.getenv("REDIS_ENABLED", "true").lower() == "true",
    "quiet": False,
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": os.getenv("REDIS_PORT", "6379"),
    "db": os.getenv("REDIS_DB", "1"),
}
