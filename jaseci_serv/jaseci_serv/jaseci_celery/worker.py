from copy import deepcopy
import re

from .celery import app

from requests import post, get, request
from requests.exceptions import HTTPError
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


json_escape = re.compile("[^a-zA-Z0-9_]")
internal = re.compile("\(([a-zA-Z0-9_\.\[\]\$\#]*?)\)")
full = re.compile("^\{\{([a-zA-Z0-9_\.\[\]\$\#\(\)]*?)\}\}$")
partial = re.compile("\{\{([a-zA-Z0-9_\.\[\]\$\#\(\)]*?)\}\}")


def get_deep_value(data, keys, default):
    if len(keys) == 0:
        return data

    key = keys.pop(0)
    t = type(data)

    if t is dict and key in data:
        return get_deep_value(data[key], keys, default)
    elif t is list and key.isnumeric():
        return get_deep_value(data[int(key)], keys, default)
    else:
        return default


def get_value(persistence, container, keys, default=None):
    while internal.search(keys):
        for intern in internal.findall(keys):
            keys = keys.replace(
                "(" + intern + ")", get_value(persistence, container, intern, "")
            )

    if keys:
        keys = keys.split(".")
        key = keys.pop(0)
        if key == "#":
            return get_deep_value(persistence, keys, default)
        elif key == "$":
            t = type(container)
            if t is dict or t is list:
                return get_deep_value(container, keys, default)
            else:
                return container
    return default


def compare(condition, expected, actual):
    if condition == "eq":
        return actual == expected
    elif condition == "ne":
        return actual != expected
    elif condition == "gt":
        return actual > expected
    elif condition == "gte":
        return actual >= expected
    elif condition == "lt":
        return actual < expected
    elif condition == "lte":
        return actual <= expected
    elif condition == "regex":
        return re.compile(expected).match(actual)


def condition(persistence, loop, filter):
    for cons in filter["condition"].keys():
        if not (filter["condition"][cons] is None) and not compare(
            cons, filter["condition"][cons], get_value(persistence, loop, filter["by"])
        ):
            return False
    return True


def or_condition(persistence, loop, filter):
    for filt in filter:
        if "condition" in filt and condition(persistence, loop, filt):
            return True
        elif "or" in filt and or_condition(persistence, loop, filt["or"]):
            return True
        elif "and" in filt and and_condition(persistence, loop, filt["and"]):
            return True
    return False


def and_condition(persistence, loop, filter):
    for filt in filter:
        if "condition" in filt and not condition(persistence, loop, filt):
            return False
        elif "or" in filt and not or_condition(persistence, loop, filt["or"]):
            return False
        elif "and" in filt and not and_condition(persistence, loop, filt["and"]):
            return False
    return True


def deep_replace_str(persistence, container, data, key):
    matcher = full.match(data[key])
    if matcher:
        data[key] = get_value(persistence, container, matcher.group(1))
    else:
        for rep in partial.findall(data[key]):
            data[key] = data[key].replace(
                "{{" + rep + "}}", get_value(persistence, container, rep, "")
            )


def deep_replace_dict(persistence, container, data):
    for key in data.keys():
        if key != "loop":
            t = type(data[key])
            if t is str:
                deep_replace_str(persistence, container, data, key)
            elif t is dict:
                deep_replace_dict(persistence, container, data[key])


@app.task(bind=True)
def dynamic_request(self, requests, persistence={}, container={}):

    if "parent_current" in container:
        container["current"] = container["parent_current"]

    for req in requests:

        if "current" in container:
            deep_replace_dict(persistence, container["current"], req)

        if "save_req_to" in req:
            persistence[json_escape.sub("_", req["save_req_to"])] = req

        method = req["method"].upper()

        try:
            if method == "POST":
                response = post(
                    req["url"], json=req.get("body", {}), headers=req.get("header", {})
                )
            elif method == "GET":
                response = get(req["url"], headers=req.get("header", {}))

            response.raise_for_status()

            if "application/json" in response.headers.get("Content-Type"):
                container["current"] = response.json()
            else:
                container["current"] = response.text

            if "loop" in req:
                for loop in get_value(
                    persistence, container["current"], req["loop"]["by"], []
                ):
                    if "filter" in req["loop"] and not and_condition(
                        persistence, loop, req["loop"]["filter"]
                    ):
                        continue
                    loop_container = {"parent_current": loop}
                    dynamic_request(
                        requests=deepcopy(req["loop"]["requests"]),
                        persistence=persistence,
                        container=loop_container,
                    )

        except HTTPError as err:
            container["current"] = {
                "status": err.response.status_code,
                "message": err.response.reason,
            }

        if "save_to" in req:
            persistence[json_escape.sub("_", req["save_to"])] = container["current"]
