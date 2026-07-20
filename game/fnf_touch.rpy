# ==========================================================
# game/fnf_touch.rpy — МУЛЬТИТАЧ v2
# Ren'Py по умолчанию не передаёт события пальцев в мини-игру.
# Эта настройка включает их. Больше ничего не нужно.
# ==========================================================

init python:
    import pygame
    config.pygame_events.extend([
        pygame.FINGERDOWN,
        pygame.FINGERUP,
        pygame.FINGERMOTION,
    ])
