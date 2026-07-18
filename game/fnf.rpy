# game/fnf.rpy - FNF (arrow sprites + texture cache + DLC+)
init python:
    import random, math
    try:
        import pygame_sdl2 as pygame
    except ImportError:
        import pygame

    NAMES = {0: "left", 1: "down", 2: "up", 3: "right"}
    FNF_KEYS = {
        pygame.K_d: 0, pygame.K_LEFT: 0,
        pygame.K_f: 1, pygame.K_DOWN: 1,
        pygame.K_j: 2, pygame.K_UP: 2,
        pygame.K_k: 3, pygame.K_RIGHT: 3,
    }


    def fnf_demo_chart(difficulty="normal", bpm=150.0):
        cfg = {"easy": (10, 3, 3), "normal": (14, 3, 4), "hard": (16, 4, 5)}
        bars, lo, hi = cfg.get(difficulty, cfg["normal"])
        spb = 60000.0 / bpm
        chart, rng, last = [], random.Random(7), []
        for bar in range(bars):
            side = 0 if bar % 2 == 0 else 1
            if side == 0:
                slots = sorted(rng.sample(range(8), rng.randint(lo, hi)))
                pat = [(s, rng.randint(0, 3)) for s in slots]
                last = pat
            else:
                pat = list(last)
            for (s, lane) in pat:
                chart.append({"t": (bar * 4 + s * 0.5) * spb, "lane": lane, "side": side,
                              "judged": False, "hit": False})
        return chart


    class FNFGame(renpy.Displayable):
        def __init__(self, difficulty="normal", song=None, bpm=150.0, leadin=3000, **kw):
            renpy.Displayable.__init__(self, **kw)
            self.song, self.leadin = song, leadin
            self.chart = fnf_demo_chart(difficulty, bpm)
            self.approach = {"easy": 1500.0, "normal": 1150.0, "hard": 880.0}.get(difficulty, 1150.0)
            self.started = None
            self.music_started = False
            self.health, self.score, self.combo, self.maxcombo = 1.0, 0, 0, 0
            self.counts = {"sick": 0, "good": 0, "bad": 0, "miss": 0}
            self.result = None
            self.lights = [0.0, 0.0, 0.0, 0.0]
            self.olights = [0.0, 0.0, 0.0, 0.0]
            self.popups = []
            self.lastt = max([n["t"] for n in self.chart]) if self.chart else 0
            self._w, self._h = 1280, 720
            self.note = {l: "images/fnf/note_%s.png" % NAMES[l] for l in range(4)}
            self.rec = {l: "images/fnf/rec_%s.png" % NAMES[l] for l in range(4)}
            self._tf = {}
            self._td = {}
            self._px = [0, 0, 0, 0]
            self._recy_p = 0

        def _tf_get(self, path, zoom):
            key = (path, round(zoom, 3))
            d = self._tf.get(key)
            if d is None:
                d = Transform(path, zoom=zoom)
                self._tf[key] = d
            return d

        def _blit_img(self, r, path, cx, cy, zoom, st, at):
            cr = renpy.render(self._tf_get(path, zoom), self._w, self._h, st, at)
            cw, ch = cr.get_size()
            r.blit(cr, (int(cx - cw / 2), int(cy - ch / 2)))

        def _text(self, r, s, x, y, size, col, st, at):
            key = (s, size, col)
            d = self._td.get(key)
            if d is None:
                d = Text(s, size=size, color=col, outlines=[(2, "#000000cc", 0, 0)])
                self._td[key] = d
            cr = renpy.render(d, self._w, self._h, st, at)
            tw, th = cr.get_size()
            r.blit(cr, (int(x - tw / 2), int(y)))

        def songpos(self, st):
            return (st - self.started) * 1000.0

        def press(self, lane, sp):
            self.lights[lane] = 0.11
            best, bd = None, 99999
            for n in self.chart:
                if n["side"] != 1 or n["judged"] or n["lane"] != lane:
                    continue
                d = abs(n["t"] - sp)
                if d < bd:
                    bd, best = d, n
            if best is not None and bd <= 170:
                best["judged"] = best["hit"] = True
                if bd <= 45:
                    j = "sick"; self.score += 350
                elif bd <= 95:
                    j = "good"; self.score += 200
                else:
                    j = "bad"; self.score += 100
                self.counts[j] += 1
                self.combo += 1
                self.maxcombo = max(self.maxcombo, self.combo)
                self.health = min(2.0, self.health + 0.023)
                self.popups.append([j, 0.0, lane])

        def render(self, width, height, st, at):
            self._w, self._h = width, height
            if self.started is None:
                self.started = st + self.leadin / 1000.0
            sp = self.songpos(st)
            r = renpy.Render(width, height)

            r.blit(renpy.render(im.Scale("images/fnf/bg.png", width, height), width, height, st, at), (0, 0))

            recy_p, recy_o = int(height * 0.82), int(height * 0.15)
            zp = (height * 0.17) / 160.0
            zo = (height * 0.115) / 160.0
            px = [int(width * (0.5 + (i - 1.5) * 0.13)) for i in range(4)]
            ox = [int(width * (0.10 + i * 0.072)) for i in range(4)]
            scroll = recy_p / self.approach
            self._px, self._recy_p = px, recy_p

            if self.song and not self.music_started and sp >= 0:
                self.music_started = True
                try:
                    renpy.music.play(self.song, channel="music", loop=False)
                except Exception:
                    pass

            for lane in range(4):
                self._blit_img(r, (self.note[lane] if self.olights[lane] > 0 else self.rec[lane]), ox[lane], recy_o, zo, st, at)
                self._blit_img(r, (self.note[lane] if self.lights[lane] > 0 else self.rec[lane]), px[lane], recy_p, zp, st, at)

            if self.result is None:
                for n in self.chart:
                    if n["judged"]:
                        continue
                    if n["side"] == 1:
                        y = recy_p - (n["t"] - sp) * scroll
                        if -70 <= y <= recy_p + 46:
                            self._blit_img(r, self.note[n["lane"]], px[n["lane"]], int(y), zp, st, at)
                    else:
                        y = recy_o - (n["t"] - sp) * scroll
                        if -70 <= y <= height + 70:
                            self._blit_img(r, self.note[n["lane"]], ox[n["lane"]], int(y), zo, st, at)

            bw, bh = int(width * 0.44), 20
            bx, by = (width - bw) // 2, int(height * 0.055)
            hud = renpy.Render(bw + 8, bh + 8)
            hc = hud.canvas()
            hc.rect((18, 10, 26, 255), (0, 0, bw + 8, bh + 8))
            hc.rect((198, 66, 92, 255), (4, 4, bw, bh))
            pw = int(bw * (self.health / 2.0))
            hc.rect((92, 206, 112, 255), (4 + bw - pw, 4, max(2, pw), bh))
            r.blit(hud, (bx - 4, by - 4))

            tot = sum(self.counts.values())
            acc = int(round((self.counts["sick"] + self.counts["good"] * 0.66 + self.counts["bad"] * 0.33) / tot * 100)) if tot else 100
            self._text(r, u"Score  %d      \u0422\u043e\u0447\u043d\u043e\u0441\u0442\u044c  %d%%" % (self.score, acc), width / 2, by + bh + 6, 26, "#ffffff", st, at)
            if self.combo > 1:
                self._text(r, u"%d x" % self.combo, width / 2, int(height * 0.40), 46, "#ffffff", st, at)
            for p in self.popups:
                lab = {"sick": "SICK!", "good": "GOOD", "bad": "BAD", "miss": "MISS"}[p[0]]
                colr = {"sick": "#5cd6ff", "good": "#5cd67a", "bad": "#e8c454", "miss": "#e75660"}[p[0]]
                self._text(r, lab, px[p[2]], int(recy_p - 78 - p[1] * 26), 30, colr, st, at)
            if sp < 0:
                lab = "GO!" if -sp < 260 else str(int(-sp / 1000) + 1)
                self._text(r, lab, width / 2, int(height * 0.42), 100, "#ffffff", st, at)

            if self.result is not None:
                over = renpy.Render(width, height)
                oc = over.canvas()
                oc.rect((10, 6, 16, 255), (0, 0, width, height))
                r.blit(over, (0, 0))
                title = u"\u041f\u041e\u0411\u0415\u0414\u0410!" if self.result == "clear" else u"\u041f\u0420\u041e\u0412\u0410\u041b"
                self._text(r, title, width / 2, int(height * 0.30), 70, "#5cd67a" if self.result == "clear" else "#e75660", st, at)
                self._text(r, u"Score  %d      \u041c\u0430\u043a\u0441. \u043a\u043e\u043c\u0431\u043e  %d" % (self.score, self.maxcombo), width / 2, int(height * 0.46), 30, "#ffffff", st, at)
                self._text(r, u"\u043a\u043e\u0441\u043d\u0438\u0441\u044c \u044d\u043a\u0440\u0430\u043d\u0430, \u0447\u0442\u043e\u0431\u044b \u0432\u044b\u0439\u0442\u0438", width / 2, int(height * 0.56), 26, "#ffd0d8", st, at)

            dt = 0.016
            for i in range(4):
                if self.lights[i] > 0:
                    self.lights[i] -= dt
                if self.olights[i] > 0:
                    self.olights[i] -= dt
            for p in self.popups:
                p[1] += dt
            self.popups = [p for p in self.popups if p[1] <= 0.55]

            if self.result is None and sp >= 0:
                for n in self.chart:
                    if n["side"] == 0 and not n["judged"] and sp >= n["t"]:
                        n["judged"] = n["hit"] = True
                        self.olights[n["lane"]] = 0.11
                    if n["side"] == 1 and not n["judged"] and sp > n["t"] + 170:
                        n["judged"] = True
                        self.combo = 0
                        self.health = max(0.0, self.health - 0.045)
                        self.counts["miss"] += 1
                        self.popups.append(["miss", 0.0, n["lane"]])
                if self.health <= 0:
                    self.result = "fail"
                    try:
                        renpy.music.stop(channel="music")
                    except Exception:
                        pass
                elif sp > self.lastt + 2200:
                    self.result = "clear"
                    try:
                        renpy.music.stop(channel="music")
                    except Exception:
                        pass

            renpy.redraw(self, 0)
            return r

        def event(self, ev, x, y, st):
            if self.started is None:
                return None
            sp = self.songpos(st)
            if self.result is not None:
                if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    try:
                        renpy.music.stop(channel="music")
                    except Exception:
                        pass
                    return self.score
                return None
            if ev.type == pygame.KEYDOWN and ev.key in FNF_KEYS:
                self.press(FNF_KEYS[ev.key], sp)
                raise renpy.IgnoreEvent()
            if ev.type == pygame.MOUSEBUTTONDOWN and y > self._h * 0.58:
                lane = min(range(4), key=lambda i: abs(x - self._px[i]))
                self.press(lane, sp)
                raise renpy.IgnoreEvent()
            return None

screen fnf_levels():
    add Solid("#160f1f")
    vbox:
        align (0.5, 0.5)
        spacing 22
        text "DLC+  —  выбор уровня" size 54 color "#ff5da2" xalign 0.5
        textbutton "Лёгкий" action Return("easy") xalign 0.5 text_size 40
        textbutton "Нормальный" action Return("normal") xalign 0.5 text_size 40
        textbutton "Сложный" action Return("hard") xalign 0.5 text_size 40
        null height 20
        textbutton "Назад" action Return(None) xalign 0.5 text_size 30


label dlc_plus:
    $ quick_menu = False
    scene expression Solid("#141018")
    call screen fnf_levels
    $ _diff = _return
    if _diff:
        call fnf_battle(_diff)
        $ _sc = _return
        scene expression Solid("#141018")
        "Уровень пройден! Твои очки: [_sc]"
        jump dlc_plus
    return


label fnf_battle(difficulty="normal"):
    window hide
    $ quick_menu = False
    # song: FNFGame(difficulty=difficulty, song="audio/fnf_song.ogg")
    $ ui.add(FNFGame(difficulty=difficulty, song=None))
    $ _fnf_score = ui.interact(suppress_overlay=True, suppress_underlay=True)
    $ quick_menu = True
    window auto
    return _fnf_score
