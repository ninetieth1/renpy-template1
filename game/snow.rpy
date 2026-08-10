# ==========================================================
# game/snow.rpy
# «Девяностые» (c) MR LIMBO
#
# Снег-оверлей поверх уличных сцен + переключатель в настройках.
# story.rpy править НЕ нужно: этот файл сам подменяет bg().
#
# Файл ролика: game/video/snow.webm (зациклен)
# ==========================================================


# ===== Настройки =====
define SNOW_VIDEO = "video/snow.webm"

# Прозрачность оверлея (0.0 - 1.0)
define SNOW_ALPHA = 0.55

# Режим наложения:
#   None  - если у ролика ПРОЗРАЧНЫЙ фон (VP9 с альфой)
#   "add" - если у ролика ЧЁРНЫЙ фон, чёрное станет невидимым
define SNOW_BLEND = "add"

# Включён ли снег по умолчанию
default persistent.snow_enabled = True


# ===== Уличные сцены =====
# Тут снег включается сам. Добавляй или убирай имена как хочешь.
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


init python:

    def snow_available():
        return renpy.loadable(SNOW_VIDEO)

    def snow_show():
        """Показать снег, если он включён в настройках и ролик есть."""
        if persistent.snow_enabled and snow_available():
            renpy.show_screen("snow_overlay")
        else:
            renpy.hide_screen("snow_overlay")

    def snow_hide():
        renpy.hide_screen("snow_overlay")

    def snow_toggle():
        persistent.snow_enabled = not persistent.snow_enabled
        if persistent.snow_enabled:
            snow_show()
        else:
            snow_hide()


init 10 python:

    # Подменяем bg() из story.rpy: снег сам включается на улице
    # и сам выключается в помещении.
    def bg(name, trans=None):
        renpy.scene()
        if renpy.has_image(name, exact=True):
            renpy.show(name)
        else:
            renpy.show("black")

        if name in SNOW_SCENES:
            snow_show()
        else:
            snow_hide()

        renpy.with_statement(trans if trans is not None else store.smooth)


# ===== Экран снега =====
screen snow_overlay():

    zorder 90

    if persistent.snow_enabled and renpy.loadable(SNOW_VIDEO):

        if SNOW_BLEND:
            add Transform(
                Movie(play=SNOW_VIDEO, loop=True, start_image=Null()),
                xysize=(config.screen_width, config.screen_height),
                fit="cover",
                alpha=SNOW_ALPHA,
                blend=SNOW_BLEND)
        else:
            add Transform(
                Movie(play=SNOW_VIDEO, loop=True, start_image=Null()),
                xysize=(config.screen_width, config.screen_height),
                fit="cover",
                alpha=SNOW_ALPHA)


# ==========================================================
# Настройки с переключателем снега
# Полностью заменяет экран из limbo_ui.rpy
# ==========================================================

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
