# ==========================================================
# game/social.rpy
# «Девяностые» (c) MR LIMBO
# Telegram, YouTube, «Поддержать» в главном меню.
# ==========================================================

define LINK_TG = "https://t.me/kievi_limbo"
define LINK_YT = "https://youtube.com/@mrlimbov"


screen social_row():

    hbox:
        xalign 0.03
        yalign 0.95
        spacing 26

        textbutton "✈":
            action OpenURL(LINK_TG)
            text_size 52
            text_color "#2aabee"
            text_hover_color "#ffffff"
            background None

        textbutton "▶":
            action OpenURL(LINK_YT)
            text_size 52
            text_color "#ff0033"
            text_hover_color "#ffffff"
            background None

        textbutton "♥":
            action Show("support_screen")
            text_size 52
            text_color "#ff5a82"
            text_hover_color "#ffffff"
            background None


screen support_screen():

    modal True
    zorder 270

    add Solid("#000000cc")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1120
        padding (60, 50, 60, 50)
        background Solid("#0a1018f5")

        vbox:
            spacing 18

            text "Поддержать создателя":
                xalign 0.5
                size 52
                color "#ffffff"

            null height 6

            text "«Девяностые» я делал один, по вечерам, без бюджета и без команды. Игра бесплатная и такой останется.":
                size 30
                color "#c3ced9"
                line_spacing 8

            text "Если история тебя зацепила, помочь можно так:":
                size 30
                color "#c3ced9"

            null height 4

            text "·  Написать мне в Telegram, я отвечаю всем":
                size 28
                color "#a9b6c2"

            text "·  Отправить звёзды Telegram или подарок":
                size 28
                color "#a9b6c2"

            text "·  Оставить честный отзыв и рассказать друзьям":
                size 28
                color "#a9b6c2"

            text "·  Подписаться на YouTube, там будет продолжение":
                size 28
                color "#a9b6c2"

            null height 10

            text "Любая поддержка много значит. Спасибо, что ты здесь.":
                size 28
                color "#00b3ff"

            null height 20

            hbox:
                xalign 0.5
                spacing 30

                textbutton "Telegram":
                    action OpenURL(LINK_TG)
                    text_size 34
                    text_color "#5c7a99"
                    text_hover_color "#ffffff"

                textbutton "YouTube":
                    action OpenURL(LINK_YT)
                    text_size 34
                    text_color "#5c7a99"
                    text_hover_color "#ffffff"

                textbutton "Закрыть":
                    action Hide("support_screen")
                    text_size 34
                    text_color "#46617a"
                    text_hover_color "#ffffff"
