# ==========================================================
# game/animations.rpy
# Девяностые (c) MR LIMBO
#
# Минималистичный набор анимаций и переходов, который
# используют в большинстве визуальных новелл.
# ==========================================================


################################################################
# ПЕРЕХОДЫ
#   scene scene_7 with smooth
################################################################

# Мягкое растворение. Замена обычному dissolve.
define smooth = Dissolve(0.5)

# Быстрое растворение для реплик внутри одной локации
define quick = Dissolve(0.25)

# Медленное затемнение через чёрный: смена главы, скачок времени
define slowfade = Fade(0.8, 0.3, 0.8)

# Резкая вспышка белым: удар, испуг, воспоминание
define flashbang = Fade(0.1, 0.0, 0.4, color="#ffffff")

# Уход в чёрное и обратно, короткий
define blink = Fade(0.25, 0.1, 0.25)

# Сдвиг кадра вбок: смена ракурса
define slideleft = MoveTransition(0.6, enter=offscreenright, leave=offscreenleft)


################################################################
# АНИМАЦИИ ФОНА
#   scene scene_20 at kenburns with smooth
################################################################

# Медленный наезд. Самый ходовой приём: кадр перестаёт быть
# мёртвой картинкой.
transform kenburns(z=1.10, t=25.0):
    zoom 1.0
    linear t zoom z

# Медленный отъезд
transform kenburns_out(z=1.10, t=25.0):
    zoom z
    linear t zoom 1.0

# Панорама вправо / влево
transform pan_right(d=120, t=25.0):
    zoom 1.12 xoffset 0
    linear t xoffset -d

transform pan_left(d=120, t=25.0):
    zoom 1.12 xoffset -d
    linear t xoffset 0

# Еле заметное "дыхание" кадра. Ставить на статичные сцены.
transform breathe:
    zoom 1.0
    ease 6.0 zoom 1.02
    ease 6.0 zoom 1.0
    repeat

# Появление фона снизу вверх с растворением
transform bg_in:
    alpha 0.0 yoffset 24
    parallel:
        linear 0.6 alpha 1.0
    parallel:
        ease 0.9 yoffset 0


################################################################
# ТРЯСКА И УДАРЫ
#   show scene_29 at shake_hard
################################################################

transform shake(n=8, amp=14):
    subpixel True
    block:
        linear 0.03 xoffset amp
        linear 0.03 xoffset -amp
        repeat n
    linear 0.03 xoffset 0

transform shake_hard:
    subpixel True
    block:
        linear 0.02 xoffset 30 yoffset -12
        linear 0.02 xoffset -26 yoffset 10
        linear 0.02 xoffset 18 yoffset -6
        repeat 6
    linear 0.04 xoffset 0 yoffset 0


################################################################
# ПЕРСОНАЖИ И СПРАЙТЫ
#   show andrey at char_in_left
################################################################

transform char_in_left:
    xalign 0.25 yalign 1.0
    alpha 0.0 xoffset -60
    parallel:
        linear 0.45 alpha 1.0
    parallel:
        ease 0.55 xoffset 0

transform char_in_right:
    xalign 0.75 yalign 1.0
    alpha 0.0 xoffset 60
    parallel:
        linear 0.45 alpha 1.0
    parallel:
        ease 0.55 xoffset 0

# Говорящий на свету, молчащий притемнён
transform speaking:
    matrixcolor BrightnessMatrix(0.0)
    linear 0.25 zoom 1.0

transform silent:
    matrixcolor BrightnessMatrix(-0.28)
    linear 0.25 zoom 0.98


################################################################
# ТЕКСТОВЫЕ КАРТОЧКИ
################################################################

# Плавное появление и уход надписи вроде "Новый день"
transform card_in:
    alpha 0.0
    linear 0.7 alpha 1.0

transform card_out:
    linear 0.7 alpha 0.0

# Мигающий указатель "дальше"
transform blink_soft:
    alpha 0.25
    linear 0.8 alpha 1.0
    linear 0.8 alpha 0.25
    repeat
