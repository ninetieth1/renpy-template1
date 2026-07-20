# ==========================================================
# game/intro.rpy — ключи доступа, интро, загрузка, плашка,
# тексты перед игрой/DLC, "Об игре", тизер DLC «Советские 90-е»
# ==========================================================

# ===== КЛЮЧИ ДОСТУПА =====
# Впиши свои ключи в кавычках, через запятую. Регистр и пробелы не важны.
define MY_KEYS = ["ADP-7XQ9-KM4N-V2RT-J8WP", "ALN-4PZF-8YQ2-MX7K-T5RD", "ALX-9VHK-3QPM-W8T2-NY6F", "DEV-0X9M-Q7LF-2KWR-Z8PA", "GIFT-6NRQ-W3XJ-K9TM-P4VH", "NNF-5TQ8-LW3P-X7RK-M2DZ", "DNL-8YRP-V6QM-K3TX-F9WA"]

# Видео-интро: файл game/video/intro.webm
define MY_INTRO_VIDEO = "video/intro.webm"
define MY_LOAD_SECONDS = 5.0
define MY_HOLD_SECONDS = 5.0

# ===== ТЕКСТ: плашка после загрузки =====
define MY_TEXT_AFTER_LOAD = "Дорогой контент-креатор!\n\nМы безумно рады, что ты решил заглянуть в нашу игру — для нас это очень много значит, и мы бесконечно благодарны.\n\nЭто бета-версия: в игре могут встречаться баги. Именно благодаря твоим видео мы их найдём и исправим.\n\nСпасибо, что согласился сыграть. Устраивайся поудобнее… Камера. Мотор. ДЕВЯНОСТЫЕ!"

# ===== ТЕКСТ: перед новой игрой (3 экрана) =====
define MY_TEXT_BEFORE_GAME = [
    "Пара слов перед стартом.\n\nНе все механики, о которых говорилось в Telegram-канале, попали в эту версию — возникли некоторые сложности. Пожалуйста, не считай это за минус: всё лучшее впереди.",
    "Основной сюжет займёт примерно 30–40 минут. После финала тебя ждёт бонус — DLC PLUS и немного дополнительной информации.",
    "Это моя первая полноценная игра, которую я разрабатывал практически в одиночку — со мной была лишь пара верных помощников. Озвучка остальных персонажей появится после релиза.\n\nОценивай честно и справедливо — и обязательно скажи, что стоит сделать лучше, а что не стоит. Приятной игры!",
]

# ===== ТЕКСТ: перед входом в DLC (3 экрана) =====
define MY_TEXT_BEFORE_DLC = [
    "Поздравляем — основной сюжет «Девяностых» пройден!\n\nТы достойно дошёл до конца, и в награду открывается DLC PLUS.",
    "Важно: DLC PLUS никак не связан с основным сюжетом. Это отдельная мини-игра, которую я долго и с душой разрабатывал, чтобы порадовать тебя.",
    "Я искренне благодарен каждому, кто играет в мои проекты, — вы делаете для меня очень много, и я вас по-настоящему уважаю. Надеюсь, эта мини-игра подарит тебе нотку приятной теплоты… и немного напряжения.\n\nИграй и будь счастлив. И следи за новыми проектами в моём Telegram-канале!",
]

# ===== ТЕКСТ: тизер будущего DLC =====
define MY_DLC2_INFO = "Крупное обновление с DLC «Советские 90-е» выйдет ориентировочно в сентябре — ноябре и будет доступно ВСЕМ игрокам.\n\nСледи за новостями в Telegram-канале!"

init 999 python:
    gui.about = _(u"""«Девяностые» — визуальная новелла.

Это специальная БЕТА-ВЕРСИЯ для контент-креаторов и ютуберов. Финальный релиз может заметно отличаться — многое будет доработано и исправлено.

Мы будем очень рады, если вы поможете нашему проекту стать лучше. Ваши видео и отзывы — лучшая поддержка!""")

init python:
    def my_key_check(k):
        k = k.strip().upper().replace(" ", "")
        for good in MY_KEYS:
            if k == good.strip().upper().replace(" ", ""):
                return True
        return False

# ===== Запуск: ключ -> видео -> загрузка -> плашка -> музыка меню =====
label splashscreen:
    if not persistent.my_key_ok:
        call screen my_key_entry
    if renpy.loadable(MY_INTRO_VIDEO):
        $ renpy.movie_cutscene(MY_INTRO_VIDEO)
    scene expression Solid("#000000")
    show screen my_loading
    $ renpy.pause(MY_LOAD_SECONDS, hard=True)
    hide screen my_loading
    call screen my_hold_text(MY_TEXT_AFTER_LOAD)
    play music "audio/menu.mp3" fadein 1.0
    return

# ===== Экран ввода ключа =====
screen my_key_entry():
    modal True
    default key_text = ""
    default key_err = False

    add Solid("#000000")

    vbox:
        xalign 0.5
        yalign 0.40
        spacing 26

        text "ВВЕДИ КЛЮЧ ДОСТУПА" xalign 0.5 size 44 color "#ffffff" font "kazmann-sans.ttf"
        text "Ключ выдаётся вместе с игрой" xalign 0.5 size 24 color "#8899aa"

        frame:
            xalign 0.5
            xsize int(config.screen_width * 0.55)
            padding (24, 18)
            background Solid("#141822")
            input:
                value ScreenVariableInputValue("key_text")
                length 40
                size 34
                color "#ffffff"
                xalign 0.5

        if key_err:
            text "Неверный ключ. Проверь и попробуй ещё раз." xalign 0.5 size 26 color "#ff6b6b"

        textbutton "ВОЙТИ":
            xalign 0.5
            text_size 38
            action If(my_key_check(key_text),
                [SetField(persistent, "my_key_ok", True), Return(True)],
                SetScreenVariable("key_err", True))

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

# ===== Чёрный экран с текстом (поддерживает несколько страниц) =====
label my_disclaimer(txt=""):
    scene expression Solid("#000000")
    python:
        _my_pages = txt if isinstance(txt, list) else [txt]
    $ _my_i = 0
    while _my_i < len(_my_pages):
        $ renpy.say(None, _my_pages[_my_i])
        $ _my_i += 1
    return

# ===== Тизер DLC «Советские 90-е» =====
screen soviet_dlc_teaser():
    modal True
    zorder 200
    button:
        xfill True
        yfill True
        background Solid("#000000b0")
        action Hide("soviet_dlc_teaser")
    frame:
        xalign 0.5
        yalign 0.5
        xsize int(config.screen_width * 0.62)
        padding (40, 36)
        background Solid("#10141e")
        vbox:
            spacing 24
            xfill True
            text "DLC: СОВЕТСКИЕ 90-е" xalign 0.5 size 44 color "#f2c14e" font "kazmann-sans.ttf"
            text "СКОРО…" xalign 0.5 size 34 color "#ffffff"
            hbox:
                xalign 0.5
                spacing 50
                textbutton "ПОДРОБНО" text_size 30 action [Hide("soviet_dlc_teaser"), Show("soviet_dlc_info")]
                textbutton "ЗАКРЫТЬ" text_size 30 action Hide("soviet_dlc_teaser")

screen soviet_dlc_info():
    modal True
    zorder 200
    button:
        xfill True
        yfill True
        background Solid("#000000b0")
        action Hide("soviet_dlc_info")
    frame:
        xalign 0.5
        yalign 0.5
        xsize int(config.screen_width * 0.66)
        padding (40, 36)
        background Solid("#10141e")
        vbox:
            spacing 24
            xfill True
            text "DLC: СОВЕТСКИЕ 90-е" xalign 0.5 size 40 color "#f2c14e" font "kazmann-sans.ttf"
            text "[MY_DLC2_INFO]" xalign 0.5 size 28 color "#ffffff" text_align 0.5
            textbutton "ЗАКРЫТЬ" xalign 0.5 text_size 30 action Hide("soviet_dlc_info")
