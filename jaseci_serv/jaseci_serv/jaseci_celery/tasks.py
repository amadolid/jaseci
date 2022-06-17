import requests

from celery import shared_task


@shared_task
def async_post(request, api, is_general):
    request["_req_ctx"]["headers"].pop("Content-Type")
    return requests.post(
        "http://localhost:8000/js_celery/asynchronous",
        json={"_request_": request, "_api_": api, "_is_general_": is_general},
        headers=request["_req_ctx"]["headers"],
    ).json()
