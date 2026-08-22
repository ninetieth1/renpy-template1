# Зацикленное видео главного меню.
# Файл лежит в game/video/, поэтому путь задаётся относительно game/.
image main_menu_bg = Movie(
    play="video/bg_menu_loop.webm",
    loop=True
)

# Все версии экрана main_menu используют эту переменную.
define gui.main_menu_background = main_menu_bg
