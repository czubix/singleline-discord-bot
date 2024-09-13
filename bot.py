"""
Copyright 2022-2024 czubix

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

(
    asyncio := __import__("asyncio"),
    aiohttp := __import__("aiohttp"),
    Enum := __import__("enum").Enum,
    reduce := __import__("functools").reduce,
    cycle := __import__("itertools").cycle,
    sys := __import__("sys"),

    _Opcodes := dict(
        DISPATCH = 0,
        HEARTBEAT = 1,
        IDENTIFY = 2,
        PRESENCE_UPDATE = 3,
        VOICE_STATE_UPDATE = 4,
        RESUME = 6,
        RECONNECT = 7,
        REQUEST_GUILD_MEMBERS = 8,
        INVALID_SESSION = 9,
        HELLO = 10,
        HEARTBEAT_ACK = 11
    ),

    _Intents := dict(
        GUILDS = 1 << 0,
        GUILD_MEMBERS = 1 << 1,
        GUILD_BANS = 1 << 2,
        GUILD_EMOJIS = 1 << 3,
        GUILD_INTEGRATIONS = 1 << 4,
        GUILD_WEBHOOKS = 1 << 5,
        GUILD_INVITES = 1 << 6,
        GUILD_VOICE_STATES = 1 << 7,
        GUILD_PRESENCES = 1 << 8,
        GUILD_MESSAGES = 1 << 9,
        GUILD_MESSAGE_REACTIONS = 1 << 10,
        GUILD_MESSAGE_TYPING = 1 << 11,
        DIRECT_MESSAGES = 1 << 12,
        DIRECT_MESSAGE_REACTIONS = 1 << 13,
        DIRECT_MESSAGE_TYPING = 1 << 14
    ),

    Opcodes := type("Opcodes", (Enum,), type("EnumType", (dict,), {"_member_names": list(_Opcodes.keys())})(**_Opcodes)),
    Intents := type("Intents", (Enum,), type("EnumType", (dict,), {"_member_names": list(_Intents.keys())})(**_Intents)),

    Route := type("Route", (), {
        "__init__": lambda self, method, *args: (
            setattr(self, "method", method),
            setattr(self, "endpoint", "/" + "/".join(args)), None)[-1]
    }),

    Http := type("Http", (), {
        "URL": "https://discord.com/api/v10",
        "__init__": lambda self, token: (
            setattr(self, "token", token),
            setattr(self, "session", aiohttp.ClientSession()),
            setattr(self, "headers", {"Authorization": "Bot " + self.token, "User-Agent": "onelinelib/1.0"}), None)[-1],
        "request": lambda self, route, data: (
            (
                response := await self.session.request(route.method, Http.URL + route.endpoint, headers=self.headers, json=data),
                await response.json()
            )[-1]
            for _ in "_"
        ).__anext__(),
        "send_message": lambda self, channel_id, data:
            self.request(Route("POST", "channels", channel_id, "messages"), data)
    }),

    WebSocket := type("WebSocket", (), {
        "URL": "wss://gateway.discord.gg/?v=9&encoding=json",
        "__init__": lambda self, token, intents: (
            setattr(self, "loop", asyncio.get_event_loop()),
            setattr(self, "token", token),
            setattr(self, "intents", intents),
            setattr(self, "listeners", {}),
            setattr(self, "session", aiohttp.ClientSession()), None)[-1],
        "on": lambda self, event, func: (
            self.listeners.__setitem__(event, [])
            if event not in self.listeners else (),
            self.listeners[event].append(func), None)[-1],
        "send": lambda self, op, data: self.ws.send_json({"op": op.value, "d": data}),
        "heartbeat": lambda self, interval: (
            [
                [
                    await self.send(Opcodes.HEARTBEAT, {}),
                    await asyncio.sleep(interval / 1000)
                ]
                for _ in cycle([None])
            ]
            for _ in "_"
        ).__anext__(),
        "run": lambda self: (
            [
                setattr(self, "ws", await self.session.ws_connect(WebSocket.URL)),
                [
                    [
                        data := await self.ws.receive_json(),

                        op := Opcodes(data.get("op")),
                        d := data.get("d"),
                        t := data.get("t"),

                        await {
                            Opcodes.HELLO: lambda: (
                                (
                                    self.loop.create_task(self.heartbeat(d["heartbeat_interval"])),

                                    await self.send(Opcodes.IDENTIFY, {
                                        "token": self.token,
                                        "properties": {
                                            "os": sys.platform,
                                            "browser": "onelinelib",
                                            "device": "onelinelib"
                                        },
                                        "intents": self.intents,
                                        "large_threshold": 250
                                    })
                                )
                                for _ in "_"
                            ).__anext__(),
                            Opcodes.DISPATCH: lambda: (
                                [
                                    await listener(d)
                                    for listener in self.listeners
                                        .get(t.lower(), [lambda data: (
                                            (
                                                await asyncio.sleep(0),
                                            )
                                            for _ in "_"
                                        ).__anext__()])
                                ]
                                for _ in "_"
                            ).__anext__()
                        }.get(op, lambda: (
                            (
                                await asyncio.sleep(0)
                            )
                            for _ in "_"
                        ).__anext__())()
                    ]
                    for _ in cycle([None])
                ]
            ]
            for _ in "_"
        ).__anext__()
    }),

    Bot := type("Bot", (), {
        "__init__": lambda self, token, intents: (
            setattr(self, "ws", WebSocket(token, intents)),
            setattr(self, "http", Http(token)),
            setattr(self, "bot_user", None),
            setattr(self, "guilds", []),

            self.ws.on("ready", self.on_ready),
            self.ws.on("guild_create", self.on_guild_create),
            self.ws.on("guild_delete", self.on_guild_delete), None)[-1],
        "get_guild": lambda self, guild_id: (
            guild := [guild for guild in self.guilds if guild["id"] == guild_id], guild[0] if guild else None)[-1],
        "on_ready": lambda self, data: (
            (
                await asyncio.sleep(0),
                setattr(self, "bot_user", data["user"])
            )
            for _ in "_"
        ).__anext__(),
        "on_guild_create": lambda self, guild: (
            (
                await asyncio.sleep(0),
                self.guilds.append(guild)
            )
            for _ in "_"
        ).__anext__(),
        "on_guild_delete": lambda self, guild: (
            (
                await asyncio.sleep(0),
                self.guilds.remove(self.get_guild(guild["id"]))
            )
            for _ in "_"
        ).__anext__()
    }),

    main := lambda: (
        (
            token_file := open("token", "r"),
            token := token_file.read(),
            token_file.close(),

            bot := Bot(token, reduce(lambda a, b: a | b, [intent.value for intent in Intents])),

            bot.ws.on("ready", lambda _: (
                (
                    await asyncio.sleep(0),
                    print("logged in", bot.bot_user["username"])
                )
                for _ in "_"
            ).__anext__()),

            bot.ws.on("message_create", lambda message: (
                (
                    await {
                        "4ping": lambda: (
                            (
                                await bot.http.send_message(message["channel_id"], {"content": "Pong"})
                            )
                            for _ in "_"
                        ).__anext__(),
                        "4guilds": lambda: (
                            (
                                await bot.http.send_message(message["channel_id"], {"content": ", ".join([guild["name"] for guild in bot.guilds])})
                            )
                            for _ in "_"
                        ).__anext__()
                    }.get(message["content"], lambda: (
                        (
                            await asyncio.sleep(0),
                        )
                        for _ in "_"
                    ).__anext__())()
                )
                for _ in "_"
            ).__anext__()),

            await bot.ws.run()
        )[-1]
        for _ in "_"
    ).__anext__(),

    (
        loop := asyncio.new_event_loop(),
        asyncio.set_event_loop(loop),

        loop.run_until_complete(main())
    ) if __name__ == "__main__" else ()
)