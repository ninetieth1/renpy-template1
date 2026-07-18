# game/fnf.rpy — FNF, встроенный в Ren'Py (стрелки как в FNF)
init python:
    import random, math
    try:
        import pygame_sdl2 as pygame
    except ImportError:
        import pygame

    FNF_RGB = [(199,72,220),(66,196,232),(106,214,120),(231,86,96)]
    FNF_KEYS = {
        pygame.K_d:0, pygame.K_LEFT:0,
        pygame.K_f:1, pygame.K_DOWN:1,
        pygame.K_j:2, pygame.K_UP:2,
        pygame.K_k:3, pygame.K_RIGHT:3,
    }
    FNF_ANG = {0:270, 1:180, 2:0, 3:90}

    def fnf_demo_chart(difficulty="normal", bpm=150.0):
        cfg = {"easy":(10,3,3), "normal":(14,3,4), "hard":(16,4,5)}
        bars, lo, hi = cfg.get(difficulty, cfg["normal"])
        spb = 60000.0/bpm
        chart, rng, last = [], random.Random(7), []
        for bar in range(bars):
            side = 0 if bar % 2 == 0 else 1
            if side == 0:
                slots = sorted(rng.sample(range(8), rng.randint(lo,hi)))
                pat = [(s, rng.randint(0,3)) for s in slots]; last = pat
            else:
                pat = list(last)
            for (s,lane) in pat:
                chart.append({"t":(bar*4+s*0.5)*spb, "lane":lane, "side":side,
                              "judged":False, "hit":False})
        return chart

    class FNFGame(renpy.Displayable):
        def __init__(self, difficulty="normal", song=None, bpm=150.0, leadin=3000, **kw):
            renpy.Displayable.__init__(self, **kw)
            self.bpm, self.song, self.leadin = bpm, song, leadin
            self.chart = fnf_demo_chart(difficulty, bpm)
            self.approach = {"easy":1450.0,"normal":1100.0,"hard":850.0}.get(difficulty,1100.0)
            self.started = None
            self.music_started = False
            self.health, self.score, self.combo, self.maxcombo = 1.0, 0, 0, 0
            self.counts = {"sick":0,"good":0,"bad":0,"miss":0}
            self.result = None
            self.lights = [0.0,0.0,0.0,0.0]
            self.olights = [0.0,0.0,0.0,0.0]
            self.popups = []
            self.lastt = max([n["t"] for n in self.chart]) if self.chart else 0
            self._w, self._h = 1280, 720

        def songpos(self, st):
            return (st - self.started) * 1000.0

        def _arrow(self, canvas, lane, cx, cy, s, filled):
            ang = math.radians(FNF_ANG[lane])
            base = [(0,-s),(-s,-s*0.18),(-s*0.42,-s*0.18),(-s*0.42,s),
                    (s*0.42,s),(s*0.42,-s*0.18),(s,-s*0.18)]
            ca, sa = math.cos(ang), math.sin(ang)
            pts = [(int(cx+x*ca-y*sa), int(cy+x*sa+y*ca)) for (x,y) in base]
            col = FNF_RGB[lane]
            if filled:
                canvas.polygon(col+(255,), pts)
                canvas.polygon((25,12,35,255), pts, 4)
            else:
                dim = tuple(int(v*0.55) for v in col)
                canvas.polygon(dim+(255,), pts, 6)

        def _text(self, r, s, x, y, size, col, st, at):
            tr = renpy.render(Text(s, size=size, color=col), self._w, self._h, st, at)
            tw, th = tr.get_size()
            r.blit(tr, (int(x-tw/2), int(y)))

        def press(self, lane, sp):
            self.lights[lane] = 0.12
            best, bd = None, 99999
            for n in self.chart:
                if n["side"] != 1 or n["judged"] or n["lane"] != lane: continue
                d = abs(n["t"]-sp)
                if d < bd: bd, best = d, n
            if best is not None and bd <= 170:
                best["judged"] = best["hit"] = True
                if bd <= 45: r = "sick"; self.score += 350
                elif bd <= 95: r = "good"; self.score += 200
                else: r = "bad"; self.score += 100
                self.counts[r] += 1; self.combo += 1
                self.maxcombo = max(self.maxcombo, self.combo)
                self.health = min(2.0, self.health + 0.023)
                self.popups.append([r, 0.0, lane])

        def render(self, width, height, st, at):
            self._w, self._h = width, height
            if self.started is None:
                self.started = st + self.leadin/1000.0
            sp = self.songpos(st)
            r = renpy.Render(width, height)
            canvas = r.canvas()

            for i,c in enumerate([(58,42,106),(138,74,122),(200,90,85),(255,138,74)]):
                canvas.rect(c+(255,), (0, i*(height//4), width, height//4+2))

            if self.song and not self.music_started and sp >= 0:
                self.music_started = True
                try: renpy.music.play(self.song, channel="music", loop=False)
                except Exception: pass

            recy_p, recy_o = int(height*0.84), int(height*0.14)
            px = [int(width*f) for f in (0.31,0.45,0.60,0.74)]
            ox = [int(width*f) for f in (0.11,0.18,0.25,0.32)]
            scroll = recy_p/self.approach

            for lane in range(4):
                self._arrow(canvas, lane, ox[lane], recy_o, 22, self.olights[lane] > 0)
                self._arrow(canvas, lane, px[lane], recy_p, 38, self.lights[lane] > 0)

            if self.result is None:
                for n in self.chart:
                    if n["judged"]: continue
                    if n["side"] == 1:
                        y = recy_p-(n["t"]-sp)*scroll
                        if -80 <= y <= height+80:
                            self._arrow(canvas, n["lane"], px[n["lane"]], int(y), 38, True)
                    else:
                        y = recy_o-(n["t"]-sp)*scroll
                        if -80 <= y <= height+80:
                            self._arrow(canvas, n["lane"], ox[n["lane"]], int(y), 22, True)

            bw, bh = int(width*0.42), 22
            bx, by = (width-bw)//2, int(height*0.05)
            canvas.rect((20,12,28,255), (bx-4,by-4,bw+8,bh+8))
            canvas.rect((192,64,90,255), (bx,by,bw,bh))
            pw = int(bw*(self.health/2.0))
            canvas.rect((87,200,106,255), (bx+bw-pw,by,max(1,pw),bh))

            if self.result is not None:
                canvas.rect((10,6,16,235), (0,0,width,height))

            tot = sum(self.counts.values())
            acc = int(round((self.counts["sick"]+self.counts["good"]*0.66+self.counts["bad"]*0.33)/tot*100)) if tot else 100
            self._text(r, u"Score: %d    Точность: %d%%" % (self.score,acc), width/2, by+bh+8, 26, "#ffffff", st, at)
            if self.combo > 1:
                self._text(r, str(self.combo), width/2, int(height*0.42), 44, "#ffffffdd", st, at)
            for p in self.popups:
                a = max(0.0, 1.0-p[1]/0.6)
                lab = {"sick":"SICK!","good":"GOOD","bad":"BAD","miss":"MISS"}[p[0]]
                base = {"sick":"#6ad6ff","good":"#6ad678","bad":"#e8c454","miss":"#e75660"}[p[0]]
                self._text(r, lab, px[p[2]], int(recy_p-70-p[1]*30), 30, base+("%02x"%int(a*255)), st, at)
            if sp < 0:
                lab = "GO!" if -sp < 250 else str(int(-sp/1000)+1)
                self._text(r, lab, width/2, int(height/2-48), 96, "#ffffff", st, at)
            if self.result is not None:
                title = u"ПОБЕДА!" if self.result == "clear" else u"ПРОВАЛ"
                self._text(r, title, width/2, int(height*0.30), 64, "#6ad678" if self.result == "clear" else "#e75660", st, at)
                self._text(r, u"Score: %d   Комбо: %d   —   коснись, чтобы выйти" % (self.score,self.maxcombo), width/2, int(height*0.46), 28, "#ffffff", st, at)

            dt = 0.016
            for i in range(4):
                if self.lights[i] > 0: self.lights[i] -= dt
                if self.olights[i] > 0: self.olights[i] -= dt
            for p in self.popups: p[1] += dt
            self.popups = [p for p in self.popups if p[1] <= 0.6]

            if self.result is None and sp >= 0:
                for n in self.chart:
                    if n["side"] == 0 and not n["judged"] and sp >= n["t"]:
                        n["judged"] = n["hit"] = True; self.olights[n["lane"]] = 0.12
                    if n["side"] == 1 and not n["judged"] and sp > n["t"]+170:
                        n["judged"] = True; self.combo = 0
                        self.health = max(0.0, self.health-0.045)
                        self.counts["miss"] += 1; self.popups.append(["miss",0.0,n["lane"]])
                if self.health <= 0:
                    self.result = "fail"
                    try: renpy.music.stop(channel="music")
                    except Exception: pass
                elif sp > self.lastt+2200:
                    self.result = "clear"
                    try: renpy.music.stop(channel="music")
                    except Exception: pass

            renpy.redraw(self, 0)
            return r

        def event(self, ev, x, y, st):
            if self.started is None: return None
            sp = self.songpos(st)
            if self.result is not None:
                if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    try: renpy.music.stop(channel="music")
                    except Exception: pass
                    return self.score
                return None
            if ev.type == pygame.KEYDOWN and ev.key in FNF_KEYS:
                self.press(FNF_KEYS[ev.key], sp); raise renpy.IgnoreEvent()
            if ev.type == pygame.MOUSEBUTTONDOWN and y > self._h*0.66:
                lane = max(0, min(3, int(x/(self._w/4.0))))
                self.press(lane, sp); raise renpy.IgnoreEvent()
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
    # со своей песней: FNFGame(difficulty=difficulty, song="audio/fnf_song.ogg")
    $ ui.add(FNFGame(difficulty=difficulty, song=None))
    $ _fnf_score = ui.interact(suppress_overlay=True, suppress_underlay=True)
    $ quick_menu = True
    window auto
    return _fnf_score
