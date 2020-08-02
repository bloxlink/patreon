from asyncio import sleep
from aiohttp.client_exceptions import ContentTypeError
from os import environ as env
import asyncio
import aiohttp
#import aredis
import json

from rethinkdb.errors import ReqlDriverError

try:
    from rethinkdb import RethinkDB; r = RethinkDB() # pylint: disable=no-name-in-module
except ImportError:
    import rethinkdb as r

r.set_loop_type("asyncio")

loop = asyncio.get_event_loop()
session = aiohttp.ClientSession(headers={"Connection": "close"}, loop=asyncio.get_event_loop())


BASE_URL = "https://www.patreon.com/api/oauth2"

try:
    from config import RETHINKDB
except ImportError:
    RETHINKDB = {
        "HOST": env.get("RETHINKDB_HOST"),
        "PORT": int(env.get("RETHINKDB_PORT")),
        "DB": env.get("RETHINKDB_DB"),
        "PASSWORD": env.get("RETHINKDB_PASSWORD")
    }

try:
    from config import PATREON
except ImportError:
    PATREON = {
        "CLIENT_ID": env.get("PATREON_CLIENT_ID"),
        "CLIENT_SECRET": env.get("PATREON_CLIENT_SECRET"),
        "REFRESH_TOKEN": env.get("PATREON_REFRESH_TOKEN")
    }

"""
try:
    from config import REDIS
except ImportError:
    REDIS = {
        "HOST": env.get("REDIS_HOST"),
        "PORT": int(env.get("REDIS_PORT"))
    }
"""

try:
    from config import RELEASE
except ImportError:
    RELEASE = env.get("RELEASE", "CANARY")



class Patreon:
    def __init__(self, loop, r, session):
        self.session = session
        self.loop = loop
        self.r = r

        self.refresh_token = None
        self.access_token = None
        self.campaign_id = None

    async def setup(self):
        await self.generate_token()

    async def generate_token(self, skip_from_db=False):
        await self.r.db("patreon").wait().run()

        refresh_token = await self.r.db("patreon").table("refreshTokens").get(f"{RELEASE}_refreshToken").run() or {}

        if refresh_token and not skip_from_db:
            refresh_token = refresh_token["refreshToken"]
        else:
            refresh_token = PATREON["REFRESH_TOKEN"]

        try:
            async with self.session.post(
                f"{BASE_URL}/token",
                params={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": PATREON["CLIENT_ID"],
                    "client_secret": PATREON["CLIENT_SECRET"]
                }
            ) as response:
                json = await response.json()

                self.access_token = json["access_token"]
                self.refresh_token = json["refresh_token"]

                await self.r.db("patreon").table("refreshTokens").insert({
                    "id": f"{RELEASE}_refreshToken",
                    "refreshToken": self.refresh_token
                }, conflict="update").run()

                await self.load_pledges()

                print("PATREON | Loaded pledges.", flush=True)

        except ContentTypeError:
            await sleep(500)

            return await self.generate_token()

        except KeyError:
            if not skip_from_db:
                return await self.generate_token(skip_from_db=True)

            raise RuntimeError("Unable to load pledges.")


    async def load_pledges(self, url="{BASE_URL}/api/campaigns/{campaign_id}/pledges"):
        url = url.format(BASE_URL=BASE_URL, campaign_id=await self.get_campaign_id())

        async with self.session.get(
            url,
            headers={
                "Authorization": f"Bearer {self.access_token}"
            }
        ) as response:
            json = await response.json()

            try:
                for patron in json["data"]:
                    if patron.get("type") == "pledge":
                        is_active = False
                        discord_id = None
                        patron_id = patron["relationships"]["patron"]["data"]["id"]
                        amount_cents = 0

                        for extra_info in json["included"]:
                            if extra_info["id"] == patron_id:
                                discord = extra_info["attributes"]["social_connections"].get("discord")

                                if discord:
                                    discord_id = discord["user_id"]

                        if not patron["attributes"].get("declined_since"):
                            amount_cents = patron["attributes"]["amount_cents"]

                            if not amount_cents or amount_cents >= 500:
                                is_active = True

                        await self.r.db("patreon").table("patrons").insert({
                            "id": patron_id,
                            "discord_id": discord_id,
                            "pledged": amount_cents,
                            "active": is_active
                        }, conflict="update").run()

                if json.get("links", {}).get("next"):
                    await self.load_pledges(json.get("links", {}).get("next"))

            except KeyError as e:
                pass


    async def get_campaign_id(self):
        if self.campaign_id:
            return self.campaign_id

        try:
            async with self.session.get(
                f"{BASE_URL}/api/current_user/campaigns",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            ) as response:
                json = await response.json()

                self.campaign_id = json["data"][0]["id"]
                return self.campaign_id

        except ContentTypeError:
            await sleep(500)

            return await self.get_campaign_id()


async def start():
    conn = await r.connect(
        RETHINKDB["HOST"],
        RETHINKDB["PORT"],
        RETHINKDB["DB"],
        password=RETHINKDB["PASSWORD"]
    )

    conn.repl()

    loop = asyncio.get_event_loop()

    patreon = Patreon(loop, r, session)
    await patreon.setup()

    #redis = aredis.StrictRedis(host=REDIS["HOST"], port=REDIS["PORT"])
    #await redis.flushdb()



loop.run_until_complete(start())
