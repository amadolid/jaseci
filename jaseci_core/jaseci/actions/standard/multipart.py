"""Built in actions for Jaseci"""
from jaseci.actions.live_actions import jaseci_action
from jaseci.actions.standard.request import multipart
from jaseci.actions.standard.file import base64_to_bytesio, string_to_stringio


@jaseci_action()
def byBase64(url: str, header: dict, files: list= None, file: dict = None):
    """
    Issue request
    Param 1 - url
    Param 3 - header
    Param 3 - file (Optional) used for single file
    Param 4 - files (Optional) used for multiple files
    Note - file and files can't be None at the same time

    Return - response object
    """

    if file is None and files is None:
        return {
            "status_code": 400,
            "error": "Please include base64 using this format {\"field\":val,\"name\":val,\"base64\":val} using parameter `file` and `files` for array file"
        }

    formData = []

    if file is not None:
        formData.append(
            (
                file["field"] if "field" in file else "file",
                (file["name"], base64_to_bytesio(file["base64"]))
            )
        )
    if files is not None:
        for f in files:
            formData.append(
                (
                    f["field"] if "field" in f else "file",
                    (f["name"], base64_to_bytesio(f["base64"]))
                )
            )

    return multipart(url=url, files=formData, header=header)


@jaseci_action()
def byString(url: str, headers: dict, name: str, data: str, field: str = "file"):
    """
    Issue request
    Param 1 - url
    Param 3 - header
    Param 3 - name
    Param 4 - data
    Param 5 - field (Optional)

    Return - response object
    """
    
    formData = [
        (field, (name, string_to_stringio(data)))   
    ]

    return multipart(url=url, files=formData, header=headers)

    