# ==========================================================
# game/limbo_overrides.rpy
# Девяностые (c) MR LIMBO
#
# Чинит story.rpy и меню, НЕ редактируя их.
# Экраны отсюда перекрывают старые, потому что объявлены
# с более высоким приоритетом init.
#
# Класть в папку game/ рядом с остальными файлами.
# ==========================================================


# ==========================================================
# 1. Подмена текста на карточках между сценами
#
# Сцена 1 говорила "1970 год — 9 января", хотя Андрей через
# две реплики отвечает "Пятое, мама", а газета пишет про
# "минувший 1970 год". Три разные даты в одной истории.
# Тут карточка подменяется на лету, story.rpy не трогаем.
# ==========================================================

define CARD_FIXES = {
    u"1970 год — 9 января — Долиновка": u"1971 год, 5 января, Долиновка",
    u"Чуть позже — вечером": u"Чуть позже, вечером",
}

init 100 python:

    def fix_card(msg):
        try:
            return CARD_FIXES.get(msg, msg)
        except Exception:
            return msg


init 100:

    screen card_screen(msg, tsize=64):

        add Solid("#000000")

        text fix_card(msg):
            xalign 0.5
            yalign 0.5
            text_align 0.5
            size tsize
            color "#ffffff"
            xsize 1750
            line_spacing 6


    # ======================================================
    # 2. Газета
    #
    # story.rpy зовёт hold_to_continue со старым нечитаемым
    # текстом. Перехватываем вызов и показываем нормальную
    # газету из newspaper.rpy.
    # ======================================================

    screen hold_to_continue(msg="", hold_time=8.0):
        use newspaper(6.0)


    # ======================================================
    # 3. Главное меню без кнопки "DLC+"
    #
    # После удаления fnf.rpy её label исчезает, и нажатие
    # уронило бы игру. Поэтому кнопки просто нет.
    # На телефоне убраны "Выход" и "Помощь": там системная
    # кнопка "назад".
    # ======================================================

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


    # ======================================================
    # 4. Боковое меню (тоже без DLC+)
    # ======================================================

    screen navigation():

        vbox:
            style_prefix "navigation"
            xpos gui.navigation_xpos
            yalign 0.5
            spacing gui.navigation_spacing

            if main_menu:

                textbutton _("Начать новую игру") action Start()
                textbutton _("Продолжить") action ShowMenu("load")
                textbutton _("Настройки") action ShowMenu("preferences")
                textbutton _("Об игре") action ShowMenu("about")

                if renpy.variant("pc"):
                    textbutton _("Выход") action Quit(confirm=True)

            else:

                textbutton _("История") action ShowMenu("history")
                textbutton _("Сохранить") action ShowMenu("save")
                textbutton _("Загрузить") action ShowMenu("load")
                textbutton _("Настройки") action ShowMenu("preferences")

                if _in_replay:
                    textbutton _("Закончить повтор") action EndReplay(confirm=True)
                else:
                    textbutton _("Главное меню") action MainMenu()

                textbutton _("Об игре") action ShowMenu("about")

                if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):
                    textbutton _("Помощь") action ShowMenu("help")

                if renpy.variant("pc"):
                    textbutton _("Выход") action Quit(confirm=not main_menu)


    # ======================================================
    # 5. Заглушка DLC на случай, если где-то остался вызов
    # ======================================================

    screen dlc_stub():
        modal True
        add Solid("#000000")
        text _("Этот раздел появится в следующем обновлении."):
            xalign 0.5
            yalign 0.5
            size 40
            color "#ffffff"
        textbutton _("Назад"):
            action Return()
            xalign 0.5
            yalign 0.72


label dlc_plus:
    call screen dlc_stub
    return MainMenu(confirm=False)
