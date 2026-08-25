# ==========================================================
# Режимы графики DLC: Низкие / Средние / Высокие.
# Видео оверлея для высокого режима: game/video/dlc_high_snow.webm
# ==========================================================

default persistent.dlc_graphics_quality = "medium"

init 192 python:

    DLC_HIGH_SNOW_VIDEO = "video/dlc_high_snow.webm"

    def dlc_quality_label():
        value = getattr(persistent, "dlc_graphics_quality", "medium")
        return {
            "low": u"Низкие",
            "medium": u"Средние",
            "high": u"Высокие",
        }.get(value, u"Средние")

    def dlc_set_quality(value):
        if value not in ("low", "medium", "high"):
            value = "medium"
        persistent.dlc_graphics_quality = value
        renpy.save_persistent()
        renpy.restart_interaction()

    def dlc_high_snow_available():
        return renpy.loadable(DLC_HIGH_SNOW_VIDEO)

    def dlc_quality_blur():
        # Лёгкое размытие снижает нагрузку на слабых устройствах.
        return 1.2 if getattr(persistent, "dlc_graphics_quality", "medium") == "low" else 0.0

    # В низком режиме убираем старый SnowBlossom полностью.
    # В среднем он остаётся, в высоком его заменяет видео-оверлей.
    if renpy.has_image("dlc_snow_layer", exact=True):
        _dlc_snow_base = renpy.get_registered_image("dlc_snow_layer")
        renpy.image(
            "dlc_snow_layer",
            ConditionSwitch(
                "getattr(persistent, 'dlc_graphics_quality', 'medium') == 'low'",
                Null(),
                "True",
                _dlc_snow_base
            )
        )

screen dlc_quality_overlay():
    # Панель доступна поверх окна настроек DLC.
    if renpy.get_screen("dlc_prefs"):
        frame:
            xpos 420
            ypos 745
            xsize 1180
            padding (18, 14, 18, 14)
            background Solid("#070d15dd")

            hbox:
                spacing 24
                yalign 0.5

                text _("ГРАФИКА"):
                    size 30
                    color "#8fbcff"
                    kerning 3
                    yalign 0.5

                textbutton _("Низкие"):
                    action Function(dlc_set_quality, "low")
                    selected (persistent.dlc_graphics_quality == "low")
                    text_size 28

                textbutton _("Средние"):
                    action Function(dlc_set_quality, "medium")
                    selected (persistent.dlc_graphics_quality == "medium")
                    text_size 28

                textbutton _("Высокие"):
                    action Function(dlc_set_quality, "high")
                    selected (persistent.dlc_graphics_quality == "high")
                    text_size 28

                text ("[dlc_quality_label()]"):
                    size 26
                    color "#c2cfdc"
                    yalign 0.5

    # Высокий режим использует отдельный видео-оверлей без аудио.
    if renpy.get_screen("dlc_select_screen") and persistent.dlc_graphics_quality == "high" and dlc_high_snow_available():
        add Movie(play=DLC_HIGH_SNOW_VIDEO, loop=True, channel="movie")

init 193 python:
    # Оверлей добавляется только поверх нужных DLC-экранов.
    if "dlc_quality_overlay" not in config.overlay_screens:
        config.overlay_screens.append("dlc_quality_overlay")
