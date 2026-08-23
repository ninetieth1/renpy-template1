# ==========================================================
# game/scripts/dlc_youtuber.rpy
# Раздел «Я ЮТУБЕР»: кадры для превью,
# которые открываются по ходу DLC.
# ==========================================================

default persistent.yt_name = u"MR LIMBO"
default persistent.yt_unlocked = []


init -5 python:

    # id кадра, подпись, этап
    YT_SHOTS = [
        ("sc_4_1",  u"Дорога в Сосновку",     1),
        ("sc_13",   u"Коридор второго этажа", 1),
        ("sc_14_2", u"На крыльце",            1),
        ("sc_20_4", u"Она у забора",          2),
        ("sc_23",   u"Мужик с лопатой",       2),
        ("sc_28",   u"Восемь имён",           2),
        ("sc_31",   u"Рассвет у стены",      3),
    ]

    # Где что открывается
    YT_UNLOCK_AT = {
        "dlc_ch_doroga":    ["sc_4_1"],
        "dlc_ch_za_dveryu": ["sc_13"],
        "dlc_ch_krylco":    ["sc_14_2"],
        "dlc_ch_son_1":     ["sc_20_4"],
        "dlc_ch_muzhik":    ["sc_23"],
        "dlc_ch_stena":     ["sc_28"],
    }

    YT_THUMB_W = 260 if renpy.variant("small") else 300
    YT_THUMB_H = int(YT_THUMB_W * 9 / 16)


init 5 python:

    def yt_is_open(shot_id):
        try:
            return shot_id in persistent.yt_unlocked
        except Exception:
            return False

    def yt_open_count():
        return len([s for s, n, st in YT_SHOTS if yt_is_open(s)])

    def yt_total():
        return len(YT_SHOTS)

    def yt_unlock(ids):
        """Открывает кадры и сообщает об этом в углу."""
        if persistent.yt_unlocked is None:
            persistent.yt_unlocked = []

        fresh = []
        for sid in ids:
            if not renpy.loadable("images/%s.png" % sid):
                continue
            if sid not in persistent.yt_unlocked:
                persistent.yt_unlocked.append(sid)
                fresh.append(sid)

        if fresh:
            try:
                renpy.show_screen("yt_note", shot=fresh[-1], extra=len(fresh) - 1)
                renpy.restart_interaction()
            except Exception:
                pass

    def yt_check_finale():
        """Финальный кадр открывается, когда история пройдена."""
        try:
            if persistent.completed and not yt_is_open("sc_31"):
                yt_unlock(["sc_31"])
        except Exception:
            pass

    def yt_thumb(shot_id):
        return Transform(
            "images/%s.png" % shot_id,
            xysize=(YT_THUMB_W, YT_THUMB_H),
            fit="cover",
            align=(0.5, 0.5)
        )


# ==========================================================
# Отслеживание прогресса
# ==========================================================

init 310 python:

    _yt_prev_label_cb = config.label_callback

    def _yt_label_cb(label_name, abnormal):

        if _yt_prev_label_cb is not None:
            _yt_prev_label_cb(label_name, abnormal)

        try:
            ids = YT_UNLOCK_AT.get(label_name)
            if ids:
                yt_unlock(ids)
        except Exception:
            pass

    config.label_callback = _yt_label_cb


label yt_finale_unlock:
    $ yt_unlock(["sc_31"])
    return


# ==========================================================
# Уведомление в углу
# ==========================================================

transform yt_note_in:
    alpha 0.0 xoffset 90
    easein 0.45 alpha 1.0 xoffset 0
    pause 4.4
    easeout 0.4 alpha 0.0 xoffset 60


screen yt_note(shot=None, extra=0):

    zorder 220

    frame:
        xalign 1.0
        yalign 0.0
        xoffset -28
        yoffset 26
        padding (18, 14, 22, 14)
        background Solid("#060b12ee")
        at yt_note_in

        hbox:
            spacing 16

            if shot and renpy.loadable("images/%s.png" % shot):
                add Transform(
                    "images/%s.png" % shot,
                    xysize=(168, 94),
                    fit="cover",
                    align=(0.5, 0.5)
                ) yalign 0.5

            vbox:
                yalign 0.5
                spacing 4

                text _("НОВОЕ ФОТО ДЛЯ ПРЕВЬЮ"):
                    size 22
                    color "#8fbcff"
                    kerning 3

                if extra > 0:
                    text _("И ещё [extra]. Раздел «Я ютубер» в меню DLC"):
                        size 24
                        color "#c2cfdc"
                else:
                    text _("Раздел «Я ютубер» в меню DLC"):
                        size 24
                        color "#c2cfdc"

    timer 5.4 action Hide("yt_note")


# ==========================================================
# Галерея
# ==========================================================

screen yt_screen():

    modal True
    zorder 140

    key "game_menu" action Hide("yt_screen")

    default yt_open = yt_open_count()
    default yt_all = yt_total()

    add Solid("#03060af2")

    vbox:
        xpos 108
        ypos 88
        spacing 10

        text _("Я ЮТУБЕР"):
            size 52
            font "kazmann-sans.ttf"
            color "#e8eef5"
            kerning 7

        text _("Кадры для превью. Открываются по ходу истории: [yt_open] из [yt_all]."):
            size 26
            color "#8c9bab"

    # Имя на превью
    frame:
        xpos 108
        ypos 206
        xsize 1180
        padding (24, 18, 24, 18)
        background Solid("#070d15cc")

        hbox:
            spacing 22

            text _("ПОДПИСЬ"):
                size 26
                color "#8fbcff"
                kerning 3
                yalign 0.5
                xsize 150

            input:
                value FieldInputValue(persistent, "yt_name", default=False)
                length 24
                size 30
                color "#ffffff"
                yalign 0.5
                xsize 520

            text _("кликни и пиши"):
                size 22
                color "#5c7a99"
                yalign 0.5

    # Сетка кадров
    viewport:
        xpos 108
        ypos 318
        xsize 1700
        ysize (540 if not renpy.variant("small") else 500)
        draggable True
        mousewheel True
        scrollbars "vertical"

        vpgrid:
            cols (5 if not renpy.variant("small") else 4)
            spacing 20
            xfill False

            for sid, sname, stage in YT_SHOTS:

                vbox:
                    spacing 8

                    if yt_is_open(sid):

                        button:
                            xysize (YT_THUMB_W, YT_THUMB_H)
                            background yt_thumb(sid)
                            hover_foreground dlc_frame(YT_THUMB_W, YT_THUMB_H, "#ffffff", 3)
                            action Show("yt_shot", shot=sid)

                        text sname:
                            size 22
                            color "#c2cfdc"
                            xsize YT_THUMB_W

                    else:

                        fixed:
                            xysize (YT_THUMB_W, YT_THUMB_H)
                            add Solid("#0a121cf2")
                            add dlc_frame(YT_THUMB_W, YT_THUMB_H, "#2b3947", 2)
                            text "?":
                                align (0.5, 0.5)
                                size 54
                                color "#2f3f4f"

                        text _("Закрыто"):
                            size 22
                            color "#4a5764"
                            xsize YT_THUMB_W

    textbutton _("НАЗАД"):
        style_prefix "dlc_btn"
        xpos 108
        yalign 0.94
        action Hide("yt_screen")


# ==========================================================
# Превью во весь экран
# ==========================================================

screen yt_shot(shot=""):

    modal True
    zorder 160

    key "game_menu" action Hide("yt_shot")

    add Transform(
        "images/%s.png" % shot,
        xysize=(config.screen_width, config.screen_height),
        fit="cover",
        align=(0.5, 0.5)
    )

    add Transform(Solid("#000000"), ysize=260, yalign=0.0, alpha=0.45)
    add Transform(Solid("#000000"), ysize=300, yalign=1.0, alpha=0.55)

    if _dlc_logo:
        add _dlc_logo:
            xpos 92
            ypos 74
            xsize (560 if not renpy.variant("small") else 640)

    vbox:
        xpos 96
        yalign 0.86
        spacing 10

        add Transform(Solid("#ffffff"), xysize=(120, 3), alpha=0.85)

        text "[persistent.yt_name!q]":
            size (54 if not renpy.variant("small") else 62)
            font "kazmann-sans.ttf"
            color "#ffffff"
            kerning 4

    text _("На ПК клавиша S сохраняет скриншот в папку игры"):
        xalign 0.5
        yalign 0.985
        size 22
        color "#8c9bab"

    textbutton _("ЗАКРЫТЬ"):
        style_prefix "dlc_btn"
        xalign 0.97
        yalign 0.90
        action Hide("yt_shot")
