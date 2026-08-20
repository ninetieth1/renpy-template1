# ==========================================================
# game/scripts/dlc_menu_hook.rpy
# Подключение нового DLC в главное меню и в меню кодов.
# Не трогает старый dlc_plus.
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


screen dlc_select_screen():
    tag menu
    add Solid("#000000e6")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 24

        text "DLC":
            xalign 0.5
            size 62
            color "#ffffff"

        textbutton "Сосновка":
            xalign 0.5
            action Start("dlc_sosnovka_start")
            text_size 36
            text_color "#00b3ff"
            text_hover_color "#ffffff"

        textbutton "Назад":
            xalign 0.5
            action Return()
            text_size 30
            text_color "#7f8c99"
            text_hover_color "#ffffff"


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
