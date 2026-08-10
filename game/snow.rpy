# ==========================================================
# game/snow.rpy
# «Девяностые» (c) MR LIMBO
#
# Снег на частицах. Лёгкий, без видео.
# story.rpy править не нужно, файл сам подменяет bg().
# ==========================================================

default persistent.snow_enabled = True

define SNOW_COUNT_PC = 80
define SNOW_COUNT_MOBILE = 40


init python:

    snow_ok = False

    try:
        _n = SNOW_COUNT_MOBILE if renpy.variant("small") else SNOW_COUNT_PC

        _flake_far = Transform(Solid("#ffffff"), xysize=(4, 4), alpha=0.45)
        _flake_near = Transform(Solid("#ffffff"), xysize=(7, 7), alpha=0.70)

        snow_far = SnowBlossom(_flake_far,
                               count=_n,
                               border=60,
                               xspeed=(-30, 30),
                               yspeed=(50, 110),
                               start=2,
                               fast=True)

        snow_near = SnowBlossom(_flake_near,
                                count=int(_n * 0.4),
                                border=80,
                                xspeed=(-60, 60),
                                yspeed=(120, 220),
                                start=2,
                                fast=True)

        renpy.image("snow_layer", Fixed(snow_far, snow_near))
        snow_ok = True

    except Exception:
        snow_ok = False


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


default snow_here = False


init python:

    def snow_show():
        if snow_ok and persistent.snow_enabled:
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
    if snow_ok and persistent.snow_enabled:
        add "snow_layer"
