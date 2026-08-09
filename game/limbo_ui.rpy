# ==========================================================
# game/limbo_ui.rpy
# Девяностые (c) MR LIMBO
#
# Интерфейс: диалоговое окно, быстрое меню, настройки,
# автосохранение, выборы. Этот файл ПЕРЕОПРЕДЕЛЯЕТ часть
# screens.rpy, поэтому сам screens.rpy править не нужно.
# Просто положи файл в game/ и всё.
# ==========================================================


################################################################
# 1. Настройки движка (то, что должно быть в релизной новелле)
################################################################

# Откат к прошлой реплике
define config.rollback_enabled = True
define config.hard_rollback_limit = 200
define config.rollback_length = 256

# Пропуск. Непрочитанное листается, только если игрок сам
# включит это в настройках (галочка "Пропускать непрочитанное").
define config.allow_skipping = True
define config.fast_skipping = True

# Автосохранение
define config.has_autosave = True
define config.autosave_slots = 12
define config.autosave_frequency = 250
define config.autosave_on_choice = True
define config.autosave_on_quit = True

# Каждые сколько секунд делать автосейв по таймеру
define AUTOSAVE_EVERY_SECONDS = 120.0

default _limbo_last_autosave = None

init python:

    import time as _limbo_time

    def _limbo_timed_autosave():

        # не в главном меню
        if getattr(renpy.store, "main_menu", False):
            return

        # не во время роликов и скрытого интерфейса
        if not getattr(renpy.store, "quick_menu", True):
            return

        # не поверх меню сохранений/настроек
        for _s in ("save", "load", "preferences", "main_menu"):
            if renpy.get_screen(_s):
                return

        now = _limbo_time.time()
        last = getattr(renpy.store, "_limbo_last_autosave", None)

        if last is None:
            renpy.store._limbo_last_autosave = now
            return

        if now - last >= AUTOSAVE_EVERY_SECONDS:
            renpy.store._limbo_last_autosave = now
            try:
                renpy.force_autosave(take_screenshot=True)
                renpy.notify(_("Автосохранение"))
            except Exception:
                pass

    config.interact_callbacks.append(_limbo_timed_autosave)


################################################################
# 2. Диалоговое окно
################################################################

transform ctc_blink:
    alpha 0.20
    linear 0.8 alpha 1.0
    linear 0.8 alpha 0.20
    repeat

init 100:

    screen say(who, what):

        window:
            id "window"

            if who is not None:

                window:
                    id "namebox"
                    style "namebox"
                    text who id "who"

            text what id "what"

            # индикатор "дальше"
            text "▼":
                xalign 0.99
                yalign 0.90
                size 24
                color "#00b3ff"
                at ctc_blink

            # скрыть интерфейс
            textbutton "✕":
                action HideInterface()
                xalign 1.0
                yalign 0.0
                xoffset -22
                yoffset 12
                text_size 34
                text_color "#46617a"
                text_hover_color "#ffffff"

        if not renpy.variant("small"):
            add SideImage() xalign 0.0 yalign 1.0


style window:
    xalign 0.5
    xfill True
    yalign 1.0
    ysize gui.textbox_height
    background Fixed(
        Solid("#04070ceb"),
        Transform(Solid("#0b1b2b"), ysize=120, yalign=0.0, alpha=0.55),
        Transform(Solid("#00b3ff"), ysize=3, yalign=0.0),
        )

style namebox:
    xpos gui.name_xpos
    xanchor 0.0
    ypos 4
    padding (26, 8, 30, 10)
    background Fixed(
        Solid("#08161fF2"),
        Transform(Solid("#00b3ff"), xsize=5, xalign=0.0),
        )

style say_label:
    color "#00b3ff"
    outlines []

style say_dialogue:
    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos
    line_spacing 8
    color "#eef3f8"


################################################################
# 3. Выборы
################################################################

style choice_button:
    xminimum 900
    ypadding 16
    idle_background Solid("#080e17cc")
    hover_background Solid("#0c2438f0")

style choice_button_text:
    idle_color "#9fb0c0"
    hover_color "#ffffff"


################################################################
# 4. Быстрое меню
################################################################

init 100:

    screen quick_menu():

        zorder 100

        if quick_menu:

            hbox:
                style_prefix "quick"
                style "quick_menu"
                spacing (34 if renpy.variant("small") else 26)

                textbutton _("Назад") action Rollback()
                textbutton _("Авто") action Preference("auto-forward", "toggle")
                textbutton _("Пропуск"):
                    action Skip()
                    alternate Skip(fast=True, confirm=True)
                textbutton _("История") action ShowMenu("history")
                textbutton _("Сохранить") action ShowMenu("save")
                textbutton _("Загрузить") action ShowMenu("load")
                textbutton _("Настройки") action ShowMenu("preferences")
                textbutton _("Скрыть") action HideInterface()

style quick_menu:
    xalign 0.5
    yalign 1.0
    yoffset -14

style quick_button_text:
    size (32 if renpy.variant("small") else 24)
    idle_color "#5c7a99"
    hover_color "#ffffff"
    selected_color "#00b3ff"


################################################################
# 5. Настройки
################################################################

init 100:

    screen preferences():

        tag menu

        use game_menu(_("Настройки"), scroll="viewport", spacing=22):

            vbox:
                spacing 22
                xsize 1300

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
                            text _("Скорость текста") style "pref_item" xsize 380
                            bar value Preference("text speed") xsize 640 yalign 0.5

                        hbox:
                            spacing 24
                            text _("Задержка авто-режима") style "pref_item" xsize 380
                            bar value Preference("auto-forward time") xsize 640 yalign 0.5

                        textbutton _("Авто-режим после озвучки"):
                            action Preference("auto-forward after click", "toggle")
                            style "check_button"

                frame:
                    style "pref_card"
                    vbox:
                        spacing 6
                        text _("ПРОПУСК") style "pref_head"
                        textbutton _("Пропускать непрочитанный текст"):
                            action Preference("skip", "toggle")
                            style "check_button"
                        textbutton _("Не останавливаться на выборах"):
                            action Preference("after choices", "toggle")
                            style "check_button"
                        textbutton _("Пропускать переходы"):
                            action Preference("transitions", "toggle")
                            style "check_button"

                frame:
                    style "pref_card"
                    vbox:
                        spacing 10
                        text _("ЗВУК") style "pref_head"

                        if config.has_music:
                            hbox:
                                spacing 24
                                text _("Музыка") style "pref_item" xsize 380
                                bar value Preference("music volume") xsize 640 yalign 0.5

                        if config.has_sound:
                            hbox:
                                spacing 24
                                text _("Звуки") style "pref_item" xsize 380
                                bar value Preference("sound volume") xsize 640 yalign 0.5

                        if config.has_voice:
                            hbox:
                                spacing 24
                                text _("Голос") style "pref_item" xsize 380
                                bar value Preference("voice volume") xsize 640 yalign 0.5

                        textbutton _("Выключить весь звук"):
                            action Preference("all mute", "toggle")
                            style "check_button"

style pref_card is frame:
    background Solid("#070b12cc")
    padding (28, 22, 28, 22)
    xfill True

style pref_head is gui_text:
    size 30
    color "#00b3ff"
    kerning 4

style pref_item is gui_text:
    size 28
    color "#c3ced9"
    yalign 0.5


################################################################
# 6. Русские заголовки меню + "Об игре"
################################################################

init 100:

    screen save():
        tag menu
        use file_slots(_("Сохранение"))

    screen load():
        tag menu
        use file_slots(_("Загрузка"))

    screen about():

        tag menu

        use game_menu(_("Об игре"), scroll="viewport"):

            style_prefix "about"

            vbox:
                spacing 6
                text "[config.name!t]" size 54 color "#ffffff"
                text _("Версия: Release [config.version!t]\n") size 28 color "#00b3ff"

                if gui.about:
                    text "[gui.about!t]\n" size 28 color "#c3ced9" line_spacing 6

                text _("Сделано на {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only].") size 24 color "#7f8c99"
