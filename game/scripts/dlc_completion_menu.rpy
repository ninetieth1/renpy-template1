# Финальный фон и возврат в меню DLC после прохождения.
# Файл видео: game/video/dlc_menu_complete.webm

init 191 python:

    DLC_COMPLETE_VIDEO = "video/dlc_menu_complete.webm"
    DLC_BASE_VIDEO = "video/dlc_menu.webm"
    DLC_COMPLETE_STILL = "images/dlc_menu_complete.png"

    def dlc_refresh_menu_background():
        try:
            completed = bool(getattr(persistent, "completed", False))
        except Exception:
            completed = False

        if completed and renpy.loadable(DLC_COMPLETE_VIDEO):
            source = Movie(play=DLC_COMPLETE_VIDEO, loop=True, channel="movie")
        elif completed and renpy.loadable(DLC_COMPLETE_STILL):
            source = DLC_COMPLETE_STILL
        elif renpy.loadable(DLC_BASE_VIDEO):
            source = Movie(play=DLC_BASE_VIDEO, loop=True, channel="movie")
        elif renpy.loadable("images/dlc_menu.png"):
            source = "images/dlc_menu.png"
        else:
            source = Solid("#0a0e14")

        renpy.image(
            "dlc_menu_bg",
            Transform(source, xysize=(config.screen_width, config.screen_height), fit="cover", align=(0.5, 0.5))
        )

    dlc_refresh_menu_background()

    def dlc_mark_completed_and_open_menu():
        persistent.completed = True
        renpy.save_persistent()
        dlc_refresh_menu_background()
        renpy.music.stop(channel="music", fadeout=0.5)
        renpy.music.stop(channel="ambient", fadeout=0.5)
        renpy.music.stop(channel="movie", fadeout=0.5)


label dlc_completed_menu:
    $ dlc_mark_completed_and_open_menu()
    call screen dlc_select_screen
    return


# Возврат в меню DLC после завершения истории.
init 400 python:
    _dlc_old_end_game_callback = getattr(config, "end_game_callback", None)

    def _dlc_end_game_callback():
        if getattr(persistent, "completed", False) and renpy.has_label("dlc_completed_menu"):
            renpy.call_in_new_context("dlc_completed_menu")
        elif _dlc_old_end_game_callback is not None:
            _dlc_old_end_game_callback()

    config.end_game_callback = _dlc_end_game_callback
