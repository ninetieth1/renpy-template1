################################################################################
## ui_overrides.rpy — Панель, кнопки, убираем артефакты
################################################################################

init offset = 1

################################################################################
## Задача 5: Полупрозрачная панель за кнопками навигации
################################################################################

style main_menu_frame:
    xsize 420
    yfill True
    ## Убираем дефолтный PNG-оверлей, ставим полупрозрачный чёрный
    background Frame(Solid("#00000050"), Borders(0,0,0,0))


################################################################################
## Задача 6: Убираем артефакты дефолтных рамок
################################################################################

style game_menu_outer_frame:
    bottom_padding 45
    top_padding 180
    ## Убираем game_menu.png overlay, ставим полупрозрачный тёмный
    background Frame(Solid("#050a14e6"), Borders(0,0,0,0))


################################################################################
## Задача 7: Красивые кнопки с эффектами
################################################################################

## Навигационные кнопки — подсветка + лёгкий сдвиг

style navigation_button:
    size_group "navigation"
    left_padding 16
    right_padding 16
    top_padding 8
    bottom_padding 8
    hover_background Frame(Solid("#00b3ff18"), Borders(4,4,4,4))
    selected_background Frame(Solid("#00b3ff10"), Borders(4,4,4,4))

style navigation_button_text:
    size gui.interface_text_size
    idle_color "#7a8fa8"
    hover_color "#47a6ff"
    selected_color "#00b3ff"
    insensitive_color "#3a4d637f"
    ## Эффект подсветки через outlines (лёгкое свечение)
    hover_outlines [(0, "#47a6ff40", 2, 2)]
    selected_outlines [(0, "#00b3ff30", 2, 2)]


################################################################################
## Задача 8: Дополнительные фиксы
################################################################################

## Фон игрового меню — тёмный вместо дефолтного PNG
init python:
    gui.game_menu_background = "#05070d"

## Убираем рамки у фреймов (дефолтный frame.png даёт полосы)
style frame:
    padding gui.frame_borders.padding
    background Frame(Solid("#0a1628c0"), gui.frame_borders)

## Confirm фрейм — чистый тёмный без полос
style confirm_frame:
    padding gui.confirm_frame_borders.padding
    background Frame(Solid("#0a1a2ef0"), gui.confirm_frame_borders)
    xalign 0.5
    yalign 0.5

## Quick menu кнопки — немного крупнее для тача
style quick_button_text:
    size 24
    idle_color "#5c7a99"
    hover_color "#47a6ff"
    selected_color "#00b3ff"
