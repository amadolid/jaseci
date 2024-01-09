import asyncio
import websocket
from os import getenv
from re import search
from orjson import dumps
from playwright.async_api import async_playwright, Page
from websocket import create_connection as _create_connection

from jac_misc.scraper.utils import (
    notify_client,
    add_url,
    add_crawl,
    get_script,
    get_hostname,
)


def create_connection() -> websocket:
    ws = _create_connection(getenv("SCRAPER_SOCKET_URL", "ws://jaseci-socket/ws"))
    ws.send(dumps({"type": "client_connect", "data": {}}))
    return ws


def notify_client(
    websocket: websocket,
    target: str,
    pages: list,
    urls: dict,
    processing: dict,
    content=None,
):
    if websocket and target:
        data = {
            "processing": processing,
            "pending": [p["goto"]["url"] for p in pages],
            "scanned": list(urls["scanned"]),
        }
        if content:
            data["response"] = content

        websocket.send(
            dumps(
                {
                    "type": "notify_client",
                    "data": {
                        "target": target,
                        "data": {"type": "scraper", "data": data},
                    },
                }
            )
        )


async def scrape(
    pages: list, pre_configs: list = [], detailed: bool = False, target: str = None
):
    content = ""
    urls = {"scanned": set(), "scraped": set(), "crawled": set()}

    ws = create_connection()

    async with async_playwright() as aspw:
        browser = await aspw.chromium.launch()
        page = await browser.new_page()

        while pages:
            pg: dict = pages.pop(0)

            pg_goto = pg.get("goto") or {}
            url = pg_goto.get("url") or "N/A"

            notify_client(ws, target, pages, urls, {"url": url, "status": "started"})

            await goto(page, pg_goto, urls)

            content += await getters(page, pg.get("getters") or [], urls)

            await crawler(page, pg.get("crawler") or {}, urls, pages, pre_configs)

            notify_client(ws, target, pages, urls, {"url": url, "status": "completed"})

        await browser.close()

    content = " ".join(content.split())

    if detailed:
        content = {
            "content": content,
            "scanned": list(urls["scanned"]),
            "scraped": list(urls["scraped"]),
        }

    notify_client(ws, target, pages, urls, None, content)
    ws.close()

    return content


async def goto(page: Page, specs: dict, urls: dict):
    if specs:
        post = get_script(specs, "post")
        await run_scripts(page, get_script(specs, "pre"), urls)

        print(f'[goto]: loading {specs["url"]}')

        await page.goto(**specs)
        add_url(page, urls)

        await run_scripts(page, post, urls)


async def getters(page: Page, specss: list[dict], urls: dict):
    content = ""
    for specs in specss:
        if specs:
            post = get_script(specs, "post")
            await run_scripts(page, get_script(specs, "pre"), urls)

            exel_str = ""
            for exel in (
                specs.get("excluded_element", ["script", "style", "link", "noscript"])
                or []
            ):
                exel_str += (
                    f'clone.querySelectorAll("{exel}").forEach(d => d.remove());\n'
                )

            method = specs.get("method")
            if method == "selector":
                expression = f"""
                    Array.prototype.map.call(
                        document.querySelectorAll("{specs.get("expression")}"),
                        d => {{
                            clone = d.cloneNode(true);
                            {exel_str}
                            return clone.textContent;
                        }}).join("\n");
                """
            elif method == "custom":
                expression = f'{{{specs.get("expression")}}}'
            elif method == "none":
                expression = '""'
            else:
                expression = f"""{{
                    clone = document.body.cloneNode(true);
                    {exel_str}
                    return clone.textContent;
                }}"""

            if expression:
                print(f"[getters]: getting content from {page.url}")
                content += await page.evaluate(f"() =>{expression}")
            add_url(page, urls, expression)

            await run_scripts(page, post, urls)

    return content


async def crawler(page: Page, specs: dict, urls: dict, pages: list, pre_configs: list):
    if specs:
        post = get_script(specs, "post")
        await run_scripts(page, get_script(specs, "pre"), urls)

        queries = specs.get("queries") or [{"selector": "a[href]", "attribute": "href"}]
        filters = specs.get("filters") or []
        depth = specs.get("depth", 1) or 0

        if depth > 0:
            for query in queries:
                for node in await page.query_selector_all(
                    query.get("selector") or "a[href]"
                ):
                    url = await node.get_attribute(query.get("attribute") or "href")
                    c_url = get_hostname(page)

                    if url.startswith("/"):
                        url = f"{c_url}{url}"

                    if url.startswith("http") and url not in urls["crawled"]:
                        included = not bool(filters)

                        for filter in filters:
                            if search(filter, url):
                                included = True
                                break

                        if included:
                            add_crawl(
                                pages,
                                pre_configs,
                                urls,
                                url,
                                {
                                    "queries": queries,
                                    "depth": depth - 1,
                                    "filters": filters,
                                },
                            )

        await run_scripts(page, post, urls)


async def run_scripts(page: Page, scripts: list[dict], urls: dict):
    for script in scripts:
        method = script.pop("method", "evalutate") or "evaluate"
        print(f"[script]: running method {method}\n{str(script)}")
        await getattr(page, method)(**script)
        add_url(page, urls)
