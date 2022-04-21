"""Built in actions for Jaseci"""
from jaseci.actions.live_actions import jaseci_action
from base64 import b64decode, b64encode
from io import BytesIO, StringIO
import json, requests


@jaseci_action()
def load_str(fn: str, max_chars: int = None):
    """Standard built in for loading from file to string"""
    with open(fn, 'r') as file:
        data = file.read(max_chars)
    return data


@jaseci_action()
def load_json(fn: str):
    """Standard built in for loading json from file to dictionary"""
    with open(fn, 'r') as file:
        data = json.load(file)
    return data


@jaseci_action()
def dump_str(fn: str, s: str):
    """Standard built in for dumping to file from string"""
    with open(fn, 'w') as file:
        num_chars = file.write(s)
    return num_chars


@jaseci_action()
def append_str(fn: str, s: str):
    """Standard built in for appending to file from string"""
    with open(fn, 'a') as file:
        num_chars = file.write(s)
    return num_chars


@jaseci_action()
def dump_json(fn: str, obj, indent: int = None):
    """Standard built in for dumping json to file from dictionary"""
    with open(fn, 'w') as file:
        json.dump(obj, file, indent=indent)


@jaseci_action()
def base64_to_bytesio(b64: str):
    """Standard built in for converting base64 to file (in-memory)"""
    """BytesIO avoids file writing on server"""
    return BytesIO(b64decode(b64))


@jaseci_action()
def string_to_stringio(data: str):
    """Standard built in for converting string to file (in-memory)"""
    """StringIO avoids file writing on server"""
    return StringIO(data)


@jaseci_action()
def load_url(url: str, header: dict):
    """Standard built in for download file from url"""
    with requests.get(url, stream = True, headers = header) as res:
        res.raise_for_status()
        with BytesIO() as buffer:
            for chunk in res.iter_content(chunk_size=8192):
                buffer.write(chunk)
            ret = buffer.getvalue()
    return ret


@jaseci_action()
def bytes_to_base64(file: bytes, encoding: str = "utf-8"):
    """Standard built in for converting bytes to base64"""
    return b64encode(file).decode(encoding)