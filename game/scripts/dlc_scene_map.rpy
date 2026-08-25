# ==========================================================
# game/scripts/dlc_scene_map.rpy
# DLC «Сосновка» — единая карта кадров.
# ==========================================================

init python:

    _dlc_low_size = (640, 360)
    _dlc_screen_size = (config.screen_width, config.screen_height)

    def _dlc_scene_displayable(path):
        # im.Scale создаёт отдельную уменьшенную текстуру, а не просто
        # меняет размер вывода. Поэтому на низких качество действительно ниже.
        low_image = im.Scale(path, _dlc_low_size[0], _dlc_low_size[1])
        low = Transform(low_image, xysize=_dlc_screen_size, fit="cover", align=(0.5, 0.5))
        normal = Transform(path, xysize=_dlc_screen_size, fit="cover", align=(0.5, 0.5))

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

            if _dlc_name.startswith("sc_"):
                _dlc_suffix = _dlc_name[3:]
                if _dlc_suffix.isdigit() and 17 <= int(_dlc_suffix) <= 32:
                    renpy.image("dlc_s" + _dlc_suffix, _dlc_displayable)

    if renpy.has_image("sc_32", exact=True):
        renpy.image("dlc_s32_end", "sc_32")

    def dlc_show(name, trans=None):
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
