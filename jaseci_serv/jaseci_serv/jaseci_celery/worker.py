from copy import deepcopy
import re
from typing import Tuple

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
internal = re.compile("\(([a-zA-Z0-9_\.\[\]\$\#\@]*?)\)")
full = re.compile("^\{\{([a-zA-Z0-9_\.\[\]\$\#\(\)\@]*?)\}\}$")
partial = re.compile("\{\{([a-zA-Z0-9_\.\[\]\$\#\(\)\@]*?)\}\}")


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


def get_value(holder: Tuple, keys: str, default=None):
    while internal.search(keys):
        for intern in internal.findall(keys):
            keys = keys.replace("(" + intern + ")", get_value(holder, intern, ""))

    if keys:
        keys = keys.split(".")
        key = keys.pop(0)
        if key == "#":
            return get_deep_value(holder[0], keys, default)
        elif key == "$":
            t = type(holder[1])
            if t is dict or t is list:
                return get_deep_value(holder[1], keys, default)
            else:
                return holder[1]
        elif key == "@":
            t = type(holder[2])
            if t is dict or t is list:
                return get_deep_value(holder[2], keys, default)
            else:
                return holder[2]
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


def condition(holder: Tuple, filter):
    for cons in filter["condition"].keys():
        if not (filter["condition"][cons] is None) and not compare(
            cons, filter["condition"][cons], get_value(holder, filter["by"])
        ):
            return False
    return True


def or_condition(holder: Tuple, filter):
    for filt in filter:
        if "condition" in filt and condition(holder, filt):
            return True
        elif "or" in filt and or_condition(holder, filt["or"]):
            return True
        elif "and" in filt and and_condition(holder, filt["and"]):
            return True
    return False


def and_condition(holder: Tuple, filter):
    for filt in filter:
        if "condition" in filt and not condition(holder, filt):
            return False
        elif "or" in filt and not or_condition(holder, filt["or"]):
            return False
        elif "and" in filt and not and_condition(holder, filt["and"]):
            return False
    return True


def deep_replace_str(holder: Tuple, data, key):
    matcher = full.match(data[key])
    if matcher:
        data[key] = get_value(holder, matcher.group(1))
    else:
        for rep in partial.findall(data[key]):
            data[key] = data[key].replace("{{" + rep + "}}", get_value(holder, rep, ""))


def deep_replace_dict(holder: Tuple, data):
    for key in data.keys():
        if key != "__def_loop__":
            t = type(data[key])
            if t is str:
                deep_replace_str(holder, data, key)
            elif t is dict:
                deep_replace_dict(holder, data[key])


def save(holder: Tuple, req, params):
    if params in req:
        holder[0][json_escape.sub("_", req[params])] = holder[1]


@app.task(bind=True)
def dynamic_request(self, requests: dict, persistence: dict = {}, container: dict = {}):

    if "parent_current" in container:
        container["current"] = container["parent_current"]

    for req in requests:
        try:
            if "current" in container:
                deep_replace_dict(
                    (
                        persistence,
                        container["current"],
                        container.get("parent_current", {}),
                    ),
                    req,
                )

            save((persistence, req), req, "save_req_to")

            method = req["method"].upper()
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

            if "__def_loop__" in req:
                def_loop = req["__def_loop__"]
                for loop in get_value(
                    (persistence, container["current"]), def_loop["by"], []
                ):
                    if "filter" in def_loop and not and_condition(
                        (persistence, loop), def_loop["filter"]
                    ):
                        continue
                    loop_container = {"parent_current": loop}
                    dynamic_request(
                        requests=deepcopy(def_loop["requests"]),
                        persistence=persistence,
                        container=loop_container,
                    )

            save((persistence, container["current"]), req, "save_to")

        except Exception as err:
            container["current"] = (
                {
                    "status": err.response.status_code,
                    "message": err.response.reason,
                }
                if isinstance(err, HTTPError)
                else {
                    "worker_error": str(err),
                }
            )

            save((persistence, container["current"]), req, "save_to")

            if "ignore_error" not in req or not req["ignore_error"]:
                if "parent_current" in container:
                    raise err
                break
