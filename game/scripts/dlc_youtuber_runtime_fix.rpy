# Безопасное окно ввода ника.
# renpy.input нельзя запускать прямо внутри Function из screen interaction.

init 10 python:
    def yt_edit_nickname():
        renpy.call_in_new_context("yt_nickname_prompt")

label yt_nickname_prompt:
    $ _yt_new_name = renpy.input(
        u"Введи ник:",
        default=persistent.yt_name or u"MR LIMBO",
        length=32,
        allow="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-"
    )
    $ persistent.yt_name = ((_yt_new_name or "").strip() or u"MR LIMBO")[:32]
    $ renpy.save_persistent()
    return
