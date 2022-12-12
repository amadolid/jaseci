import unittest

from jaseci_serv.svc import MetaService


def skip_without_celery(test):
    """
    Skip test if expected not to work without redis.
    """

    def skipper(*args, **kwargs):
        task = MetaService().get_service("task")
        if not task.is_running():
            raise unittest.SkipTest("No Celery!")
        test(*args, **kwargs)

    return skipper


def skip_without_kube(test):
    """
    Skip test if expected not to work without access to a kubernete cluster
    """

    def skipper(*args, **kwargs):
        meta = MetaService()
        if not meta.in_cluster():
            raise unittest.SkipTest("Jaseci not in a kubernetes context!")
        test(*args, **kwargs)

    return skipper
