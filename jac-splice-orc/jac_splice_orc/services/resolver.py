from re import compile

placeholder_full = compile(r"^\$j\{(.*?)\}$")
placeholder_partial = compile(r"\$j\{(.*?)\}")
placeholder_splitter = compile(r"\.?([^\.\[\"\]]+)(?:\[\"?([^\"\]]+)\"?\])?")


def get_splitter(val: str):
    matches = placeholder_splitter.findall(val)
    _matches = []
    for match in matches:
        for m in match:
            if m:
                _matches.append(m)
    return _matches


def get_value(source: dict, keys: list):
    if keys:
        key = keys.pop(0)
        if key in source:
            if keys:
                if isinstance(source[key], dict):
                    return get_value(source[key], keys)
            else:
                return source[key]
    return None


def placeholder_resolver(manifest, data: dict | list):
    for k, d in list(data.items()) if isinstance(data, dict) else enumerate(data):
        if isinstance(k, str):
            pk = k
            matcher = placeholder_full.search(k)
            if matcher:
                keys = get_splitter(matcher.group(1))
                pk = get_value(manifest, keys)
            else:
                for matcher in placeholder_partial.findall(k):
                    keys = get_splitter(matcher)
                    pk = pk.replace("$j{" + matcher + "}", get_value(manifest, keys))
            if pk != k:
                d = data.pop(k)
                k = pk
                data[pk] = d

        if isinstance(d, (dict, list)):
            placeholder_resolver(manifest, d)
        elif isinstance(d, str):
            matcher = placeholder_full.search(d)
            if matcher:
                keys = get_splitter(matcher.group(1))
                data[k] = get_value(manifest, keys)
            else:
                for matcher in placeholder_partial.findall(d):
                    keys = get_splitter(matcher)
                    data[k] = data[k].replace(
                        "$j{" + matcher + "}", get_value(manifest, keys)
                    )
