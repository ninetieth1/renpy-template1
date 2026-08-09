# ==========================================================
# game/intro.rpy
# Девяностые (c) MR LIMBO
# Интро -> загрузка -> приветственная плашка "зажми и держи"
#
# ВАЖНО: механика удержания переписана на кастомный
# displayable HoldGate. Старая версия считала прогресс через
# hovered/unhovered, из-за чего полоска ползла от простого
# наведения мыши на ПК и намертво залипала на тачскрине.
# Теперь ловятся реальные события нажатия/отпускания:
# мышь, палец (touch) и пробел/Enter.
# ==========================================================

define MY_INTRO_VIDEO = "video/intro.webm"

# Сколько секунд крутится "ЗАГРУЗКА..." после видео
define MY_LOAD_SECONDS = 5.0

# Сколько секунд надо ДЕРЖАТЬ, чтобы плашка исчезла
define MY_HOLD_SECONDS = 5.0

# ===== Текст приветствия (показывается один раз, при запуске игры) =====
define MY_TEXT_AFTER_LOAD = _(u"""Привет, мой дорогой друг.

Я очень рад, что ты заглянул в мой проект, и искренне благодарен тебе за это.

Буду рад ещё больше, если после прохождения ты оставишь отзыв: честный и без прикрас.

Приятной игры.""")

# Тексты перед новой игрой и перед DLC убраны по задаче.
# Пустые строки оставлены намеренно: если где-то в сюжете остался
# вызов my_disclaimer, он просто ничего не покажет и не сломает игру.
define MY_TEXT_BEFORE_GAME = ""
define MY_TEXT_BEFORE_DLC = ""


# ==========================================================
# HoldGate: "зажми и держи" (мышь / палец / пробел)
# ==========================================================

init -1 python:

    import pygame_sdl2 as _pg

    class HoldGate(renpy.Displayable):
        """
        Панель или полный экран с механикой удержания.
        Возвращает True, когда игрок продержал duration секунд.

        message    - крупный текст по центру (None = только полоска)
        duration   - сколько держать, в секундах
        hint       - подпись над полоской
        width/height - фиксированный размер (для встраивания в vbox)
        local_only - считать удержание только внутри своей области
                     (нужно, чтобы не мешать перетаскиванию/скроллу)
        """

        def __init__(self, message=None, duration=5.0,
                     hint=u"ЗАЖМИ И ДЕРЖИ", text_size=38,
                     width=None, height=None, local_only=False,
                     accent="#00b3ff", bg=None, **kwargs):

            super(HoldGate, self).__init__(**kwargs)

            self.message = message
            self.duration = max(0.2, float(duration))
            self.hint = hint
            self.text_size = text_size
            self.fixed_width = width
            self.fixed_height = height
            self.local_only = local_only
            self.accent = accent
            self.bg = bg

            self.progress = 0.0
            self.holding = False
            self.last_st = None
            self.box = (0, 0)
            self.done = False
            self._cache = None

        # ---------- отрисовка ----------

        def _message_text(self, w):
            if self._cache is None or self._cache[0] != w:
                t = Text(self.message, size=self.text_size, color="#eaeaea",
                         text_align=0.5, line_spacing=8, xsize=int(w * 0.82))
                self._cache = (w, t)
            return self._cache[1]

        def render(self, width, height, st, at):

            w = int(self.fixed_width or width)
            h = int(self.fixed_height or height)
            self.box = (w, h)

            if self.last_st is None:
                self.last_st = st
            dt = max(0.0, st - self.last_st)
            self.last_st = st

            if self.holding:
                self.progress = min(1.0, self.progress + dt / self.duration)
            else:
                # отпустил: полоска плавно откатывается назад
                self.progress = max(0.0, self.progress - dt / (self.duration * 0.5))

            r = renpy.Render(w, h)

            if self.bg is not None:
                r.blit(renpy.render(Solid(self.bg), w, h, st, at), (0, 0))

            if self.message:
                mr = renpy.render(self._message_text(w), int(w * 0.82), h, st, at)
                mw, mh = mr.get_size()
                r.blit(mr, (int((w - mw) / 2), int(h * 0.38 - mh / 2)))

            hint_color = self.accent if self.holding else "#8c99a6"
            hr = renpy.render(
                Text(self.hint, size=max(20, int(self.text_size * 0.62)),
                     color=hint_color, kerning=3),
                w, h, st, at)
            hw, hh = hr.get_size()

            bar_w = int(w * 0.46)
            bar_h = 8
            bar_x = int((w - bar_w) / 2)

            if self.fixed_height:
                hint_y = int(h * 0.12)
                bar_y = int(h * 0.66)
            else:
                hint_y = int(h * 0.74)
                bar_y = int(h * 0.83)

            r.blit(hr, (int((w - hw) / 2), hint_y))
            r.blit(renpy.render(Solid("#ffffff1f"), bar_w, bar_h, st, at), (bar_x, bar_y))

            fill = int(bar_w * self.progress)
            if fill > 0:
                r.blit(renpy.render(Solid(self.accent), fill, bar_h, st, at), (bar_x, bar_y))

            renpy.redraw(self, 0)

            if self.holding:
                renpy.timeout(0.03)

            return r

        # ---------- ввод ----------

        def _inside(self, x, y):
            if not self.local_only:
                return True
            w, h = self.box
            return (0 <= x <= w) and (0 <= y <= h)

        def event(self, ev, x, y, st):

            if self.done:
                return None

            keys = (_pg.K_SPACE, _pg.K_RETURN, _pg.K_KP_ENTER)

            down = getattr(_pg, "MOUSEBUTTONDOWN", None)
            up = getattr(_pg, "MOUSEBUTTONUP", None)
            fdown = getattr(_pg, "FINGERDOWN", None)
            fup = getattr(_pg, "FINGERUP", None)

            if down is not None and ev.type == down and getattr(ev, "button", 1) == 1:
                self.holding = self._inside(x, y)
            elif up is not None and ev.type == up and getattr(ev, "button", 1) == 1:
                self.holding = False
            elif fdown is not None and ev.type == fdown:
                self.holding = self._inside(x, y)
            elif fup is not None and ev.type == fup:
                self.holding = False
            elif ev.type == _pg.KEYDOWN and getattr(ev, "key", None) in keys:
                self.holding = True
            elif ev.type == _pg.KEYUP and getattr(ev, "key", None) in keys:
                self.holding = False

            if self.progress >= 1.0:
                self.done = True
                return True

            if not self.local_only:
                raise renpy.IgnoreEvent()

            return None


# ==========================================================
# Запуск игры: видео -> загрузка -> приветствие -> музыка меню
# ==========================================================

label splashscreen:

    if renpy.loadable(MY_INTRO_VIDEO):
        $ renpy.movie_cutscene(MY_INTRO_VIDEO)

    scene expression Solid("#000000")

    show screen my_loading
    $ renpy.pause(MY_LOAD_SECONDS, hard=True)
    hide screen my_loading

    call screen my_hold_text(MY_TEXT_AFTER_LOAD)

    play music "audio/menu.mp3" fadein 1.0
    return


transform my_blink:
    linear 0.6 alpha 0.3
    linear 0.6 alpha 1.0
    repeat


screen my_loading():
    add Solid("#000000")
    text "ЗАГРУЗКА..." xalign 0.5 yalign 0.5 size 44 color "#ffffff" at my_blink


screen my_hold_text(txt=""):
    modal True
    zorder 250

    add HoldGate(
        txt,
        MY_HOLD_SECONDS,
        hint=u"ЗАЖМИ И ДЕРЖИ, ЧТОБЫ ПРОДОЛЖИТЬ",
        text_size=(46 if renpy.variant("small") else 38),
        bg="#000000")


# ===== Чёрный экран с текстом (оставлен для совместимости) =====
label my_disclaimer(txt=""):
    if not txt:
        return
    scene expression Solid("#000000")
    "[txt]"
    return
