# TurtleGlasses GTK v2 — Rediseño completo del tema GTK3

Estado: en curso
Repo: git en `main`, origen en `/home/sbi/turtleShell/TurtleGlassesTheme/TurtleGlassesGTK`;
      expuesto a GTK via symlink `~/.local/share/themes/TurtleGlasses-GTK`;
      respaldo del original en `gtk-3.0/gtk.css.orig`

## Objetivo

Reescribir el tema GTK3 `TurtleGlasses-GTK` como un tema **completo, coherente y
medible**: capa de tokens semánticos como única fuente de verdad, parciales
modulares, cobertura de todos los widgets GTK3 y validación por muestreo de
píxeles + contraste WCAG.

## Por qué

El tema actual es un único archivo de 430 líneas con cobertura parcial: todo
widget no estilizado cae a los valores por defecto de GTK y rompe la armonía.
Además usa una paleta descoordinada con el tema VSCode `TurtleGlasses` de la
misma marca (acento `#8a7f6a` marrón grisáceo → se ve embarrado).

## Decisiones tomadas por el usuario

1. **Acento**: navy TurtleGlasses `#2a3d5c` (unifica con el tema VSCode).
2. **Alcance**: GTK3 solamente. GTK4/libadwaita queda como paso futuro.
3. **Metodología**: CSS modular + tokens, cero dependencias, sin paso de build.

## Restricción firmada

`#f0e9d2` (fondo de ventana, el beige/cremita principal) **NO SE TOCA**. Es el
ancla del tema. Todos los demás colores derivan de él.

## Contrato de tokens (CONGELADO — `parts/00-tokens.css`)

Estos nombres y valores son el contrato. Los parciales solo consumen tokens;
**ningún hex literal fuera de `00-tokens.css`**.

```css
/* Superficies (beige/marfil) */
@define-color tk_ivory          #faf7ec;  /* áreas de texto, marfil */
@define-color tk_bg             #f0e9d2;  /* FIRMADO: fondo de ventana */
@define-color tk_chrome         #e9e0c3;  /* headerbar, toolbar, menubar, tabs */
@define-color tk_panel          #e3d8b8;  /* sidebar, paneles secundarios */
@define-color tk_sunken         #dcd0aa;  /* troughs, track de scrollbar, insets */
@define-color tk_button         #f6f2e3;  /* botón en reposo */
@define-color tk_hover          #e7ddbe;  /* hover */
@define-color tk_active         #d8cb9e;  /* pressed / checked */

/* Bordes */
@define-color tk_border         #b8b0a0;  /* borde principal (marca) */
@define-color tk_border_soft    #cdc6b6;  /* separadores, bordes suaves */
@define-color tk_border_strong  #a19683;  /* énfasis */

/* Acento navy TurtleGlasses */
@define-color tk_accent         #2a3d5c;
@define-color tk_accent_hover   #3a4a6e;
@define-color tk_accent_active  #1e2e45;
@define-color tk_on_accent      #f8f6f0;
@define-color tk_accent_soft    rgba(42, 61, 92, 0.13);
@define-color tk_accent_veil    rgba(42, 61, 92, 0.27);

/* Texto */
@define-color tk_fg             #2a2a2a;
@define-color tk_fg_secondary   #555555;
@define-color tk_fg_muted       #857e70;
@define-color tk_fg_disabled    #9a8f7c;

/* Semánticos capa FORMA (rellenos, bordes e indicadores no-texto, >= 3:1) */
@define-color tk_error          #b85a7a;
@define-color tk_warning        #a67c1c;
@define-color tk_success        #5b7a4c;
@define-color tk_info           #4d8fa8;
@define-color tk_gold           #b8860b;

/* Semánticos capa TEXTO (AA >= 4.5:1 sobre beige y marfil) */
@define-color tk_error_text     #813f55;
@define-color tk_warning_text   #7f6526;
@define-color tk_success_text   #4d6642;
@define-color tk_gold_text      #815e08;

/* Rellenos con texto claro encima (>= 4.5:1 con tk_on_accent) */
@define-color tk_error_fill     #a3465f;

/* Enlaces (AA sobre beige y marfil) */
@define-color tk_link           #23607d;
@define-color tk_link_hover     #2a6f8f;

/* Backdrop (ventana sin foco) */
@define-color tk_bg_backdrop      #eae3d3;
@define-color tk_ivory_backdrop   #f2eee1;
@define-color tk_chrome_backdrop  #e4dcc7;
@define-color tk_fg_backdrop      #6f6a60;
@define-color tk_border_backdrop  #cdc5b4;

/* Sombras */
@define-color tk_shadow        rgba(62, 54, 40, 0.26);
@define-color tk_shadow_soft   rgba(62, 54, 40, 0.13);
```

### Regla de uso de la capa semántica

- Formas, bordes, rellenos de progreso y puntos indicadores usan la capa
  **FORMA** (`tk_error`, `tk_warning`, `tk_success`, `tk_info`).
- Cualquier texto semántico (`entry.warning`, `infobar label`, mensajes de
  error) usa la capa **TEXTO** (`*_text`). Nunca usar la capa FORMA como color
  de texto.
- Un botón destructivo usa `tk_error_fill` como fondo con `tk_on_accent` como
  texto (contraste 5.40:1).

### Alias GTK estándar (obligatorios, en `00-tokens.css`)

Al menos: `theme_bg_color`, `theme_fg_color`, `theme_base_color`,
`theme_text_color`, `theme_selected_bg_color`, `theme_selected_fg_color`,
`theme_unfocused_bg_color`, `theme_unfocused_fg_color`,
`theme_unfocused_base_color`, `theme_unfocused_text_color`,
`theme_unfocused_selected_bg_color`, `theme_unfocused_selected_fg_color`,
`borders`, `unfocused_borders`, `error_color`, `warning_color`,
`success_color`, `insensitive_bg_color`, `insensitive_fg_color`,
`insensitive_base_color`, `content_view_bg`, `text_view_bg`,
`placeholder_text_color`, `dim_label`, y el juego `wm_bg_a`, `wm_bg_b`,
`wm_title`, `wm_unfocused_title`, `wm_border_focused`,
`wm_border_unfocused`. Todos aliasados a tokens `tk_*` — nunca redefinidos con
hex.

## Escala de diseño (documentar como comentario en `00-tokens.css`)

- Radios: `r1 = 3px` (controles densos), `r2 = 6px` (botones, entries),
  `r3 = 9px` (popovers, menús, tarjetas), `r4 = 12px` (CSD / ventanas).
- Espaciado: 2 / 4 / 6 / 8 / 12 px. Prohibido `padding` con decimales.
- Grosor de borde: siempre `1px` entero (escala 1.0 ⇒ píxel exacto).

## Mapa de módulos

```
gtk-3.0/gtk.css              ← solo @imports, en este orden exacto
gtk-3.0/parts/00-tokens.css
gtk-3.0/parts/01-base.css
gtk-3.0/parts/02-chrome.css
gtk-3.0/parts/03-controls.css
gtk-3.0/parts/04-views.css
gtk-3.0/parts/05-menus.css
gtk-3.0/parts/06-scroll.css
gtk-3.0/parts/07-feedback.css
```

`gtk.css` debe importar con rutas relativas:
`@import url("parts/00-tokens.css");` etc.

## Cobertura exigida

- **01-base**: `*` (mínimo imprescindible), `GtkWindow`, `.background`,
  `:backdrop` global, tipografía y `.dim-label`, `:disabled`, `selection` y
  `*:selected`, `separator` (horizontal/vertical), `frame > border`, `.frame`,
  `.view`, anillo de foco vía `outline` + `-gtk-outline-radius` (sin border
  para no desplazar layout), `*:link` / `*:visited`, `tooltip`/`.tooltip`.
- **02-chrome**: `window.csd`, `decoration`, `.csd`, `.solid-csd`,
  `window.background.csd` (esquinas redondeadas r4), `headerbar`, `.titlebar`,
  `headerbar .title`, `headerbar .subtitle`, `button.titlebutton`
  (close/minimize/maximize), `headerbar entry`, `menubar` + `menuitem`,
  `toolbar`, `actionbar`, `notebook` (header, tab, tab:checked, tab:hover,
  tab:backdrop), `stackswitcher`, `.linked` / `button.linked` (radios
  combinados).
- **03-controls**: `button` (+ `:hover`, `:active`, `:checked`, `:disabled`,
  `:backdrop`, `.flat`, `.suggested-action`, `.destructive-action`, `.text-button`,
  `.image-button`), `entry` (+ `:focus`, `:disabled`, `:backdrop`,
  `entry progress`, `entry.error`, `entry.warning`), `spinbutton`
  (+ `button.up` / `button.down`, `:focus`), `combobox` / `button.combo`
  (+ flecha), `check` / `radio` (+ `:checked`, `:indeterminate`,
  `:inconsistent`, `:disabled`), `switch` (+ `:checked`, `slider`),
  `scale` (marks, trough, highlight, slider, `:disabled`), `progressbar`
  (+ `trough`, `progress`, `:backdrop`), `levelbar` (block filled/empty),
  `colorswatch`.
- **04-views**: `treeview.view`, `treeview.view header button`, `iconview`,
  `list`/`row` (+ `:hover`, `:selected`, `:selected:focus`, `:disabled`),
  `.sidebar`, `placessidebar` (+ `row:selected`), `cell` (`:selected`,
  `:editing`), `expander`, `paned > separator`, `.dnd`, `.trough`.
- **05-menus**: `menu`, `menu menuitem` (+ `:hover`, `:disabled`),
  `menuitem accelerator`, `menu separator`, `menuitem arrow`,
  `popover` (+ `.background`, `> list`, esquinas r3, sombra suave),
  `modelbutton`, `menu.button`, `combobox window > popup`.
- **06-scroll**: `scrollbar` (+ `trough`, `slider`, `slider:hover`,
  `slider:active`, `slider:disabled`), variantes `overlay-indicator`,
  `scrollbar.vertical` / `.horizontal` con `min-width`/`min-height` correctos,
  `scrollbar:hover`, `scrollbar:backdrop` y anulación total de `scrollbar button`
  (steppers).
- **07-feedback**: `infobar` (+ `.info`, `.warning`, `.error`,
  `revealer`, `button`), `statusbar`, `spinner`, `calendar`, `assistant`,
  `.osd`, `.dnd`, `.badge`, `levelbar` en infobar, `.app-notification`,
  `.monospace`, `progressbar.osd`.

## Hallazgos verificados de plataforma (GTK 3.24.49)

Estos hechos se midieron por píxeles sobre este build y condicionan el CSS.
Sustituyen a cualquier suposición previa.

1. **La superficie pintable del scrollbar es el nodo `scrollbar`, no
   `trough`.** Un override opaco sobre `scrollbar trough` solo alcanza ~18 px
   (los bordes internos); el mismo override sobre `scrollbar` pinta toda la
   tira. En Adwaita el gris visible de la barra es el fondo del propio nodo
   `scrollbar`. Por eso el track se declara en `scrollbar:hover` y `trough`
   queda transparente de forma explícita.
2. **Los steppers de la barra clásica son `button`.** Sin estilo propio
   heredan la regla genérica de `button` y aparecen como dos cuadrados de
   16x34 px con borde en los extremos, ensanchando la tira de 12 px a 18 px.
   Verificado con un override azul sobre `scrollbar button`. Se anulan.
3. **El nodo `trough` del switch/scale sí pinta** (`scale trough` colorea
   correctamente); la excepción es la barra de desplazamiento.
4. **En el render offscreen el slider del scrollbar se dibuja a tamaño
   completo** en este build, tanto con Adwaita como con este tema: es un
   artefacto del orden de asignación, no un defecto del tema. La verificación
   de la barra debe apoyarse en colores y anchos, no en la longitud del slider.
5. **`font-family` en el tema es inerte**: `gtk-font-name` del usuario gana
   incluso a prioridad THEME. No se declara ninguna familia.

## Reglas de rendimiento (paint por frame)

1. **Cero gradientes** (`linear-gradient`, `radial-gradient`) en superficies
   grandes. Solo relleno sólido.
2. **Cero `box-shadow` con blur** en superficies grandes (`button`, `entry`,
   `headerbar`, `treeview`). Permitido solo en superficies pequeñas flotantes
   (`popover`, `menu`, `tooltip`) y con blur ≤ 8px.
3. **Sin `-gtk-icon-shadow`** salvo en `.osd` / tooltips oscuros.
4. Transiciones **solo** sobre `background-color`, `border-color`, `color` y
   con duración ≤ 150ms. Nunca sobre `box-shadow`, `background-image` ni
   propiedades de layout.
5. El bloque `*` inicial debe contener solo: `background-clip`, las propiedades
   `-gtk-*` heredadas del tema original y la **línea base del anillo de foco**
   (`outline-style`, `outline-width`, `outline-offset`, `outline-color`,
   `-gtk-outline-radius`). Nada más. El anillo se activa en `:focus` por nodo.
6. Sin `background-image: none` redundante y sin `alpha()`/`mix()` en
   propiedades pintadas por frame distintas de `background-color`.
7. Los estados `:focus` de nodos interactivos activan el anillo
   (`outline-width: 1px`, `outline-color: @tk_accent`) **sin** tocar `border`
   ni `padding`, para no desplazar el layout. `-gtk-outline-radius` debe
   igualar el radio del widget.
8. Los parciales NO pueden contener literales `#rgb`, `#rrggbb`, `rgb(` ni
   `rgba(` en ninguna parte, **ni siquiera en comentarios**. Para transparencias
   usar `alpha(@token, 0.13)`. El harness falla si aparece uno.

## Reglas de nitidez (cada píxel)

1. Todo borde `1px` entero. Prohibido `0.5px` o decimales.
2. `padding`/`margin` enteros y pares donde el borde deba caer en píxel exacto.
3. Bordes con color sólido de token (nunca `alpha()` para bordes estructurales),
   para evitar antialias difuso en la línea de 1px.
4. Radios consistentes con la escala, sin mezclar 3/4/5 al azar.
5. `outline-offset: -4px` + `-gtk-outline-radius` igual al radio del widget,
   para que el foco no desplace el layout ni se vea recortado.

## Criterios de aceptación

- [ ] `gtk.css` importa 8 parciales y ningún hex fuera de `00-tokens.css`.
- [ ] Carga con **0 errores** de parseo en `Gtk.CssProvider`.
- [ ] Todos los tokens estándar GTK existen y resuelven a color válido.
- [ ] Contraste WCAG ≥ 4.5:1 en: `tk_fg`/`tk_bg`, `tk_fg`/`tk_ivory`,
      `tk_on_accent`/`tk_accent`, `tk_fg_secondary`/`tk_bg`.
- [ ] `tk_bg` del pixel de fondo de ventana == `#f0e9d2` exacto.
- [ ] Borde de `button` es exactamente 1px y de color `tk_border` sin mezcla.
- [ ] La barra de desplazamiento clásica no contiene ningún píxel de
      `tk_button`: la tira mide 15 px y el slider 8 px, sin steppers.
- [ ] Selección de `treeview`/`entry` == `tk_accent` exacto.
- [ ] `python3 tools/check-theme.py` sale con código 0.

## Verificación

- `python3 tools/check-theme.py` — harness ya construido y en ROJO sobre el tema
  viejo (falla por capa de tokens ausente, que es lo correcto). Comprueba:
  0 errores de parseo, los 8 `@import`, ausencia de hex literal en todo `.css`
  excepto `00-tokens.css` (**cuenta también los comentarios**), píxel congelado
  `#f0e9d2`, borde de botón de exactamente 1px, presencia exacta de
  `tk_accent`/`tk_fg`/`tk_ivory`/`tk_chrome`, ausencia del viejo `#8a7f6a` en el
  chrome, y 7 pares de contraste WCAG. Sale 0 solo si todo pasa.
  Incorpora además una comprobación de steppers: renderiza una barra clásica
  (`overlay-scrolling` desactivado) y exige 0 píxeles de `tk_button` en la
  región de la tira, 15 px de ancho de tira y 8 px de slider.
- Recarga manual: cambiar de tema y volver (ver README).

## Bitácora

- [x] T1. Respaldo del original y documento de tareas.
- [x] T2. Harness de validación `tools/check-theme.py`.
- [x] T3. `00-tokens.css` + `gtk.css` (entrypoint).
- [x] T4. `01-base.css` + `02-chrome.css`.
- [x] T5. `03-controls.css` + `06-scroll.css`.
- [x] T6. `04-views.css` + `05-menus.css` + `07-feedback.css`.
- [x] T7. `index.theme` corregido (`GtkTheme=TurtleGlasses-GTK`) + `README.md`.
- [x] T8. Correr harness, corregir hallazgos, re-verificar.

Correcciones posteriores al cierre del widget layer:

- [x] Añadido el token `tk_ivory_backdrop` (#f2eee1) y reapuntado el alias
      `theme_unfocused_base_color` y `.view:backdrop` para no oscurecer el
      marfil de golpe al perder foco.
- [x] Eliminado el `font-family` inerte de `GtkWindow` en `01-base.css`.
- [x] Anulados los steppers heredados de `button` en la barra clásica
      (defecto de 16x34 px en los extremos, no cubierto por el harness).
- [x] Añadido al harness la comprobación `scrollbar-steppers` (RED: 1008 px de
      `tk_button` y tira de 18 px con el bloque anulado; GREEN: 0 px y 12/8 px).
      El harness queda en 26 comprobaciones, exit 0.
- [x] Ajuste de densidad (petición del usuario): tira clásica 12 px → 15 px
      (ancho efectivo de Adwaita), slider 8 px intacto; actualizado el check
      `scrollbar-steppers` (15/8 px) y las referencias del README y este
      documento. 26/26, exit 0.
- [x] Diagnóstico de "pantalla más ancha / waybar desajustada": resolución
      intacta según niri (1920x1080 @ 1 en ambos outputs); waybar idéntica
      (24 px, x=1896..1919) con ambos temas — la causa fue el cambio de config
      de waybar del mismo día (commits 14:32 y 15:02 del Dotfiles-SbiDev).
