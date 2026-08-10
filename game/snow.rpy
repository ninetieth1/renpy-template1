# ==========================================================
# game/snow.rpy
# «Девяностые» (c) MR LIMBO
#
# Снег на частицах вместо видео: в разы легче для телефона.
# story.rpy править не нужно, файл сам подменяет bg().
# ==========================================================

default persistent.snow_enabled = True

# Плотность. На телефоне автоматически меньше.
define SNOW_COUNT_PC = 90
define SNOW_COUNT_MOBILE = 45


init python:

    def snow_count():
        return SNOW_COUNT_MOBILE if renpy.variant("small") else SNOW_COUNT_PC

    # Снежинка рисуется кодом, картинка не нужна
    def make_flake(size, alpha):
        return Transform(Solid("#ffffff"), xysize=(size, size),
                         alpha=alpha, corner_radius=size / 2.0)


init python:

    snow_far = SnowBlossom(
        make_flake(4, 0.45),
        count=snow_count(),
        border=60,
        xspeed=(-30, 30),
        yspeed=(50, 110),
        start=2,
        fast=True)

    snow_near = SnowBlossom(
        make_flake(8, 0.70),
        count=int(snow_count() * 0.4),
        border=80,
        xspeed=(-60, 60),
        yspeed=(120, 220),
        start=2,
        fast=True)


image snow_layer = Fixed(snow_far, snow_near)


# ===== Уличные сцены =====
define SNOW_SCENES = set([
    "scene_19", "scene_20", "scene_21", "scene_22", "scene_23",
    "scene_24", "scene_25", "scene_26", "scene_27", "scene_28",
    "scene_29", "scene_30", "scene_31", "scene_36", "scene_37",
    "scene_38", "scene_39", "scene_40",
    "scene_2_1", "scene_2_2", "scene_2_3", "scene_2_5",
    "scene_2_5_5", "scene_2_6_6", "scene_2_7_7", "scene_2_8_8",
    "scene_2_10_10", "scene_2_10_11", "scene_2_12_12",
    "scene_finall",
])


init python:

    def snow_show():
        if persistent.snow_enabled:
            renpy.show_screen("snow_overlay")
        else:
            renpy.hide_screen("snow_overlay")

    def snow_hide():
        renpy.hide_screen("snow_overlay")

    def snow_toggle():
        persistent.snow_enabled = not persistent.snow_enabled
        if persistent.snow_enabled and store.snow_here:
            snow_show()
        else:
            snow_hide()


default snow_here = False


init 10 python:

    def bg(name, trans=None):
        renpy.scene()
        if renpy.has_image(name, exact=True):
            renpy.show(name)
        else:
            renpy.show("black")

        store.snow_here = (name in SNOW_SCENES)
        if store.snow_here:
            snow_show()
        else:
            snow_hide()

        renpy.with_statement(trans if trans is not None else store.smooth)


screen snow_overlay():
    zorder 90
    if persistent.snow_enabled:
        add "snow_layer"
