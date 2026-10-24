QTYPES = "Behavioral, Technical, Experience, Motivation, Salary, Logistics, Small talk, Other"
QUIET = 1.3     # konusma durduktan kac sn sonra tur biter
QUIET_Q = 0.7   # son cumle soruysa daha kisa bekle

async def suggest(ws: WebSocket, sid: int, history: list[str], context: str, turn_text: str):
    try:
        if len(turn_text.split()) < 4 and "?" not in turn_text:
            await ws.send_json({"type": "no_reply", "id": sid})
            return
        convo = "\n".join(f"- {h}" for h in history[-8:])
        prompt = (
            "You are my real-time interview coach. I am the candidate speaking.\n"
            f"MY BACKGROUND/CONTEXT: {context or 'Senior UA & Growth Marketing Specialist'}\n"
            f"RECENT CONVERSATION (latest last):\n{convo}\n"
            f"THE OTHER PERSON'S LATEST TURN: {turn_text}\n\n"
            "If their latest turn is only a small acknowledgement that expects no answer "
            "(for example: mhm, great, okay, thanks), output exactly: SKIP\n"
            "Otherwise use this exact format:\n"
            f"Line 1: TYPE: <one of: {QTYPES}>\n"
            "Line 2: three distinct replies I can say next, in first person, separated by '|||'. "
            "No JSON, numbering or bullets.\n"
            "Angle 1: direct and concise, metric/execution focus. Angle 2: a concrete example from my background. "
            "Angle 3: strategic insight plus a sharp follow-up question.\n"
            "Base every claim ONLY on my background above. Never invent employers, numbers, tools or "
            "achievements that are not written there; if a fact is missing, answer honestly in general "
            "terms or ask a sharp question back.\n"
            "Keep each reply to 1-2 natural spoken English sentences."
        )
        stream = await client.aio.models.generate_content_stream(
            model=REPLY_MODEL,
            contents=prompt,
            config=FAST_REPLY_CONFIG,
        )
        full = ""
        async for chunk in stream:
            if not chunk.text:
                continue
            full += chunk.text
            s = full.lstrip()
            if "\n" not in s:
                continue  # etiket satiri henuz tamamlanmadi (ya da SKIP)
            head, rest = s.split("\n", 1)
            if head.upper().startswith("TYPE:"):
                label = head[5:].strip()
            else:
                label, rest = "", s
            parts = [p.strip() for p in rest.split("|||")]
            await ws.send_json({"type": "replies_stream", "id": sid, "label": label, "replies": parts[:3]})
        if full.strip().upper().startswith("SKIP"):
            await ws.send_json({"type": "no_reply", "id": sid})
    except asyncio.CancelledError:
        raise
    except Exception as e:
        await ws.send_json({"type": "error", "text": f"Öneri hatası: {e}"})


class TurnBuffer:
    """Transkript parcalarini cumlelere, cumleleri de konusma turuna cevirir."""

    def __init__(self, on_sentence, on_turn):
        self.on_sentence, self.on_turn = on_sentence, on_turn
        self.buf, self.turn, self.timer = "", [], None

    def _arm(self):
        if self.timer:
            self.timer.cancel()
        last = (self.buf if self.buf.strip() else (self.turn[-1] if self.turn else "")).rstrip()
        wait = QUIET_Q if last.endswith("?") else QUIET
        self.timer = asyncio.create_task(self._quiet(wait))

    async def _quiet(self, wait):
        await asyncio.sleep(wait)
        self.timer = None
        await self.flush()

    async def _emit(self):
        s = self.buf.strip()
        self.buf = ""
        if s:
            self.turn.append(s)
            await self.on_sentence(s)

    async def add(self, text):
        self.buf += text
        b = self.buf.rstrip()
        if b.endswith((".", "?", "!")) or len(b.split()) >= 12:
            await self._emit()
        self._arm()

    def touch(self):
        if self.buf.strip() or self.turn:
            self._arm()

    async def flush(self):
        await self._emit()
        if self.turn:
            text = " ".join(self.turn)
            self.turn = []
            await self.on_turn(text)

    def cancel(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    st = {"sid": 0, "suggest": None, "mic": None, "n": 0}
    history, context = [], ""
    bg = set()
    audio_q = asyncio.Queue(maxsize=300)

    async def on_sentence(text: str):
        st["sid"] += 1
        sid = st["sid"]
        history.append(text)
        await ws.send_json({"type": "en", "id": sid, "text": text})
        t = asyncio.create_task(translate(ws, sid, text))
        bg.add(t)
        t.add_done_callback(bg.discard)

    async def on_turn(text: str):
        if st["suggest"] and not st["suggest"].done():
            st["suggest"].cancel()
        st["suggest"] = asyncio.create_task(suggest(ws, st["sid"], history, context, text))

    tb = TurnBuffer(on_sentence, on_turn)

    async def transcriber():
        while True:
            try:
                async with client.aio.live.connect(
                    model=TRANSCRIBE_MODEL, config=TRANSCRIBE_CONFIG
                ) as session:
                    print("LIVE API BAGLANDI:", TRANSCRIBE_MODEL, flush=True)
                    async def pump():
                        while True:
                            chunk = await audio_q.get()
                            await session.send_realtime_input(
                                audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
                            )
                    pump_task = asyncio.create_task(pump())
                    try:
                        async for r in session.receive():
                            sc = r.server_content
                            if not sc:
                                continue
                            it = getattr(sc, "interim_input_transcription", None)
                            if it and it.text:
                                tb.touch()
                                await ws.send_json({"type": "interim", "text": (tb.buf + it.text).strip()})
                            ft = getattr(sc, "input_transcription", None)
                            if ft and ft.text:
                                await tb.add(ft.text)
                                if tb.buf.strip():
                                    await ws.send_json({"type": "interim", "text": tb.buf.strip()})
                            if getattr(sc, "turn_complete", False):
                                await tb.flush()
                    finally:
                        pump_task.cancel()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print("TRANSKRIPT HATASI:", repr(e), flush=True)
                try:
                    await ws.send_json({"type": "error", "text": f"Transkript hatası ({TRANSCRIBE_MODEL}): {e}"})
                except Exception:
                    return
                await asyncio.sleep(2)

    try:
        while True:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                break
            if msg.get("bytes") is not None:
                if audio_q.full():
                    try:
                        audio_q.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                audio_q.put_nowait(msg["bytes"])
                st["n"] += 1
                if st["n"] % 50 == 1:
                    print(f"Ses paketi alindi: #{st['n']}", flush=True)
                continue
            if msg.get("text"):
                data = json.loads(msg["text"])
                kind = data.get("type")
                if kind == "context":
                    context = data.get("text", "")
                elif kind == "start":
                    print("START sinyali alindi, transcriber baslatiliyor...", flush=True)
                    while not audio_q.empty():
                        audio_q.get_nowait()
                    if not st["mic"] or st["mic"].done():
                        st["mic"] = asyncio.create_task(transcriber())
                elif kind == "stop":
                    print("STOP sinyali alindi.", flush=True)
                    if st["mic"]:
                        st["mic"].cancel()
                        st["mic"] = None
                    while not audio_q.empty():
                        audio_q.get_nowait()
                    await tb.flush()
                elif kind == "text":
                    t = data.get("text", "").strip()
                    if t:
                        await on_sentence(t)
                        await on_turn(t)
    finally:
        tb.cancel()
        for k in ("mic", "suggest"):
            if st[k]:
                st[k].cancel()
        for t in list(bg):
            t.cancel()
