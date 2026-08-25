# ==========================================================
# Режимы графики DLC: Низкие / Средние / Высокие.
# Видео оверлея для высокого режима: game/video/dlc_high_snow.webm
# ==========================================================

default persistent.dlc_graphics_quality = "medium"

init 192 python:

    DLC_HIGH_SNOW_VIDEO = "video/dlc_high_snow.webm"

    def dlc_quality_label():
        return {
            "low": u"Низкие",
            "medium": u"Средние",
            "high": u"Высокие",
        }.get(getattr(persistent, "dlc_graphics_quality", "medium"), u"Средние")

    def dlc_set_quality(value):
        if value not in ("low", "medium", "high"):
            value = "medium"
        persistent.dlc_graphics_quality = value
        # Старый кодовый снег работает только в среднем режиме.
        store.dlc_snow_ok = (value == "medium")
        renpy.save_persistent()
        renpy.restart_interaction()

    def dlc_high_snow_available():
        return renpy.loadable(DLC_HIGH_SNOW_VIDEO)

    # Восстанавливаем режим после запуска игры.
    store.dlc_snow_ok = (getattr(persistent, "dlc_graphics_quality", "medium") == "medium")

screen dlc_quality_overlay():
    # Панель появляется поверх окна настроек DLC.
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

                text "[dlc_quality_label()]":
                    size 26
                    color "#c2cfdc"
                    yalign 0.5

    # В высоком режиме старый снег выключен, а оверлей включён только если ролик есть.
    if renpy.get_screen("dlc_select_screen") and getattr(persistent, "dlc_graphics_quality", "medium") == "high" and dlc_high_snow_available():
        add Movie(play=DLC_HIGH_SNOW_VIDEO, loop=True, channel="movie")

init 193 python:
    if "dlc_quality_overlay" not in config.overlay_screens:
        config.overlay_screens.append("dlc_quality_overlay")
