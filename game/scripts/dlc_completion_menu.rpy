# ==========================================================
# Финальный фон и титры DLC «Девяностые: Heritage».
# Музыка титров: game/audio/dlc_credits.mp3
# ==========================================================

default persistent.dlc_completed = False

init 191 python:
    DLC_COMPLETE_VIDEO = "video/dlc_menu_complete.webm"
    DLC_BASE_VIDEO = "video/dlc_menu.webm"
    DLC_COMPLETE_STILL = "images/dlc_menu_complete.png"

    def _dlc_menu_source(completed):
        if completed and renpy.loadable(DLC_COMPLETE_VIDEO):
            return Movie(play=DLC_COMPLETE_VIDEO, loop=True)
        if completed and renpy.loadable(DLC_COMPLETE_STILL):
            return DLC_COMPLETE_STILL
        if renpy.loadable(DLC_BASE_VIDEO):
            return Movie(play=DLC_BASE_VIDEO, loop=True)
        if renpy.loadable("images/dlc_menu.png"):
            return "images/dlc_menu.png"
        return Solid("#0a0e14")

    renpy.image(
        "dlc_menu_bg",
        ConditionSwitch(
            "getattr(persistent, 'dlc_completed', False)",
            Transform(_dlc_menu_source(True), xysize=(config.screen_width, config.screen_height), fit="cover", align=(0.5, 0.5)),
            "True",
            Transform(_dlc_menu_source(False), xysize=(config.screen_width, config.screen_height), fit="cover", align=(0.5, 0.5))
        )
    )

    def dlc_mark_completed():
        persistent.dlc_completed = True
        renpy.save_persistent()
        renpy.music.stop(channel="ambient", fadeout=0.5)

    def dlc_credits_tick():
        if renpy.music.get_playing(channel="music") is None:
            renpy.end_interaction(True)

label dlc_credits:
    $ dlc_mark_completed()
    $ renpy.music.play("audio/dlc_credits.mp3", channel="music", loop=False, fadein=1.5)
    call screen dlc_credits_screen
    $ renpy.music.stop(channel="music", fadeout=0.8)
    call screen dlc_select_screen
    return

screen dlc_credits_screen():
    modal True
    zorder 300

    add Solid("#05070b")

    fixed:
        xfill True
        yfill True

        # Начинаем прямо за нижним краем экрана, а не на двойной высоте.
        vbox:
            xalign 0.5
            ypos 0
            xsize 1500
            spacing 34
            at dlc_credits_roll

            text "ДЕВЯНОСТЫЕ: HERITAGE":
                xalign 0.5
                size 64
                color "#e8eef5"
                font "kazmann-sans.ttf"
                kerning 6

            null height 80

            text "ФИНАЛЬНЫЕ ТИТРЫ":
                xalign 0.5
                size 38
                color "#8fbcff"
                font "kazmann-sans.ttf"
                kerning 5

            null height 70

            text "История и сценарий":
                xalign 0.5
                size 34
                color "#c2cfdc"
            text "MR LIMBO":
                xalign 0.5
                size 42
                color "#ffffff"

            null height 40

            text "Артём и Катя":
                xalign 0.5
                size 34
                color "#c2cfdc"
            text "Спасибо, что дошёл до конца.":
                xalign 0.5
                size 34
                color "#ffffff"

            null height 100

            text "Никто не должен быть забыт.":
                xalign 0.5
                size 40
                color "#8fbcff"
                font "kazmann-sans.ttf"

            null height 180

            text "Конец DLC":
                xalign 0.5
                size 30
                color "#5c7a99"

    timer 0.5 repeat True action Function(dlc_credits_tick)

transform dlc_credits_roll:
    yoffset 1080
    linear 78.0 yoffset -1200
