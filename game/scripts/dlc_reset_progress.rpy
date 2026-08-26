# ==========================================================
# Сброс прогресса DLC для тестирования.
# ==========================================================

init 195 python:
    def dlc_reset_progress():
        persistent.dlc_completed = False
        persistent.completed = False
        persistent.yt_unlocked = []
        renpy.save_persistent()
        renpy.restart_interaction()

screen dlc_reset_progress_button():
    if renpy.get_screen("dlc_prefs"):
        textbutton _("СБРОСИТЬ ПРОГРЕСС DLC"):
            xalign 0.5
            yalign 0.93
            text_size 26
            text_color "#ff8a9a"
            text_hover_color "#ffffff"
            action Show("dlc_reset_confirm")

screen dlc_reset_confirm():
    modal True
    zorder 250

    add Solid("#02040acc")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 760
        padding (34, 28, 34, 28)
        background Solid("#070d15f2")

        vbox:
            spacing 22
            xalign 0.5

            text _("Сбросить прогресс DLC?"):
                xalign 0.5
                size 38
                color "#ffffff"

            text _("Будут закрыты все превью и убран финальный фон."):
                xalign 0.5
                size 25
                color "#c2cfdc"

            hbox:
                spacing 28
                xalign 0.5

                textbutton _("СБРОСИТЬ"):
                    text_size 30
                    text_color "#ff8a9a"
                    text_hover_color "#ffffff"
                    action [Function(dlc_reset_progress), Hide("dlc_reset_confirm")]

                textbutton _("ОТМЕНА"):
                    text_size 30
                    action Hide("dlc_reset_confirm")

init 196 python:
    if "dlc_reset_progress_button" not in config.overlay_screens:
        config.overlay_screens.append("dlc_reset_progress_button")
