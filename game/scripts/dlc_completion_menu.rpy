# ==========================================================
# Финальный фон меню DLC после прохождения.
# Файл для видео: game/video/dlc_menu_complete.webm
# ==========================================================

init 191 python:

    DLC_COMPLETE_VIDEO = "video/dlc_menu_complete.webm"
    DLC_BASE_VIDEO = "video/dlc_menu.webm"
    DLC_COMPLETE_STILL = "images/dlc_menu_complete.png"

    def dlc_refresh_menu_background():
        """Выбирает фон DLC и всегда отключает звук у фонового видео."""
        try:
            completed = bool(getattr(persistent, "completed", False))
        except Exception:
            completed = False

        if completed and renpy.loadable(DLC_COMPLETE_VIDEO):
            source = Movie(play=DLC_COMPLETE_VIDEO, loop=True, audio=False)
        elif completed and renpy.loadable(DLC_COMPLETE_STILL):
            source = DLC_COMPLETE_STILL
        elif renpy.loadable(DLC_BASE_VIDEO):
            source = Movie(play=DLC_BASE_VIDEO, loop=True, audio=False)
        elif renpy.loadable("images/dlc_menu.png"):
            source = "images/dlc_menu.png"
        else:
            source = Solid("#0a0e14")

        renpy.image(
            "dlc_menu_bg",
            Transform(
                source,
                xysize=(config.screen_width, config.screen_height),
                fit="cover",
                align=(0.5, 0.5)
            )
        )

    # При запуске игры сразу восстанавливает нужный фон из persistent.
    dlc_refresh_menu_background()

    def dlc_mark_completed_and_open_menu():
        persistent.completed = True
        renpy.save_persistent()
        dlc_refresh_menu_background()
        renpy.music.stop(channel="music", fadeout=0.5)
        renpy.music.stop(channel="ambient", fadeout=0.5)


label dlc_completed_menu:
    $ dlc_mark_completed_and_open_menu()
    call screen dlc_select_screen
    return
