# ==========================================================
# game/fnf.rpy — FNF мини-игра (DLC+) v3
# - Читает НАСТОЯЩИЙ формат чартов s1..s8.json (difficulties/normal/notes,
#   t в секундах, hold = зажимные стрелки, fake пропускаются)
# - Меню: карусель треков по центру, все персонажи ровно, GF на колонках
# - Последовательная разблокировка треков, "душит" на треках 6-8
# - Оптимизация под слабые телефоны (Samsung A20)
# ВАЖНО: файла game/fnf_fix.rpy быть НЕ должно!
# ==========================================================

define config.image_cache_size_mb = 256

init python:
    import random, json
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

    # ===== НАСТРОЙКИ ВИЗУАЛА (крути эти числа, если спрайты с прозрачными полями) =====
    FNF_SPK_H = 0.26         # высота колонок в геймплее (доля экрана)
    FNF_GF_OVERLAP = 0.055   # насколько GF "усажена" в колонки в геймплее
    FNF_MENU_CH_H = 0.80     # рост Игрока/Соперника в меню (доля жёлтой полосы)
    FNF_MENU_GF_H = 0.50     # рост GF в меню
    FNF_MENU_SPK_H = 0.40    # высота колонок в меню
    FNF_MENU_GF_OVER = 0.045 # насколько GF "усажена" в колонки в меню (доля экрана)

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

    LANE_COLS = {0: "#c24b99cc", 1: "#00d8ffcc", 2: "#3df05ccc", 3: "#f9393fcc"}

    def fnf_track_title(i):
        if 0 <= i < len(FNF_TITLES):
            return FNF_TITLES[i]
        return u"?"

    def fnf_cleared(i):
        try:
            return int(i) in set(persistent.fnf_cleared or [])
        except Exception:
            return False

    # Последовательная разблокировка: открыт трек N+1, где N подряд пройдено
    def fnf_tracks_open():
        n = 0
        while n < 8 and fnf_cleared(n):
            n += 1
        return min(8, n + 1)

    def fnf_best(i):
        try:
            return int((persistent.fnf_scores or {}).get(int(i), 0))
        except Exception:
            return 0

    def fnf_week_score():
        try:
            return sum((persistent.fnf_scores or {}).values())
        except Exception:
            return 0

    def fnf_on_clear(track, score=0):
        try:
            cl = list(persistent.fnf_cleared or [])
            if int(track) not in cl:
                cl.append(int(track))
                persistent.fnf_cleared = cl
            sc = dict(persistent.fnf_scores or {})
            if int(score) > int(sc.get(int(track), 0)):
                sc[int(track)] = int(score)
                persistent.fnf_scores = sc
        except Exception:
            pass

    def fnf_sfx(name):
        try:
            p = "audio/%s.ogg" % name
            if renpy.loadable(p):
                renpy.sound.play(p, channel="sound")
        except Exception:
            pass

    # Подгон картинки под высоту в пикселях
    def fnf_fit(path, th):
        try:
            w, h = renpy.image_size(path)
            if h:
                return Transform(path, zoom=float(th) / float(h))
        except Exception:
            pass
        return Transform(path)

    def fnf_demo_chart(bpm=150.0):
        spb = 60000.0 / bpm
        chart, rng, last = [], random.Random(7), []
        for bar in range(14):
            side = 0 if bar % 2 == 0 else 1
            if side == 0:
                slots = sorted(rng.sample(range(8), rng.randint(3, 4)))
                pat = [(s, rng.randint(0, 3)) for s in slots]
                last = pat
            else:
                pat = list(last)
            for (s, lane) in pat:
                chart.append({"t": (bar * 4 + s * 0.5) * spb, "lane": lane, "side": side,
                              "sus": 0.0, "judged": False, "hit": False})
        return chart

    # ФИКС: читаем РЕАЛЬНЫЙ формат чартов
    # { "bpm": 97, "difficulties": { "normal": { "notes": [
    #     {"t": сек, "lane": 0-3, "side": "player"/"opponent", "hold": сек, "fake": bool} ] } } }
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
                diffs = data.get("difficulties") or {}
                d = diffs.get(difficulty) or diffs.get("normal")
                if d is None and diffs:
                    d = list(diffs.values())[0]
                if d:
                    for it in d.get("notes", []):
                        try:
                            if it.get("fake"):
                                continue
                            notes.append({
                                "t": float(it.get("t", 0.0)) * 1000.0,
                                "lane": int(it.get("lane", 0)) % 4,
                                "side": 1 if it.get("side") == "player" else 0,
                                "sus": max(0.0, float(it.get("hold", 0) or 0)) * 1000.0,
                                "judged": False, "hit": False,
                            })
                        except Exception:
                            continue
                if not notes:
                    # старый простой формат на всякий случай
                    for it in data.get("notes", []):
                        notes.append({"t": float(it[0]), "lane": int(it[1]) % 4,
                                      "side": int(it[2]) % 2, "sus": 0.0,
                                      "judged": False, "hit": False})
                if notes:
                    notes.sort(key=lambda n: n["t"])
                    return notes, bpm2, True
            except Exception:
                pass
        return fnf_demo_chart(bpm), bpm, False

    class FNFGame(renpy.Displayable):
        def __init__(self, track=0, song=None, difficulty="normal", bpm=150.0, **kw):
            renpy.Displayable.__init__(self, **kw)
            self.track = int(track)
            self.song = song
            self.title = fnf_track_title(self.track)
            self.qmode = (self.track == 6)
            self.qdrain = (self.track >= 5)   # "ДУШИТ" на треках 6-8
            self.chart, self.bpm, self.chart_real = fnf_load_chart(self.track, difficulty, bpm)
            self.bpm = float(self.bpm)
            self.leadin = 2600.0
            self.intro_done = False
            self.approach = 1150.0
            self.started = None
            self.music_started = False
            self.music_ok = False
            self.health, self.score, self.combo, self.maxcombo = 1.0, 0, 0, 0
            self.counts = {"sick": 0, "good": 0, "bad": 0, "miss": 0}
            self.result = None
            self.lights = [0.0, 0.0, 0.0, 0.0]
            self.olights = [0.0, 0.0, 0.0, 0.0]
            self.down = [False, False, False, False]
            self.holds = {}    # lane -> время конца зажатой ноты (игрок)
            self.oholds = {}   # lane -> время конца (соперник)
            self.popups = []
            self.splash = []
            self.flash = 0.0
            self.lastt = max([n["t"] + n["sus"] for n in self.chart]) if self.chart else 0
            self._w, self._h = 1280, 720
            self.note = {l: "images/fnf/note_%s.png" % NAMES[l] for l in range(4)}
            self.rec = {l: "images/fnf/rec_%s.png" % NAMES[l] for l in range(4)}
            self.bgp = "images/fnf/bg.png"   # фон ВСЕГДА bg.png
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
            self._i0 = 0
            self._lastst = None
            self._spk = {}
            self._gf_foot = None
            self._mlane = None

        # Предзагрузка текстур (меньше фризов на старте)
        def visit(self):
            out = []
            paths = list(self.note.values()) + list(self.rec.values())
            paths += [self.bgp, "images/fnf/speakers.png",
                      "images/fnf/icon_opponent.png", "images/fnf/icon_player.png"]
            paths += [c[0] for c in self.chars.values()]
            for key in self.chars:
                for d in NAMES.values():
                    paths.append(self.chars[key][0][:-4] + "_" + d + ".png")
            for p in paths:
                if renpy.loadable(p):
                    img = self._imgc.get(p)
                    if img is None:
                        img = Image(p)
                        self._imgc[p] = img
                    out.append(img)
            return out

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

        def _char_path(self, key):
            base = self.chars[key][0]
            s = self.sing.get(key)
            if s and s[1] > 0:
                dirp = base[:-4] + "_" + NAMES[s[0]] + ".png"
                if renpy.loadable(dirp):
                    return dirp
            return base

        # Пульс квантован в 7 ступеней — меньше уникальных текстур, меньше лагов
        def _pulse(self, sp):
            if sp <= 0:
                return 1.0
            spb = 60000.0 / self.bpm
            phase = (sp % spb) / spb
            return 1.0 + 0.01 * int(6 * (1.0 - phase))

        def _nat_h(self, path, st, at):
            nh = self._nath.get(path)
            if nh is None:
                img = self._imgc.get(path)
                if img is None:
                    img = Image(path)
                    self._imgc[path] = img
                nh = renpy.render(img, self._w, self._h, st, at).get_size()[1]
                self._nath[path] = nh
            return nh

        def _blit_char(self, r, key, sp, st, at):
            base_path, xf, hf = self.chars[key]
            path = self._char_path(key)
            if not renpy.loadable(path):
                return
            nh = self._nat_h(path, st, at)
            if not nh:
                return
            # Игрок НЕ пульсирует, соперник и GF — пульсируют
            pulse = 1.0 if key == "bf" else self._pulse(sp)
            z = (self._h * hf) / float(nh) * pulse
            cr = renpy.render(self._tf_get(path, z), self._w, self._h, st, at)
            cw, ch = cr.get_size()
            dx, dy = 0, 0
            s = self.sing.get(key)
            if s and s[1] > 0 and path == base_path:
                # Соперник дёргается заметнее (0.06), игрок мягче (0.03)
                amp = 0.06 if key == "op" else 0.03
                off = int(self._h * amp * (s[1] / 0.30))
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
            nh = self._nat_h(path, st, at)
            if not nh:
                return
            self._blit_img(r, path, cx, cy, th / float(nh), st, at)

        def _blit_speakers(self, r, sp, st, at):
            self._gf_foot = int(self._h * 0.90)
            path = "images/fnf/speakers.png"
            if not renpy.loadable(path):
                return
            sz = self._spk.get(path)
            if sz is None:
                img = self._imgc.get(path)
                if img is None:
                    img = Image(path)
                    self._imgc[path] = img
                sz = renpy.render(img, self._w, self._h, st, at).get_size()
                self._spk[path] = sz
            nw, nh = sz
            if not nw or not nh:
                return
            # Колонки пульсируют вместе с музыкой
            z = (self._h * FNF_SPK_H) / float(nh) * self._pulse(sp)
            cr = renpy.render(self._tf_get(path, z), self._w, self._h, st, at)
            cw, ch = cr.get_size()
            bottom = int(self._h * 0.95)
            top = bottom - ch
            r.blit(cr, (int(self._w * 0.5 - cw / 2), top))
            # GF усажена на колонки
            self._gf_foot = top + int(self._h * FNF_GF_OVERLAP)

        def _text(self, r, s, x, y, size, col, st, at):
            key = (s, size, col)
            d = self._td.get(key)
            if d is None:
                d = Text(s, size=size, color=col, outlines=[(2, "#000000cc", 0, 0)])
                self._td[key] = d
            cr = renpy.render(d, self._w, self._h, st, at)
            tw, th = cr.get_size()
            r.blit(cr, (int(x - tw / 2), int(y)))

        # Хвост зажимной ноты (маленькие кэшированные полоски, дёшево)
        def _tail(self, r, x, y_top, y_bot, col, st, at):
            hgt = int(y_bot - y_top)
            if hgt <= 4:
                return
            w = max(8, int(self._w * 0.011))
            q = (hgt // 12 + 1) * 12
            key = ("tail", col, w, q)
            d = self._tf.get(key)
            if d is None:
                d = Transform(Solid(col), xysize=(w, q))
                self._tf[key] = d
            cr = renpy.render(d, self._w, self._h, st, at)
            r.blit(cr, (int(x - w / 2), int(max(-60, y_top))))

        def _solid(self, r, col, alpha_q, st, at):
            key = ("ovl", col, self._w, self._h, alpha_q)
            d = self._tf.get(key)
            if d is None:
                d = Transform(Solid(col), xysize=(self._w, self._h), alpha=alpha_q / 255.0)
                self._tf[key] = d
            r.blit(renpy.render(d, self._w, self._h, st, at), (0, 0))

        def songpos(self, st):
            return (st - self.started) * 1000.0

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
            i = self._i0
            n_len = len(self.chart)
            while i < n_len:
                n = self.chart[i]
                if n["t"] > sp + 300:
                    break
                if n["side"] == 1 and not n["judged"] and n["lane"] == lane:
                    d = abs(n["t"] - sp)
                    if d < bd:
                        bd, best = d, n
                i += 1
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
                self.splash.append([lane, 0.0, j])
                # Зажимная нота — начинаем удержание
                if best["sus"] > 0:
                    self.holds[lane] = best["t"] + best["sus"]

        def render(self, width, height, st, at):
            self._w, self._h = width, height
            if self.started is None:
                self.started = st + self.leadin / 1000.0
            sp = self.songpos(st)
            r = renpy.Render(width, height)

            # dt
            if self._lastst is None:
                self._lastst = st
            dt = st - self._lastst
            self._lastst = st
            if dt < 0:
                dt = 0.0
            elif dt > 0.05:
                dt = 0.05

            # Фон: кэшированный, всегда bg.png
            key = ("bg", width, height)
            d = self._tf.get(key)
            if d is None:
                if renpy.loadable(self.bgp):
                    d = Transform(self.bgp, xysize=(width, height))
                else:
                    d = Transform(Solid("#16101f"), xysize=(width, height))
                self._tf[key] = d
            r.blit(renpy.render(d, width, height, st, at), (0, 0))

            self._blit_speakers(r, sp, st, at)
            self._blit_char(r, "gf", sp, st, at)
            self._blit_char(r, "op", sp, st, at)
            self._blit_char(r, "bf", sp, st, at)

            if self.qmode:
                for ck in ("op", "gf", "bf"):
                    xf = self.chars[ck][1]
                    self._text(r, u"?", int(width * xf), int(height * 0.30), 150, "#ffffff", st, at)

            recy_p, recy_o = int(height * 0.82), int(height * 0.15)
            zp = (height * 0.17) / 160.0
            zo = (height * 0.115) / 160.0
            px = [int(width * (0.5 + (i - 1.5) * 0.13)) for i in range(4)]
            # ФИКС: дорожка соперника сдвинута влево, не залезает на игрока
            ox = [int(width * (0.06 + i * 0.062)) for i in range(4)]
            scroll = recy_p / self.approach
            self._px = px

            if self.song and not self.music_started and sp >= 0:
                self.music_started = True
                try:
                    renpy.music.play(self.song, channel="music", loop=False)
                    self.music_ok = True
                except Exception:
                    self.music_ok = False

            # Ресепторы (с "панчем" при нажатии — спецэффект)
            for lane in range(4):
                zzo = zo * (1.15 if self.olights[lane] > 0 else 1.0)
                zzp = zp * (1.18 if self.lights[lane] > 0 else 1.0)
                self._blit_img(r, (self.note[lane] if self.olights[lane] > 0 else self.rec[lane]), ox[lane], recy_o, zzo, st, at)
                self._blit_img(r, (self.note[lane] if self.lights[lane] > 0 else self.rec[lane]), px[lane], recy_p, zzp, st, at)

            # ===== ОДИН проход по видимому окну чарта (оптимизация) =====
            n_len = len(self.chart)
            while self._i0 < n_len:
                n = self.chart[self._i0]
                if n["judged"] and (n["t"] + n["sus"]) < sp - 600:
                    self._i0 += 1
                else:
                    break

            maxt = sp + self.approach + 600
            i = self._i0
            while i < n_len:
                n = self.chart[i]
                if n["t"] > maxt:
                    break
                lane = n["lane"]
                if n["side"] == 0:
                    # Соперник: автоигра
                    if self.result is None and sp >= 0 and not n["judged"] and sp >= n["t"]:
                        n["judged"] = n["hit"] = True
                        self.olights[lane] = 0.12
                        self.sing["op"] = [lane, 0.34]
                        if n["sus"] > 0:
                            self.oholds[lane] = n["t"] + n["sus"]
                        # ДУШИТ (треки 6-8): каждая нота соперника отжирает хп до 15%
                        if self.qdrain and self.health > 0.15:
                            self.health = max(0.15, self.health - 0.013)
                    # Хвост зажимной ноты соперника
                    if n["sus"] > 0 and (n["t"] + n["sus"]) > sp - 50:
                        y_head = recy_o if n["hit"] else recy_o - (n["t"] - sp) * scroll
                        y_end = recy_o - (n["t"] + n["sus"] - sp) * scroll
                        if not n["judged"] or n["hit"]:
                            self._tail(r, ox[lane], y_end, y_head, LANE_COLS[lane], st, at)
                    # Голова
                    if not n["judged"]:
                        y = recy_o - (n["t"] - sp) * scroll
                        if -70 <= y <= height + 70:
                            self._blit_img(r, self.note[lane], ox[lane], int(y), zo, st, at)
                else:
                    # Игрок: просрочка = мисс
                    if self.result is None and sp >= 0 and not n["judged"] and sp > n["t"] + 205:
                        n["judged"] = True
                        self.combo = 0
                        self.health = max(0.0, self.health - 0.045)
                        self.counts["miss"] += 1
                        self.popups.append(["miss", 0.0, lane])
                    # Хвост зажимной ноты игрока
                    if n["sus"] > 0 and (n["t"] + n["sus"]) > sp - 50:
                        if not n["judged"]:
                            y_head = recy_p - (n["t"] - sp) * scroll
                            y_end = recy_p - (n["t"] + n["sus"] - sp) * scroll
                            self._tail(r, px[lane], y_end, y_head, LANE_COLS[lane], st, at)
                        elif n["hit"] and lane in self.holds and self.holds[lane] > sp:
                            y_end = recy_p - (self.holds[lane] - sp) * scroll
                            self._tail(r, px[lane], y_end, recy_p, LANE_COLS[lane], st, at)
                    # Голова
                    if not n["judged"]:
                        y = recy_p - (n["t"] - sp) * scroll
                        if -70 <= y <= recy_p + 46:
                            self._blit_img(r, self.note[lane], px[lane], int(y), zp, st, at)
                i += 1

            # ===== Удержания игрока: буст очков и хп =====
            for lane in list(self.holds.keys()):
                end = self.holds[lane]
                if sp >= end:
                    del self.holds[lane]
                    self.score += 50
                elif not self.down[lane]:
                    del self.holds[lane]   # отпустил раньше — просто перестаёт капать
                else:
                    self.lights[lane] = max(self.lights[lane], 0.06)
                    self.sing["bf"] = [lane, max(self.sing["bf"][1], 0.15)]
                    self.score += int(220 * dt)
                    self.health = min(2.0, self.health + 0.02 * dt)

            # Удержания соперника: держит позу и подсветку
            for lane in list(self.oholds.keys()):
                if sp >= self.oholds[lane]:
                    del self.oholds[lane]
                else:
                    self.olights[lane] = max(self.olights[lane], 0.06)
                    self.sing["op"] = [lane, max(self.sing["op"][1], 0.15)]

            # Кольца при попадании (на SICK — двойное)
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
                    if s[2] == "sick":
                        rad2 = max(4, int(rad * 0.55))
                        dd2 = rad2 * 2 + 8
                        ring2 = renpy.Render(dd2, dd2)
                        ring2.canvas().circle((92, 214, 255, alpha), (dd2 // 2, dd2 // 2), rad2, 3)
                        r.blit(ring2, (px[s[0]] - dd2 // 2, recy_p - dd2 // 2))
                except Exception:
                    pass

            # Вспышка на SICK (кэшированная, без пересоздания поверхности)
            if self.flash > 0:
                av = int(70 * (self.flash / 0.10))
                self._solid(r, "#ffffff", max(12, (av // 12) * 12), st, at)

            # HUD
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
            # Название трека — ЖЁСТКО сверху
            self._text(r, self.title, width / 2, int(height * 0.012), 24, "#ffd0d8", st, at)
            if not self.chart_real:
                self._text(r, u"! ЧАРТ НЕ ПРОЧИТАН — ДЕМО !", int(width * 0.15), int(height * 0.012), 20, "#e75660", st, at)

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
                    try:
                        if renpy.loadable("audio/intro.ogg"):
                            renpy.sound.play("audio/intro.ogg", channel="sound")
                    except Exception:
                        pass
                self._text(r, lab, width / 2, int(height * 0.42), 100, "#ffffff", st, at)

            if self.result is not None:
                self._solid(r, "#0a0610", 216, st, at)
                title = u"ПОБЕДА!" if self.result == "clear" else u"ПРОВАЛ"
                self._text(r, title, width / 2, int(height * 0.30), 70, "#5cd67a" if self.result == "clear" else "#e75660", st, at)
                self._text(r, u"Score %d  Макс. комбо %d" % (self.score, self.maxcombo), width / 2, int(height * 0.46), 30, "#ffffff", st, at)
                self._text(r, u"коснись экрана, чтобы выйти", width / 2, int(height * 0.56), 26, "#ffd0d8", st, at)

            # Таймеры эффектов
            for i2 in range(4):
                if self.lights[i2] > 0:
                    self.lights[i2] -= dt
                if self.olights[i2] > 0:
                    self.olights[i2] -= dt
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

            # Конец трека / смерть
            if self.result is None and sp >= 0:
                if self.health <= 0:
                    self.result = "fail"
                    self._play_sfx("sfx_fail")
                    try:
                        renpy.music.stop(channel="music")
                    except Exception:
                        pass
                else:
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

            # Чистка кэшей — защита от утечек памяти и GC-фризов
            if len(self._td) > 400:
                self._td.clear()
            if len(self._tf) > 500:
                self._tf.clear()

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
                    return (self.result, self.score)
                return None
            if ev.type == pygame.KEYDOWN and ev.key in FNF_KEYS:
                lane = FNF_KEYS[ev.key]
                self.down[lane] = True
                self.press(lane, sp)
                raise renpy.IgnoreEvent()
            if ev.type == pygame.KEYUP and ev.key in FNF_KEYS:
                self.down[FNF_KEYS[ev.key]] = False
                return None
            if ev.type == pygame.MOUSEBUTTONDOWN and y > self._h * 0.58:
                lane = min(range(4), key=lambda i: abs(x - self._px[i]))
                self._mlane = lane
                self.down[lane] = True
                self.press(lane, sp)
                raise renpy.IgnoreEvent()
            if ev.type == pygame.MOUSEBUTTONUP:
                if self._mlane is not None:
                    self.down[self._mlane] = False
                    self._mlane = None
                return None
            return None

transform fnf_pulse:
    ease 0.4 zoom 1.0
    ease 0.4 zoom 1.06
    repeat

# ==========================================================
# Экран выбора трека: карусель ПО ЦЕНТРУ, без сложности и "НЕДЕЛЯ 1"
# ==========================================================
screen fnf_week():
    tag menu
    default sel = 0
    $ _h = config.screen_height
    $ _ws = fnf_week_score()
    $ _open = fnf_tracks_open()
    $ _locked = (sel >= _open)
    $ _num = sel + 1
    $ _best = fnf_best(sel)
    $ _band_top = int(_h * 0.08)
    $ _band_h = int(_h * 0.50)
    $ _feet = _band_top + _band_h - int(_h * 0.02)
    $ _spk_px = int(_band_h * FNF_MENU_SPK_H)
    $ _gf_bot = _feet - _spk_px + int(_h * FNF_MENU_GF_OVER)

    add Solid("#000000")

    # Жёлтая полоса
    frame:
        xfill True
        ypos _band_top
        ysize _band_h
        background Solid("#f2c14e")

    # Персонажи: ОДИНАКОВЫЙ рост, ОДНА линия ног
    if renpy.loadable("images/fnf/char_opponent.png"):
        add fnf_fit("images/fnf/char_opponent.png", int(_band_h * FNF_MENU_CH_H)) xpos 0.18 xanchor 0.5 ypos _feet yanchor 1.0
    if renpy.loadable("images/fnf/char_player.png"):
        add fnf_fit("images/fnf/char_player.png", int(_band_h * FNF_MENU_CH_H)) xpos 0.50 xanchor 0.5 ypos _feet yanchor 1.0
    if renpy.loadable("images/fnf/speakers.png"):
        add fnf_fit("images/fnf/speakers.png", _spk_px) xpos 0.82 xanchor 0.5 ypos _feet yanchor 1.0
    if renpy.loadable("images/fnf/char_gf.png"):
        add fnf_fit("images/fnf/char_gf.png", int(_band_h * FNF_MENU_GF_H)) xpos 0.82 xanchor 0.5 ypos _gf_bot yanchor 1.0

    # Шапка
    text "WEEK SCORE: [_ws]" xpos 24 ypos 10 size 38 color "#ffffff"
    textbutton "Назад":
        xalign 0.99
        ypos 6
        text_size 34
        text_color "#ffd0d8"
        text_hover_color "#ffffff"
        action [Function(fnf_sfx, "sfx_cancel"), MainMenu(confirm=False)]

    # Стрелки листания
    textbutton "◄":
        xpos 0.02
        ypos int(_h * 0.585)
        text_size 96
        text_color "#ffffff"
        text_hover_color "#ff5da2"
        action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel - 1) % 8)]
    textbutton "►":
        xalign 0.98
        ypos int(_h * 0.585)
        text_size 96
        text_color "#ffffff"
        text_hover_color "#ff5da2"
        action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel + 1) % 8)]

    # Название трека ПО ЦЕНТРУ, КРУПНО
    text (fnf_track_title(sel) if not _locked else "? ? ?"):
        xalign 0.5
        ypos int(_h * 0.60)
        size 76
        color ("#ffffff" if not _locked else "#777777")
        outlines [ (4, "#000000", 0, 0) ]
        at fnf_pulse

    # Статус трека
    text "Трек [_num] / 8":
        xalign 0.5
        ypos int(_h * 0.715)
        size 30
        color "#9a8fb0"
    if _locked:
        text "ЗАКРЫТО — сначала пройди трек [_open]":
            xalign 0.5
            ypos int(_h * 0.755)
            size 34
            color "#e75660"
    elif fnf_cleared(sel):
        text "ПРОЙДЕН — лучший счёт: [_best]":
            xalign 0.5
            ypos int(_h * 0.755)
            size 34
            color "#5cd67a"
    else:
        text "ОТКРЫТ — жми ИГРАТЬ":
            xalign 0.5
            ypos int(_h * 0.755)
            size 34
            color "#ffd23f"

    # Номера треков по центру (зелёный = пройден, серый = закрыт)
    hbox:
        xalign 0.5
        ypos int(_h * 0.815)
        spacing 30
        for i in range(8):
            textbutton ("%d" % (i + 1)):
                text_size (52 if i == sel else 40)
                text_color ("#5cd67a" if fnf_cleared(i) else ("#ffffff" if i < _open else "#555555"))
                text_hover_color "#ff5da2"
                action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", i)]

    # ИГРАТЬ
    if not _locked:
        textbutton "ИГРАТЬ":
            xalign 0.5
            yalign 0.975
            xysize (420, 80)
            background Solid("#2e7d43")
            hover_background Solid("#46cc72")
            text_size 46
            text_color "#ffffff"
            text_xalign 0.5
            text_yalign 0.5
            action [Function(fnf_sfx, "sfx_confirm"), Return(sel)]
    else:
        frame:
            xalign 0.5
            yalign 0.975
            xysize (420, 80)
            background Solid("#3a3a3a")
            text "ЗАКРЫТО" xalign 0.5 yalign 0.5 size 46 color "#777777"

    key "K_LEFT" action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel - 1) % 8)]
    key "K_RIGHT" action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel + 1) % 8)]
    key "K_RETURN" action (([Function(fnf_sfx, "sfx_confirm"), Return(sel)]) if not _locked else NullAction())

label dlc_plus:
    $ quick_menu = False
    call screen fnf_week
    $ _ti = _return
    if _ti is not None:
        call fnf_battle(_ti)
        $ _res = _return
        scene expression Solid("#141018")
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
