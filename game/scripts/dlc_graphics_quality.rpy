# ==========================================================
# game/scripts/dlc_graphics_quality.rpy
# «Девяностые» (c) MR LIMBO
#
# Режимы графики: Низкие / Средние / Высокие.
#
#   Низкие  — эконом-режим для слабых телефонов:
#             · кадры сцен рендерятся через im.Scale 640x360
#               (см. dlc_scene_map.rpy);
#             · transitions выключены, анимации меню мгновенные;
#             · в меню DLC вместо видео — статичный кадр;
#             · снега в меню DLC нет, уличный снег прорежен;
#             · кэш картинок урезан со следующего запуска.
#   Средние — обычная игра, всё как задумано (по умолчанию).
#   Высокие — та же картинка, но в меню DLC метель:
#             густой снегопад с хлопьями, ветер ~15 м/с.
#
# ВАЖНО: в dlc_graphics_compat.rpy есть заглушка dlc_set_quality
# (init 192), которая всегда ставит «Средние». Наша версия ниже
# объявлена на init 250 и перекрывает её.
# ==========================================================

default persistent.dlc_graphics_quality = "medium"


init -20 python:

    def dlc_quality():
        v = getattr(persistent, "dlc_graphics_quality", "medium")
        return v if v in ("low", "medium", "high") else "medium"

    def dlc_quality_label():
        return {
            "low": u"Низкие",
            "medium": u"Средние",
            "high": u"Высокие",
        }.get(dlc_quality(), u"Средние")

    def dlc_quality_hint():
        return {
            "low": u"Быстрый режим: упрощённые кадры, без видео в меню, без снега в меню.",
            "medium": u"Обычная игра: всё как задумано, в меню DLC идёт снег.",
            "high": u"Та же картинка, но в меню DLC — метель с хлопьями.",
        }.get(dlc_quality(), u"")


init python:

    # Экономия памяти на слабых устройствах (размер кэша картинок).
    # Вступает в силу со следующего запуска игры.
    if dlc_quality() == "low":
        config.image_cache_size = 10


init 250 python:

    def dlc_set_quality(value):
        if value not in ("low", "medium", "high"):
            value = "medium"
        persistent.dlc_graphics_quality = value
        renpy.save_persistent()

        # На «низких» выключаем transitions — интерфейс проще и быстрее.
        try:
            renpy.run(Preference("transitions", "none" if value == "low" else "all"))
        except Exception:
            pass

        # Кэш картинок мог быть накачан под другой режим.
        try:
            renpy.free_memory()
        except Exception:
            pass

        renpy.restart_interaction()


    def dlc_is_completed():
        # Не используем общий persistent.completed: он мог быть выставлен
        # основной игрой или старым сохранением.
        return bool(getattr(persistent, "dlc_completed", False))


    def dlc_menu_snow():
        """Слой снега для меню DLC по текущему качеству."""
        q = dlc_quality()
        if q == "low":
            return None
        return snowstorm_layer("menu" if q == "medium" else "menu_high")
