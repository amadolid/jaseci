import re

from .celery import app

from requests import post, get, request
from datetime import datetime
from celery.schedules import crontab


@app.task(bind=True)
def daily(self, test=""):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Daily - Current Time =", current_time)
    print(test)
    return


@app.task(bind=True)
def per_minute(self, test=""):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Per minute - Current Time =", current_time)
    print(test)
    return


@app.task(bind=True)
def per_minute(self, test=""):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Per minute - Current Time =", current_time)
    print(test)
    return


@app.task(bind=True)
def async_post(self, request, api, is_general):
    request["_req_ctx"]["headers"].pop("Content-Type")
    return post(
        "http://localhost:8000/js_celery/asynchronous",
        json={"_request_": request, "_api_": api, "_is_general_": is_general},
        headers=request["_req_ctx"]["headers"],
    ).json()


@app.task()
def add_scheduler(test="custom"):
    app.add_periodic_task(crontab(), per_minute.s(), name=test)


full = re.compile("^\{\{([a-zA-Z0-9_\.\[\]\$\#]*?)\}\}$")
partial = re.compile("\{\{([a-zA-Z0-9_\.\[\]\$\#]*?)\}\}")


def get_deep_value(data, keys):
    if len(keys) == 0:
        return data

    key = keys.pop(0)
    t = type(data)

    if t is dict and key in data:
        return get_deep_value(data[key], keys)
    elif t is list and key.isnumeric():
        return get_deep_value(data[int(key)], keys)
    else:
        return None


def get_value(data, keys):
    if keys:
        keys = keys.split(".")
        key = keys.pop(0)
        if key == "#":
            return get_deep_value(data["history"], keys)
        elif key == "$":
            t = type(data["current"])
            if t is dict or t is list:
                return get_deep_value(data["current"], keys)
            else:
                return data
    return None


def deep_replace_str(data, key, container):
    matcher = full.match(data[key])
    if matcher:
        data[key] = get_value(container, matcher.group(1))
    else:
        for rep in partial.findall(data[key]):
            data[key] = data[key].replace("{{" + rep + "}}", get_value(container, rep))


def deep_replace_dict(data, container):
    for key in data.keys():
        t = type(data[key])
        if t is str:
            deep_replace_str(data, key, container)
        elif t is dict:
            deep_replace_dict(data[key], container)


@app.task(bind=True)
def dynamic_request(self, requests):
    container = {"history": [], "temp_req_hist": []}
    for req in requests:
        deep_replace_dict(req, container)
        container["temp_req_hist"].append(req)
        method = req["method"].upper()
        if method == "POST":
            response = post(
                req["url"], json=req.get("body", {}), headers=req.get("header", {})
            )
        elif method == "GET":
            response = get(req["url"], headers=req.get("header", {}))
        if "application/json" in response.headers.get("Content-Type"):
            container["current"] = response.json()
        else:
            container["current"] = response.text
        container["history"].append(container["current"])

    print("##################################")
    print(container)
    print("##################################")
