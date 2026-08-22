# ==========================================================
# game/scripts/dlc_scene_map.rpy
# DLC «Сосновка» — единая карта кадров.
# Все кадры лежат в game/images/ как sc_*.png
# ==========================================================

init python:

    # Регистрируем каждый DLC-кадр как полноэкранный фон.
    # fit="cover" заполняет экран без полос и сохраняет пропорции.
    for _dlc_bg in renpy.list_files():
        if _dlc_bg.startswith("images/sc_") and _dlc_bg.endswith(".png") and "/" not in _dlc_bg[len("images/"):]:
            _dlc_name = _dlc_bg[len("images/"):-4]
            _dlc_displayable = Transform(
                _dlc_bg,
                xysize=(config.screen_width, config.screen_height),
                fit="cover",
                align=(0.5, 0.5)
            )
            renpy.image(_dlc_name, _dlc_displayable)

            # Старые имена второй части связываем с загруженными sc_17...sc_32.
            if _dlc_name.startswith("sc_"):
                _dlc_suffix = _dlc_name[3:]
                if _dlc_suffix.isdigit() and 17 <= int(_dlc_suffix) <= 32:
                    renpy.image("dlc_s" + _dlc_suffix, _dlc_displayable)

    # Финальный старый псевдоним показывает загруженный кадр сцены 32.
    if renpy.has_image("sc_32", exact=True):
        renpy.image("dlc_s32_end", "sc_32")

    def dlc_show(name, trans=None):
        """
        Показывает полноэкранный кадр DLC по имени файла без расширения.
        Если файла нет, используем чёрный фон.
        """
        image_path = "images/%s.png" % name

        renpy.scene()

        if renpy.loadable(image_path) and renpy.has_image(name, exact=True):
            renpy.show(name)
        elif renpy.has_image("black", exact=True):
            renpy.show("black")

        renpy.with_statement(trans if trans is not None else store.smooth)


label dlc_black(secs=0.0):
    scene black with smooth
    if secs > 0.0:
        $ renpy.pause(secs)
    return
