# Совместимость со старыми кнопками графики в меню DLC.
default persistent.dlc_graphics_quality = "medium"

init 192 python:
    def dlc_set_quality(value):
        # Настройки графики отключены: всегда используется стандартный средний режим.
        persistent.dlc_graphics_quality = "medium"
        renpy.save_persistent()
        renpy.restart_interaction()
