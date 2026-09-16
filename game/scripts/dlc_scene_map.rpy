# ==========================================================
# game/scripts/dlc_scene_map.rpy
# DLC «Сосновка» — единая карта кадров.
# Все кадры лежат в game/images/ как sc_*.png
# ==========================================================

init python:

    _dlc_low_size = (640, 360)
    _dlc_screen_size = (config.screen_width, config.screen_height)

    def _dlc_scene_displayable(path):
        # На «низких» кадр заранее уменьшается до 640x360: im.Scale
        # создаёт отдельную уменьшенную текстуру, поэтому рендер
        # действительно проще — экономит память и ускоряет слабые
        # устройства. Средние/Высокие показывают исходное качество.
        low_image = Transform(path, xysize=_dlc_low_size, fit="cover")
        low = Transform(low_image, xysize=_dlc_screen_size, fit="cover", align=(0.5, 0.5))
        normal = Transform(
            path,
            xysize=_dlc_screen_size,
            fit="cover",
            align=(0.5, 0.5)
        )

        return ConditionSwitch(
            "getattr(persistent, 'dlc_graphics_quality', 'medium') == 'low'",
            low,
            "True",
            normal
        )

    for _dlc_bg in renpy.list_files():
        if _dlc_bg.startswith("images/sc_") and _dlc_bg.endswith(".png") and "/" not in _dlc_bg[len("images/"):]:
            _dlc_name = _dlc_bg[len("images/"):-4]
            _dlc_displayable = _dlc_scene_displayable(_dlc_bg)
            renpy.image(_dlc_name, _dlc_displayable)

    def dlc_show(name, trans=None):
        image_path = "images/%s.png" % name

        # Как и bg() в основной игре: хвост предыдущего звука не тянется
        # в следующий кадр.
        renpy.sound.stop(channel="sound", fadeout=0.35)

        renpy.scene()
        if renpy.loadable(image_path) and renpy.has_image(name, exact=True):
            renpy.show(name, layer="master")
        elif renpy.has_image("black", exact=True):
            renpy.show("black", layer="master")

        # Снег включается только на уличных кадрах.
        try:
            store.snow_here = (name in SNOW_SCENES)
            if store.snow_here:
                snow_show()
            else:
                snow_hide()
        except Exception:
            pass

        # Кадр открыт по-настоящему — только теперь он попадает в «Я ютубер».
        try:
            yt_unlock([name])
        except Exception:
            pass

        renpy.with_statement(trans if trans is not None else store.smooth)


label dlc_black(secs=0.0):
    scene black with smooth
    if secs > 0.0:
        $ renpy.pause(secs)
    return
