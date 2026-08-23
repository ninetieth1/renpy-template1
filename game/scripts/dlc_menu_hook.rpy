# ==========================================================
# game/scripts/dlc_menu_hook.rpy
# Меню DLC «Девяностые: Heritage» + коды глав.
# ==========================================================

init 100 python:

    try:
        STORY_CODES.update({
            "2010": ("dlc_ch_urok", u"DLC. Сцена 1. Класс после каникул"),
            "2020": ("dlc_ch_deeprichastie", u"DLC. Сцена 2. Деепричастный оборот"),
            "2030": ("dlc_ch_priglashenie", u"DLC. Сцена 3. Приглашение"),
            "2040": ("dlc_ch_doroga", u"DLC. Сцена 4. Дорога в Сосновку"),
            "2050": ("dlc_ch_dom42", u"DLC. Сцена 5. Дом 42"),
            "2060": ("dlc_ch_kuhnya", u"DLC. Сцена 6. Кухня"),
            "2070": ("dlc_ch_mat", u"DLC. Сцена 7. Мать Кати"),
            "2080": ("dlc_ch_otkrovenno", u"DLC. Сцена 8. Откровенный разговор"),
            "2090": ("dlc_ch_proshchanie", u"DLC. Сцена 9. Прощание"),
            "2100": ("dlc_ch_ponedelnik", u"DLC. Сцена 10. Школьный двор"),
            "2110": ("dlc_ch_sluhi", u"DLC. Сцена 11. Слухи о Сосновке"),
            "2120": ("dlc_ch_proekt", u"DLC. Сцена 12. Защита проекта"),
            "2130": ("dlc_ch_direktor", u"DLC. Сцена 13. Директор"),
            "2140": ("dlc_ch_za_dveryu", u"DLC. Сцена 14. За дверью"),
            "2150": ("dlc_ch_krylco", u"DLC. Сцена 15. Крыльцо"),
            "2160": ("dlc_ch_zvonok", u"DLC. Сцена 16. Телефонный звонок"),
            "2170": ("dlc_ch_kino", u"DLC. Сцена 17. Кинотеатр"),
            "2180": ("dlc_ch_net_docheri", u"DLC. Сцена 18. У меня нет дочери"),
            "2190": ("dlc_ch_pustaya_parta", u"DLC. Сцена 19. Пустая парта"),
            "2200": ("dlc_ch_nastoyashiy_direktor", u"DLC. Сцена 20. Настоящий директор"),
            "2210": ("dlc_ch_ne_v_perviy_raz", u"DLC. Сцена 21. Не в первый раз"),
            "2220": ("dlc_ch_son_1", u"DLC. Сцена 22. Первый сон"),
            "2230": ("dlc_ch_muzhik", u"DLC. Сцена 23. Мужик с лопатой"),
            "2240": ("dlc_ch_zapiska", u"DLC. Сцена 24. Записка"),
            "2250": ("dlc_ch_son_2", u"DLC. Сцена 25. Второй сон"),
            "2260": ("dlc_ch_golos", u"DLC. Сцена 26. Голос"),
            "2270": ("dlc_ch_vrach_ne_pomozhet", u"DLC. Сцена 27. Голос рядом"),
            "2280": ("dlc_ch_tetrad", u"DLC. Сцена 28. Тетрадь"),
            "2290": ("dlc_ch_reshenie", u"DLC. Сцена 29. Решение"),
            "2300": ("dlc_ch_proshchanie_dom", u"DLC. Сцена 30. Дом"),
            "2310": ("dlc_ch_peshkom", u"DLC. Сцена 31. Путь пешком"),
            "2320": ("dlc_ch_stena", u"DLC. Сцена 32. Стена"),
        })
    except Exception:
        pass


# ==========================================================
# Рамка для кнопок: только обводка, без картинок.
# ==========================================================

init -10 python:

    DLC_BTN_W = 620 if renpy.variant("small") else 560
    DLC_BTN_H = 84 if renpy.variant("small") else 68

    def dlc_frame(w, h, line, thickness=2, fill=None):
        """Прямоугольная обводка из четырёх тонких полос."""
        parts = []

        if fill:
            parts.append(Transform(Solid(fill), xysize=(w, h)))

        parts.append(Transform(Solid(line), xysize=(w, thickness), align=(0.0, 0.0)))
        parts.append(Transform(Solid(line), xysize=(w, thickness), align=(0.0, 1.0)))
        parts.append(Transform(Solid(line), xysize=(thickness, h), align=(0.0, 0.0)))
        parts.append(Transform(Solid(line), xysize=(thickness, h), align=(1.0, 0.0)))

        return Fixed(*parts, xysize=(w, h))


# ==========================================================
# Снег для меню: средние шестилучевые снежинки, не точки.
# ==========================================================

init 185 python:

    dlc_snow_ok = False

    def _dlc_flake(size, alpha):
        bar_w = max(2, int(size * 0.16))
        bar = Transform(Solid("#ffffff"), xysize=(size, bar_w))
        star = Fixed(
            Transform(bar, align=(0.5, 0.5)),
            Transform(bar, rotate=60, align=(0.5, 0.5)),
            Transform(bar, rotate=120, align=(0.5, 0.5)),
            xysize=(size + 6, size + 6)
        )
        return Transform(star, alpha=alpha)

    try:
        _small = renpy.variant("small")
        _cnt = 26 if _small else 46

        _dlc_snow_far = SnowBlossom(
            _dlc_flake(15, 0.34),
            count=_cnt,
            border=90,
            xspeed=(-26, 26),
            yspeed=(45, 90),
            start=3,
            fast=True
        )

        _dlc_snow_near = SnowBlossom(
            _dlc_flake(24, 0.52),
            count=int(_cnt * 0.45),
            border=110,
            xspeed=(-48, 48),
            yspeed=(95, 165),
            start=3,
            fast=True
        )

        renpy.image("dlc_snow_layer", Fixed(_dlc_snow_far, _dlc_snow_near))
        dlc_snow_ok = True

    except Exception:
        dlc_snow_ok = False


# ==========================================================
# Фон меню DLC и логотип
# ==========================================================

init 190 python:

    _dlc_menu_video = "video/dlc_menu.webm"
    _dlc_menu_still = "images/dlc_menu.png"

    if renpy.loadable(_dlc_menu_video):
        _dlc_menu_layer = Movie(play=_dlc_menu_video, loop=True)
    elif renpy.loadable(_dlc_menu_still):
        _dlc_menu_layer = _dlc_menu_still
    else:
        _dlc_menu_layer = Solid("#0a0e14")

    renpy.image(
        "dlc_menu_bg",
        Transform(
            _dlc_menu_layer,
            xysize=(config.screen_width, config.screen_height),
            fit="cover",
            align=(0.5, 0.5)
        )
    )

    _dlc_logo = None
    for _cand in (
        "images/logo.png",
        "images/logo_ice2.png",
        "images/logo_ice.png",
        "images/logo_w.png",
    ):
        if renpy.loadable(_cand):
            _dlc_logo = _cand
            break

    # ---------- звук меню: без музыки, только зимний ветер ----------

    def dlc_menu_audio_on():
        renpy.music.stop(channel="music", fadeout=1.0)
        if renpy.loadable("audio/winter.mp3"):
            renpy.music.play(
                "audio/winter.mp3",
                channel="ambient",
                loop=True,
                fadein=1.5,
                relative_volume=0.55
            )

    def dlc_menu_wind_off():
        renpy.music.stop(channel="ambient", fadeout=0.6)

    def dlc_menu_audio_off():
        renpy.music.stop(channel="ambient", fadeout=1.0)
        # Музыку главного меню возвращаем только если остались в меню.
        if getattr(renpy.store, "main_menu", False):
            if renpy.loadable("audio/menu.mp3"):
                renpy.music.play(
                    "audio/menu.mp3",
                    channel="music",
                    loop=True,
                    fadein=1.5
                )


# ==========================================================
# Стили кнопок: обводка, все состояния заданы явно.
# ==========================================================

style dlc_btn is button
style dlc_btn_text is button_text

style dlc_btn:
    xysize (DLC_BTN_W, DLC_BTN_H)
    padding (30, 0, 22, 0)
    background dlc_frame(DLC_BTN_W, DLC_BTN_H, "#7d94ab7a", 2, "#050a1059")
    hover_background dlc_frame(DLC_BTN_W, DLC_BTN_H, "#ffffff", 2, "#0c1a2799")
    selected_background dlc_frame(DLC_BTN_W, DLC_BTN_H, "#c8d8e8", 2, "#0c1a2799")
    selected_hover_background dlc_frame(DLC_BTN_W, DLC_BTN_H, "#ffffff", 2, "#0c1a2799")
    insensitive_background dlc_frame(DLC_BTN_W, DLC_BTN_H, "#48566433", 2, "#05090f40")
    hover_xoffset 12
    selected_xoffset 12

style dlc_btn_text:
    font "kazmann-sans.ttf"
    size (36 if renpy.variant("small") else 30)
    kerning 3.0
    yalign 0.5
    xalign 0.0
    idle_color "#c2cfdc"
    hover_color "#ffffff"
    selected_color "#ffffff"
    selected_idle_color "#ffffff"
    selected_hover_color "#ffffff"
    insensitive_color "#4a5764"
    outlines []


transform dlc_slide(delay=0.0):
    alpha 0.0 xoffset -70
    pause delay
    parallel:
        easein 0.5 xoffset 0
    parallel:
        linear 0.35 alpha 1.0


# ==========================================================
# Меню DLC
# ==========================================================

screen dlc_select_screen():

    tag menu
    modal True

    on "show" action [Function(dlc_menu_audio_on), Function(yt_check_finale)]
    on "hide" action Function(dlc_menu_audio_off)

    key "game_menu" action Return()

    add "dlc_menu_bg"

    if dlc_snow_ok:
        add "dlc_snow_layer"

    # Логотип
    if _dlc_logo:
        add _dlc_logo:
            xpos 104
            ypos 118
            xsize (620 if renpy.variant("small") else 560)
            at dlc_slide(0.05)
    else:
        text "ДЕВЯНОСТЫЕ":
            xpos 108
            ypos 138
            size 92
            font "kazmann-sans.ttf"
            color "#e8eef5"
            kerning 5.0
            at dlc_slide(0.05)

        text "H E R I T A G E":
            xpos 112
            ypos 238
            size 34
            font "kazmann-sans.ttf"
            color "#8fbcff"
            kerning 8.0
            at dlc_slide(0.12)

    # Кнопки
    vbox:
        xpos 108
        ypos (430 if renpy.variant("small") else 480)
        spacing 14

        textbutton _("НОВАЯ ИГРА"):
            style_prefix "dlc_btn"
            action [Function(dlc_menu_wind_off), Start("dlc_sosnovka_start")]
            at dlc_slide(0.20)

        textbutton _("ПРОДОЛЖИТЬ"):
            style_prefix "dlc_btn"
            action ShowMenu("load")
            at dlc_slide(0.28)

        textbutton _("Я ЮТУБЕР"):
            style_prefix "dlc_btn"
            action Show("yt_screen")
            at dlc_slide(0.36)

        textbutton _("НАСТРОЙКИ"):
            style_prefix "dlc_btn"
            action Show("dlc_prefs")
            at dlc_slide(0.44)

        textbutton _("НАЗАД"):
            style_prefix "dlc_btn"
            action Return()
            at dlc_slide(0.52)

    text "MR LIMBO":
        xalign 1.0
        yalign 1.0
        xoffset -34
        yoffset -22
        size 26
        font "kazmann-sans.ttf"
        color "#5c7a9977"


# ==========================================================
# Настройки поверх меню DLC.
# Отдельный экран без tag menu, поэтому меню под ним не пропадает,
# а «Назад» возвращает именно в меню DLC, а не в главное.
# ==========================================================

screen dlc_prefs():

    modal True
    zorder 130

    key "game_menu" action Hide("dlc_prefs")

    add Solid("#03060ad9")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 22
        xsize 1180

        text _("НАСТРОЙКИ"):
            xalign 0.5
            size 44
            font "kazmann-sans.ttf"
            color "#e8eef5"
            kerning 6

        if renpy.variant("pc") or renpy.variant("web"):
            frame:
                style "pref_card"
                vbox:
                    spacing 8
                    text _("ЭКРАН") style "pref_head"
                    hbox:
                        spacing 26
                        textbutton _("Оконный"):
                            action Preference("display", "window")
                            style "radio_button"
                        textbutton _("Полный экран"):
                            action Preference("display", "fullscreen")
                            style "radio_button"

        frame:
            style "pref_card"
            vbox:
                spacing 10
                text _("ТЕКСТ") style "pref_head"

                hbox:
                    spacing 24
                    text _("Скорость текста") style "pref_item" xsize 360
                    bar value Preference("text speed") xsize 620 yalign 0.5

                hbox:
                    spacing 24
                    text _("Задержка авто-режима") style "pref_item" xsize 360
                    bar value Preference("auto-forward time") xsize 620 yalign 0.5

        frame:
            style "pref_card"
            vbox:
                spacing 10
                text _("ЗВУК") style "pref_head"

                hbox:
                    spacing 24
                    text _("Музыка") style "pref_item" xsize 360
                    bar value Preference("music volume") xsize 620 yalign 0.5

                hbox:
                    spacing 24
                    text _("Звуки") style "pref_item" xsize 360
                    bar value Preference("sound volume") xsize 620 yalign 0.5

                textbutton _("Выключить весь звук"):
                    action Preference("all mute", "toggle")
                    style "check_button"

        null height 8

        textbutton _("НАЗАД"):
            style_prefix "dlc_btn"
            xalign 0.5
            action Hide("dlc_prefs")


# ==========================================================
# Плашка 16+ убрана: экран сразу закрывается сам.
# Вызовы call age_gate в сюжете трогать не надо.
# ==========================================================

init 300:

    screen age_gate():
        timer 0.01 action Return(True)


# ==========================================================
# Главное меню с кнопкой DLC
# ==========================================================

init 200:

    screen main_menu():

        tag menu

        add gui.main_menu_background

        text "Девяностые":
            xalign 0.5
            yalign 0.34
            size 110
            font "kazmann-sans.ttf"
            color "#ffffff"
            kerning 4.0
            outlines [(3, "#00b3ff88", 0, 0)]

        vbox:
            style_prefix "main_nav"
            xalign 0.5
            yalign 0.68
            spacing 8

            textbutton _("Начать новую игру") action Start()
            textbutton _("DLC") action ShowMenu("dlc_select_screen")
            textbutton _("Продолжить") action ShowMenu("load")
            textbutton _("Настройки") action ShowMenu("preferences")
            textbutton _("Об игре") action ShowMenu("about")

            if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):
                textbutton _("Помощь") action ShowMenu("help")

            if renpy.variant("pc"):
                textbutton _("Выход") action Quit(confirm=True)

        text "MR LIMBO":
            xalign 1.0
            yalign 1.0
            xoffset -30
            yoffset -20
            size 30
            color "#5c7a9966"
            font "kazmann-sans.ttf"
        use social_row
