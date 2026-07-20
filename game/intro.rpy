# ==========================================================
# game/intro.rpy — интро, загрузка, плашка (держать 5 сек),
# тексты перед игрой/DLC, текст "Об игре"
# ==========================================================

# Видео-интро: положи файл в game/videos/intro.webm
define MY_INTRO_VIDEO = "video/intro.webm"
# Сколько секунд крутится "ЗАГРУЗКА..." после видео
define MY_LOAD_SECONDS = 5.0
# Сколько секунд надо ДЕРЖАТЬ экран, чтобы плашка исчезла
define MY_HOLD_SECONDS = 5.0

# ===== ТВОИ ТЕКСТЫ (пока заглушки — пришли свои, я перепишу) =====
define MY_TEXT_AFTER_LOAD = "Здесь будет твой текст после загрузки.\nЧтобы продолжить — зажми экран и держи."
define MY_TEXT_BEFORE_GAME = "Здесь будет твой текст перед началом новой игры."
define MY_TEXT_BEFORE_DLC = "Здесь будет твой текст перед входом в DLC."

init 999 python:
    # Текст во вкладке "Об игре" (пришли свой — перепишу)
    gui.about = _(u"""«Девяностые» — визуальная новелла.

Здесь будет твой текст об игре.""")

# ===== Запуск игры: видео -> загрузка -> плашка с текстом =====
label splashscreen:
    if renpy.loadable(MY_INTRO_VIDEO):
        $ renpy.movie_cutscene(MY_INTRO_VIDEO)
    scene expression Solid("#000000")
    show screen my_loading
    $ renpy.pause(MY_LOAD_SECONDS, hard=True)
    hide screen my_loading
    call screen my_hold_text(MY_TEXT_AFTER_LOAD)
    return

transform my_blink:
    linear 0.6 alpha 0.3
    linear 0.6 alpha 1.0
    repeat

screen my_loading():
    add Solid("#000000")
    text "ЗАГРУЗКА..." xalign 0.5 yalign 0.5 size 44 color "#ffffff" at my_blink

# ===== Плашка: исчезает, только если держать экран 5 секунд =====
screen my_hold_text(txt=""):
    modal True
    default held = 0.0
    default holding = False

    add Solid("#000000")

    frame:
        xalign 0.5
        yalign 0.38
        xsize int(config.screen_width * 0.82)
        padding (44, 34)
        background Solid("#141018")
        text "[txt]" size 30 color "#ffffff" xalign 0.5 text_align 0.5

    text "ЗАЖМИ ЭКРАН И ДЕРЖИ [MY_HOLD_SECONDS:.0f] СЕК":
        xalign 0.5
        yalign 0.78
        size 26
        color "#ffd0d8"

    bar:
        value StaticValue(held, MY_HOLD_SECONDS)
        xalign 0.5
        yalign 0.86
        xsize int(config.screen_width * 0.6)

    button:
        xfill True
        yfill True
        background None
        action NullAction()
        hovered SetScreenVariable("holding", True)
        unhovered SetScreenVariable("holding", False)

    timer 0.1 repeat True action If(holding,
        SetScreenVariable("held", min(MY_HOLD_SECONDS, held + 0.1)),
        SetScreenVariable("held", 0.0))

    if held >= MY_HOLD_SECONDS:
        timer 0.05 action Return(True)

# ===== Чёрный экран с текстом (перед игрой и перед DLC) =====
label my_disclaimer(txt=""):
    scene expression Solid("#000000")
    "[txt]"
    return
