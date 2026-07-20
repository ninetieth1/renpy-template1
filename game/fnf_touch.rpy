# ==========================================================
# game/fnf_touch.rpy — МУЛЬТИТАЧ (опрос пальцев каждый кадр)
# Новый отдельный файл. В fnf.rpy ничего менять не нужно.
# ==========================================================

init 999 python:
    try:
        from pygame_sdl2 import touch as _fnf_touch
    except Exception:
        _fnf_touch = None

    if _fnf_touch is not None:

        def _fnf_poll_fingers(self):
            pts = []
            try:
                nd = _fnf_touch.get_num_devices()
            except Exception:
                return pts
            for di in range(nd):
                try:
                    dev = _fnf_touch.get_device(di)
                    for fi in range(_fnf_touch.get_num_fingers(dev)):
                        f = _fnf_touch.get_finger(dev, fi)
                        if f:
                            pts.append((float(f.get("x", 0.5)) * self._w,
                                        float(f.get("y", 0.5)) * self._h))
                except Exception:
                    continue
            return pts

        def _fnf_mt_update(self, sp):
            pts = self._poll_fingers()
            self._dbg_fd = len(pts)
            if pts:
                self._touch = True
            cur = set()
            on4 = False
            for (fx, fy) in pts:
                if self._in_btnq(fx, fy):
                    self._mt_quit = True
                    continue
                if self._in_btn4(fx, fy):
                    on4 = True
                    cur.update((0, 1, 2, 3))
                    continue
                if fy > self._h * FNF_TOUCH_TOP:
                    lane = min(range(4), key=lambda i: abs(fx - self._px[i]))
                    cur.add(lane)
            if on4:
                self._btnlit = 0.15
            prev = getattr(self, "_mt_prev", set())
            for lane in cur - prev:
                self.down[lane] = True
                self.press(lane, sp)
            for lane in prev - cur:
                self.down[lane] = False
            self._mt_prev = cur

        FNFGame._poll_fingers = _fnf_poll_fingers
        FNFGame._mt_update = _fnf_mt_update

        _fnf_render_orig = FNFGame.render
        def _fnf_render_mt(self, width, height, st, at):
            self._w, self._h = width, height
            if (self.started is not None and self.result is None
                    and self._btn4[2] > 0):
                try:
                    self._mt_update(self.songpos(st))
                except Exception:
                    pass
            return _fnf_render_orig(self, width, height, st, at)
        FNFGame.render = _fnf_render_mt

        _fnf_event_orig = FNFGame.event
        def _fnf_event_mt(self, ev, x, y, st):
            if getattr(self, "_mt_quit", False) and self.result is None:
                self._mt_quit = False
                return self._quit_game()
            return _fnf_event_orig(self, ev, x, y, st)
        FNFGame.event = _fnf_event_mt
