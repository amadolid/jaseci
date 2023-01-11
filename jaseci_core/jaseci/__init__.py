from os.path import dirname, join


def get_ver():
    with open(join(dirname(__file__), "VERSION")) as version_file:
        return version_file.read().strip()


__version__ = get_ver()
__creator__ = "Jason Mars and friends"
__url__ = "https://jaseci.org"


def load_standard():
    from jaseci.actions.standard import (
        rand,
        request,
        std,
        file,
        vector,
        date,
        jaseci,
        mail,
        elastic,
        task,
        internal,
        zlib,
        webtool,
    )  # noqa


load_standard()
