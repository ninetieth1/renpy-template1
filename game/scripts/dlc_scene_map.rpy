# ==========================================================
# game/scripts/dlc_scene_map.rpy
# DLC «Сосновка» — единая карта кадров.
# Все кадры лежат в game/images/ как sc_*.png
# ==========================================================

init python:

    def dlc_show(name, trans=None):
        """
        Показывает кадр DLC по имени файла без расширения.
        Если файла нет, используем чёрный фон.
        """
        image_path = "images/%s.png" % name

        renpy.scene()

        if renpy.loadable(image_path):
            # Файлы в game/images автоматически регистрируются Ren'Py
            # под именем файла без расширения, например sc_1.
            renpy.show(name)
        elif renpy.has_image("black", exact=True):
            renpy.show("black")

        renpy.with_statement(trans if trans is not None else store.smooth)


label dlc_black(secs=0.0):
    scene black with smooth
    if secs > 0.0:
        $ renpy.pause(secs)
    return
