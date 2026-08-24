default persistent.yt_name = u"MR LIMBO"
default persistent.yt_unlocked = []

init -5 python:
    YT_SHOTS = [
        ("sc_4_1", u"Дорога в Сосновку", 1, "dlc_ch_doroga"),
        ("sc_13", u"Коридор второго этажа", 1, "dlc_ch_za_dveryu"),
        ("sc_14_2", u"На крыльце", 1, "dlc_ch_krylco"),
        ("sc_20_4", u"Она у забора", 2, "dlc_ch_son_1"),
        ("sc_23", u"Мужик с лопатой", 2, "dlc_ch_muzhik"),
        ("sc_28", u"Восемь имён", 2, "dlc_ch_stena"),
        ("sc_31", u"Рассвет у стены", 3, None),
    ]
    YT_THUMB_W = 300 if renpy.variant("small") else 340
    YT_THUMB_H = int(YT_THUMB_W * 9 / 16)

init 5 python:
    def yt_trigger(shot_id):
        for sid, name, stage, trig in YT_SHOTS:
            if sid == shot_id:
                return trig
        return None

    def yt_is_open(shot_id):
        try:
            if persistent.yt_unlocked and shot_id in persistent.yt_unlocked:
                return True
        except Exception:
            pass
        trig = yt_trigger(shot_id)
        if trig is None:
            return bool(getattr(persistent, "completed", False))
        try:
            return bool(renpy.seen_label(trig))
        except Exception:
            return False

    def yt_open_count():
        return len([s for s, n, st, tr in YT_SHOTS if yt_is_open(s)])

    def yt_total():
        return len(YT_SHOTS)

    def yt_unlock(ids):
        known = list(persistent.yt_unlocked or [])
        fresh = []
        for sid in ids:
            if renpy.loadable("images/%s.png" % sid) and sid not in known:
                known.append(sid)
                fresh.append(sid)
        persistent.yt_unlocked = known
        if fresh:
            try:
                renpy.show_screen("yt_note", shot=fresh[-1], extra=len(fresh) - 1)
                renpy.restart_interaction()
            except Exception:
                pass

    def yt_sync():
        known = list(persistent.yt_unlocked or [])
        for sid, name, stage, trig in YT_SHOTS:
            if sid not in known and renpy.loadable("images/%s.png" % sid) and yt_is_open(sid):
                known.append(sid)
        persistent.yt_unlocked = known

    def yt_check_finale():
        yt_sync()

    def yt_save_name(value):
        value = (value or "").strip() or u"MR LIMBO"
        persistent.yt_name = value[:32]
        renpy.save_persistent()

    def yt_thumb(shot_id):
        return Transform("images/%s.png" % shot_id, xysize=(YT_THUMB_W, YT_THUMB_H), fit="cover", align=(0.5, 0.5))

init 310 python:
    _yt_prev_label_cb = config.label_callback
    YT_UNLOCK_AT = {}
    for _sid, _name, _stage, _trig in YT_SHOTS:
        if _trig:
            YT_UNLOCK_AT.setdefault(_trig, []).append(_sid)

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
                add Transform("images/%s.png" % shot, xysize=(168, 94), fit="cover", align=(0.5, 0.5)) yalign 0.5
            vbox:
                yalign 0.5
                spacing 4
                text _("НОВОЕ ФОТО ДЛЯ ПРЕВЬЮ"):
                    size 24
                    color "#8fbcff"
                    kerning 3
                if extra > 0:
                    text _("И ещё [extra]. Раздел «Я ютубер» в меню DLC"):
                        size 26
                        color "#c2cfdc"
                else:
                    text _("Раздел «Я ютубер» в меню DLC"):
                        size 26
                        color "#c2cfdc"
    timer 5.4 action Hide("yt_note")

screen yt_screen():
    modal True
    zorder 140
    on "show" action Function(yt_sync)
    key "game_menu" action Hide("yt_screen")
    default yt_open = yt_open_count()
    default yt_all = yt_total()
    default yt_edit_name = persistent.yt_name

    add Solid("#03060af2")

    vbox:
        xpos 108
        ypos 72
        spacing 12
        text _("Я ЮТУБЕР"):
            size 76
            font "kazmann-sans.ttf"
            color "#e8eef5"
            kerning 7
        text _("Кадры для превью. Открываются по ходу истории: [yt_open] из [yt_all]."):
            size 36
            color "#8c9bab"

    frame:
        xpos 108
        ypos 196
        xsize 1600
        padding (30, 24, 30, 24)
        background Solid("#070d15dd")
        hbox:
            spacing 28
            yalign 0.5
            text _("НИК"):
                size 36
                color "#8fbcff"
                kerning 3
                yalign 0.5
                xsize 130
            input:
                value VariableInputValue("yt_edit_name")
                length 32
                size 46
                color "#ffffff"
                caret "#8fbcff"
                yalign 0.5
                xsize 850
                allow "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-"
            textbutton _("СОХРАНИТЬ"):
                action Function(yt_save_name, yt_edit_name)
                yalign 0.5
                text_size 34
                text_color "#8fbcff"
                text_hover_color "#ffffff"
            text _("кликни по полю и печатай"):
                size 28
                color "#5c7a99"
                yalign 0.5

    viewport:
        xpos 108
        ypos 330
        xsize 1700
        ysize (560 if not renpy.variant("small") else 470)
        draggable True
        mousewheel True
        scrollbars "vertical"
        vpgrid:
            cols (4 if not renpy.variant("small") else 3)
            spacing 26
            xfill False
            for sid, sname, stage, strig in YT_SHOTS:
                vbox:
                    spacing 10
                    if yt_is_open(sid):
                        button:
                            xysize (YT_THUMB_W, YT_THUMB_H)
                            background yt_thumb(sid)
                            hover_foreground dlc_frame(YT_THUMB_W, YT_THUMB_H, "#ffffff", 3)
                            action Show("yt_shot", shot=sid)
                        text sname:
                            size 30
                            color "#c2cfdc"
                            xsize YT_THUMB_W
                    else:
                        fixed:
                            xysize (YT_THUMB_W, YT_THUMB_H)
                            add Solid("#0a121cf2")
                            add dlc_frame(YT_THUMB_W, YT_THUMB_H, "#2b3947", 2)
                            text "?":
                                align (0.5, 0.5)
                                size 68
                                color "#2f3f4f"
                        text _("Закрыто"):
                            size 30
                            color "#4a5764"
                            xsize YT_THUMB_W

    textbutton _("НАЗАД"):
        style_prefix "dlc_btn"
        xpos 108
        yalign 0.96
        action Hide("yt_screen")

screen yt_shot(shot=""):
    modal True
    zorder 160
    key "game_menu" action Hide("yt_shot")
    add Transform("images/%s.png" % shot, xysize=(config.screen_width, config.screen_height), fit="cover", align=(0.5, 0.5))
    add Transform(Solid("#000000"), ysize=118, yalign=0.0, alpha=0.38)
    add Transform(Solid("#000000"), ysize=150, yalign=1.0, alpha=0.46)
    if _dlc_logo:
        add _dlc_logo:
            xpos 60
            ypos 34
            xsize (300 if not renpy.variant("small") else 360)
    vbox:
        xpos 62
        yalign 0.9
        spacing 8
        add Transform(Solid("#ffffff"), xysize=(96, 3), alpha=0.85)
        text "[persistent.yt_name!q]":
            size (54 if not renpy.variant("small") else 62)
            font "kazmann-sans.ttf"
            color "#ffffff"
            kerning 4
    textbutton _("ЗАКРЫТЬ"):
        style_prefix "dlc_btn"
        xalign 0.97
        yalign 0.06
        action Hide("yt_shot")
