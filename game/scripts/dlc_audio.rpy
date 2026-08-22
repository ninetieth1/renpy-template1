# ==========================================================
# game/scripts/dlc_audio.rpy
# Отдельная звуковая система DLC.
# ==========================================================

init 300 python:

    _dlc_audio_active = False
    _dlc_current_label = None
    _dlc_previous_label_callback = config.label_callback

    _dlc_class_labels = {
        "dlc_ch_urok",
        "dlc_ch_deeprichastie",
        "dlc_ch_proekt",
        "dlc_ch_pustaya_parta",
        "dlc_ch_golos",
    }

    _dlc_hall_labels = {
        "dlc_ch_priglashenie",
        "dlc_ch_direktor",
        "dlc_ch_za_dveryu",
        "dlc_ch_nastoyashiy_direktor",
    }

    _dlc_winter_labels = {
        "dlc_ch_doroga",
        "dlc_ch_ponedelnik",
        "dlc_ch_sluhi",
        "dlc_ch_krylco",
        "dlc_ch_kino",
        "dlc_ch_muzhik",
        "dlc_ch_peshkom",
        "dlc_ch_stena",
    }

    def _dlc_play_soundtrack():
        tracks = ["audio/d1.mp3", "audio/d2.mp3"]
        renpy.random.shuffle(tracks)
        renpy.music.play(
            tracks,
            channel="music",
            loop=True,
            fadein=2.0,
            relative_volume=0.25
        )

    def _dlc_set_ambience(label_name):
        ambience = None
        volume = 0.0

        if label_name in _dlc_class_labels:
            ambience = "audio/class.mp3"
            volume = 0.22
        elif label_name in _dlc_hall_labels:
            ambience = "audio/hall.mp3"
            volume = 0.20
        elif label_name in _dlc_winter_labels:
            ambience = "audio/winter.mp3"
            volume = 0.28

        if ambience and renpy.loadable(ambience):
            renpy.music.play(
                ambience,
                channel="ambient",
                loop=True,
                fadein=1.0,
                fadeout=1.0,
                relative_volume=volume
            )
        else:
            renpy.music.stop(channel="ambient", fadeout=1.0)

    def _dlc_label_audio(label_name, abnormal):
        global _dlc_audio_active, _dlc_current_label

        if _dlc_previous_label_callback is not None:
            _dlc_previous_label_callback(label_name, abnormal)

        if label_name.startswith("dlc_"):
            _dlc_current_label = label_name

            if not _dlc_audio_active:
                _dlc_audio_active = True
                _dlc_play_soundtrack()

            _dlc_set_ambience(label_name)

        elif label_name in ("start", "story_start") and _dlc_audio_active:
            _dlc_audio_active = False
            _dlc_current_label = None
            renpy.music.stop(channel="ambient", fadeout=1.0)

    config.label_callback = _dlc_label_audio

    # Старые story.mp3 и tension.mp3 остаются для основной игры,
    # но вызовы из DLC больше не могут заменить d1/d2.
    _base_bgm = bgm
    _base_bgm_stop = bgm_stop
    _base_sfx = sfx

    def bgm(name, fade=2.0):
        if not _dlc_audio_active:
            _base_bgm(name, fade)

    def bgm_stop(fade=2.0):
        if not _dlc_audio_active:
            _base_bgm_stop(fade)

    def sfx(name, volume=1.0):
        if _dlc_audio_active and (
            name == "school_bell.mp3" or
            (name == "game_beep.mp3" and _dlc_current_label == "dlc_ch_pustaya_parta")
        ):
            if renpy.loadable("audio/bell.mp3"):
                renpy.sound.play(
                    "audio/bell.mp3",
                    channel="sound",
                    relative_volume=volume
                )
        else:
            _base_sfx(name, volume)
