# Финальный фон меню DLC после прохождения.
# Файл видео: game/video/dlc_menu_complete.webm

init 191 python:

    DLC_COMPLETE_VIDEO = "video/dlc_menu_complete.webm"
    DLC_BASE_VIDEO = "video/dlc_menu.webm"
    DLC_COMPLETE_STILL = "images/dlc_menu_complete.png"

    def dlc_refresh_menu_background():
        # Общий persistent.completed основной игры здесь не используется.
        completed = bool(getattr(persistent, "dlc_completed", False))

        if completed and renpy.loadable(DLC_COMPLETE_VIDEO):
            source = Movie(play=DLC_COMPLETE_VIDEO, loop=True)
        elif completed and renpy.loadable(DLC_COMPLETE_STILL):
            source = DLC_COMPLETE_STILL
        elif renpy.loadable(DLC_BASE_VIDEO):
            source = Movie(play=DLC_BASE_VIDEO, loop=True)
        elif renpy.loadable("images/dlc_menu.png"):
            source = "images/dlc_menu.png"
        else:
            source = Solid("#0a0e14")

        renpy.image(
            "dlc_menu_bg",
            Transform(source, xysize=(config.screen_width, config.screen_height), fit="cover", align=(0.5, 0.5))
        )

    dlc_refresh_menu_background()

    def dlc_mark_completed():
        persistent.dlc_completed = True
        renpy.save_persistent()
        dlc_refresh_menu_background()
        renpy.music.stop(channel="music", fadeout=0.5)
        renpy.music.stop(channel="ambient", fadeout=0.5)


label dlc_completed_menu:
    $ dlc_mark_completed()
    call screen dlc_select_screen
    return
