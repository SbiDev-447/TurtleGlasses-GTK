#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-theme.py - Validation harness for the TurtleGlasses-GTK GTK3 theme.

Extracts tokens from parts/00-tokens.css (transitive alias resolution), probes
gtk.css for parse errors and missing @imports, bans literal colors outside the
token layer, renders a widget gallery offscreen and probes pixels (frozen
anchor, 1-device-pixel border, exact token colors, chrome regression guard,
classic scrollbar with no steppers), and computes WCAG 2.1 contrast from the
tokens. Report strings are neutral professional Spanish; identifiers, function
names and docstrings are English.
"""

import os
import re
import sys

THEME_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GTK_3_0 = os.path.join(THEME_ROOT, "gtk-3.0")
TOKENS_PATH = os.path.join(GTK_3_0, "parts", "00-tokens.css")
ENTRY_CSS = os.path.join(GTK_3_0, "gtk.css")
EXPECTED_IMPORTS = ["parts/%02d-%s.css" % (i, n) for i, n in enumerate(
    ("tokens", "base", "chrome", "controls", "views", "menus", "scroll", "feedback"))]
FROZEN_BEIGE = (0xF0, 0xE9, 0xD2)          # signed anchor of the theme
OLD_MUDDY_SELECTION = (0x8A, 0x7F, 0x6A)   # old selection color, banned in chrome

COLOR_LITERAL_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgb(?:a)?\s*\(")
DEFINE_COLOR_RE = re.compile(r"@define-color\s+([A-Za-z_][A-Za-z0-9_-]*)\s+([^;]+);")
RGBA_RE = re.compile(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)")
RGB_RE = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")
IMPORT_RE = re.compile(r"@import\s+(?:url\(\s*)?(?:\"([^\"]+)\"|'([^']+)'|([^)\s;]+))", re.IGNORECASE)
# (check_id, fg token, bg token, minimum ratio, informational)
CONTRAST_RULES = [
    ("contrast-fg-bg", "tk_fg", "tk_bg", 4.5, False),
    ("contrast-fg-ivory", "tk_fg", "tk_ivory", 4.5, False),
    ("contrast-on-accent", "tk_on_accent", "tk_accent", 4.5, False),
    ("contrast-secondary-bg", "tk_fg_secondary", "tk_bg", 4.5, False),
    ("contrast-secondary-ivory", "tk_fg_secondary", "tk_ivory", 4.5, False),
    ("contrast-muted-bg", "tk_fg_muted", "tk_bg", 3.0, False),
    ("contrast-disabled-bg", "tk_fg_disabled", "tk_bg", 2.5, True),
]
TOKEN_LAYER_MSG = "capa de tokens ausente (no existe gtk-3.0/parts/00-tokens.css)"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    GTK_OK = True
except Exception:
    GTK_OK = False


class Report(object):
    def __init__(self):
        self.checks = []  # (check_id, ok, detail, informational)

    def add(self, check_id, ok, detail, informational=False):
        self.checks.append((check_id, bool(ok), detail, informational))

    def emit(self):
        width = max(len(c[0]) for c in self.checks) + 2
        for cid, ok, detail, info in self.checks:
            status = "PASS" if ok else "FAIL"
            tag = "  [informativo]" if info else ""
            sys.stdout.write("%s  %-*s  %s%s\n" % (status, width, cid, detail, tag))
        gated = [c for c in self.checks if not c[3]]
        passed = sum(1 for c in gated if c[1])
        failed = len(gated) - passed
        sys.stdout.write("%d passed, %d failed\n" % (passed, failed))
        return 0 if failed == 0 else 1


def hex_to_rgba(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        return (int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16), 255)
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    if len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    return None


def _resolve_value(value, raws, memo):
    if value.startswith("#"):
        return hex_to_rgba(value)
    m = RGBA_RE.match(value) or RGB_RE.match(value)
    if m:
        rgb = tuple(int(m.group(i)) for i in (1, 2, 3))
        alpha = int(round(float(m.group(4)) * 255)) if m.lastindex == 4 else 255
        return rgb + (alpha,)
    if value.startswith("@"):
        target = value[1:]
        if target in memo:
            return memo[target]
        if target not in raws:
            memo[target] = None
            return None
        memo[target] = None  # cycle guard
        result = _resolve_value(raws[target], raws, memo)
        memo[target] = result
        return result
    return None


def extract_tokens():
    if not os.path.exists(TOKENS_PATH):
        return None, 0, 0
    raws = {}
    aliases = 0
    with open(TOKENS_PATH, encoding="utf-8") as handle:
        for line in handle:
            m = DEFINE_COLOR_RE.search(line)
            if m:
                value = re.sub(r"/\*.*", "", m.group(2)).strip()
                raws[m.group(1)] = value
                aliases += value.startswith("@")
    return {name: _resolve_value(raws[name], raws, {}) for name in raws}, len(raws), aliases


def probe_css_parse(report):
    if not GTK_OK:
        report.add("parse-gtk-css", False, "módulo gi/Gtk no disponible")
        return
    if not os.path.exists(ENTRY_CSS):
        report.add("parse-gtk-css", False, "no existe gtk-3.0/gtk.css")
        return
    errors = []
    provider = Gtk.CssProvider()
    provider.connect("parsing-error",
                     lambda _p, section, error: errors.append((section, error.message)))
    try:
        provider.load_from_path(ENTRY_CSS)
    except Exception as exc:
        report.add("parse-gtk-css", False, "no se pudo cargar gtk-3.0/gtk.css: %s" % exc)
        return
    if not errors:
        report.add("parse-gtk-css", True, "0 errores de parseo en gtk-3.0/gtk.css")
        return
    detail = []
    for section, message in errors:
        f = section.get_file()
        path = f.get_path() if f is not None else None
        rel = os.path.relpath(path, THEME_ROOT) if path else "?"
        detail.append("%s:%d: %s" % (rel, section.get_start_line() + 1, message))
    report.add("parse-gtk-css", False, "; ".join(detail))


def check_imports(report):
    targets = set()
    if os.path.exists(ENTRY_CSS):
        with open(ENTRY_CSS, encoding="utf-8") as handle:
            for line in handle:
                if "@import" not in line.lower():
                    continue
                for m in IMPORT_RE.finditer(line):
                    target = m.group(1) or m.group(2) or m.group(3)
                    if target:
                        targets.add(target.strip())
    missing = os.path.exists(ENTRY_CSS)
    for partial in EXPECTED_IMPORTS:
        check_id = "import-" + partial[6:-4]
        if any(t == partial or t.endswith(partial) for t in targets):
            report.add(check_id, True, "@import %s presente" % partial)
        elif missing:
            report.add(check_id, False, "falta @import de %s en gtk.css" % partial)
        else:
            report.add(check_id, False, "no existe gtk-3.0/gtk.css")


def check_stray_colors(report):
    if not os.path.isdir(GTK_3_0):
        report.add("stray-hex", False, "no existe el directorio gtk-3.0")
        return
    hits = []
    tokens_norm = os.path.normpath(TOKENS_PATH)
    for root, _dirs, files in os.walk(GTK_3_0):
        for filename in sorted(files):
            if not filename.endswith(".css") or filename.endswith(".orig"):
                continue
            full = os.path.join(root, filename)
            if os.path.normpath(full) == tokens_norm:
                continue
            with open(full, encoding="utf-8") as handle:
                hits += ["%s:%d: %s" % (os.path.relpath(full, THEME_ROOT), n, m.group(0))
                         for n, line in enumerate(handle, 1)
                         for m in COLOR_LITERAL_RE.finditer(line)]
    if hits:
        for hit in hits:
            report.add("stray-hex", False,
                       "literal de color fuera de la capa de tokens: %s" % hit)
    else:
        report.add("stray-hex", True,
                   "sin literales de color fuera de parts/00-tokens.css")


def render_gallery():
    try:
        Gtk.Settings.get_default().set_property("gtk-theme-name", "TurtleGlasses-GTK")
        win = Gtk.OffscreenWindow()
        win.set_size_request(460, 760)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_top(6); box.set_margin_bottom(6)
        box.set_margin_start(6); box.set_margin_end(6)
        win.add(box)
        add = lambda w, e=False, f=False: box.pack_start(w, e, f, 0)
        hb = Gtk.HeaderBar(); hb.set_title("TurtleGlasses"); hb.set_show_close_button(False)
        cb = Gtk.Button.new_from_icon_name("window-close-symbolic", Gtk.IconSize.BUTTON)
        cb.get_style_context().add_class("titlebutton"); hb.pack_end(cb); add(hb)

        plain = Gtk.Button(label="Botón"); add(plain)
        sug = Gtk.Button(label="Sugerido")
        sug.get_style_context().add_class("suggested-action"); add(sug)

        entry = Gtk.Entry(); entry.set_text("texto seleccionado"); entry.select_region(0, 8); add(entry)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        chk = Gtk.CheckButton(label="Opción"); chk.set_active(True); row.pack_start(chk, False, False, 0)
        sw = Gtk.Switch(); sw.set_active(True); row.pack_start(sw, False, False, 0)
        add(row)

        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row2.pack_start(Gtk.SpinButton(adjustment=Gtk.Adjustment(
            value=5, lower=0, upper=10, step_increment=1, page_increment=1, page_size=0)), False, False, 0)
        pb = Gtk.ProgressBar(); pb.set_fraction(0.62); row2.pack_start(pb, True, True, 0)
        add(row2)

        lb = Gtk.LevelBar(); lb.set_min_value(0.0); lb.set_max_value(1.0); lb.set_value(0.62); add(lb)

        store = Gtk.ListStore(str, str)
        for r in (("alpha", "uno"), ("beta", "dos"), ("gamma", "tres")):
            store.append(r)
        tv = Gtk.TreeView(model=store)
        for i, t in enumerate(("Columna A", "Columna B")):
            tv.append_column(Gtk.TreeViewColumn(t, Gtk.CellRendererText(), text=i))
        tv.set_size_request(260, 80)
        tv.get_selection().select_path(Gtk.TreePath.new_from_string("1"))
        add(tv)

        nb = Gtk.Notebook()
        for t in ("Pestaña A", "Pestaña B"):
            nb.append_page(Gtk.Label(label=t), Gtk.Label(label=t))
        add(nb)

        sc = Gtk.ScrolledWindow(); sc.set_size_request(260, 56)
        txt = Gtk.TextView(); txt.get_buffer().set_text("línea uno\nlínea dos\nlínea tres")
        sc.add(txt); add(sc)

        combo = Gtk.ComboBoxText()
        for item in ("ítem uno", "ítem dos", "ítem tres"):
            combo.append_text(item)
        combo.set_active(0); add(combo)

        sca = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
                        adjustment=Gtk.Adjustment(value=50, lower=0, upper=100,
                                                  step_increment=1, page_increment=5, page_size=0))
        sca.set_size_request(260, -1); add(sca)

        win.set_focus(entry); win.show_all()
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        return win.get_pixbuf(), win, plain, None
    except Exception as exc:  # degrade gracefully, never emit a traceback
        return None, None, None, str(exc)


def render_scrollbar_probe():
    """Renderiza el probe de steppers: barra clasica sobre un TextView largo.

    Desactiva overlay scrolling para forzar la barra clasica (con steppers)
    y devuelve el pixbuf, la ventana y el GtkScrollbar vertical. English:
    render a classic (non-overlay) vertical scrollbar over a tall TextView.
    """
    try:
        Gtk.Settings.get_default().set_property("gtk-theme-name", "TurtleGlasses-GTK")
        win = Gtk.OffscreenWindow()
        win.set_size_request(300, 200)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        sw.set_overlay_scrolling(False)
        txt = Gtk.TextView()
        buf = txt.get_buffer()
        buf.set_text("\n".join("línea %d" % i for i in range(1, 201)))
        sw.add(txt)
        win.add(sw)
        win.show_all()
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        return win.get_pixbuf(), win, sw.get_vscrollbar(), None
    except Exception as exc:  # degrade gracefully, never emit a traceback
        return None, None, None, str(exc)


def pixel_at(pixbuf, x, y):
    if pixbuf is None or x < 0 or y < 0 or x >= pixbuf.get_width() or y >= pixbuf.get_height():
        return None
    data = pixbuf.get_pixels()
    offset = y * pixbuf.get_rowstride() + x * pixbuf.get_n_channels()
    return (data[offset], data[offset + 1], data[offset + 2])


def count_color_pixels(pixbuf, rgb, x_start=0, y_start=0, x_end=None, y_end=None):
    """Cuenta los pixel exactamente iguales a rgb dentro del rectangulo dado.

    Los limites son inclusivos-exclusivos ([x_start, x_end) x [y_start, y_end)).
    Con x_end/y_end en None se recorre toda la imagen. English: count exact
    color matches inside a rectangle of the pixbuf.
    """
    if pixbuf is None:
        return 0
    width = pixbuf.get_width()
    height = pixbuf.get_height()
    x_end = width if x_end is None else min(x_end, width)
    y_end = height if y_end is None else min(y_end, height)
    x_start, y_start = max(0, x_start), max(0, y_start)
    if x_start >= x_end or y_start >= y_end:
        return 0
    data = pixbuf.get_pixels()
    stride = pixbuf.get_rowstride()
    channels = pixbuf.get_n_channels()
    total = 0
    for y in range(y_start, y_end):
        base = y * stride
        for x in range(x_start, x_end):
            offset = base + x * channels
            if (data[offset], data[offset + 1], data[offset + 2]) == rgb:
                total += 1
    return total


def first_color_hit(pixbuf, rgb, y_start=0, y_end=None):
    if pixbuf is None:
        return None
    width = pixbuf.get_width()
    height = pixbuf.get_height()
    y_end = height if y_end is None else min(y_end, height)
    data = pixbuf.get_pixels()
    stride = pixbuf.get_rowstride()
    channels = pixbuf.get_n_channels()
    pattern = bytes(rgb) if channels == 3 else bytes(rgb + (255,))
    for y in range(max(0, y_start), max(0, y_end)):
        index = data[y * stride:y * stride + width * channels].find(pattern)
        if index != -1:
            return (y, index // channels)
    return None


def hex_str(rgb):
    return "#%02X%02X%02X" % (rgb[0], rgb[1], rgb[2])


def require_rgb(tokens, name):
    if tokens is None:
        return None, TOKEN_LAYER_MSG
    if name not in tokens:
        return None, "token `%s` no definido en parts/00-tokens.css" % name
    if tokens[name] is None:
        return None, "token `%s` sin valor de color resoluble" % name
    return tokens[name][:3], None


def check_render(report, pixbuf, error):
    if pixbuf is None:
        report.add("render-gallery", False, "no se pudo renderizar la galería: %s" % error)
    else:
        report.add("render-gallery", True, "galería %dx%d, %d canales, stride %d" % (
            pixbuf.get_width(), pixbuf.get_height(),
            pixbuf.get_n_channels(), pixbuf.get_rowstride()))


def check_frozen_beige(report, pixbuf):
    if pixbuf is None:
        report.add("frozen-beige", False, "renderizado no disponible")
        return
    observed = pixel_at(pixbuf, 2, 2)
    if observed is not None and observed == FROZEN_BEIGE:
        report.add("frozen-beige", True, "px(2,2)=%s (ancla firmada)" % hex_str(observed))
    else:
        report.add("frozen-beige", False, "px(2,2)=%s, se esperaba %s" % (
            hex_str(observed) if observed else "fuera de rango", hex_str(FROZEN_BEIGE)))


def check_button_border(report, tokens, pixbuf, win, button):
    needed = {}
    for name in ("tk_border", "tk_button", "tk_bg"):
        rgb, reason = require_rgb(tokens, name)
        if rgb is None:
            report.add("button-border", False, "no se pudo verificar el borde: %s" % reason)
            return
        needed[name] = rgb
    if pixbuf is None:
        report.add("button-border", False, "renderizado no disponible")
        return
    pos = button.translate_coordinates(win, 0, 0)
    if pos is None:
        report.add("button-border", False, "no se pudo ubicar el botón en la ventana")
        return
    bx, by = int(round(pos[0])), int(round(pos[1]))
    mid_y = by + button.get_allocation().height // 2
    runs, run = [], None
    for x in range(bx - 10, bx + 11):
        px = pixel_at(pixbuf, x, mid_y)
        if px is not None and px == needed["tk_border"]:
            run = [x, x] if run is None else [run[0], x]
        elif run is not None:
            runs.append(tuple(run)); run = None
    if run is not None:
        runs.append(tuple(run))
    target = next((r for r in runs if r[0] <= bx <= r[1]), None)
    if target is None:
        seen = ", ".join("[%d,%d]" % r for r in runs) if runs else "ninguna"
        report.add("button-border", False,
                   "sin píxeles del color tk_border en el borde izquierdo del botón "
                   "(x=%d, fila=%d; corridas observadas: %s)" % (bx, mid_y, seen))
        return
    length = target[1] - target[0] + 1
    interior = pixel_at(pixbuf, target[0] + 1, mid_y)
    exterior = pixel_at(pixbuf, target[0] - 1, mid_y)
    problems = []
    if length != 1:
        problems.append("el borde no mide 1px (observado %dpx)" % length)
    if target[0] != bx:
        problems.append("el borde no cae en el borde exacto del botón (x=%d)" % target[0])
    if interior != needed["tk_button"]:
        problems.append("el píxel interior es %s, no tk_button %s" % (
            hex_str(interior) if interior else "n/d", hex_str(needed["tk_button"])))
    if exterior != needed["tk_bg"]:
        problems.append("el píxel exterior es %s, no tk_bg %s" % (
            hex_str(exterior) if exterior else "n/d", hex_str(needed["tk_bg"])))
    detail = "corrida tk_border=%dpx en x=%d (fila=%d), interior=%s, exterior=%s" % (
        length, target[0], mid_y, hex_str(interior) if interior else "n/d",
        hex_str(exterior) if exterior else "n/d")
    if problems:
        detail += " (" + "; ".join(problems) + ")"
    report.add("button-border", not problems, detail)


def check_scrollbar_steppers(report, tokens, pixbuf, win, vscroll):
    """Barra clasica sin steppers: 0 px de tk_button, tira 15px, slider 8px.

    Renderiza un ScrolledWindow con overlay desactivado y exige: cero pixeles
    del color tk_button en toda la imagen, tira de 15px y slider de 8px dentro
    de la region de la barra. English: classic scrollbar has no steppers, the
    strip is 15px wide and the slider pill 8px wide.
    """
    needed = {}
    for name in ("tk_button", "tk_border_strong"):
        rgb, reason = require_rgb(tokens, name)
        if rgb is None:
            report.add("scrollbar-steppers", False, "no se pudo verificar: %s" % reason)
            return
        needed[name] = rgb
    if pixbuf is None:
        report.add("scrollbar-steppers", False, "renderizado no disponible")
        return
    if win is None or vscroll is None:
        report.add("scrollbar-steppers", False, "no se pudo ubicar la barra en la ventana")
        return
    pos = vscroll.translate_coordinates(win, 0, 0)
    if pos is None:
        report.add("scrollbar-steppers", False, "no se pudo ubicar la barra en la ventana")
        return
    alloc = vscroll.get_allocation()
    sx, sy = int(round(pos[0])), int(round(pos[1]))
    x0, y0 = sx, sy
    x1, y1 = sx + alloc.width, sy + alloc.height
    strip_w = alloc.width
    button_pixels = count_color_pixels(pixbuf, needed["tk_button"])
    best_run = 0
    for y in range(y0, y1):
        run, width = 0, 0
        for x in range(x0, x1):
            if pixel_at(pixbuf, x, y) == needed["tk_border_strong"]:
                width += 1
            else:
                width = 0
            if width > run:
                run = width
        if run > best_run:
            best_run = run
    problems = []
    if button_pixels != 0:
        problems.append("píxeles tk_button=%d (se exigen 0)" % button_pixels)
    if strip_w != 15:
        problems.append("tira=%dpx (se esperan 15px)" % strip_w)
    if best_run != 8:
        problems.append("slider=%dpx (se esperan 8px)" % best_run)
    detail = "píxeles tk_button=%d, tira=%dpx, slider=%dpx" % (button_pixels, strip_w, best_run)
    if problems:
        detail += " (" + "; ".join(problems) + ")"
    report.add("scrollbar-steppers", not problems, detail)


def check_color_presence(report, tokens, pixbuf, check_id, token, description):
    rgb, reason = require_rgb(tokens, token)
    if rgb is None:
        report.add(check_id, False, "no se pudo verificar %s: %s" % (description, reason))
        return
    if pixbuf is None:
        report.add(check_id, False, "renderizado no disponible")
        return
    hit = first_color_hit(pixbuf, rgb)
    if hit is not None:
        report.add(check_id, True, "%s presente (fila %d, columna %d)" % (
            description, hit[0], hit[1]))
    else:
        report.add(check_id, False, "%s ausente en toda la galería" % description)


def check_no_stray_chrome(report, pixbuf):
    if pixbuf is None:
        report.add("chrome-no-stray", False, "renderizado no disponible")
        return
    hit = first_color_hit(pixbuf, OLD_MUDDY_SELECTION, y_start=0, y_end=40)
    if hit is None:
        report.add("chrome-no-stray", True,
                   "sin píxeles %s en las 40 filas superiores" % hex_str(OLD_MUDDY_SELECTION))
    else:
        report.add("chrome-no-stray", False,
                   "color antiguo de selección %s en la fila %d (zona de chrome)" % (
                       hex_str(OLD_MUDDY_SELECTION), hit[0]))


def wcag_contrast(rgb_a, rgb_b):
    def lin(channel):
        value = channel / 255.0
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
    lum = lambda rgb: 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])
    la, lb = lum(rgb_a), lum(rgb_b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def run_contrast_checks(report, tokens):
    for check_id, fg, bg, minimum, informational in CONTRAST_RULES:
        if tokens is None:
            report.add(check_id, False, TOKEN_LAYER_MSG, informational)
            continue
        fg_rgb, fg_reason = require_rgb(tokens, fg)
        bg_rgb, bg_reason = require_rgb(tokens, bg)
        if fg_rgb is None or bg_rgb is None:
            report.add(check_id, False, fg_reason if fg_rgb is None else bg_reason, informational)
            continue
        ratio = wcag_contrast(fg_rgb, bg_rgb)
        report.add(check_id, ratio >= minimum,
                   "%s %s sobre %s %s: ratio %.2f:1 (mínimo %.1f:1)" % (
                       fg, hex_str(fg_rgb), bg, hex_str(bg_rgb), ratio, minimum),
                   informational)


def main():
    report = Report()
    tokens, total, aliases = extract_tokens()
    if tokens is None:
        report.add("tokens-layer", False, TOKEN_LAYER_MSG)
    elif total == 0:
        report.add("tokens-layer", False,
                   "no se encontró ningún @define-color en parts/00-tokens.css")
    else:
        report.add("tokens-layer", True,
                   "%d tokens definidos, %d resueltos (%d alias)" % (
                       total, sum(1 for v in tokens.values() if v is not None), aliases))
    probe_css_parse(report)
    check_imports(report)
    check_stray_colors(report)
    if GTK_OK:
        pixbuf, win, plain_button, render_error = render_gallery()
    else:
        pixbuf, win, plain_button, render_error = (None, None, None,
                                                   "módulo gi/Gtk no disponible")
    check_render(report, pixbuf, render_error)
    check_frozen_beige(report, pixbuf)
    check_button_border(report, tokens, pixbuf, win, plain_button)
    if GTK_OK:
        sb_pixbuf, sb_win, sb_vscroll, sb_error = render_scrollbar_probe()
    else:
        sb_pixbuf, sb_win, sb_vscroll, sb_error = (None, None, None,
                                                   "módulo gi/Gtk no disponible")
    if sb_pixbuf is None:
        report.add("scrollbar-steppers", False,
                   "no se pudo renderizar el probe de la barra: %s" % sb_error)
    else:
        check_scrollbar_steppers(report, tokens, sb_pixbuf, sb_win, sb_vscroll)
    for check_id, token, description in (
            ("color-selection", "tk_accent", "color de acento exacto"),
            ("color-text", "tk_fg", "texto principal exacto"),
            ("color-ivory", "tk_ivory", "marfil exacto"),
            ("color-chrome", "tk_chrome", "chrome exacto")):
        check_color_presence(report, tokens, pixbuf, check_id, token, description)
    check_no_stray_chrome(report, pixbuf)
    run_contrast_checks(report, tokens)
    return report.emit()


if __name__ == "__main__":
    sys.exit(main())