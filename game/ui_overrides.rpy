################################################################################
## UI v2 — объёмные кнопки и увеличенный интерфейс
################################################################################

init offset = 1

image ui_button_idle = Composite(
    (520, 82),
    (0, 9), Solid("#02070d", xysize=(520, 73)),
    (0, 0), Solid("#0b1725", xysize=(520, 73)),
    (0, 0), Solid("#18344a", xysize=(520, 2))
)

image ui_button_hover = Composite(
    (520, 82),
    (0, 9), Solid("#03101a", xysize=(520, 73)),
    (0, 0), Solid("#102b40", xysize=(520, 73)),
    (0, 0), Solid("#47a6ff", xysize=(520, 3))
)

image ui_button_selected = Composite(
    (520, 82),
    (0, 7), Solid("#02101a", xysize=(520, 75)),
    (0, 2), Solid("#12344c", xysize=(520, 73)),
    (0, 2), Solid("#00b3ff", xysize=(520, 3))
)

style game_menu_outer_frame:
    bottom_padding 45
    top_padding 180
    background Solid("#050a14")

style frame:
    padding gui.frame_borders.padding
    background Solid("#0a1628")

style main_nav_button:
    xalign 0.5
    xsize 520
    ysize 82
    background Frame("ui_button_idle", Borders(18, 18, 18, 22))
    hover_background Frame("ui_button_hover", Borders(18, 18, 18, 22))
    selected_background Frame("ui_button_selected", Borders(18, 18, 18, 22))
    activate_sound "ui/click_003.ogg"

style main_nav_button_text:
    xalign 0.5
    yalign 0.43
    size 52
    font "kazmann-sans.ttf"
    idle_color "#9bb4cc"
    hover_color "#ffffff"
    selected_color "#00b3ff"
    insensitive_color "#44576a"
    idle_outlines [(1, "#02060c", 0, 2)]
    hover_outlines [(2, "#006fa3", 0, 2)]

style navigation_button:
    size_group "navigation"
    xsize 420
    ysize 76
    background Frame("ui_button_idle", Borders(18, 18, 18, 22))
    hover_background Frame("ui_button_hover", Borders(18, 18, 18, 22))
    selected_background Frame("ui_button_selected", Borders(18, 18, 18, 22))

style navigation_button_text:
    xalign 0.5
    yalign 0.43
    size 46
    idle_color "#9bb4cc"
    hover_color "#ffffff"
    selected_color "#00b3ff"
    idle_outlines [(1, "#02060c", 0, 2)]

style return_button:
    xpos 60
    yalign 1.0
    yoffset -35
    xsize 300
    ysize 70

style return_button_text:
    xalign 0.5
    size 44

style radio_button:
    xsize 500
    ysize 72
    left_padding 62
    background Frame("ui_button_idle", Borders(18, 18, 18, 22))
    hover_background Frame("ui_button_hover", Borders(18, 18, 18, 22))
    selected_background Frame("ui_button_selected", Borders(18, 18, 18, 22))
    foreground "gui/button/radio_[prefix_]foreground.png"

style radio_button_text:
    size 44
    idle_color "#9bb4cc"
    hover_color "#ffffff"
    selected_color "#00b3ff"

style check_button:
    xsize 500
    ysize 72
    left_padding 62
    background Frame("ui_button_idle", Borders(18, 18, 18, 22))
    hover_background Frame("ui_button_hover", Borders(18, 18, 18, 22))
    selected_background Frame("ui_button_selected", Borders(18, 18, 18, 22))
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    size 44
    idle_color "#9bb4cc"
    hover_color "#ffffff"
    selected_color "#00b3ff"

style pref_label_text:
    size 46
    yalign 1.0

style slider_label_text:
    size 43

style slider_slider:
    xsize 620
    ysize 48

style page_button_text:
    size 36

style slot_button_text:
    size 32

style confirm_button:
    xsize 300
    ysize 76
    background Frame("ui_button_idle", Borders(18, 18, 18, 22))
    hover_background Frame("ui_button_hover", Borders(18, 18, 18, 22))

style confirm_button_text:
    xalign 0.5
    size 44

style confirm_frame:
    padding gui.confirm_frame_borders.padding
    background Solid("#0a1a2e")
    xalign 0.5
    yalign 0.5

style quick_button:
    xminimum 82
    yminimum 64

style quick_button_text:
    size 40
    idle_color "#7f9ab3"
    hover_color "#ffffff"
    selected_color "#00b3ff"
    outlines [(1, "#02060c", 0, 2)]
