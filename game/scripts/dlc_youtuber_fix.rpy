# Исправление поля ника в разделе «Я ЮТУБЕР».
# VariableInputValue обращается к переменной store, поэтому она
# должна быть объявлена глобально, а не только через screen default.

default yt_edit_name = ""

init 6 python:
    def yt_prepare_edit_name():
        store.yt_edit_name = persistent.yt_name or u"MR LIMBO"

    def yt_save_name_fixed(value):
        value = (value or "").strip() or u"MR LIMBO"
        persistent.yt_name = value[:32]
        store.yt_edit_name = persistent.yt_name
        renpy.save_persistent()

screen yt_name_input_fix():
    on "show" action Function(yt_prepare_edit_name)
