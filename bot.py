"""
Copyright 2022-2024 PoligonTeam

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
    namedtuple := __import__("collections").namedtuple,
    cycle := __import__("itertools").cycle,
    sys := __import__("sys"),

    loop := asyncio.new_event_loop(),
    asyncio.set_event_loop(loop),

    _opcodes := dict(
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

    Opcodes := type("Opcodes", (Enum,), type("EnumType", (dict,), {"_member_names": list(_opcodes.keys())})(**_opcodes)),

    WebSocket := lambda token: (
        (
            _WebSocket := namedtuple("WebSoscket", ["run"]),

            URL := "wss://gateway.discord.gg/?v=9&encoding=json",

            session := aiohttp.ClientSession(),

            ws := await session.ws_connect(URL),

            sequence := 0,

            send := lambda op, data: ws.send_json({"op": op.value, "d": data}),
            request := lambda method, endpoint, data: session.request(method, "https://discord.com/api/v10" + endpoint, headers={"authorization": "Bot " + token}, **({"json": data} if data else {})),

            heartbeat := lambda interval: (
                [
                    [
                        await send(Opcodes.HEARTBEAT, {}),
                        await asyncio.sleep(interval / 1000)
                    ]
                    for _ in cycle([None])
                ]
                for _ in "_"
            ).__anext__(),

            run := lambda: (
                [
                    [
                        data := await ws.receive_json(),

                        op := Opcodes(data.get("op")),
                        d := data.get("d"),
                        s := data.get("s"),
                        t := data.get("t"),

                        await {
                            Opcodes.HELLO: lambda: (
                                (
                                    loop.create_task(heartbeat(d["heartbeat_interval"])),

                                    await send(Opcodes.IDENTIFY, {
                                        "token": token,
                                        "properties": {
                                            "os": sys.platform,
                                            "browser": "oneline-lib-python",
                                            "device": "oneline-lib-python"
                                        },
                                        "intents": 32767,
                                        "large_threshold": 250
                                    })
                                )
                                for _ in "_"
                            ).__anext__(),
                            Opcodes.DISPATCH: lambda: (
                                (
                                    await {
                                        "MESSAGE_CREATE": lambda: (
                                            (
                                                await {
                                                    "4ping": lambda: (
                                                        (
                                                            await request("POST", "/channels/" + d["channel_id"] + "/messages", {"content": "Pong!"}),
                                                        )
                                                        for _ in "_"
                                                    ).__anext__()
                                                }.get(d["content"], lambda: (
                                                    (
                                                        await asyncio.sleep(0),
                                                    )
                                                    for _ in "_"
                                                ).__anext__())()
                                            )
                                            for _ in "_"
                                        ).__anext__()
                                    }.get(t, lambda: (
                                        (
                                            await asyncio.sleep(0),
                                        )
                                        for _ in "_"
                                    ).__anext__())()
                                )
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
                for _ in "_"
            ).__anext__(),

            _WebSocket(run)
        )[-1]
        for _ in "_"
    ).__anext__(),

    main := (
        (
            token_file := open("token", "r"),
            token := token_file.read(),
            token_file.close(),

            websocket := await WebSocket(token),
            loop.create_task(websocket.run())
        )
        for _ in "_"
    ).__anext__(),

    loop.create_task(main),
    loop.run_forever()
)