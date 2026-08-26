# ==========================================================
# game/scripts/dlc_sosnovka_2.rpy
# DLC «Сосновка» (c) MR LIMBO — часть 2, сцены 17-32
# ==========================================================

# Финальная сцена находится в label dlc_ch_stena.
# После её последней реплики она должна переходить в титры.

label dlc_ch_stena:
    $ dlc_show("sc_27_1")
    $ bgm("tension.mp3", 3.0)
    "Финальная сцена DLC завершена."
    $ persistent.dlc_completed = True
    $ renpy.save_persistent()
    scene black with Dissolve(1.5)
    jump dlc_credits
