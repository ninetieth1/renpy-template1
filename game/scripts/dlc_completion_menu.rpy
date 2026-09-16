# ==========================================================
# Финальный фон и титры DLC «Девяностые: Heritage».
# Музыка титров: game/audio/dlc_credits.mp3
#
# Фон меню выбирается ConditionSwitch'ом прямо при показе:
#   · пройдена игра -> финальное видео, иначе базовое;
#   · на «низких» графике вместо видео показывается
#     статичный кадр (images/dlc_menu_still.png и
#     images/dlc_menu_complete_still.png) — декодировать
#     видео целыми циклами дорого для слабых телефонов.
# ==========================================================

default persistent.dlc_completed = False

init 191 python:
    DLC_COMPLETE_VIDEO = "video/dlc_menu_complete.webm"
    DLC_BASE_VIDEO = "video/dlc_menu.webm"
    DLC_COMPLETE_STILL = "images/dlc_menu_complete_still.png"
    DLC_BASE_STILL = "images/dlc_menu_still.png"

    def _dlc_menu_source(completed, low):
        # На «низких» экономим: статичный кадр вместо видео.
        if low:
            if completed and renpy.loadable(DLC_COMPLETE_STILL):
                return DLC_COMPLETE_STILL
            if renpy.loadable(DLC_BASE_STILL):
                return DLC_BASE_STILL
        if completed and renpy.loadable(DLC_COMPLETE_VIDEO):
            return Movie(play=DLC_COMPLETE_VIDEO, loop=True, channel="dlcmenu")
        if completed and renpy.loadable(DLC_COMPLETE_STILL):
            return DLC_COMPLETE_STILL
        if renpy.loadable(DLC_BASE_VIDEO):
            return Movie(play=DLC_BASE_VIDEO, loop=True, channel="dlcmenu")
        if renpy.loadable("images/dlc_menu.png"):
            return "images/dlc_menu.png"
        return Solid("#0a0e14")

    def _dlc_menu_fit(src):
        return Transform(src, xysize=(config.screen_width, config.screen_height),
                         fit="cover", align=(0.5, 0.5))

    # Состояние прохождения читаем один раз при запуске: раньше в
    # ConditionSwitch создавались сразу оба Movie (обычное и финальное
    # видео) — лишняя нагрузка на слабые устройства. После титров игра
    # всё равно возвращается в главное меню полным рестартом.
    _dlc_done = bool(getattr(persistent, "dlc_completed", False))

    renpy.image(
        "dlc_menu_bg",
        ConditionSwitch(
            "getattr(persistent, 'dlc_graphics_quality', 'medium') == 'low'",
            _dlc_menu_fit(_dlc_menu_source(_dlc_done, True)),
            "True",
            _dlc_menu_fit(_dlc_menu_source(_dlc_done, False))
        )
    )

    def dlc_mark_completed():
        persistent.dlc_completed = True
        renpy.save_persistent()
        renpy.music.stop(channel="ambient", fadeout=0.5)

label dlc_credits:
    # Нижняя панель (Назад/Скрыть/...) не должна висеть поверх титров и меню.
    $ quick_menu = False
    window hide
    $ dlc_mark_completed()
    $ renpy.music.play("audio/dlc_credits.mp3", channel="music", loop=True, fadein=2.0)
    call screen dlc_credits_screen
    $ renpy.music.stop(channel="music", fadeout=1.8)
    scene black with Dissolve(1.0)
    $ quick_menu = True
    # Сюда приходят через jump, стек вызовов пуст: возвращаемся в главное
    # меню честным рестартом, а не «return» в никуда.
    $ renpy.full_restart()


# ==========================================================
# Титры DLC.
# Длительность и высота считаются по содержимому, поэтому
# прокрутка стартует за кадром, идёт ровно и заканчивается
# вместе с текстом.
# ==========================================================

init 200 python:

    def _dlc_credits_data():
        # Берём титры основной игры, убираем финальный мемориальный блок
        # («ВЕЧНАЯ ПАМЯТЬ» и «MR LIMBO · 1991») — в DLC он не нужен.
        drop = (u"ВЕЧНАЯ ПАМЯТЬ", u"MR LIMBO  ·  1991", u"MR LIMBO · 1991")
        items = []
        for kind, val in CREDITS:
            if kind in ("head", "small", "name", "line") and val in drop:
                continue
            items.append((kind, val))

        # Хвостовые пустоты после удаления блока не нужны.
        while items and items[-1][0] == "gap":
            items.pop()

        # Заголовок — свой.
        for i, (kind, val) in enumerate(items):
            if kind == "head":
                items[i] = ("head", u"ДЕВЯНОСТЫЕ: HERITAGE")
                break

        items += [
            ("gap", 90),
            ("title", u"В ГЛАВНЫХ РОЛЯХ"),
            ("name", u"ЖЕНЯ"),
            ("small", u"роль Кати"),
            ("gap", 26),
            ("name", u"АЛИНА"),
            ("small", u"роль ученицы школы"),
            ("gap", 110),
            ("thanks", u"СПАСИБО ЗА УЧАСТИЕ"),
            ("gap", 160),
        ]
        return items

    DLC_CREDITS = _dlc_credits_data()

    _DLC_CREDITS_H = {
        "gap": 0, "head": 96, "thanks": 84, "title": 112,
        "name": 58, "small": 42, "line": 44,
    }

    def _dlc_credits_height():
        h = 0
        for kind, val in DLC_CREDITS:
            h += int(val) if kind == "gap" else _DLC_CREDITS_H.get(kind, 44)
            h += 8
        return h

    def _dlc_edge_fade(height, top=True, steps=16):
        """Мягкая градиентная шторка вместо жёсткой чёрной полосы."""
        band = max(1, int(height / steps))
        parts = []
        for i in range(steps):
            a = (steps - i) / float(steps) if top else (i + 1) / float(steps)
            parts.append(
                Transform(Solid("#000000"),
                          xysize=(config.screen_width, band + 1),
                          alpha=a, ypos=i * band)
            )
        return Fixed(*parts, xysize=(config.screen_width, band * steps))

    DLC_CREDITS_SPEED = 95.0
    DLC_CREDITS_H = _dlc_credits_height()
    DLC_CREDITS_TIME = (DLC_CREDITS_H + config.screen_height) / DLC_CREDITS_SPEED


init 200:

    transform dlc_credits_roll:
        ypos config.screen_height
        linear DLC_CREDITS_TIME ypos -DLC_CREDITS_H

    transform dlc_credits_fade:
        alpha 0.0
        linear 1.4 alpha 1.0

    transform dlc_credits_pulse:
        alpha 0.75
        block:
            linear 1.8 alpha 1.0
            linear 1.8 alpha 0.75
            repeat

    screen dlc_credits_screen():
        modal True
        zorder 300

        add Solid("#000000")

        # Лёгкий холодный подтон, чтобы чёрный экран не был плоским.
        add Transform(Solid("#0b1622"), xysize=(config.screen_width, config.screen_height), alpha=0.35)

        fixed:
            xfill True
            yfill True
            at dlc_credits_fade

            vbox:
                xalign 0.5
                xsize 1700
                spacing 8
                at dlc_credits_roll

                for _k, _v in DLC_CREDITS:

                    if _k == "gap":
                        null height _v

                    elif _k == "head":
                        text _v:
                            xalign 0.5
                            size 78
                            color "#ffffff"
                            font "kazmann-sans.ttf"
                            kerning 6
                            outlines [(3, "#00b3ff55", 0, 0)]

                    elif _k == "thanks":
                        text _v:
                            xalign 0.5
                            size 52
                            color "#8fbcff"
                            font "kazmann-sans.ttf"
                            kerning 4
                            at dlc_credits_pulse

                    elif _k == "title":
                        null height 26
                        text _v:
                            xalign 0.5
                            size 34
                            color "#00b3ff"
                            font "kazmann-sans.ttf"
                            kerning 5
                        null height 6
                        add Transform(Solid("#00b3ff"), xysize=(210, 2), alpha=0.5) xalign 0.5
                        null height 8

                    elif _k == "name":
                        text _v:
                            xalign 0.5
                            size 42
                            color "#eef3f8"

                    elif _k == "small":
                        text _v:
                            xalign 0.5
                            size 26
                            color "#7f8c99"

                    else:
                        text _v:
                            xalign 0.5
                            size 27
                            color "#a9b6c2"

        # Плавные градиентные шторки: текст появляется и уходит без резкой кромки.
        add _dlc_edge_fade(170, True) yalign 0.0
        add _dlc_edge_fade(170, False) yalign 1.0

        # Экран закрывается сам ровно тогда, когда текст ушёл вверх.
        timer (DLC_CREDITS_TIME + 1.2) action Return(True)

        textbutton _("Пропустить"):
            xalign 0.98
            yalign 0.96
            action Return(True)
            text_size 26
            text_color "#46617a"
            text_hover_color "#ffffff"
