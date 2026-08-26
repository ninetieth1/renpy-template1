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

    add Solid("#000000")

    fixed:
        xfill True
        yfill True

        vbox:
            xalign 0.5
            ypos 1080
            xsize 1700
            spacing 8
            at dlc_credits_roll

            for index, item in enumerate(CREDITS):
                $ kind, val = item

                if kind == "gap":
                    null height val
                elif kind == "head":
                    text ("ДЕВЯНОСТЫЕ: HERITAGE" if index == 0 else val):
                        xalign 0.5
                        size 78
                        color "#ffffff"
                        font "kazmann-sans.ttf"
                        kerning 6
                elif kind == "title":
                    null height 26
                    text val:
                        xalign 0.5
                        size 34
                        color "#00b3ff"
                        font "kazmann-sans.ttf"
                        kerning 5
                    null height 10
                elif kind == "name":
                    text val:
                        xalign 0.5
                        size 42
                        color "#eef3f8"
                elif kind == "small":
                    text val:
                        xalign 0.5
                        size 26
                        color "#7f8c99"
                else:
                    text val:
                        xalign 0.5
                        size 27
                        color "#a9b6c2"

            null height 120

            text "В ГЛАВНЫХ РОЛЯХ":
                xalign 0.5
                size 48
                color "#00b3ff"
                font "kazmann-sans.ttf"
                kerning 5

            null height 28

            text "ЖЕНЯ":
                xalign 0.5
                size 58
                color "#ffffff"
                font "kazmann-sans.ttf"
            text "роль Кати":
                xalign 0.5
                size 40
                color "#eef3f8"

            null height 34

            text "АЛИНА":
                xalign 0.5
                size 58
                color "#ffffff"
                font "kazmann-sans.ttf"
            text "роль ученицы школы":
                xalign 0.5
                size 40
                color "#eef3f8"

            null height 150

            text "СПАСИБО ЗА УЧАСТИЕ":
                xalign 0.5
                size 52
                color "#8fbcff"
                font "kazmann-sans.ttf"

    timer 0.5 repeat True action Function(dlc_credits_tick)

transform dlc_credits_roll:
    yoffset 1080
    linear 110.0 yoffset -6200
