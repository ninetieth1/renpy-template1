# ==========================================================
# game/fixes.rpy
# «Девяностые» (c) MR LIMBO
#
# 1. Звук больше не тянется в следующие сцены:
#    каждый эффект обрезается по длине и глушится при
#    смене фона.
# 2. Титры закрываются сами, когда прокрутка дошла до конца.
#
# Файл ничего не заменяет вручную, просто лежит в game/.
# ==========================================================


# ===== Максимальная длина звуков, в секундах =====
define SFX_MAX = {
    "steps_snow.mp3": 3.0,
    "wind.mp3": 8.0,
    "game_beep.mp3": 1.5,
    "dogs.mp3": 3.0,
    "siren.mp3": 4.0,
    "fire.mp3": 5.0,
    "door.mp3": 2.0,
    "cough.mp3": 2.5,
    "paper.mp3": 2.5,
    "sleigh.mp3": 4.0,
    "hit.mp3": 2.0,
}


init 20 python:

    def sfx(name, volume=1.0):
        """Короткий звук. Обрезается, чтобы не тянуться в другие сцены."""
        p = "audio/sfx/" + name
        if not renpy.loadable(p):
            return
        cut = SFX_MAX.get(name)
        if cut:
            p = "<to %.2f>%s" % (cut, p)
        renpy.sound.play(p, channel="sound", relative_volume=volume)

    def sfx_stop(fade=0.3):
        renpy.sound.stop(channel="sound", fadeout=fade)


init 20 python:

    # Перекрываем bg() ещё раз, поверх snow.rpy:
    # при каждой смене кадра гасим хвост предыдущего звука.
    def bg(name, trans=None):

        renpy.sound.stop(channel="sound", fadeout=0.35)

        renpy.scene()
        if renpy.has_image(name, exact=True):
            renpy.show(name)
        else:
            renpy.show("black")

        try:
            store.snow_here = (name in SNOW_SCENES)
            if store.snow_here:
                snow_show()
            else:
                snow_hide()
        except Exception:
            pass

        renpy.with_statement(trans if trans is not None else store.smooth)


# ==========================================================
# Титры: длительность считается сама
# ==========================================================

init 200 python:

    def credits_height():
        h = 0
        for kind, val in CREDITS:
            if kind == "gap":
                h += int(val)
            elif kind == "head":
                h += 96
            elif kind == "title":
                h += 106
            elif kind == "name":
                h += 58
            elif kind == "small":
                h += 42
            else:
                h += 44
            h += 8
        return h

    CREDITS_SPEED = 95.0
    CREDITS_H = credits_height()
    CREDITS_TIME = (CREDITS_H + config.screen_height) / CREDITS_SPEED


init 200:

    transform credits_scroll:
        ypos config.screen_height
        linear CREDITS_TIME ypos -CREDITS_H

    screen credits_roll():

        modal True
        zorder 250

        add Solid("#000000")

        vbox:
            xalign 0.5
            spacing 8
            at credits_scroll

            for kind, val in CREDITS:

                if kind == "gap":
                    null height val

                elif kind == "head":
                    text val xalign 0.5 size 78 color "#ffffff" kerning 6

                elif kind == "title":
                    null height 26
                    text val xalign 0.5 size 34 color "#00b3ff" kerning 5
                    null height 10

                elif kind == "name":
                    text val xalign 0.5 size 42 color "#eef3f8"

                elif kind == "small":
                    text val xalign 0.5 size 26 color "#7f8c99"

                else:
                    text val xalign 0.5 size 27 color "#a9b6c2"

        # экран закрывается сам, когда прокрутка дошла до конца
        timer (CREDITS_TIME + 1.5) action Return(True)

        textbutton _("Пропустить"):
            xalign 0.98
            yalign 0.96
            action Return(True)
            text_size 26
            text_color "#46617a"
            text_hover_color "#ffffff"
