# ==========================================================
# fnf_fix.rpy — патч экрана выбора трека (fnf_week)
# Исправляет:
#   1. Убирает жёлтый прямоугольник (#f2c14e) который перекрывал фон
#   2. Показывает персонажей прямо на фоне без цветной плашки
# Этот файл загружается ПОСЛЕ fnf.rpy (алфавитный порядок)
# и переопределяет screen fnf_week()
# ==========================================================

transform fnf_pulse:
    on show:
        easein 0.2 zoom 1.08
    on hide:
        easeout 0.15 zoom 1.0
    linear 0.5 zoom 1.0
    linear 0.5 zoom 1.06
    repeat

screen fnf_week():
    tag menu
    default sel = 0
    $ _nu = fnf_tracks_unlocked()
    $ _bg = "images/fnf/bg%d.png" % (sel + 1)

    # --- Фон: per-track или общий bg.png ---
    if renpy.loadable(_bg) and renpy.image_size(_bg)[0] > 100:
        add _bg
    elif renpy.loadable("images/fnf/bg.png"):
        add "images/fnf/bg.png"
    else:
        add Solid("#160f1f")

    # Лёгкое затемнение поверх фона
    add Solid("#00000088")

    # --- Шапка: НЕДЕЛЯ 1 ---
    frame:
        xfill True
        ypos 0
        ysize 54
        background Solid("#000000cc")
        text "НЕДЕЛЯ 1" size 34 color "#ffffff" xpos 20 yalign 0.5

    # --- Персонажи поверх фона (БЕЗ жёлтой плашки) ---
    if renpy.loadable("images/fnf/char_opponent.png"):
        add "images/fnf/char_opponent.png" xpos 0.17 xanchor 0.5 yalign 0.72 zoom 0.40
    if renpy.loadable("images/fnf/char_player.png"):
        add "images/fnf/char_player.png" xpos 0.50 xanchor 0.5 yalign 0.72 zoom 0.46
    if renpy.loadable("images/fnf/speakers.png"):
        add "images/fnf/speakers.png" xpos 0.83 xanchor 0.5 yalign 0.78 zoom 0.30
    if renpy.loadable("images/fnf/char_gf.png"):
        add "images/fnf/char_gf.png" xpos 0.83 xanchor 0.5 yalign 0.68 zoom 0.30

    # --- Название трека по центру внизу ---
    text fnf_track_title(sel):
        xalign 0.5
        yalign 0.86
        size 60
        color "#ffffff"
        outlines [ (4, "#2a0d1c", 0, 0) ]
        at fnf_pulse

    # --- Сложность ---
    vbox:
        xalign 0.97
        yalign 0.86
        text "СЛОЖНОСТЬ" size 22 color "#ffe08a" xalign 0.5
        text "1" size 54 color "#ffd23f" xalign 0.5

    # --- Список треков слева ---
    vbox:
        xpos 0.03
        yalign 0.88
        spacing 2
        text "ТРЕКИ" size 26 color "#ff5da2"
        for i in range(_nu):
            text ("%d. %s" % (i + 1, fnf_track_title(i))) size 18 color ("#ffffff" if i == sel else "#9a8fb0")

    # --- Кнопки влево/вправо ---
    textbutton "\u25c4":
        xpos 0.01
        yalign 0.5
        text_size 70
        text_color "#ffffff"
        text_hover_color "#ff5da2"
        action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel - 1) % _nu)]
    textbutton "\u25ba":
        xalign 0.99
        yalign 0.5
        text_size 70
        text_color "#ffffff"
        text_hover_color "#ff5da2"
        action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel + 1) % _nu)]

    # --- Кнопка ИГРАТЬ ---
    textbutton "ИГРАТЬ":
        xalign 0.5
        yalign 0.97
        xysize (360, 66)
        background Solid("#2e7d43")
        hover_background Solid("#46cc72")
        text_size 40
        text_color "#ffffff"
        text_xalign 0.5
        text_yalign 0.5
        action [Function(fnf_sfx, "sfx_confirm"), Return(sel)]

    # --- Кнопка Назад ---
    textbutton "\u25c4 Назад":
        xpos 0.01
        ypos 6
        text_size 24
        text_color "#ffd0d8"
        text_hover_color "#ffffff"
        action [Function(fnf_sfx, "sfx_cancel"), MainMenu(confirm=False)]

    # --- Клавиатурные хоткеи ---
    key "K_LEFT"  action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel - 1) % _nu)]
    key "K_RIGHT" action [Function(fnf_sfx, "sfx_scroll"), SetScreenVariable("sel", (sel + 1) % _nu)]
    key "K_RETURN" action [Function(fnf_sfx, "sfx_confirm"), Return(sel)]
