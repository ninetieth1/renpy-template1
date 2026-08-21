# ==========================================================
# game/scripts/dlc_scene_map.rpy
# DLC «Сосновка» — единая карта кадров.
# Все кадры лежат в game/images/ как sc_*.png
# ==========================================================

init python:

    def dlc_show(name, trans=None):
        """
        Показывает кадр DLC по имени файла без расширения.
        Если файла нет, падаем в black, чтобы сборка не ломалась.
        """
        image_name = "images/%s.png" % name

        renpy.scene()

        if renpy.loadable(image_name):
            renpy.show(
                Transform(image_name, xysize=(1920, 1080), fit="cover", align=(0.5, 0.5)),
                what=None
            )
        else:
            if renpy.has_image("black", exact=True):
                renpy.show("black")
            else:
                renpy.scene()

        renpy.with_statement(trans if trans is not None else store.smooth)


label dlc_black(secs=0.0):
    scene black with smooth
    if secs > 0.0:
        $ renpy.pause(secs)
    return
