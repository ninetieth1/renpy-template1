# ==========================================================
# game/game_flow.rpy
# Возрастное предупреждение, отметка о прохождении, отзыв.
# ==========================================================

default persistent.completed = False

# ПОДСТАВЬ СВОЮ ССЫЛКУ НА СТРАНИЦУ ИГРЫ
define REVIEW_URL = "https://rustore.ru/"


screen age_gate():

    modal True
    zorder 260

    add Solid("#000000")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 26
        xsize 1300

        text "16+":
            xalign 0.5
            size 130
            color "#ff2b3d"
            kerning 6

        text _("Игра содержит сцены, не предназначенные для детей: болезнь, смерть, насилие и нецензурную лексику."):
            xalign 0.5
            text_align 0.5
            size 34
            color "#eef3f8"
            line_spacing 8

        text _("Все события вымышлены."):
            xalign 0.5
            size 26
            color "#7f8c99"

        null height 30

        textbutton _("Мне есть 16"):
            xalign 0.5
            action Return(True)
            text_size 38
            text_color "#5c7a99"
            text_hover_color "#ffffff"


screen completed_badge():
    zorder 50
    if persistent.completed and main_menu:
        vbox:
            xalign 0.5
            yalign 0.90
            spacing 6
            text _("Игра пройдена"):
                xalign 0.5
                size 28
                color "#00b3ff"
            textbutton _("Оставить отзыв"):
                xalign 0.5
                action OpenURL(REVIEW_URL)
                text_size 26
                text_color "#5c7a99"
                text_hover_color "#ffffff"

init python:
    config.overlay_screens.append("completed_badge")


label age_gate:
    $ quick_menu = False
    call screen age_gate
    $ quick_menu = True
    return
