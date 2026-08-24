# ==========================================================
# game/codes.rpy
# «Девяностые» (c) MR LIMBO
#
# Коды продолжения. Игрок вводит номер и попадает
# в начало нужной главы.
# Вкладка «Коды» в меню сохранения и загрузки.
# ==========================================================

define STORY_CODES = {
    "1010": ("ch_dom",      u"Глава 1. Дом"),
    "1020": ("ch_bolezn",   u"Глава 2. Болезнь"),
    "1030": ("ch_vrach",    u"Глава 3. Врач"),
    "1040": ("ch_gazeta",   u"Глава 4. Газета"),
    "1050": ("ch_uhod",     u"Глава 5. Уход из дома"),
    "1060": ("ch_ded",      u"Глава 6. Дед и сани"),
    "1070": ("ch_noch",     u"Глава 7. Ночь в снегу"),
    "1080": ("ch_babka",    u"Глава 8. Деревня и бабка"),
    "1090": ("ch_uchenyy",  u"Глава 9. Учёный"),
    "6767": ("ch_nazad",    u"Глава 10. Дорога домой"),
    "1110": ("ch_milicia",  u"Глава 11. Милиция"),
    "1120": ("ch_final",    u"Глава 12. Последняя ночь"),

    # Тестовый код: сразу перед последней сценой DLC.
    "24012011": ("dlc_ch_stena", u"DLC. Финальная сцена"),
}


# DLC-коды длиннее обычных кодов основной игры.
default code_input = ""
default code_msg = ""


init python:

    def code_add(d):
        if len(store.code_input) < 8:
            store.code_input += d
            store.code_msg = ""

    def code_back():
        store.code_input = store.code_input[:-1]
        store.code_msg = ""

    def code_clear():
        store.code_input = ""
        store.code_msg = ""

    def code_title():
        item = STORY_CODES.get(store.code_input)
        return item[1] if item else ""

    def code_go():
        item = STORY_CODES.get(store.code_input)
        if not item:
            store.code_msg = u"Такого кода нет"
            return
        target = item[0]
        store.code_input = ""
        store.code_msg = ""
        renpy.full_restart(label=target, save=False)


screen codes_screen():

    tag menu

    use game_menu(_("Коды"), scroll=None):

        vbox:
            xalign 0.5
            yalign 0.5
            spacing 18

            text _("Введи код продолжения, чтобы вернуться к своей главе."):
                xalign 0.5
                size 28
                color "#a9b6c2"

            null height 6

            frame:
                xalign 0.5
                xsize 420
                padding (20, 14, 20, 14)
                background Solid("#070b12")
                text ("[code_input]" if code_input else "— — — —"):
                    xalign 0.5
                    size 56
                    color "#ffffff"
                    kerning 8

            text code_title():
                xalign 0.5
                size 28
                color "#00b3ff"

            text code_msg:
                xalign 0.5
                size 26
                color "#ff5a82"

            null height 4

            grid 3 4:
                xalign 0.5
                spacing 12

                for d in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    textbutton d:
                        action Function(code_add, d)
                        xsize 110
                        text_size 44
                        text_xalign 0.5
                        text_color "#c3ced9"
                        text_hover_color "#ffffff"
                        background Solid("#0d141f")
                        hover_background Solid("#14283c")

                textbutton "←":
                    action Function(code_back)
                    xsize 110
                    text_size 40
                    text_xalign 0.5
                    text_color "#7f8c99"
                    text_hover_color "#ffffff"
                    background Solid("#0d141f")
                    hover_background Solid("#14283c")

                textbutton "0":
                    action Function(code_add, "0")
                    xsize 110
                    text_size 44
                    text_xalign 0.5
                    text_color "#c3ced9"
                    text_hover_color "#ffffff"
                    background Solid("#0d141f")
                    hover_background Solid("#14283c")

                textbutton "✕":
                    action Function(code_clear)
                    xsize 110
                    text_size 36
                    text_xalign 0.5
                    text_color "#7f8c99"
                    text_hover_color "#ff5a82"
                    background Solid("#0d141f")
                    hover_background Solid("#14283c")

            null height 10

            textbutton _("Продолжить"):
                xalign 0.5
                action Function(code_go)
                text_size 40
                text_color "#00b3ff"
                text_hover_color "#ffffff"


# ===== Кнопка «Коды» в меню сохранения и загрузки =====

init 210:

    screen save():
        tag menu
        use file_slots(_("Сохранение"))
        textbutton _("Коды"):
            xalign 0.97
            yalign 0.07
            action ShowMenu("codes_screen")
            text_size 32
            text_color "#00b3ff"
            text_hover_color "#ffffff"

    screen load():
        tag menu
        use file_slots(_("Загрузка"))
        textbutton _("Коды"):
            xalign 0.97
            yalign 0.07
            action ShowMenu("codes_screen")
            text_size 32
            text_color "#00b3ff"
            text_hover_color "#ffffff"
