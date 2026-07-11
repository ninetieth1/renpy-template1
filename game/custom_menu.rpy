################################################################################
# custom_menu.rpy — анимированный фон главного меню (Ren'Py 8.5.2, Android)
#
# Эффект: "neuro noise" (плазма #000000 -> #47a6ff -> #ffffff, тёмная)
#         + "dithering sphere" (шар #00b3ff, Bayer 4x4, дыхание/вращение).
#
# Всё в одном файле. Положить в папку game/ проекта.
#
# ВАЖНО про fragment_200 / fragment_300: это НЕ версии OpenGL, а порядок
# вставки кода в main() шейдера. Ren'Py сам компилирует один и тот же исходник
# и под GLES2, и под GLES3, сам добавляет #version и precision. Код ниже
# написан строго в подмножестве GLSL ES 1.00 (без dFdx, textureLod,
# битовых операций, динамических индексов массивов), поэтому работает
# на обоих профилях. Мы используем обе стадии (200 — вычисления,
# 300 — запись gl_FragColor), как и требовалось.
################################################################################

init -10 python:

    vn_shaders_ok = False

    try:
        # ----------------------------------------------------------------
        # ШЕЙДЕР 1: neuro noise (фон)
        # ----------------------------------------------------------------
        renpy.register_shader(
            "vn.neuro_noise",

            variables="""
                uniform vec2 u_model_size;
                uniform float u_tick;
                attribute vec2 a_tex_coord;
                varying vec2 v_vn_uv;
            """,

            vertex_300="""
                v_vn_uv = a_tex_coord;
            """,

            fragment_functions="""
                vec2 vn_rot(vec2 uv, float th) {
                    return mat2(cos(th), sin(th), -sin(th), cos(th)) * uv;
                }

                // Итеративный "нейро-шум" (по мотивам neuro noise из
                // paper-design; фиксированное число итераций — требование ES2).
                float vn_neuro(vec2 uv, float t) {
                    vec2 sine_acc = vec2(0.0);
                    vec2 res = vec2(0.0);
                    float scale = 8.0;
                    for (int j = 0; j < 12; j++) {
                        uv = vn_rot(uv, 1.0);
                        sine_acc = vn_rot(sine_acc, 1.0);
                        vec2 layer = uv * scale + float(j) + sine_acc - t;
                        sine_acc += sin(layer);
                        res += (0.5 + 0.5 * cos(layer)) / scale;
                        scale *= 1.2;
                    }
                    return res.x + res.y;
                }
            """,

            # Стадия 200: вычисляем сырой шум.
            fragment_200="""
                vec2 vn_uv = v_vn_uv - vec2(0.5);
                vn_uv.x *= u_model_size.x / max(u_model_size.y, 1.0);
                float vn_t = u_tick * 0.15;              // speed ~ медленно
                float vn_n = vn_neuro(vn_uv * 2.2, vn_t);
            """,

            # Стадия 300: тонмаппинг + палитра + запись цвета.
            fragment_300="""
                // brightness ~0.05, contrast ~0.3 (подобрано под тёмный фон)
                float vn_m = clamp(vn_n * 0.5, 0.0, 1.0);
                vn_m = pow(vn_m, 3.0);                          // тонкие нити
                float vn_v = clamp(vn_m * 0.65 + 0.05, 0.0, 1.0);

                vec3 vn_back  = vec3(0.0, 0.0, 0.0);            // #000000
                vec3 vn_mid   = vec3(0.278, 0.651, 1.0);        // #47a6ff
                vec3 vn_front = vec3(1.0, 1.0, 1.0);            // #ffffff

                vec3 vn_col = mix(vn_back, vn_mid, smoothstep(0.0, 0.65, vn_v));
                vn_col = mix(vn_col, vn_front, smoothstep(0.65, 1.0, vn_v));
                vn_col *= 0.5;   // общий притемнитель, чтобы читался текст меню

                gl_FragColor = vec4(vn_col, 1.0);
            """,
        )

        # ----------------------------------------------------------------
        # ШЕЙДЕР 2: dithering sphere (шар с Bayer 4x4)
        # ----------------------------------------------------------------
        renpy.register_shader(
            "vn.dither_sphere",

            variables="""
                uniform vec2 u_model_size;
                uniform float u_phase;
                attribute vec2 a_tex_coord;
                varying vec2 v_vn_uv2;
            """,

            vertex_300="""
                v_vn_uv2 = a_tex_coord;
            """,

            fragment_functions="""
                // Bayer 4x4 без массивов (динамическая индексация массивов
                // запрещена в ES2). Возвращает 16 уровней: 0..15/16.
                float vn_bayer2(vec2 a) {
                    a = floor(a);
                    return fract(a.x / 2.0 + a.y * a.y * 0.75);
                }
                float vn_bayer4(vec2 a) {
                    return vn_bayer2(0.5 * a) * 0.25 + vn_bayer2(a);
                }
            """,

            # Стадия 200: пикселизация, "объём" шара, освещение.
            fragment_200="""
                float vn_px = 4.0;   // размер дизер-ячейки в пикселях (type 4x4, size~2)
                vec2 vn_res = max(u_model_size, vec2(1.0));
                vec2 vn_cell = floor(v_vn_uv2 * vn_res / vn_px);
                vec2 vn_cuv = (vn_cell + 0.5) * vn_px / vn_res;

                // Позиция шара: x = 0.4 (чуть левее центра), y = 0.5
                vec2 vn_p = vn_cuv - vec2(0.4, 0.5);
                vn_p.x *= vn_res.x / vn_res.y;

                // "Дыхание" радиуса (периодично по u_phase — бесшовный цикл)
                float vn_r = 0.27 * (1.0 + 0.05 * sin(2.0 * u_phase));

                float vn_d = length(vn_p);
                float vn_lum = 0.0;

                if (vn_d < vn_r) {
                    float vn_z = sqrt(max(vn_r * vn_r - vn_d * vn_d, 0.0));
                    vec3 vn_nrm = normalize(vec3(vn_p.x, -vn_p.y, vn_z));
                    // Медленно вращающийся источник света
                    vec3 vn_l = normalize(vec3(
                        cos(u_phase),
                        0.55,
                        0.4 + 0.6 * (0.5 + 0.5 * sin(u_phase))));
                    vn_lum = clamp(dot(vn_nrm, vn_l), 0.0, 1.0);
                    vn_lum = pow(vn_lum, 1.3) * 0.95 + 0.05;
                }
            """,

            # Стадия 300: упорядоченный дизеринг + premultiplied alpha.
            fragment_300="""
                float vn_thr = vn_bayer4(vn_cell) + 1.0 / 32.0;
                float vn_on = step(vn_thr, vn_lum);

                vec3 vn_scol = vec3(0.0, 0.702, 1.0);   // #00b3ff

                // Ren'Py ждёт premultiplied alpha: rgb уже умножен на alpha.
                gl_FragColor = vec4(vn_scol * vn_on, vn_on);
            """,
        )

        vn_shaders_ok = True

    except Exception:
        # Регистрация не удалась — меню не роняем, ниже подставится
        # статичный тёмный фон.
        vn_shaders_ok = False


################################################################################
# Трансформы с анимацией кастомных uniform.
# Ren'Py перерисовывает экран только когда что-то меняется, поэтому
# непрерывность обеспечиваем через linear ... repeat на uniform,
# а НЕ через u_time.
################################################################################

# Фон: u_tick = "секунды". Цикл длинный (1 час), чтобы стык был редким.
transform vn_neuro_anim:
    mesh True
    shader "vn.neuro_noise"
    u_tick 0.0
    linear 3600.0 u_tick 3600.0
    repeat

# Шар: u_phase пробегает ровно 2*pi — цикл полностью бесшовный.
transform vn_sphere_anim:
    mesh True
    shader "vn.dither_sphere"
    u_phase 0.0
    linear 48.0 u_phase 6.2831853
    repeat


################################################################################
# Финальный фон меню: шум + шар. Если шейдеры не зарегистрировались —
# статичный тёмный фон вместо падения.
################################################################################

init 10 python:

    if vn_shaders_ok:
        renpy.image(
            "main_menu_bg",
            Composite(
                (1920, 1080),
                (0, 0), At(Solid("#000000", xysize=(1920, 1080)), vn_neuro_anim),
                (0, 0), At(Solid("#000000", xysize=(1920, 1080)), vn_sphere_anim),
            ),
        )
    else:
        renpy.image(
            "main_menu_bg",
            Solid("#ff0000", xysize=(1920, 1080)),
        )


################################################################################
# Переопределение фона главного меню ПОСЛЕ gui.rpy.
################################################################################

init 999 python:
    gui.main_menu_background = "#ff0000"
