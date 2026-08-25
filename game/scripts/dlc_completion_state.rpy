# Отдельное состояние прохождения DLC.
# Не зависит от persistent.completed основной игры и старых сохранений.

default persistent.dlc_completed = False

init 401 python:
    _dlc_previous_label_callback = config.label_callback

    def _dlc_label_callback(label_name, abnormal):
        if _dlc_previous_label_callback is not None:
            _dlc_previous_label_callback(label_name, abnormal)
        if label_name == "dlc_ch_stena":
            persistent.dlc_completed = True
            renpy.save_persistent()

    config.label_callback = _dlc_label_callback
