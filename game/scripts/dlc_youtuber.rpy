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

    def yt_edit_nickname():
        value = renpy.input(u"Введи ник:", default=persistent.yt_name or u"MR LIMBO", length=32, allow="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-")
        value = (value or "").strip() or u"MR LIMBO"
        persistent.yt_name = value[:32]
        renpy.save_persistent()
        renpy.restart_interaction()

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

init 6 python:
    def yt_stage_roman(stage):
        return {1: u"I", 2: u"II", 3: u"III"}.get(stage, u"—")

    def yt_first_letter():
        try:
            return (persistent.yt_name or u"M")[:1].upper()
        except Exception:
            return u"M"

screen yt_screen():
    modal True
    zorder 140
    on "show" action Function(yt_sync)
    key "game_menu" action Hide("yt_screen")
    default yt_filter = "all"

    add Solid("#04070cf7")
    if renpy.loadable("images/ui_vignette.png"):
        add "ui_vignette"

    # ===== Заголовок и прогресс =====
    vbox:
        xpos 108
        ypos 44
        spacing 6
        text _("Я ЮТУБЕР"):
            size 66
            font "kazmann-sans.ttf"
            color "#e8eef5"
            kerning 6
        text _("Кадры для превью. Открываются по ходу истории."):
            size 30
            color "#8c9bab"

    $ yt_open_n = yt_open_count()
    $ yt_all_n = max(yt_total(), 1)
    vbox:
        xalign 0.95
        ypos 58
        spacing 12
        xsize 460
        text _("ОТКРЫТО [yt_open_n] ИЗ [yt_all_n]"):
            size 30
            color "#8fbcff"
            kerning 2
            xalign 1.0
        fixed:
            ysize 10
            add Solid("#22344a"):
                xysize (460, 10)
            add Solid("#8fbcff"):
                xysize (int(460 * yt_open_n / float(yt_all_n)), 10)

    # ===== Ник и аватар =====
    hbox:
        xpos 108
        ypos 192
        spacing 24
        fixed:
            xysize (104, 104)
            if renpy.loadable("images/ui_avatar_ring.png"):
                add "ui_avatar_ring":
                    xysize (104, 104)
            text yt_first_letter():
                align (0.5, 0.5)
                size 46
                color "#e8eef5"
                font "kazmann-sans.ttf"
        vbox:
            yalign 0.5
            spacing 8
            hbox:
                spacing 18
                textbutton "[persistent.yt_name!q]":
                    ysize 60
                    padding (20, 0, 20, 0)
                    text_size 40
                    text_xalign 0.0
                    text_color "#ffffff"
                    text_hover_color "#8fbcff"
                    background Solid("#16263b")
                    hover_background Solid("#203b5c")
                    action Function(yt_edit_nickname)
                textbutton _("ИЗМЕНИТЬ"):
                    yalign 0.5
                    text_size 30
                    text_color "#8fbcff"
                    text_hover_color "#ffffff"
                    action Function(yt_edit_nickname)
            text _("нажми на ник, чтобы поменять"):
                size 24
                color "#5c7a99"

    # ===== Фильтры =====
    hbox:
        xpos 108
        ypos 326
        spacing 14
        for yt_f, yt_ft in (("all", u"ВСЕ"), ("open", u"ОТКРЫТЫЕ"), ("locked", u"ЗАКРЫТЫЕ")):
            textbutton yt_ft:
                xysize (252, 58)
                text_size 28
                text_kerning 2.0
                action SetScreenVariable("yt_filter", yt_f)
                selected (yt_filter == yt_f)
                background dlc_frame(252, 58, "#7d94ab7a", 2, "#050a1059")
                hover_background dlc_frame(252, 58, "#ffffff", 2, "#0c1a2799")
                selected_background dlc_frame(252, 58, "#c8d8e8", 2, "#12283cdd")
                selected_hover_background dlc_frame(252, 58, "#ffffff", 2, "#12283cdd")
                text_idle_color "#c2cfdc"
                text_hover_color "#ffffff"
                text_selected_color "#ffffff"

    # ===== Сетка кадров =====
    $ yt_cards = [(s, n, st) for s, n, st, tr in YT_SHOTS if (yt_filter == "all") or ((yt_filter == "open") == yt_is_open(s))]

    viewport:
        xpos 100
        ypos 406
        xsize 1720
        ysize 556
        draggable True
        mousewheel True
        scrollbars "vertical"
        vpgrid:
            cols (4 if not renpy.variant("small") else 3)
            spacing 34
            xfill False
            for sid, sname, stage in yt_cards:
                if yt_is_open(sid):
                    button:
                        xysize (YT_THUMB_W, YT_THUMB_H)
                        background yt_thumb(sid)
                        hover_foreground dlc_frame(YT_THUMB_W, YT_THUMB_H, "#ffffff", 3)
                        action Show("yt_shot", shot=sid)
                        if renpy.loadable("images/ui_gradient_dark.png"):
                            add "ui_gradient_dark":
                                xysize (YT_THUMB_W, 110)
                                yalign 1.0
                        vbox:
                            xalign 0.0
                            yalign 1.0
                            xpos 14
                            yoffset -10
                            xsize (YT_THUMB_W - 28)
                            spacing 2
                            text ("ЧАСТЬ " + yt_stage_roman(stage)):
                                size 20
                                color "#8fbcff"
                                kerning 2
                            text sname:
                                size 26
                                color "#f2f6fa"
                                outlines [(1, "#000000cc", 0, 0)]
                else:
                    fixed:
                        xysize (YT_THUMB_W, YT_THUMB_H)
                        add Solid("#0a121cf2")
                        add dlc_frame(YT_THUMB_W, YT_THUMB_H, "#2b3947", 2)
                        text "?":
                            align (0.5, 0.42)
                            size 88
                            color "#2f3f4f"
                        vbox:
                            xalign 0.5
                            yalign 1.0
                            yoffset -12
                            spacing 2
                            text _("Закрыто"):
                                size 26
                                color "#4a5764"
                            text _("откроется по ходу истории"):
                                size 20
                                color "#39434e"

    textbutton _("НАЗАД"):
        style_prefix "dlc_btn"
        xpos 108
        yalign 0.965
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
