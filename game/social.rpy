# ==========================================================
# game/social.rpy
# «Девяностые» (c) MR LIMBO
#
# Кнопки Telegram, YouTube, «Поддержать» в главном меню.
# Иконки рисуются кодом, картинки не нужны.
# ==========================================================

define LINK_TG = "https://t.me/kievi_limbo"
define LINK_YT = "https://youtube.com/@mrlimbov"


init python:

    class SocialIcon(renpy.Displayable):
        """kind: tg | yt | heart"""

        def __init__(self, kind, size=64, alpha=0.8, **kw):
            renpy.Displayable.__init__(self, **kw)
            self.kind = kind
            self.size = int(size)
            self.alpha = alpha

        def render(self, width, height, st, at):
            s = self.size
            r = renpy.Render(s, s)
            c = r.canvas()
            a = int(255 * self.alpha)

            if self.kind == "tg":
                c.circle((42, 171, 238, a), (s // 2, s // 2), s // 2, 0)
                p = lambda x, y: (int(x * s / 512.0), int(y * s / 512.0))
                c.polygon((255, 255, 255, a),
                          [p(108, 246), p(404, 132), p(352, 392), p(216, 322)], 0)
                c.polygon((205, 228, 243, a),
                          [p(216, 322), p(352, 392), p(232, 386)], 0)

            elif self.kind == "yt":
                c.rect((255, 0, 51, a), (0, int(s * 0.18), s, int(s * 0.64)))
                p = lambda x, y: (int(x * s / 512.0), int(y * s / 512.0))
                c.polygon((255, 255, 255, a),
                          [p(212, 176), p(212, 336), p(348, 256)], 0)

            else:
                rad = int(s * 0.17)
                c.circle((255, 90, 130, a), (int(s * 0.34), int(s * 0.38)), rad, 0)
                c.circle((255, 90, 130, a), (int(s * 0.66), int(s * 0.38)), rad, 0)
                c.polygon((255, 90, 130, a),
                          [(int(s * 0.16), int(s * 0.44)),
                           (int(s * 0.84), int(s * 0.44)),
                           (int(s * 0.50), int(s * 0.84))], 0)

            return r


screen social_row():

    zorder 60

    if main_menu:

        hbox:
            xalign 0.02
            yalign 0.96
            spacing 20

            button:
                action OpenURL(LINK_TG)
                idle_child SocialIcon("tg", 64, 0.75)
                hover_child SocialIcon("tg", 70, 1.0)
                background None

            button:
                action OpenURL(LINK_YT)
                idle_child SocialIcon("yt", 64, 0.75)
                hover_child SocialIcon("yt", 70, 1.0)
                background None

            button:
                action Show("support_screen")
                idle_child SocialIcon("heart", 64, 0.75)
                hover_child SocialIcon("heart", 70, 1.0)
                background None

init python:
    config.overlay_screens.append("social_row")


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
            spacing 20

            text _("Поддержать создателя"):
                xalign 0.5
                size 52
                color "#ffffff"

            null height 6

            text _("«Девяностые» я делал один, по вечерам, без бюджета и без команды. Игра бесплатная и такой останется."):
                size 30
                color "#c3ced9"
                line_spacing 8
                justify True

            text _("Если история тебя зацепила, помочь можно так:"):
                size 30
                color "#c3ced9"

            null height 4

            text _("·  Написать мне в Telegram, я отвечаю всем"):
                size 28
                color "#a9b6c2"
            text _("·  Отправить звёзды Telegram или подарок"):
                size 28
                color "#a9b6c2"
            text _("·  Оставить честный отзыв и рассказать друзьям"):
                size 28
                color "#a9b6c2"
            text _("·  Подписаться на YouTube, там будет продолжение"):
                size 28
                color "#a9b6c2"

            null height 10

            text _("Любая поддержка много значит. Спасибо, что ты здесь."):
                size 28
                color "#00b3ff"

            null height 20

            hbox:
                xalign 0.5
                spacing 30

                textbutton _("Telegram"):
                    action OpenURL(LINK_TG)
                    text_size 34
                    text_color "#5c7a99"
                    text_hover_color "#ffffff"

                textbutton _("YouTube"):
                    action OpenURL(LINK_YT)
                    text_size 34
                    text_color "#5c7a99"
                    text_hover_color "#ffffff"

                textbutton _("Закрыть"):
                    action Hide("support_screen")
                    text_size 34
                    text_color "#46617a"
                    text_hover_color "#ffffff"
