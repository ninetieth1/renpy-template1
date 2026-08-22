# Зацикленное видео главного меню.
# Файл лежит в game/video/, поэтому путь задаётся относительно game/.
# gui.main_menu_background уже указывает на это имя в gui.rpy, повторно его объявлять нельзя.
image main_menu_bg = Movie(
    play="video/bg_menu_loop.webm",
    loop=True
)
