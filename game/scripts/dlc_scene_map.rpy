# ==========================================================
# game/scripts/dlc_scene_map.rpy
# DLC «Сосновка» — единая карта кадров.
# Все кадры лежат в game/images/ как sc_*.png
# ==========================================================

init python:

    # Низкие: сначала рендерим кадр в 960x540, затем растягиваем до экрана.
    # Средние/высокие: полный размер экрана.
    _dlc_low_size = (960, 540)
    _dlc_screen_size = (config.screen_width, config.screen_height)

    def _dlc_scene_displayable(path):
        low = Transform(path, xysize=_dlc_low_size, fit="cover", align=(0.5, 0.5))
        normal = Transform(path, xysize=_dlc_screen_size, fit="cover", align=(0.5, 0.5))

        # Проверка выполняется при показе кадра, поэтому переключение качества
        # работает без перезапуска и после загрузки сохранения.
        return ConditionSwitch(
            "getattr(persistent, 'dlc_graphics_quality', 'medium') == 'low'",
            Transform(low, xysize=_dlc_screen_size, fit="fill"),
            "True",
            normal
        )

    # Регистрируем имя изображения, а не Transform в renpy.show().
    for _dlc_bg in renpy.list_files():
        if _dlc_bg.startswith("images/sc_") and _dlc_bg.endswith(".png") and "/" not in _dlc_bg[len("images/"):]:
            _dlc_name = _dlc_bg[len("images/"):-4]
            _dlc_displayable = _dlc_scene_displayable(_dlc_bg)
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
        """Показывает полноэкранный кадр DLC по имени файла без расширения."""
        image_path = "images/%s.png" % name

        renpy.scene()

        if renpy.loadable(image_path) and renpy.has_image(name, exact=True):
            renpy.show(name, layer="master")
        elif renpy.has_image("black", exact=True):
            renpy.show("black", layer="master")

        renpy.with_statement(trans if trans is not None else store.smooth)


label dlc_black(secs=0.0):
    scene black with smooth
    if secs > 0.0:
        $ renpy.pause(secs)
    return
