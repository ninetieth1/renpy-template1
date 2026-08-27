# ==========================================================
# game/snow.rpy
# «Девяностые» (c) MR LIMBO
#
# Снег на улице истории. Сам эффект живёт в snowstorm.rpy
# (хлопья, глубина, ветер), здесь — привязка к сценам и тумблер.
# story.rpy править не нужно, файл сам подменяет bg().
# ==========================================================

default persistent.snow_enabled = True


init python:

    snow_ok = (renpy.loadable("images/snow_puff.png")
               or renpy.loadable("images/snow_crystal.png"))

    def snow_preset_name():
        q = getattr(persistent, "dlc_graphics_quality", "medium")
        return {
            "low": "street_low",
            "medium": "street",
            "high": "street_high",
        }.get(q, "street")

    def snow_current_layer():
        if not persistent.snow_enabled:
            return None
        return snowstorm_layer(snow_preset_name())


# ===== Уличные сцены =====
define SNOW_SCENES = set([
    "scene_19", "scene_20", "scene_21", "scene_22", "scene_23",
    "scene_24", "scene_25", "scene_26", "scene_27", "scene_28",
    "scene_29", "scene_30", "scene_31", "scene_36", "scene_37",
    "scene_38", "scene_39", "scene_40",
    "scene_2_1", "scene_2_2", "scene_2_3", "scene_2_5",
    "scene_2_5_5", "scene_2_6_6", "scene_2_7_7", "scene_2_8_8",
    "scene_2_10_10", "scene_2_10_11", "scene_2_12_12",
    "scene_finall",
])


default snow_here = False


init python:

    def snow_show():
        if snow_ok and persistent.snow_enabled:
            renpy.show_screen("snow_overlay")
        else:
            renpy.hide_screen("snow_overlay")

    def snow_hide():
        renpy.hide_screen("snow_overlay")

    def snow_toggle():
        persistent.snow_enabled = not persistent.snow_enabled
        if persistent.snow_enabled and store.snow_here:
            snow_show()
        else:
            snow_hide()


init 10 python:

    def bg(name, trans=None):
        renpy.scene()
        if renpy.has_image(name, exact=True):
            renpy.show(name)
        else:
            renpy.show("black")

        store.snow_here = (name in SNOW_SCENES)
        if store.snow_here:
            snow_show()
        else:
            snow_hide()

        renpy.with_statement(trans if trans is not None else store.smooth)


screen snow_overlay():
    zorder 90
    $ snow_active = snow_current_layer()
    if snow_active is not None:
        add snow_active
init 200:

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
                        spacing 6
                        text _("ЭФФЕКТЫ") style "pref_head"
                        textbutton _("Снег на улице"):
                            action Function(snow_toggle)
                            style "check_button"
                            selected persistent.snow_enabled

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

                        textbutton _("Выключить весь звук"):
                            action Preference("all mute", "toggle")
                            style "check_button"
