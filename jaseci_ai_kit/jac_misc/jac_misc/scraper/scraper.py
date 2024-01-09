import asyncio
from sys import argv
from os import getenv
from orjson import dumps
from websocket import WebSocketApp as wsa
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel

from jaseci.utils.utils import logger
from jaseci.jsorc.jsorc import JsOrc
from jaseci.extens.svc import SocketService as Ss
from jaseci.jsorc.live_actions import jaseci_action
from jac_misc.scraper.sync_scraper import scrape as sync_scrape
from jac_misc.scraper.async_scraper import scrape as async_scrape


if any(["uvicorn" in arg for arg in argv]):
    if getenv("SCRAPER_SOCKET_ENABLED") == "true":

        @JsOrc.service(
            name="socket",
            config="SOCKET_CONFIG",
            manifest="SOCKET_MANIFEST",
            priority=1,
            pre_loaded=True,
        )
        class SocketService(Ss):
            def run(self):
                self.queue = []
                super().run()

            def on_open(self, ws: wsa):
                self.send(
                    ws,
                    {"type": "client_connect", "data": {}},
                )

                for que in self.queue:
                    logger.info(f"resending {que}")
                    self.send(ws, que)

            def send(self, ws: wsa, data: dict):
                try:
                    ws.send(dumps(data))
                except BrokenPipeError:
                    JsOrc.svc_reset("socket", SocketService).queue.append(data)
                except Exception:
                    logger.exception("Failed to send event!")

        JsOrc.settings("SOCKET_CONFIG").update(
            {
                "enabled": True,
                "url": getenv("SCRAPER_SOCKET_URL", "ws://jaseci-socket/ws"),
                "ping_url": getenv(
                    "SCRAPER_SOCKET_PING_URL", "http://jaseci-socket/healthz"
                ),
            }
        )
        JsOrc.svc("socket", Ss).poke()

    class ScraperRequest(BaseModel):
        pages: list
        pre_configs: list = []
        detailed: bool = False
        target: str = None
        is_async: bool = False

    app = FastAPI()

    @app.post("/scrape/")
    async def scrape(sr: ScraperRequest):
        if sr.is_async:
            asyncio.create_task(
                async_scrape(sr.pages, sr.pre_configs, sr.detailed, sr.target)
            )
            return Response()
        else:
            return await async_scrape(sr.pages, sr.pre_configs, sr.detailed, sr.target)

    @app.get("/jaseci_actions_spec/")
    def action_list():
        return {
            "wbs.scrape": ["pages", "pre_configs", "detailed", "target", "is_async"]
        }

else:

    @jaseci_action(act_group=["wbs"])
    def setup():
        pass

    @jaseci_action(act_group=["wbs"])
    def scrape(
        pages: list, pre_configs: list = [], detailed: bool = False, target: str = None
    ):
        return sync_scrape(pages, pre_configs, detailed, target)
