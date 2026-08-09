## ==========================================================
## game/options.rpy
## Девяностые (c) MR LIMBO
## ==========================================================

## Basics ######################################################################

define config.name = _("Девяностые")

define gui.show_name = True

## Версия игры. В разделе "Об игре" выводится как Release 1.0.
define config.version = "1.0" # x-release-please-version

## Текст в разделе "Об игре".
## Никакого {b}: в kazmann-sans нет жирного начертания, движок
## подделывает его сдвигом глифа и текст плывёт.
define gui.about = _p("""
История о мальчике Андрее, который зимой уходит за двадцать восемь километров в чужую деревню, чтобы достать лекарство для младшей сестры. Дойти он должен до темноты.

Что нового в Release 1.0:

·  История полностью проходима от начала до обоих финалов
·  Новое диалоговое окно и переработанное главное меню
·  Аккуратные настройки: скорость текста, авто-режим, пропуск, громкость
·  Автосохранение каждые две минуты
·  Быстрое меню: возврат к прошлой реплике, история, авто, пропуск
·  Плавные переходы и анимации сцен
·  Читаемая газета с прокруткой
·  Починено удержание экрана: корректно работает и мышью, и пальцем
·  Убрана ритм-мини-игра и всё, что было с ней связано
·  Сборки под ПК и Android

Автор: MR LIMBO

Спасибо, что играешь. Если не сложно, оставь честный отзыв.
""")

## Короткое имя для файлов сборки. Только ASCII, без пробелов.
define build.name = "Ninetieth"


## Sounds and music ############################################################

define config.has_sound = True
define config.has_music = True
define config.has_voice = True

define config.main_menu_music = "audio/menu.mp3"


## Transitions #################################################################

define config.enter_transition = dissolve
define config.exit_transition = dissolve
define config.intra_transition = dissolve
define config.after_load_transition = None
define config.end_game_transition = None


## Window management ###########################################################

define config.window = "auto"

define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)


## Preference defaults #########################################################

## 20 знаков в секунду это очень медленно для длинных описаний.
default preferences.text_cps = 40
default preferences.afm_time = 15


## Save directory ##############################################################
##
## Менять после релиза нельзя: игроки потеряют сохранения.
## Сейчас, до 1.0, самое время поставить нормальное имя.

define config.save_directory = "Ninetieth-Devyanostye"


## Icon ########################################################################

define config.window_icon = "gui/window_icon.png"


## Build configuration #########################################################

init python:

    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)

    ## Заметки и README в сборку не тащим
    build.classify('**.md', None)

    build.documentation('*.html')
    build.documentation('*.txt')


## Google Play ключ, если будешь выкладывать в Play
# define build.google_play_key = "..."

## itch.io: username/project. ПОДСТАВЬ СВОЙ, тут заглушка.
define build.itch_project = "mrlimbo/devyanostye"
