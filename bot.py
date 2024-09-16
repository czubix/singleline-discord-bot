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
    sys := __import__("sys"),

    While := type("While", (), {
        "__init__": lambda self, check: (
            setattr(self, "check", check),
            setattr(self, "count", 0),
            setattr(self, "_stop", False), None)[-1],
        "stop": lambda self: setattr(self, "_stop", True),
        "__iter__": lambda self: self,
        "__next__": lambda self: (
            setattr(self, "count", self.count + 1),
            self.count if self.check(self) and not self._stop else next(iter(())))[-1]
    }),

    try_except := lambda coro: (
        (
            task := loop.create_task(coro),
            [
                await asyncio.sleep(0.01)
                for _ in While(lambda _: not task.done())
            ],
            exc if isinstance(exc := task.exception(), Exception) else task.result()
        )[-1]
        for _ in "_"
    ).__anext__(),

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

    Embed := type("Embed", (), {
        "__init__": lambda self, *, title = None, url = None, description = None, color = None, timestamp = None: (
            setattr(self, "title", title) if title else (),
            setattr(self, "url", url) if url else (),
            setattr(self, "description", description) if description else (),
            setattr(self, "color", color) if color else (),
            setattr(self, "timestamp", timestamp) if timestamp else (), None)[-1],
        "set_title": lambda self, title: (
            setattr(self, "title", title), self)[-1],
        "set_description": lambda self, description: (
            setattr(self, "description", description), self)[-1],
        "set_color": lambda self, color: (
            setattr(self, "color", color), self)[-1],
        "set_timestamp": lambda self, timestamp: (
            setattr(self, "color", timestamp), self)[-1],
        "set_image": lambda self, url: (
            setattr(self, "image", {"url": url}), self)[-1],
        "set_thumbnail": lambda self, url: (
            setattr(self, "thumbnail", {"url": url}), self)[-1],
        "set_footer": lambda self, text = None, icon_url = None: (
            setattr(self, "footer", {"text": text, "icon_url": icon_url}), self)[-1],
        "set_author": lambda self, name = None, url = None, icon_url = None: (
            setattr(self, "author", {"name": name, "url": url, "icon_url": icon_url}), self)[-1],
        "add_field": lambda self, name = None, value = None, inline = False: (
            setattr(self, "fields", []) if not hasattr(self, "fields") else (),
            self.fields.append({"name": name, "value": value, "inline": inline}), self)[-1],
        "add_blank_field": lambda self, inline = True: (
            self.add_field(name="\u200b", value="\u200b", inline=inline), self)[-1]
    }),

    Channel := type("Channel", (), {
        "__init__": lambda self, __client, *, id, name, type, **kwargs: (
            setattr(self, "__client", __client),
            setattr(self, "id", id),
            setattr(self, "name", name),
            setattr(self, "type", type), None)[-1],
        "__str__": lambda self:
            f"<Channel id={self.id!r} name={self.name!r} type={self.type!r}>",
        "__repr__": lambda self:
            f"<Channel id={self.id!r} name={self.name!r} type={self.type!r}>",
        "send": lambda self, content = None, *, embed = None, embeds = None, other = None: (
            data := (
                ({"content": content} if content else {}) |
                ({"embeds": [embed.__dict__ for embed in embeds or []] + [embed.__dict__] if embed else []} if embeds or embed else {}) |
                ({"allowed_mentions": {"parse": [], "users": [], "replied_user": False}}) |
                (other or {})
            ),
            self.__client.http.request(Route("POST", "channels", self.id, "messages"), data))[-1]
    }),

    Role := type("Role", (), {
        "__init__": lambda self, __client, *, id, name, color, hoist, position, permissions, mentionable, **kwargs: (
            setattr(self, "__client", __client),
            setattr(self, "id", id),
            setattr(self, "name", name),
            setattr(self, "color", color),
            setattr(self, "hoist", hoist),
            setattr(self, "position", position),
            setattr(self, "permissions", permissions),
            setattr(self, "mentionable", mentionable), None)[-1],
        "__str__": lambda self:
            f"<Role id={self.id!r} name={self.name!r} color={self.color!r} hoist={self.hoist!r} position={self.position!r} permissions={self.permissions!r} mentionable={self.mentionable!r}>",
        "__repr__": lambda self:
            f"<Role id={self.id!r} name={self.name!r} color={self.color!r} hoist={self.hoist!r} position={self.position!r} permissions={self.permissions!r} mentionable={self.mentionable!r}>"
    }),

    Emoji := type("Emoji", (), {
        "__init__": lambda self, __client, *, id, name, animated, **kwargs: (
            setattr(self, "__client", __client),
            setattr(self, "id", id),
            setattr(self, "name", name),
            setattr(self, "animated", animated), None)[-1],
        "__str__": lambda self:
            f"<Emoji id={self.id!r} name={self.name!r} animated={self.animated!r}>",
        "__repr__": lambda self:
            f"<Emoji id={self.id!r} name={self.name!r} animated={self.animated!r}>"
    }),

    Sticker := type("Sticker", (), {
        "__init__": lambda self, __client, *, id, name, description, **kwargs: (
            setattr(self, "__client", __client),
            setattr(self, "id", id),
            setattr(self, "name", name),
            setattr(self, "description", description), None)[-1],
        "__str__": lambda self:
            f"<Sticker id={self.id!r} name={self.name!r} description={self.description!r}>",
        "__repr__": lambda self:
            f"<Sticker id={self.id!r} name={self.name!r} description={self.description!r}>"
    }),

    User := type("User", (), {
        "__init__": lambda self, __client, *, id, username, avatar, bot, **kwargs: (
            setattr(self, "__client", __client),
            setattr(self, "id", id),
            setattr(self, "username", username),
            setattr(self, "avatar", avatar),
            setattr(self, "bot", bot), None)[-1],
        "__str__": lambda self:
            f"<User id={self.id!r} username={self.username!r}>",
        "__repr__": lambda self:
            f"<User id={self.id!r} username={self.username!r}>"
    }),

    Member := type("Member", (), {
        "__init__": lambda self, __client, guild, *, user, roles, **kwargs: (
            setattr(self, "__client", __client),
            setattr(self, "user", User(__client, **user)),
            setattr(self, "roles", [guild.get_role(role) for role in roles]), None)[-1],
        "__str__": lambda self:
            f"<Member user={self.user!r} roles={self.roles!r}>",
        "__repr__": lambda self:
            f"<Member user={self.user!r} roles={self.roles!r}>"
    }),

    Guild := type("Guild", (), {
        "__init__": lambda self, __client, *, id, name, description, owner_id, icon, channels, roles, members, emojis, stickers, **kwargs: (
            setattr(self, "__client", __client),
            setattr(self, "id", id),
            setattr(self, "name", name),
            setattr(self, "description", description),
            setattr(self, "icon", icon),
            setattr(self, "channels", [Channel(__client, **channel) for channel in channels]),
            setattr(self, "roles", [Role(__client, **role) for role in roles]),
            setattr(self, "members", [Member(__client, self, **member) for member in members]),
            setattr(self, "owner", self.get_member(owner_id)),
            setattr(self, "emojis", [Emoji(__client, **emoji) for emoji in emojis]),
            setattr(self, "stickers", [Sticker(__client, **sticker) for sticker in stickers]), None)[-1],
        "__str__": lambda self:
            f"<Guild id={self.id!r} name={self.name!r}>",
        "__repr__": lambda self:
            f"<Guild id={self.id!r} name={self.name!r}>",
        "get_channel": lambda self, channel_id: (
            channel := [channel for channel in self.channels if channel.id == channel_id], channel[0] if channel else None)[-1],
        "get_role": lambda self, role_id: (
            role := [role for role in self.roles if role.id == role_id], role[0] if role else None)[-1],
        "get_member": lambda self, user_id: (
            member := [member for member in self.members if member.user.id == user_id], member[0] if member else None)[-1]
    }),

    Message := type("Message", (), {
        "__init__": lambda self, __client, *, id, guild_id, channel_id, author, content, **kwargs: (
            setattr(self, "__client", __client),
            setattr(self, "id", id),
            setattr(self, "guild", self.__client.get_guild(guild_id)),
            setattr(self, "channel", self.guild.get_channel(channel_id)),
            setattr(self, "member", self.guild.get_member(author["id"])),
            setattr(self, "author", self.member.user),
            setattr(self, "content", content), None)[-1],
        "__str__": lambda self:
            f"<Message id={self.id!r} channel={self.channel!r} author={self.author!r} content={self.content!r}>",
        "__repr__": lambda self:
            f"<Message id={self.id!r} channel={self.channel!r} author={self.author!r} content={self.content!r}>",
        "reply": lambda self, content = None, *, embed = None, embeds = None, other = None: (
            other := (other or {}) | {"message_reference": {"guild_id": self.guild.id, "channel_id": self.channel.id, "message_id": self.id}},
            self.channel.send(content, embed=embed, embeds=embeds, other=other))[-1]
    }),

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
        "request": lambda self, route, data = None: (
            (
                response := await self.session.request(route.method, Http.URL + route.endpoint, headers=self.headers, **({"json": data} if data else {})),
                await response.json()
            )[-1]
            for _ in "_"
        ).__anext__()
    }),

    Gateway := type("Gateway", (), {
        "URL": "wss://gateway.discord.gg/?v=9&encoding=json",
        "__init__": lambda self, token, intents: (
            setattr(self, "loop", asyncio.get_event_loop()),
            setattr(self, "token", token),
            setattr(self, "intents", intents),
            setattr(self, "listeners", {}),
            setattr(self, "middlewares", {}),
            setattr(self, "session", aiohttp.ClientSession()), None)[-1],
        "on": lambda self, event, func: (
            self.listeners.__setitem__(event, [])
            if event not in self.listeners else (),
            self.listeners[event].append(func), None)[-1],
        "register_middleware": lambda self, event, func: (
            self.middlewares.__setitem__(event, func), None)[-1],
        "dispatch": lambda self, event, *args: (
            [
                await listener(*args)
                for listener in self.listeners
                    .get(event.lower(), [lambda data: (
                        (
                            await asyncio.sleep(0),
                        )
                        for _ in "_"
                    ).__anext__()])
            ]
            for _ in "_"
        ).__anext__(),
        "send": lambda self, op, data: self.ws.send_json({"op": op.value, "d": data}),
        "heartbeat": lambda self, interval: (
            [
                (
                    await self.send(Opcodes.HEARTBEAT, {}),
                    await asyncio.sleep(interval / 1000)
                )
                for _ in While(lambda _: True)
            ]
            for _ in "_"
        ).__anext__(),
        "run": lambda self: (
            (
                setattr(self, "ws", await self.session.ws_connect(Gateway.URL)),
                [
                    (
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
                                (
                                    middleware := self.middlewares.get(t),
                                    data := (
                                        data := await middleware(d),
                                        data if isinstance(data, tuple) else (data,)
                                        if data else None
                                    )[-1]
                                    if middleware else None,
                                    await self.dispatch(t, *data) if data else ()
                                )
                                for _ in "_"
                            ).__anext__()
                        }.get(op, lambda: (
                            (
                                await asyncio.sleep(0)
                            )
                            for _ in "_"
                        ).__anext__())()
                    )
                    for _ in While(lambda _: True)
                ]
            )
            for _ in "_"
        ).__anext__()
    }),

    Client := type("Client", (), {
        "__init__": lambda self, token, intents: (
            setattr(self, "ws", Gateway(token, intents)),
            setattr(self, "http", Http(token)),
            setattr(self, "bot_user", None),
            setattr(self, "guilds", []),
            setattr(self, "users", {}),
            setattr(self, "unavailable_guilds", 0),
            setattr(self, "_lock", True),
            self.register_middlewares(), None)[-1],
        "get_guild": lambda self, guild_id: (
            guild := [guild for guild in self.guilds if guild.id == guild_id], guild[0] if guild else None)[-1],
        "get_user": lambda self, user_id:
            self.users.get(user_id),
        "register_middlewares": lambda self: (
            self.ws.register_middleware("READY", lambda data: (
                (
                    await asyncio.sleep(0),
                    setattr(self, "bot_user", User(self, **data["user"])),
                    setattr(self, "unavailable_guilds", len(data["guilds"])),
                    None
                )[-1]
                for _ in "_"
            ).__anext__()),

            self.ws.register_middleware("GUILD_CREATE", lambda guild: (
                (
                    guild := Guild(self, **guild),
                    self.guilds.append(guild),
                    [
                        self.users.__setitem__(member.user.id, member.user)
                        for member in guild.members
                    ],
                    (
                        setattr(self, "_lock", False),
                        await self.ws.dispatch("ready")
                    )
                    if len(self.guilds) >= self.unavailable_guilds and self._lock else ()
                )[0]
                for _ in "_"
            ).__anext__()),

            self.ws.register_middleware("GUILD_DELETE", lambda guild: (
                (
                    await asyncio.sleep(0),
                    guild := self.get_guild(guild["id"]),
                    self.guilds.remove(guild)
                )[1]
                for _ in "_"
            ).__anext__()),

            self.ws.register_middleware("MESSAGE_CREATE", lambda message: (
                (
                    await asyncio.sleep(0),
                    Message(self, **message)
                )[-1]
                for _ in "_"
            ).__anext__())
        )
    }),

    main := lambda: (
        (
            token_file := open("token", "r"),
            token := token_file.read(),
            token_file.close(),

            client := Client(token, reduce(lambda a, b: a | b, [intent.value for intent in Intents])),

            application := await client.http.request(Route("GET", "applications", "@me")),
            owners := [member["user"]["id"] for member in application["team"]["members"]],

            client.ws.on("ready", lambda: (
                (
                    await asyncio.sleep(0),
                    print("logged in", client.bot_user.username)
                )
                for _ in "_"
            ).__anext__()),

            prefix := "4",
            commands := {
                "ping": lambda message: (
                    (
                        await message.reply("Pong")
                    )
                    for _ in "_"
                ).__anext__(),
                "stats": lambda message: (
                    (
                        await message.reply(embed=Embed(
                            title = "Bot statistics:",
                            description = f"Guilds: `{len(client.guilds)}`\nUsers: `{len(client.users)}`"
                        ))
                    )
                    for _ in "_"
                ).__anext__(),
                "eval": lambda message: (
                    (
                        code := message.content[len(prefix + "eval") + 1:],
                        result := str(await try_except(eval(f"((await asyncio.sleep(0), {code})[-1] for _ in \"_\").__anext__()", globals() | {"client": client, "message": message}))),
                        [
                            await message.reply("```" + result[i:i+1994] + "```")
                            for i in range(0, len(result), 1994)
                        ]
                    )
                    if message.author.id in owners else
                    (
                        await message.reply("You don't have permission")
                    )
                    for _ in "_"
                ).__anext__()
            },

            client.ws.on("message_create", lambda message: (
                (
                    await commands.get(message.content[len(prefix):].split(" ", 1)[0], lambda _: (
                        (
                            await asyncio.sleep(0),
                        )
                        for _ in "_"
                    ).__anext__())(message)
                    if message.content.startswith(prefix) else ()
                )
                for _ in "_"
            ).__anext__()),

            await client.ws.run()
        )[-1]
        for _ in "_"
    ).__anext__(),

    (
        loop := asyncio.new_event_loop(),
        asyncio.set_event_loop(loop),

        loop.run_until_complete(main())
    ) if __name__ == "__main__" else ()
)