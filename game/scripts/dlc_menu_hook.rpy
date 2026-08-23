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
# Фон меню DLC: зацикленное видео на весь экран.
# Если видео ещё не залито, берём статичный арт, а если нет и его,
# то просто тёмный фон. Меню не упадёт ни в одном случае.
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

    _dlc_logo = "images/logo_w.png" if renpy.loadable("images/logo_w.png") else None


# ==========================================================
# Меню DLC
# ==========================================================

style dlc_btn is button
style dlc_btn_text is button_text

style dlc_btn:
    xsize 520
    padding (26, 13, 20, 13)
    background Solid("#0c1219d9")
    hover_background Solid("#1c2634f2")
    selected_background Solid("#1c2634f2")

style dlc_btn_text:
    font "kazmann-sans.ttf"
    size 31
    kerning 3.0
    color "#c7d2de"
    hover_color "#ffffff"
    insensitive_color "#3f4b58"
    xalign 0.0


transform dlc_menu_in(delay=0.0):
    alpha 0.0 xoffset -22
    pause delay
    easein 0.45 alpha 1.0 xoffset 0


screen dlc_select_screen():

    tag menu
    modal True

    add "dlc_menu_bg"

    # Логотип DLC
    if _dlc_logo:
        add _dlc_logo:
            xpos 108
            ypos 132
            xsize 600
            at dlc_menu_in(0.05)
    else:
        text "ДЕВЯНОСТЫЕ":
            xpos 112
            ypos 150
            size 92
            font "kazmann-sans.ttf"
            color "#ffffff"
            kerning 5.0
            at dlc_menu_in(0.05)

        text "H E R I T A G E":
            xpos 116
            ypos 250
            size 34
            font "kazmann-sans.ttf"
            color "#8fbcff"
            kerning 8.0
            at dlc_menu_in(0.12)

    # Кнопки
    vbox:
        xpos 112
        ypos 512
        spacing 5

        textbutton _("НОВАЯ ИГРА"):
            style_prefix "dlc_btn"
            action Start("dlc_sosnovka_start")
            at dlc_menu_in(0.18)

        textbutton _("ПРОДОЛЖИТЬ"):
            style_prefix "dlc_btn"
            action ShowMenu("load")
            at dlc_menu_in(0.24)

        textbutton _("КОДЫ СЦЕН"):
            style_prefix "dlc_btn"
            action ShowMenu("codes_screen")
            at dlc_menu_in(0.30)

        null height 18

        textbutton _("НАСТРОЙКИ"):
            style_prefix "dlc_btn"
            action ShowMenu("preferences")
            at dlc_menu_in(0.36)

        textbutton _("АВТОРЫ"):
            style_prefix "dlc_btn"
            action ShowMenu("about")
            at dlc_menu_in(0.42)

        null height 18

        textbutton _("НАЗАД"):
            style_prefix "dlc_btn"
            action Return()
            at dlc_menu_in(0.48)

    text "MR LIMBO":
        xalign 1.0
        yalign 1.0
        xoffset -34
        yoffset -22
        size 26
        font "kazmann-sans.ttf"
        color "#5c7a9977"


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
