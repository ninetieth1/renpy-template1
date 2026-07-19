# ==========================================================
# game/fnf.rpy — FNF мини-игра (DLC+)
# ФИКСЫ:
#  [1] Фон геймплея ВСЕГДА images/fnf/bg.png (все 8 треков)
#  [2] Колонки нормального размера, GF реально сидит на них
#  [3] Музыка играет ДО КОНЦА песни, победа после конца музыки
#  [4] Экран выбора трека в стиле оригинала (жёлтая полоса, WEEK 1)
#  [5] Провал больше не пишет "Трек пройден", счёт недели сохраняется
#  ВАЖНО: удалить game/fnf_fix.rpy — он больше не нужен!
# ==========================================================

init python:
    import random, math, json
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

    FNF_TITLES = [
        u"Привет",
        u"Общение",
        u"Феноменально",
        u"Поговорим?",
        u"Всё невозможное — возможно",
        u"Договоримся?",
        u"Что?",
        u"МЫ СНОВА ВМЕСТЕ?",
    ]

    def fnf_track_title(i):
        if 0 <= i < len(FNF_TITLES):
            return FNF_TITLES[i]
        return u"?"

    def fnf_tracks_unlocked():
        try:
            return 8 if persistent.fnf_unlocked8 else 7
        except Exception:
            return 7

    def fnf_on_clear(track, score=0):
        try:
            cl = list(persistent.fnf_cleared or [])
            if int(track) not in cl:
                cl.append(int(track))
                persistent.fnf_cleared = cl
            if all(i in cl for i in range(7)):
                persistent.fnf_unlocked8 = True
            # лучший счёт за трек
            sc = dict(persistent.fnf_scores or {})
            if int(score) > int(sc.get(int(track), 0)):
                sc[int(track)] = int(score)
                persistent.fnf_scores = sc
        except Exception:
            pass

    def fnf_week_score():
        try:
            return sum((persistent.fnf_scores or {}).values())
        except Exception:
            return 0

    def fnf_sfx(name):
        try:
            p = "audio/%s.ogg" % name
            if renpy.loadable(p):
                renpy.sound.play(p, channel="sound")
        except Exception:
            pass

    # Трансформ "подогнать картинку под нужную высоту в пикселях"
    def fnf_fit(path, th):
        try:
            w, h = renpy.image_size(path)
            if h:
                return Transform(path, zoom=float(th) / float(h))
        except Exception:
            pass
        return Transform(path)

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

    def fnf_load_chart(track, difficulty="normal", bpm=150.0):
        path = "charts/s%d.json" % (track + 1)
        if renpy.loadable(path):
            try:
                f = renpy.open_file(path)
                raw = f.read()
                try:
                    f.close()
                except Exception:
                    pass
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                data = json.loads(raw)
                bpm2 = float(data.get("bpm", bpm))
                notes = []
                for it in data.get("notes", []):
                    notes.append({"t": float(it[0]), "lane": int(it[1]) % 4,
                                  "side": int(it[2]) % 2, "judged": False, "hit": False})
                if notes:
                    notes.sort(key=lambda n: n["t"])
                    return notes, bpm2
            except Exception:
                pass
        return fnf_demo_chart(difficulty, bpm), bpm

    class FNFGame(renpy.Displayable):
        def __init__(self, track=0, song=None, difficulty="normal", bpm=150.0, leadin=3000, **kw):
            renpy.Displayable.__init__(self, **kw)
            self.track = int(track)
            self.song = song
            self.title = fnf_track_title(self.track)
            self.qmode = (self.track == 6)
            self.chart, self.bpm = fnf_load_chart(self.track, difficulty, bpm)
            self.bpm = float(self.bpm)
            self.leadin = 2600.0
            self.intro_done = False
            self.approach = {"easy": 1500.0, "normal": 1150.0, "hard": 880.0}.get(difficulty, 1150.0)
            self.started = None
            self.music_started = False
            self.music_ok = False
            self.health, self.score, self.combo, self.maxcombo = 1.0, 0, 0, 0
            self.counts = {"sick": 0, "good": 0, "bad": 0, "miss": 0}
            self.result = None
            self.lights = [0.0, 0.0, 0.0, 0.0]
            self.olights = [0.0, 0.0, 0.0, 0.0]
            self.popups = []
            self.splash = []
            self.flash = 0.0
            self.lastt = max([n["t"] for n in self.chart]) if self.chart else 0
            self._w, self._h = 1280, 720
            self.note = {l: "images/fnf/note_%s.png" % NAMES[l] for l in range(4)}
            self.rec = {l: "images/fnf/rec_%s.png" % NAMES[l] for l in range(4)}
            # ФИКС [1]: фон всегда bg.png, без per-track фонов
            self.bgp = "images/fnf/bg.png"
            self.chars = {
                "op": ("images/fnf/char_opponent.png", 0.20, 0.64),
                "gf": ("images/fnf/char_gf.png", 0.50, 0.38),
                "bf": ("images/fnf/char_player.png", 0.80, 0.64),
            }
            self.sing = {"op": [0, 0.0], "bf": [0, 0.0]}
            self._imgc = {}
            self._nath = {}
            self._tf = {}
            self._td = {}
            self._px = [0, 0, 0, 0]
            self._recy_p = 0
            self._lastst = None
            self._spk = {}
            self._gf_foot = None

        def _tf_get(self, path, zoom, flip=False):
            key = (path, round(zoom, 3), flip)
            d = self._tf.get(key)
            if d is None:
                if flip:
                    d = Transform(path, zoom=zoom, xzoom=-1)
                else:
                    d = Transform(path, zoom=zoom)
                self._tf[key] = d
            return d

        def _blit_img(self, r, path, cx, cy, zoom, st, at):
            cr = renpy.render(self._tf_get(path, zoom), self._w, self._h, st, at)
            cw, ch = cr.get_size()
            r.blit(cr, (int(cx - cw / 2), int(cy - ch / 2)))

        def _char_path(self, key):
            base = self.chars[key][0]
            s = self.sing.get(key)
            if s and s[1] > 0:
                dirp = base[:-4] + "_" + NAMES[s[0]] + ".png"
                if renpy.loadable(dirp):
                    return dirp
            return base

        def _pulse(self, sp):
            spb = 60000.0 / self.bpm
            phase = (sp % spb) / spb if sp > 0 else 0.0
            return 1.0 + 0.05 * round(1.0 - phase, 2)

        def _blit_char(self, r, key, sp, st, at):
            base_path, xf, hf = self.chars[key]
            path = self._char_path(key)
            if not renpy.loadable(path):
                return
            img = self._imgc.get(path)
            if img is None:
                img = Image(path)
                self._imgc[path] = img
            nh = self._nath.get(path)
            if nh is None:
                nh = renpy.render(img, self._w, self._h, st, at).get_size()[1]
                self._nath[path] = nh
            if not nh:
                return
            z = (self._h * hf) / float(nh) * self._pulse(sp)
            cr = renpy.render(self._tf_get(path, z), self._w, self._h, st, at)
            cw, ch = cr.get_size()
            dx, dy = 0, 0
            s = self.sing.get(key)
            if s and s[1] > 0 and path == base_path:
                off = int(self._h * 0.03 * (s[1] / 0.30))
                lane = s[0]
                if lane == 0:
                    dx = -off
                elif lane == 3:
                    dx = off
                elif lane == 2:
                    dy = -off
                elif lane == 1:
                    dy = off
            if key == "gf" and self._gf_foot is not None:
                foot = self._gf_foot
            else:
                foot = int(self._h * 0.90)
            r.blit(cr, (int(self._w * xf - cw / 2) + dx, int(foot - ch) + dy))

        def _blit_icon(self, r, path, cx, cy, th, st, at):
            if not renpy.loadable(path):
                return
            img = self._imgc.get(path)
            if img is None:
                img = Image(path)
                self._imgc[path] = img
            nh = self._nath.get(path)
            if nh is None:
                nh = renpy.render(img, self._w, self._h, st, at).get_size()[1]
                self._nath[path] = nh
            if not nh:
                return
            z = th / float(nh)
            cr = renpy.render(self._tf_get(path, z), self._w, self._h, st, at)
            cw, ch = cr.get_size()
            r.blit(cr, (int(cx - cw / 2), int(cy - ch / 2)))

        def _blit_speakers(self, r, st, at):
            # ФИКС [2]: колонки масштабируются по ВЫСОТЕ (26% экрана),
            # а не по ширине — раньше на телефоне они были гигантскими,
            # и GF улетала за верх экрана.
            self._gf_foot = int(self._h * 0.90)
            path = "images/fnf/speakers.png"
            if not renpy.loadable(path):
                return
            img = self._imgc.get(path)
            if img is None:
                img = Image(path)
                self._imgc[path] = img
            sz = self._spk.get(path)
            if sz is None:
                sz = renpy.render(img, self._w, self._h, st, at).get_size()
                self._spk[path] = sz
            nw, nh = sz
            if not nw or not nh:
                return
            z = (self._h * 0.26) / float(nh)
            cr = renpy.render(self._tf_get(path, z), self._w, self._h, st, at)
            cw, ch = cr.get_size()
            bottom = int(self._h * 0.95)
            top = bottom - ch
            r.blit(cr, (int(self._w * 0.5 - cw / 2), top))
            # GF садится на верх колонок (небольшой нахлёст)
            self._gf_foot = top + int(self._h * 0.04)

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

        def _play_intro(self):
            try:
                if renpy.loadable("audio/intro.ogg"):
                    renpy.sound.play("audio/intro.ogg", channel="sound")
            except Exception:
                pass

        def _play_sfx(self, name):
            try:
                p = "audio/%s.ogg" % name
                if renpy.loadable(p):
                    renpy.sound.play(p, channel="sound")
            except Exception:
                pass

        def press(self, lane, sp):
            self.lights[lane] = 0.11
            best, bd = None, 99999
            for n in self.chart:
                if n["side"] != 1 or n["judged"] or n["lane"] != lane:
                    continue
                d = abs(n["t"] - sp)
                if d < bd:
                    bd, best = d, n
            if best is not None and bd <= 205:
                best["judged"] = best["hit"] = True
                self.sing["bf"] = [lane, 0.30]
                if bd <= 60:
                    j = "sick"; self.score += 350; self.flash = 0.10
                elif bd <= 125:
                    j = "good"; self.score += 200
                else:
                    j = "bad"; self.score += 100
                self.counts[j] += 1
                self.combo += 1
                self.maxcombo = max(self.maxcombo, self.combo)
                self.health = min(2.0, self.health + 0.023)
                self.popups.append([j, 0.0, lane])
                self.splash.append([lane, 0.0])

        def render(self, width, height, st, at):
            self._w, self._h = width, height
            if self.started is None:
                self.started = st + self.leadin / 1000.0
            sp = self.songpos(st)
            r = renpy.Render(width, height)

            # ФИКС [1]: всегда bg.png
            if renpy.loadable(self.bgp):
                r.blit(renpy.render(im.Scale(self.bgp, width, height), width, height, st, at), (0, 0))
            else:
                bgr = renpy.Render(width, height)
                bgr.canvas().rect((22, 15, 31, 255), (0, 0, width, height))
                r.blit(bgr, (0, 0))

            self._blit_speakers(r, st, at)
            self._blit_char(r, "gf", sp, st, at)
            self._blit_char(r, "op", sp, st, at)
            self._blit_char(r, "bf", sp, st, at)

            if self.qmode:
                for key in ("op", "gf", "bf"):
                    xf = self.chars[key][1]
                    self._text(r, u"?", int(width * xf), int(height * 0.30), 150, "#ffffff", st, at)

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
                    self.music_ok = True
                except Exception:
                    self.music_ok = False

            for lane in range(4):
                self._blit_img(r, (self.note[lane] if self.olights[lane] > 0 else self.rec[lane]), ox[lane], recy_o, zo, st, at)
                self._blit_img(r, (self.note[lane] if self.lights[lane] > 0 else self.rec[lane]), px[lane], recy_p, zp, st, at)

            for s in self.splash:
                prog = s[1] / 0.32
                if prog >= 1.0:
                    continue
                rad = int((0.018 + prog * 0.055) * height)
                alpha = int(210 * (1.0 - prog))
                dd = rad * 2 + 8
                try:
                    ring = renpy.Render(dd, dd)
                    ring.canvas().circle((255, 255, 255, alpha), (dd // 2, dd // 2), rad, 4)
                    r.blit(ring, (px[s[0]] - dd // 2, recy_p - dd // 2))
                except Exception:
                    pass

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

            if self.flash > 0:
                try:
                    fr = renpy.Render(width, height)
                    av = int(70 * (self.flash / 0.10))
                    if av < 0:
                        av = 0
                    elif av > 255:
                        av = 255
                    fr.canvas().rect((255, 255, 255, av), (0, 0, width, height))
                    r.blit(fr, (0, 0))
                except Exception:
                    pass

            bw, bh = int(width * 0.44), 20
            bx, by = (width - bw) // 2, int(height * 0.055)
            hud = renpy.Render(bw + 8, bh + 8)
            hc = hud.canvas()
            hc.rect((18, 10, 26, 255), (0, 0, bw + 8, bh + 8))
            hc.rect((198, 66, 92, 255), (4, 4, bw, bh))
            pw = int(bw * (self.health / 2.0))
            hc.rect((92, 206, 112, 255), (4 + bw - pw, 4, max(2, pw), bh))
            r.blit(hud, (bx - 4, by - 4))
            ih = int(height * 0.12)
            self._blit_icon(r, "images/fnf/icon_opponent.png", bx + 4, by + bh / 2, ih, st, at)
            self._blit_icon(r, "images/fnf/icon_player.png", bx + bw - 4, by + bh / 2, ih, st, at)
            self._text(r, self.title, width / 2, int(height * 0.012), 24, "#ffd0d8", st, at)

            tot = sum(self.counts.values())
            acc = int(round((self.counts["sick"] + self.counts["good"] * 0.66 + self.counts["bad"] * 0.33) / tot * 100)) if tot else 100
            self._text(r, u"Score %d  Точность %d%%" % (self.score, acc), width / 2, by + bh + 6, 26, "#ffffff", st, at)
            if self.combo > 1:
                self._text(r, u"%d x" % self.combo, width / 2, int(height * 0.40), 46, "#ffffff", st, at)
            for p in self.popups:
                lab = {"sick": "SICK!", "good": "GOOD", "bad": "BAD", "miss": "MISS"}[p[0]]
                colr = {"sick": "#5cd6ff", "good": "#5cd67a", "bad": "#e8c454", "miss": "#e75660"}[p[0]]
                self._text(r, lab, px[p[2]], int(recy_p - 78 - p[1] * 26), 30, colr, st, at)
            if sp < 0:
                frac = (-sp) / self.leadin
                if frac > 0.75:
                    lab = u"3"
                elif frac > 0.5:
                    lab = u"2"
                elif frac > 0.25:
                    lab = u"1"
                else:
                    lab = u"GO!"
                if not self.intro_done:
                    self.intro_done = True
                    self._play_intro()
                self._text(r, lab, width / 2, int(height * 0.42), 100, "#ffffff", st, at)

            if self.result is not None:
                over = renpy.Render(width, height)
                over.canvas().rect((10, 6, 16, 220), (0, 0, width, height))
                r.blit(over, (0, 0))
                title = u"ПОБЕДА!" if self.result == "clear" else u"ПРОВАЛ"
                self._text(r, title, width / 2, int(height * 0.30), 70, "#5cd67a" if self.result == "clear" else "#e75660", st, at)
                self._text(r, u"Score %d  Макс. комбо %d" % (self.score, self.maxcombo), width / 2, int(height * 0.46), 30, "#ffffff", st, at)
                self._text(r, u"коснись экрана, чтобы выйти", width / 2, int(height * 0.56), 26, "#ffd0d8", st, at)

            if self._lastst is None:
                self._lastst = st
            dt = st - self._lastst
            self._lastst = st
            if dt < 0:
                dt = 0.0
            elif dt > 0.05:
                dt = 0.05
            for i in range(4):
                if self.lights[i] > 0:
                    self.lights[i] -= dt
                if self.olights[i] > 0:
                    self.olights[i] -= dt
            for k in self.sing:
                if self.sing[k][1] > 0:
                    self.sing[k][1] -= dt
            for p in self.popups:
                p[1] += dt
            self.popups = [p for p in self.popups if p[1] <= 0.55]
            for s in self.splash:
                s[1] += dt
            self.splash = [s for s in self.splash if s[1] <= 0.32]
            if self.flash > 0:
                self.flash = max(0.0, self.flash - dt)

            if self.result is None and sp >= 0:
                for n in self.chart:
                    if n["side"] == 0 and not n["judged"] and sp >= n["t"]:
                        n["judged"] = n["hit"] = True
                        self.olights[n["lane"]] = 0.11
                        self.sing["op"] = [n["lane"], 0.30]
                    if n["side"] == 1 and not n["judged"] and sp > n["t"] + 205:
                        n["judged"] = True
                        self.combo = 0
                        self.health = max(0.0, self.health - 0.045)
                        self.counts["miss"] += 1
                        self.popups.append(["miss", 0.0, n["lane"]])
                if self.health <= 0:
                    self.result = "fail"
                    self._play_sfx("sfx_fail")
                    try:
                        renpy.music.stop(channel="music")
                    except Exception:
                        pass
                else:
                    # ФИКС [3]: победа только когда ПЕСНЯ доиграла до конца,
                    # а не через 2.2 сек после последней ноты чарта.
                    done = False
                    if self.song and self.music_ok:
                        if self.music_started and sp > 2000:
                            try:
                                done = renpy.music.get_playing(channel="music") is None
                            except Exception:
                                done = False
                    else:
                        done = sp > self.lastt + 2200
                    if done:
                        self.result = "clear"
                        fnf_on_clear(self.track, self.score)
                        self._play_sfx("sfx_win")
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
                    # ФИКС [5]: возвращаем и результат, и очки
                    return (self.result, self.score)
                return None
            if ev.type == pygame.KEYDOWN and ev.key in FNF_KEYS:
                self.press(FNF_KEYS[ev.key], sp)
                raise renpy.IgnoreEvent()
            if ev.type == pygame.MOUSEBUTTONDOWN and y > self._h * 0.58:
                lane = min(range(4), key=lambda i: abs(x - self._px[i]))
                self.press(lane, sp)
                raise renpy.IgnoreEvent()
            return None

transform fnf_pulse:
    ease 0.4 zoom 1.0
    ease 0.4 zoom 1.06
    repeat

# ==========================================================
# ФИКС [4]: экран выбора трека в стиле оригинального FNF
# Чёрный фон, жёлтая полоса с персонажами, GF на колонках,
# большое название трека, НЕДЕЛЯ 1, список треков слева.
# ==========================================================
screen fnf_week():
    tag menu
    default sel = 0
    $ _nu = fnf_tracks_unlocked()
    $ _h = config.screen_height
    $ _ws = fnf_week_score()
    $ _band_top = int(_h * 0.08)
    $ _band_h = int(_h * 0.52)
    $ _band_bot = _band_top + _band_h
    $ _feet = _band_bot - int(_h * 0.02)
    $ _spk_h = int(_band_h * 0.42)

    add Solid("#000000")

    # --- Жёлтая полоса ---
    frame:
        xfill True
        ypos _band_top
        ysize _band_h
        background Solid("#f2c14e")

    # --- Персонажи на жёлтой полосе ---
    if renpy.loadable("images/fnf/char_opponent.png"):
        add fnf_fit("images/fnf/char_opponent.png", int(_band_h * 0.78)) xpos 0.16 xanchor 0.5 ypos _feet yanchor 1.0
    if renpy.loadable("images/fnf/char_player.png"):
        add fnf_fit("images/fnf/char_player.png", int(_band_h * 0.85)) xpos 0.45 xanchor 0.5 ypos _feet yanchor 1.0
    # Колонки + GF сидит на них
    if renpy.loadable("images/fnf/speakers.png"):
        add fnf_fit("images/fnf/speakers.png", _spk_h) xpos 0.79 xanchor 0.5 ypos _feet yanchor 1.0
    if renpy.loadable("images/fnf/char_gf.png"):
        add fnf_fit("images/fnf/char_gf.png", int(_band_h * 0.50)) xpos 0.79 xanchor 0.5 ypos (_feet - _spk_h + int(_h * 0.02)) yanchor 1.0

    # --- Верхняя чёрная шапка ---
    text "WEEK SCORE: [_ws]" xpos 20 ypos 8 size 32 color "#ffffff"

    # --- Большое название трека ---
    text fnf_track_title(sel):
        xalign 0.5
        ypos int(_h * 0.655)
        size 64
        color "#ffffff"
        outlines [ (4, "#000000", 0, 0) ]
        at fnf_pulse

    # --- ◄ НОРМАЛ ► справа ---
    hbox:
        xalign 0.97
        ypos int(_h * 0.66)
        spacing 6
        textbutton "◄":
            text_size 48
            text_color "#5ce1e6"
            text_hover_color "#ffffff"
            action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel - 1) % _nu)]
        text "НОРМАЛ" size 44 color "#ffd23f" outlines [ (3, "#000000", 0, 0) ] yalign 0.5
        textbutton "►":
            text_size 48
            text_color "#5ce1e6"
            text_hover_color "#ffffff"
            action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel + 1) % _nu)]

    # --- НЕДЕЛЯ 1 ---
    text "НЕДЕЛЯ 1":
        xalign 0.5
        ypos int(_h * 0.775)
        size 80
        color "#cccccc"
        outlines [ (5, "#000000", 0, 0) ]

    # --- Список треков слева ---
    vbox:
        xpos 0.04
        ypos int(_h * 0.66)
        spacing 2
        text "ТРЕКИ" size 26 color "#ff5da2"
        for i in range(8):
            if i < _nu:
                text ("%d. %s" % (i + 1, fnf_track_title(i))) size 18 color ("#ffffff" if i == sel else "#9a8fb0")
            else:
                text ("%d. ???" % (i + 1)) size 18 color "#555555"

    # --- Кнопка ИГРАТЬ ---
    textbutton "ИГРАТЬ":
        xalign 0.5
        yalign 0.97
        xysize (360, 66)
        background Solid("#2e7d43")
        hover_background Solid("#46cc72")
        text_size 40
        text_color "#ffffff"
        text_xalign 0.5
        text_yalign 0.5
        action [Function(fnf_sfx, "sfx_confirm"), Return(sel)]

    # --- Назад ---
    textbutton "◄ Назад":
        xalign 0.99
        ypos 6
        text_size 24
        text_color "#ffd0d8"
        text_hover_color "#ffffff"
        action [Function(fnf_sfx, "sfx_cancel"), MainMenu(confirm=False)]

    key "K_LEFT" action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel - 1) % _nu)]
    key "K_RIGHT" action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel + 1) % _nu)]
    key "K_RETURN" action [Function(fnf_sfx, "sfx_confirm"), Return(sel)]

label dlc_plus:
    $ quick_menu = False
    call screen fnf_week
    $ _ti = _return
    if _ti is not None:
        call fnf_battle(_ti)
        $ _res = _return
        scene expression Solid("#141018")
        # ФИКС [5]: провал больше не пишет "Трек пройден"
        if _res[0] == "clear":
            "ПОБЕДА! Очки: [_res[1]]"
        else:
            "Провал... Очки: [_res[1]]"
    jump dlc_plus

label fnf_battle(track=0):
    window hide
    $ quick_menu = False
    stop music fadeout 0.5
    $ _sng = "audio/s%d.ogg" % (track + 1)
    if not renpy.loadable(_sng):
        $ _sng = None
    $ ui.add(FNFGame(track=track, song=_sng))
    $ _fnf_res = ui.interact(suppress_overlay=True, suppress_underlay=True)
    $ quick_menu = True
    window auto
    return _fnf_res
