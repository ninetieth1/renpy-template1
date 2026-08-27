# ==========================================================
# game/snowstorm.rpy
# «Девяностые» (c) MR LIMBO
#
# Реалистичный снег на своём движке:
#   · хлопья-пух и кристаллы (images/snow_puff.png, snow_crystal.png)
#   · три плана глубины: дальний мелкий тусклый, ближний крупный
#   · порывистый ветер (базовый сдвиг + две синусоиды с разными
#     периодами — интегрируются аналитически, поэтому движение
#     детерминировано и не боится сохранений)
#   · покачивание каждого хлопка вокруг своей траектории
#
# Слой получают через snowstorm_layer("menu" / "menu_high" / ...),
# функция кэширует готовые объекты, поэтому экраны можно
# перерисовывать сколько угодно — снег не рестартует.
# ==========================================================

init -50 python:

    import math
    import random as _ss_random
    import zlib


    class _SSFlake(python_object):
        """Один хлопок: всё нужное для расчёта позиции за O(1).

        python_object — базовый класс Ren'Py для классов со __slots__:
        обычный object с слотами не поддерживает откат (rollback).
        """
        __slots__ = ("disp", "size", "x0", "y0", "vy", "kwind",
                     "sway_amp", "sway_om", "sway_ph")

        def __init__(self, disp, size, x0, y0, vy, kwind,
                     sway_amp, sway_om, sway_ph):
            self.disp = disp
            self.size = size
            self.x0 = x0
            self.y0 = y0
            self.vy = vy
            self.kwind = kwind
            self.sway_amp = sway_amp
            self.sway_om = sway_om
            self.sway_ph = sway_ph


    class Snowstorm(renpy.Displayable):

        # Кэш живёт на классе, а не в store: так слои снега и набор
        # готовых хлопьев не попадают в файлы сохранений.
        _cache = {}
        _pool = {}

        def __init__(self, preset, seed=1):
            super(Snowstorm, self).__init__()

            rng = _ss_random.Random(seed)

            self.margin = 70
            self.tick = preset.get("tick", 0.05)
            self.near_bias = preset.get("near_bias", 0.0)

            # Ветер: средняя скорость + два порыва с разными периодами.
            self.w0 = float(preset.get("w0", 24.0))
            self.g1 = float(preset.get("g1", 20.0))
            self.t1 = float(preset.get("t1", 10.0))
            self.g2 = float(preset.get("g2", 10.0))
            self.t2 = float(preset.get("t2", 23.0))
            self.p1 = rng.uniform(0.0, 2.0 * math.pi)
            self.p2 = rng.uniform(0.0, 2.0 * math.pi)
            self.om1 = 2.0 * math.pi / max(self.t1, 1.0)
            self.om2 = 2.0 * math.pi / max(self.t2, 1.0)

            vy_min = float(preset.get("vy", (55, 300))[0])
            vy_max = float(preset.get("vy", (55, 300))[1])
            crystal_frac = float(preset.get("crystal", 0.0))
            clump_frac = float(preset.get("clump", 0.0))

            count = preset.get("count", 80)
            if renpy.variant("small"):
                count = preset.get("count_small", int(count * 0.5))

            W = config.screen_width
            H = config.screen_height
            M = self.margin

            flakes = []
            visited = []

            for i in range(count):
                band = rng.random() + self.near_bias * 0.2

                if band < 0.42:
                    # дальний план: мелкий, тусклый, медленный
                    depth = rng.uniform(0.30, 0.50)
                    size = rng.uniform(6, 11)
                    alpha = rng.uniform(0.30, 0.45)
                    blur = 0
                elif band < 0.78:
                    # средний план
                    depth = rng.uniform(0.50, 0.75)
                    size = rng.uniform(12, 21)
                    alpha = rng.uniform(0.50, 0.68)
                    blur = 1
                else:
                    # ближний план: крупный, ярче и чуть расфокусирован
                    depth = rng.uniform(0.75, 1.05)
                    size = rng.uniform(24, 40)
                    alpha = rng.uniform(0.72, 0.92)
                    blur = 2

                kind = "puff"
                if depth >= 0.72:
                    r = rng.random()
                    if r < crystal_frac:
                        kind = "crystal"
                        size = rng.uniform(22, 42)
                        alpha = rng.uniform(0.80, 0.95)
                        blur = 0
                    elif r < crystal_frac + clump_frac:
                        # большие рыхлые хлопья у самого экрана
                        kind = "clump"
                        size = rng.uniform(38, 58)
                        alpha = rng.uniform(0.75, 0.95)
                        blur = rng.choice((2, 3))
                        depth = rng.uniform(0.95, 1.15)

                disp = _ss_pool(kind, int(round(size)), round(alpha, 2), blur)
                if disp is None:
                    continue
                if disp not in visited:
                    visited.append(disp)

                vy = vy_min + (vy_max - vy_min) * ((depth - 0.30) / 0.85)
                vy *= rng.uniform(0.85, 1.15)

                flakes.append(_SSFlake(
                    disp=disp,
                    size=size,
                    x0=rng.uniform(-M, W + M),
                    y0=rng.uniform(-M, H + M),
                    vy=vy,
                    kwind=0.35 + 0.75 * depth,
                    sway_amp=size * 0.55 + rng.uniform(2.0, 12.0),
                    sway_om=2.0 * math.pi / rng.uniform(2.4, 5.6),
                    sway_ph=rng.uniform(0.0, 2.0 * math.pi),
                ))

            self.flakes = flakes
            self._visited = visited

        def wind_disp(self, t):
            # Первообразная скорости ветра: w0 + g1*sin(om1*t+p1) + g2*sin(om2*t+p2)
            d = self.w0 * t
            d -= (self.g1 / self.om1) * (math.cos(self.om1 * t + self.p1) - math.cos(self.p1))
            d -= (self.g2 / self.om2) * (math.cos(self.om2 * t + self.p2) - math.cos(self.p2))
            return d

        def render(self, width, height, st, at):
            rv = renpy.Render(width, height)

            if width > 0 and height > 0:
                M = self.margin
                wrap_x = width + 2 * M
                wrap_y = height + 2 * M
                wd = self.wind_disp(st)

                for f in self.flakes:
                    x = (f.x0 + wd * f.kwind + f.sway_amp * math.sin(f.sway_om * st + f.sway_ph)) % wrap_x - M
                    y = (f.y0 + f.vy * st) % wrap_y - M
                    rv.place(f.disp, x - f.size / 2.0, y - f.size / 2.0)

            renpy.redraw(self, self.tick)
            return rv

        def visit(self):
            return list(self._visited)


    def _ss_pool(kind, size, alpha, blur):
        """Готовые хлопья одного вида/размера переиспользуются."""
        try:
            key = (kind, size, alpha, blur)
            pool = Snowstorm._pool

            d = pool.get(key)
            if d is not None:
                return d

            if kind == "crystal" and renpy.loadable("images/snow_crystal.png"):
                src = "images/snow_crystal.png"
            elif renpy.loadable("images/snow_puff.png"):
                src = "images/snow_puff.png"
            else:
                # Совсем нет ассетов — мягкий квадрат как запасной вариант.
                src = None

            if src is not None:
                try:
                    d = Transform(src, xysize=(size, size), alpha=alpha, blur=blur, subpixel=True)
                except Exception:
                    d = Transform(src, xysize=(size, size), alpha=alpha)
            else:
                d = Transform(Solid("#ffffff"), xysize=(max(3, size // 2), max(3, size // 2)), alpha=alpha * 0.6)

            pool[key] = d
            return d
        except Exception:
            return None


    SS_PRESETS = {
        # Меню DLC, «Средние»: спокойное падение, лёгкий ветерок.
        "menu": dict(
            count=90, count_small=46,
            w0=30, g1=26, t1=10.0, g2=12, t2=23.0,
            vy=(55, 300), crystal=0.05, clump=0.07,
        ),
        # Меню DLC, «Высокие»: метель, ветер ~15 м/с, густо, с хлопьями.
        "menu_high": dict(
            count=175, count_small=92,
            w0=240, g1=120, t1=8.5, g2=70, t2=19.0,
            vy=(95, 440), crystal=0.12, clump=0.17, near_bias=1.0,
        ),
        # Уличный снег в истории, «Низкие»: экономный.
        "street_low": dict(
            count=26, count_small=14,
            w0=10, g1=8, t1=12.0, g2=5, t2=27.0,
            vy=(45, 210), crystal=0.0, clump=0.0,
        ),
        # Уличный снег, «Средние» (по умолчанию).
        "street": dict(
            count=78, count_small=40,
            w0=22, g1=18, t1=11.0, g2=10, t2=25.0,
            vy=(50, 285), crystal=0.04, clump=0.06,
        ),
        # Уличный снег, «Высокие»: плотнее и ветренее.
        "street_high": dict(
            count=128, count_small=66,
            w0=130, g1=70, t1=9.0, g2=40, t2=21.0,
            vy=(70, 380), crystal=0.09, clump=0.12,
        ),
    }


    def snowstorm_layer(preset_name):
        """Готовый слой снега по имени пресета или None."""
        if not preset_name:
            return None
        preset = SS_PRESETS.get(preset_name)
        if preset is None:
            return None
        if not (renpy.loadable("images/snow_puff.png") or renpy.loadable("images/snow_crystal.png")):
            return None

        key = preset_name + ("_m" if renpy.variant("small") else "_pc")
        inst = Snowstorm._cache.get(key)
        if inst is None:
            # Python 3: crc32 принимает только байты, не строку.
            inst = Snowstorm(preset, seed=zlib.crc32(key.encode("utf-8")) & 0x7fffffff)
            Snowstorm._cache[key] = inst
        return inst
