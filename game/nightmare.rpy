# ==========================================================
# game/nightmare.rpy
# «Девяностые» (c) MR LIMBO
#
# Кошмарный сон: ритм-игра в стиле osu!
# Кружки, слайдеры-отрезки, спиннеры.
#
# Механика температуры:
#   старт 36.6
#   не нажимаешь  -> падает до 26.0 -> смерть от холода
#   лупишь подряд -> растёт до 45.0 -> смерть от жара
#
# СЕРЕДИНЫ НЕТ. Любое отклонение от 36.6 усиливает само себя,
# поэтому удержать баланс физически невозможно. Игрок только
# выбирает, каким способом умереть. За 5 секунд до конца трека
# добивает в ту сторону, куда уже накренило.
#
# Нужные файлы (любого может не быть, игра не упадёт):
#   images/dream_bg.png
#   images/dream/flash_1.png ... flash_8.png
#   audio/nightmare.ogg
# ==========================================================


# ===== Настрой под свой трек =====
define NM_SONG = "audio/nightmare.ogg"
define NM_BPM = 150.0
define NM_DURATION = 95.0          # ДЛИНА ТРЕКА В СЕКУНДАХ

# ===== Баланс =====
define NM_AR = 0.85                # сколько секунд летит кружок
define NM_HIT_WINDOW = 0.16        # окно попадания
define NM_R = 0.075                # радиус кружка (доля высоты)

define NM_START_TEMP = 36.6
define NM_TEMP_MIN = 26.0
define NM_TEMP_MAX = 45.0

define NM_DRIFT = -0.30            # холод тянет вниз всегда
define NM_GAIN_SICK = 0.45
define NM_GAIN_GOOD = 0.30
define NM_GAIN_BAD = 0.12
define NM_GAIN_SLIDE = 0.55        # в секунду, пока ведёшь слайдер
define NM_GAIN_SPIN = 0.65         # в секунду на спиннере

# Разгон: чем дальше от 36.6, тем сильнее тащит дальше.
# Именно из-за этого середины не существует.
define NM_RUNAWAY = 0.55

# К концу трека всё множится, финал неизбежен
define NM_ESCALATE = 2.0

define NM_RUSH_TIME = 5.0
define NM_RUSH_MULT = 5.0


init python:

    import math, random

    try:
        import pygame_sdl2 as nm_pg
    except ImportError:
        import pygame as nm_pg

    def nm_clamp(v, a, b):
        return max(a, min(b, v))

    def nm_temp_color(t):
        if t >= 43.0 or t <= 28.0:
            return (255, 43, 61, 255)
        if t >= 40.0 or t <= 32.0:
            return (255, 157, 43, 255)
        return (92, 214, 122, 255)

    def nm_build_map(duration, bpm, seed=1991):
        """Карта нот генерируется сама, никаких json не нужно."""
        rnd = random.Random(seed)
        spb = 60.0 / float(bpm)
        objs = []
        t = 3.0
        limit = max(8.0, duration - NM_RUSH_TIME - 1.0)
        while t < limit:
            roll = rnd.random()
            x = rnd.uniform(0.14, 0.86)
            y = rnd.uniform(0.20, 0.80)
            if roll < 0.66:
                objs.append({"type": "circle", "t": t, "x": x, "y": y,
                             "judged": False, "hit": False})
                t += spb * rnd.choice([1.0, 1.0, 0.5, 0.5, 2.0])
            elif roll < 0.90:
                x2 = min(0.88, max(0.12, x + rnd.uniform(-0.34, 0.34)))
                y2 = min(0.82, max(0.18, y + rnd.uniform(-0.28, 0.28)))
                dur = spb * rnd.choice([2.0, 3.0, 4.0])
                objs.append({"type": "slider", "t": t, "x": x, "y": y,
                             "x2": x2, "y2": y2, "dur": dur,
                             "judged": False, "hit": False, "held": 0.0})
                t += dur + spb
            else:
                dur = spb * 4.0
                objs.append({"type": "spin", "t": t, "x": 0.5, "y": 0.5,
                             "dur": dur, "judged": False, "hit": False, "fill": 0.0})
                t += dur + spb
        objs.sort(key=lambda o: o["t"])
        return objs


    class NightmareGame(renpy.Displayable):

        def __init__(self, song=None, bpm=None, duration=None, **kw):
            renpy.Displayable.__init__(self, **kw)

            self.song = song or NM_SONG
            self.bpm = float(bpm or NM_BPM)
            self.duration = float(duration or NM_DURATION)
            self.objs = nm_build_map(self.duration, self.bpm)

            self.temp = NM_START_TEMP
            self.lean = 0.0
            self.combo = 0
            self.maxcombo = 0
            self.hits = 0
            self.misses = 0
            self.result = None

            self.started = None
            self.music_on = False
            self.cursor = (0.5, 0.5)
            self.pressed = False
            self.i0 = 0

            self.pops = []
            self.rings = []
            self.shake = 0.0
            self.flash = 0.0
            self.frame_i = 0
            self.frame_t = 0.0

            self._last = None
            self._w = 1920
            self._h = 1080
            self._td = {}
            self._tf = {}
            self._frames = [p for p in
                            ["images/dream/flash_%d.png" % i for i in range(1, 9)]
                            if renpy.loadable(p)]

        # ---------- утилиты рисования ----------

        def _text(self, r, s, x, y, size, col, st, at):
            key = (s, size, col)
            d = self._td.get(key)
            if d is None:
                d = Text(s, size=size, color=col, outlines=[(3, "#000000cc", 0, 0)])
                self._td[key] = d
            cr = renpy.render(d, self._w, self._h, st, at)
            tw, th = cr.get_size()
            r.blit(cr, (int(x - tw / 2), int(y - th / 2)))

        def _ring(self, r, px, py, rad, col, w, st, at):
            rad = int(max(2, rad))
            w = int(max(0, w))
            dd = rad * 2 + w * 2 + 6
            if dd <= 0 or dd > 4000:
                return
            try:
                surf = renpy.Render(dd, dd)
                surf.canvas().circle(col, (dd // 2, dd // 2), rad, w)
                r.blit(surf, (int(px - dd / 2), int(py - dd / 2)))
            except Exception:
                pass

        def _line(self, r, x1, y1, x2, y2, col, w, st, at):
            try:
                surf = renpy.Render(self._w, self._h)
                surf.canvas().line(col, (int(x1), int(y1)), (int(x2), int(y2)), int(w))
                r.blit(surf, (0, 0))
            except Exception:
                pass

        def _solid(self, r, col, alpha, st, at):
            key = ("s", col, self._w, self._h, int(alpha * 255))
            d = self._tf.get(key)
            if d is None:
                d = Transform(Solid(col), xysize=(self._w, self._h), alpha=alpha)
                self._tf[key] = d
            r.blit(renpy.render(d, self._w, self._h, st, at), (0, 0))

        # ---------- время ----------

        def now(self, st):
            if self.started is None:
                self.started = st
            return st - self.started

        def _add_temp(self, d):
            self.temp = nm_clamp(self.temp + d, NM_TEMP_MIN - 1.0, NM_TEMP_MAX + 1.0)

        # ---------- ввод ----------

        def press_at(self, cx, cy, now):
            best = None
            bd = 99999.0
            i = self.i0
            n = len(self.objs)
            while i < n:
                o = self.objs[i]
                if o["t"] > now + NM_HIT_WINDOW:
                    break
                if o["type"] == "circle" and not o["judged"]:
                    d = abs(o["t"] - now)
                    if d <= NM_HIT_WINDOW and d < bd:
                        if math.hypot(cx - o["x"], (cy - o["y"]) * 0.56) <= NM_R * 1.7:
                            bd = d
                            best = o
                i += 1

            if best is None:
                self.combo = 0
                self.shake = max(self.shake, 0.10)
                return

            best["judged"] = True
            best["hit"] = True
            self.hits += 1
            self.combo += 1
            self.maxcombo = max(self.maxcombo, self.combo)

            if bd <= NM_HIT_WINDOW * 0.34:
                g, lab, col = NM_GAIN_SICK, u"ЖАР!", "#5cd6ff"
            elif bd <= NM_HIT_WINDOW * 0.7:
                g, lab, col = NM_GAIN_GOOD, u"ТЕПЛО", "#5cd67a"
            else:
                g, lab, col = NM_GAIN_BAD, u"ЕДВА", "#e8c454"

            self._add_temp(g)
            self.flash = max(self.flash, 0.12)
            self.pops.append([lab, col, best["x"], best["y"], 0.0])
            self.rings.append([best["x"], best["y"], 0.0])

        def event(self, ev, x, y, st):
            if self.result is not None:
                return None

            cx = float(x) / max(1, self._w)
            cy = float(y) / max(1, self._h)
            t = self.now(st)

            keys = (getattr(nm_pg, "K_z", 122),
                    getattr(nm_pg, "K_x", 120),
                    getattr(nm_pg, "K_SPACE", 32))

            if ev.type in (getattr(nm_pg, "MOUSEMOTION", -1),
                           getattr(nm_pg, "FINGERMOTION", -2)):
                self.cursor = (cx, cy)

            elif ev.type == getattr(nm_pg, "MOUSEBUTTONDOWN", -3) and getattr(ev, "button", 1) == 1:
                self.cursor = (cx, cy)
                self.pressed = True
                self.press_at(cx, cy, t)

            elif ev.type == getattr(nm_pg, "FINGERDOWN", -4):
                self.cursor = (cx, cy)
                self.pressed = True
                self.press_at(cx, cy, t)

            elif ev.type in (getattr(nm_pg, "MOUSEBUTTONUP", -5),
                             getattr(nm_pg, "FINGERUP", -6)):
                self.pressed = False

            elif ev.type == getattr(nm_pg, "KEYDOWN", -7) and getattr(ev, "key", 0) in keys:
                self.pressed = True
                self.press_at(self.cursor[0], self.cursor[1], t)

            elif ev.type == getattr(nm_pg, "KEYUP", -8):
                self.pressed = False

            raise renpy.IgnoreEvent()

        # ---------- логика ----------

        def tick(self, dt, t):
            esc = 1.0 + NM_ESCALATE * nm_clamp(t / self.duration, 0.0, 1.0)
            left = self.duration - t
            rush = left <= NM_RUSH_TIME
            gained = 0.0

            i = self.i0
            n = len(self.objs)
            while i < n:
                o = self.objs[i]
                if o["t"] > t + NM_AR:
                    break
                ty = o["type"]

                if ty == "circle":
                    if not o["judged"] and t > o["t"] + NM_HIT_WINDOW:
                        o["judged"] = True
                        self.misses += 1
                        self.combo = 0

                elif ty == "slider":
                    if o["t"] <= t <= o["t"] + o["dur"]:
                        p = (t - o["t"]) / max(0.001, o["dur"])
                        bx = o["x"] + (o["x2"] - o["x"]) * p
                        by = o["y"] + (o["y2"] - o["y"]) * p
                        if self.pressed and math.hypot(self.cursor[0] - bx,
                                                       (self.cursor[1] - by) * 0.56) <= NM_R * 2.0:
                            o["held"] += dt
                            gained += NM_GAIN_SLIDE * dt
                    elif t > o["t"] + o["dur"] and not o["judged"]:
                        o["judged"] = True
                        if o["held"] < o["dur"] * 0.35:
                            self.misses += 1
                            self.combo = 0

                else:
                    if o["t"] <= t <= o["t"] + o["dur"]:
                        if self.pressed:
                            o["fill"] = min(1.0, o["fill"] + dt / max(0.001, o["dur"]))
                            gained += NM_GAIN_SPIN * dt
                    elif t > o["t"] + o["dur"] and not o["judged"]:
                        o["judged"] = True
                i += 1

            while self.i0 < n:
                o = self.objs[self.i0]
                if o["judged"] and (o["t"] + o.get("dur", 0.0) + 1.0) < t:
                    self.i0 += 1
                else:
                    break

            # Разгон: отклонение усиливает само себя
            dev = self.temp - NM_START_TEMP
            runaway = dev * NM_RUNAWAY * dt

            if rush:
                self.lean = 1.0 if dev >= 0 else -1.0
                self._add_temp(self.lean * 2.2 * dt * NM_RUSH_MULT
                               + runaway * NM_RUSH_MULT)
            else:
                self._add_temp((NM_DRIFT * dt + gained) * esc + runaway * esc)

            if self.temp >= NM_TEMP_MAX:
                self.result = "burn"
            elif self.temp <= NM_TEMP_MIN:
                self.result = "freeze"
            elif t >= self.duration + 1.5:
                self.result = "burn" if dev >= 0 else "freeze"

        # ---------- отрисовка ----------

        def render(self, width, height, st, at):
            self._w, self._h = width, height
            t = self.now(st)

            if self._last is None:
                self._last = st
            dt = nm_clamp(st - self._last, 0.0, 0.05)
            self._last = st

            if not self.music_on:
                self.music_on = True
                try:
                    if renpy.loadable(self.song):
                        renpy.music.play(self.song, channel="music", loop=False)
                except Exception:
                    pass

            if self.result is None:
                self.tick(dt, t)

            r = renpy.Render(width, height)

            danger = nm_clamp(max((self.temp - 39.0) / 6.0,
                                  (33.0 - self.temp) / 7.0), 0.0, 1.0)

            self.shake = max(0.0, self.shake - dt * 1.6)
            self.flash = max(0.0, self.flash - dt * 3.0)

            amp = int(self.shake * 90.0 + danger * 26.0)
            sx = random.randint(-amp, amp) if amp else 0
            sy = random.randint(-amp, amp) if amp else 0

            spb = 60.0 / self.bpm
            beat = 1.0 - ((t % spb) / spb)
            zoom = 1.0 + 0.03 * beat + 0.05 * danger

            # ---- фон ----
            bgp = "images/dream_bg.png"
            key = ("bg", width, height, round(zoom, 3))
            d = self._tf.get(key)
            if d is None:
                if renpy.loadable(bgp):
                    d = Transform(bgp, xysize=(width, height), zoom=zoom)
                else:
                    d = Transform(Solid("#14001f"), xysize=(width, height))
                self._tf[key] = d
            r.blit(renpy.render(d, width, height, st, at), (sx, sy))

            # ---- мигающие кадры ----
            if self._frames:
                self.frame_t += dt
                step = spb * (0.5 if danger > 0.5 else 1.0)
                if self.frame_t >= step:
                    self.frame_t = 0.0
                    self.frame_i = random.randrange(len(self._frames))
                if beat > 0.72 or danger > 0.6:
                    p = self._frames[self.frame_i]
                    fk = ("fr", p, width, height)
                    fd = self._tf.get(fk)
                    if fd is None:
                        fd = Transform(p, xysize=(width, height), alpha=0.55)
                        self._tf[fk] = fd
                    r.blit(renpy.render(fd, width, height, st, at),
                           (sx + random.randint(-30, 30), sy + random.randint(-30, 30)))

            if danger > 0.05:
                self._solid(r, "#ff0033", 0.30 * danger, st, at)
            if self.flash > 0:
                self._solid(r, "#ffffff", self.flash, st, at)

            # ---- объекты ----
            R = int(height * NM_R)
            i = self.i0
            n = len(self.objs)
            while i < n:
                o = self.objs[i]
                if o["t"] > t + NM_AR:
                    break
                ty = o["type"]
                px = int(o["x"] * width) + sx
                py = int(o["y"] * height) + sy

                if ty == "circle":
                    if not o["judged"]:
                        prog = nm_clamp(1.0 - (o["t"] - t) / NM_AR, 0.0, 1.6)
                        self._ring(r, px, py, int(R * (1.0 + 2.2 * (1.0 - prog))),
                                   (255, 255, 255, 150), 4, st, at)
                        self._ring(r, px, py, R, (18, 8, 26, 235), 0, st, at)
                        self._ring(r, px, py, R, (255, 60, 120, 255), 6, st, at)
                        self._ring(r, px, py, int(R * 0.55), (255, 210, 240, 220), 3, st, at)

                elif ty == "slider":
                    if t <= o["t"] + o["dur"]:
                        x2 = int(o["x2"] * width) + sx
                        y2 = int(o["y2"] * height) + sy
                        self._line(r, px, py, x2, y2, (140, 60, 200, 170), R, st, at)
                        self._ring(r, px, py, R, (255, 60, 120, 255), 5, st, at)
                        self._ring(r, x2, y2, R, (255, 60, 120, 255), 5, st, at)
                        if o["t"] <= t:
                            p = (t - o["t"]) / max(0.001, o["dur"])
                            bx = int((o["x"] + (o["x2"] - o["x"]) * p) * width) + sx
                            by = int((o["y"] + (o["y2"] - o["y"]) * p) * height) + sy
                            self._ring(r, bx, by, int(R * 0.7), (255, 255, 255, 255), 0, st, at)
                        else:
                            prog = nm_clamp(1.0 - (o["t"] - t) / NM_AR, 0.0, 1.0)
                            self._ring(r, px, py, int(R * (1.0 + 2.2 * (1.0 - prog))),
                                       (255, 255, 255, 150), 4, st, at)

                else:
                    if t <= o["t"] + o["dur"]:
                        cx0 = width // 2 + sx
                        cy0 = height // 2 + sy
                        big = int(height * 0.30)
                        self._ring(r, cx0, cy0, big, (255, 255, 255, 90), 5, st, at)
                        self._ring(r, cx0, cy0, int(big * o["fill"]),
                                   (255, 90, 160, 210), 0, st, at)
                        self._text(r, u"ДЕРЖИ", cx0, cy0 - int(big * 0.5), 54, "#ffffff", st, at)
                i += 1

            # ---- всплески ----
            keep = []
            for s in self.rings:
                s[2] += dt
                p = s[2] / 0.35
                if p < 1.0:
                    self._ring(r, int(s[0] * width) + sx, int(s[1] * height) + sy,
                               int(R * (1.0 + p * 1.6)),
                               (255, 255, 255, int(200 * (1.0 - p))), 4, st, at)
                    keep.append(s)
            self.rings = keep[-24:]

            keep = []
            for p in self.pops:
                p[4] += dt
                if p[4] < 0.6:
                    self._text(r, p[0], int(p[2] * width) + sx,
                               int(p[3] * height) + sy - int(R * 1.6) - int(p[4] * 60),
                               40, p[1], st, at)
                    keep.append(p)
            self.pops = keep[-16:]

            # ---- шкала температуры ----
            bw = int(width * 0.5)
            bh = 26
            bx = (width - bw) // 2
            by = int(height * 0.055)
            frac = nm_clamp((self.temp - NM_TEMP_MIN) / (NM_TEMP_MAX - NM_TEMP_MIN), 0.0, 1.0)
            try:
                hud = renpy.Render(bw + 8, bh + 8)
                hc = hud.canvas()
                hc.rect((14, 8, 20, 235), (0, 0, bw + 8, bh + 8))
                hc.rect((90, 30, 40, 255), (4, 4, bw, bh))
                hc.rect(nm_temp_color(self.temp), (4, 4, max(3, int(bw * frac)), bh))
                mid = int(bw * (NM_START_TEMP - NM_TEMP_MIN) / (NM_TEMP_MAX - NM_TEMP_MIN))
                hc.rect((255, 255, 255, 120), (4 + mid, 0, 2, bh + 8))
                r.blit(hud, (bx - 4 + sx, by - 4 + sy))
            except Exception:
                pass

            self._text(r, u"%.1f°" % self.temp, width / 2 + sx, by + bh + 34,
                       58, "#ffffff", st, at)

            if self.combo > 2:
                self._text(r, u"%d x" % self.combo, width / 2 + sx,
                           int(height * 0.86), 46, "#ffffff", st, at)

            left = max(0.0, self.duration - t)
            if left <= NM_RUSH_TIME and self.result is None:
                self._text(r, u"%.1f" % left, width / 2 + sx, int(height * 0.42),
                           int(150 + 60 * beat), "#ff2b3d", st, at)

            renpy.redraw(self, 0)
            return r


# ==========================================================
# Экран и запуск
# ==========================================================

screen nightmare_screen():
    modal True
    zorder 300
    default nm = NightmareGame()
    add nm
    timer 0.05 repeat True action If(nm.result is not None, Return(nm.result))


label nightmare:

    $ quick_menu = False
    scene black with slowfade
    call card_timed("Он уснул", 3.0)

    $ _nm = renpy.call_screen("nightmare_screen")

    $ renpy.music.stop(channel="music", fadeout=1.0)
    scene black with Fade(0.6, 0.4, 1.2)

    if _nm == "burn":
        "Сорок пять. Он горел изнутри, и мир побелел."
    else:
        "Двадцать шесть. Холод забрался под кожу, и всё стало тихо."

    $ quick_menu = True
    return
