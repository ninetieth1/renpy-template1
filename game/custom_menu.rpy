# Зацикленное видео главного меню.
# Файл лежит в game/video/, поэтому путь задаётся относительно game/.
# Видео заполняет экран с сохранением пропорций, лишнее обрезается по краям.
image main_menu_bg = Transform(
    Movie(
        play="video/bg_menu_loop.webm",
        loop=True
    ),
    xysize=(config.screen_width, config.screen_height),
    fit="cover",
    align=(0.5, 0.5)
)
