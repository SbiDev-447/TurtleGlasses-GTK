# TurtleGlasses-GTK

Tema claro para aplicaciones GTK3, con capa de tokens semánticos como única
fuente de verdad y parciales CSS modulares. Diseñado para mantener la armonía
visual en toda la superficie de un widget sin depender de valores por defecto
de GTK.

Este documento describe el diseño actual y las reglas que lo condicionan.
Está pensado para la persona que mantenga el tema después de su autor.

## Alcance

- Cubre aplicaciones GTK3 solamente. Las aplicaciones GTK4 (libadwaita)
  ignoran el tema por diseño.
- Queda como trabajo futuro, explícitamente fuera del alcance actual:
  - soporte GTK4 y libadwaita,
  - una variante oscura.
- El tema ya vive en un repositorio git; el respaldo local del original v1
  queda como archivo no versionado (fuera de git por higiene).
- El direccionamiento del tema se resuelve por el nombre de directorio:
  `TurtleGlasses-GTK`. El archivo `index.theme` declara ese mismo nombre en
  la clave `GtkTheme`.

## Arquitectura modular

El punto de entrada es `gtk-3.0/gtk.css`, que solo contiene los imports de
los parciales en este orden exacto:

```
gtk-3.0/gtk.css              ← solo @imports, sin reglas propias
gtk-3.0/parts/00-tokens.css  ← única capa de tokens y aliases
gtk-3.0/parts/01-base.css    ← base global
gtk-3.0/parts/02-chrome.css  ← estructura de chrome
gtk-3.0/parts/03-controls.css← controles interactivos
gtk-3.0/parts/04-views.css   ← vistas y listas
gtk-3.0/parts/05-menus.css   ← menús, popovers y popups
gtk-3.0/parts/06-scroll.css  ← barras de desplazamiento
gtk-3.0/parts/07-feedback.css← retroalimentación y estados
```

Rol de cada parcial:

- `00-tokens.css`: define todos los tokens de color y el bloque de aliases
  GTK estándar. También documenta la escala de diseño. No contiene reglas de
  widgets.
- `01-base.css`: ventanas, tipografía y `.dim-label`, estados `:disabled`,
  selección, separadores, frames, `.view`, enlaces, tooltips y la línea base
  del anillo de foco (`outline` sin tocar `border` ni `padding`).
- `02-chrome.css`: CSD (`window.csd`, `decoration`, `.solid-csd`),
  `headerbar` y `.titlebar` con sus botones de ventana, `menubar`, `toolbar`,
  `actionbar`, `notebook`, `stackswitcher` y cajas `.linked`.
- `03-controls.css`: `button` (con todas sus variantes y estados), `entry`,
  `spinbutton`, `combobox`, `check`/`radio`, `switch`, `scale`,
  `progressbar`, `levelbar` y `colorswatch`.
- `04-views.css`: `treeview`, `iconview`, `list`/`row`, `.sidebar`,
  `placessidebar`, `expander`, `paned`, `.dnd` y `.trough`.
- `05-menus.css`: `menu`, `menuitem` (hover, accelerator, flecha de
  submenu), separadores, `popover`, `modelbutton` y `menu.button`.
- `06-scroll.css`: `scrollbar` (tira, `trough`, `slider` y sus estados), la
  variante `overlay-indicator`, el estado `:backdrop` y la anulación total de
  `scrollbar button` (steppers).
- `07-feedback.css`: `infobar` (info, warning, error), `statusbar`,
  `spinner`, `calendar`, `assistant`, `.osd`, `.badge`,
  `.app-notification` y `.monospace`.

Para ajustar un widget, se edita el parcial correspondiente y nada más.
Cualquier regla nueva debe vivir en su parcial temático; `gtk.css` no crece.

## Contrato de tokens

- `parts/00-tokens.css` es la única fuente de verdad de color. Todos los
  parciales consumen tokens con la sintaxis `@token` y jamás escriben
  literales de color (ni siquiera en comentarios: el harness lo verifica).
- Para transparencias se usa `alpha(@token, valor)`. No se introducen valores
  `rgba()` ni `rgb()` fuera de la capa de tokens.
- El token del fondo de ventana es el ancla firmada del tema y no se toca.
  Todos los demás colores derivan de él.
- La capa semántica tiene dos niveles:
  - nivel FORMA (`tk_error`, `tk_warning`, `tk_success`, `tk_info`,
    `tk_gold`): para rellenos, bordes e indicadores no textuales, con
    contraste mínimo de 3:1;
  - nivel TEXTO (`tk_error_text`, `tk_warning_text`, `tk_success_text`,
    `tk_gold_text`): para cualquier texto semántico (mensajes de error,
    etiquetas de infobar, texto sobre `entry.warning`), con contraste AA de
    al menos 4.5:1 sobre beige y marfil.
  La regla es: nunca usar la capa FORMA como color de texto. Un botón
  destructivo usa el relleno semántico con texto claro encima, contraste
  verificado.
- Enlaces usan su propio par de tokens (link y hover), verificados contra AA
  sobre beige y marfil.
- `00-tokens.css` incluye el bloque de aliases GTK estándar obligatorio:
  `theme_bg_color`, `theme_fg_color`, `theme_base_color`,
  `theme_text_color`, `theme_selected_bg_color`, `theme_selected_fg_color`,
  las variantes unfocused, `borders`, `unfocused_borders`, `error_color`,
  `warning_color`, `success_color`, los colores insensitive, `content_view_bg`,
  `text_view_bg`, `placeholder_text_color`, `dim_label` y el juego `wm_*`.
  Todos son aliases a tokens `tk_*`; nunca se redefinen con hex.

## Reglas de rendimiento y nitidez

Reglas de rendimiento (pintado por frame):

- Cero gradientes en superficies grandes. Solo relleno sólido.
- Cero sombras con blur en superficies grandes (`button`, `entry`,
  `headerbar`, `treeview`). Se permite blur solo en superficies pequeñas
  flotantes (`popover`, `menu`, `tooltip`) y con un máximo de 8 px.
- Sin `-gtk-icon-shadow` salvo en `.osd` y tooltips oscuros.
- Transiciones solo sobre `background-color`, `border-color` y `color`, con
  duración máxima de 150 ms. Nunca sobre `box-shadow`, `background-image` ni
  propiedades de layout.
- El bloque `*` inicial contiene solo: `background-clip`, las propiedades
  `-gtk-*` heredadas y la línea base del anillo de foco. Nada más.

Reglas de nitidez (cada píxel cuenta):

- Bordes siempre de 1 px entero. Prohibidos los decimales como 0.5 px.
- `padding` y `margin` enteros (y pares donde el borde deba caer en un píxel
  exacto).
- Bordes estructurales con color sólido de token, nunca con `alpha()`, para
  evitar antialiasing difuso en la línea de 1 px.
- Radios con la escala fija: 3 px controles densos, 6 px botones y entries,
  9 px popovers y menús, 12 px CSD. No se mezclan radios arbitrarios.
- El anillo de foco usa `outline-offset: -4px` con
  `-gtk-outline-radius` igual al radio del widget, para no desplazar el
  layout ni recortar la esquina.

## Hallazgos verificados de plataforma

Estos hechos se midieron por píxeles sobre GTK 3.24.49 en el build actual y
condicionan el CSS. Sustituyen a cualquier suposición previa.

1. La superficie pintable del scrollbar es el nodo `scrollbar`, no `trough`.
   Un override opaco sobre `scrollbar trough` solo alcanza unos 18 px (los
   bordes internos); el mismo override sobre `scrollbar` pinta toda la tira.
   Por eso el track se declara sobre el nodo `scrollbar` (en el estado
   `:hover`) y `trough` queda transparente de forma explícita. No mover el
   track a `trough`: dejaría de pintarse.
2. En la barra clásica (overlay desactivado) los steppers de los extremos son
   nodos `button`. Sin estilo propio heredan la regla genérica de `button` y
   aparecen como dos cuadrados con borde que ensanchan la tira de 12 px a
   18 px. Deben permanecer anulados por completo: el bloque `scrollbar
   button` (y sus estados hover/active/disabled) no se elimina. El harness
   verifica que no haya ningún píxel del color de botón en el render de la
   barra clásica.
3. El nodo `trough` de `switch` y `scale` sí pinta (por ejemplo `scale
   trough` colorea correctamente); la excepción es únicamente la barra de
   desplazamiento.
4. En el render offscreen, el slider del scrollbar se dibuja a tamaño
   completo (casi toda la longitud del track) en este build, tanto con
   Adwaita como con este tema. Es un artefacto del orden de asignación, no un
   defecto. Toda verificación de la barra se apoya en colores y anchos, jamás
   en la longitud del slider.
5. `font-family` en el tema es inerte: el valor `gtk-font-name` del usuario
   gana incluso a prioridad THEME. El tema no declara ninguna familia.

## Verificación

Desde la raíz del tema, se ejecuta:

```
python3 tools/check-theme.py
```

El harness (`tools/check-theme.py`) renderiza galerías de widgets offscreen
con `gtk-theme-name=TurtleGlasses-GTK` y verifica, entre otras cosas:

- 0 errores de parseo de `gtk-3.0/gtk.css` vía `Gtk.CssProvider` con
  manejador de `parsing-error`;
- los 8 `@import` del mapa de módulos;
- ausencia de literales de color fuera de `parts/00-tokens.css`
  (contando también los comentarios);
- el píxel ancla del fondo de ventana;
- el borde del botón de exactamente 1 px;
- presencia de los tokens de acento, texto, marfil y chrome;
- ausencia del color de selección antiguo en la zona de chrome;
- la barra clásica sin steppers: cero píxeles del color de botón en el
  render, tira de 15 px y slider de 8 px;
- 7 pares de contraste WCAG.

El harness debe terminar con "N passed, 0 failed" y código de salida 0.
Un fallo de cualquier comprobación no informativa rompe el exit code.

Para recargar el tema en aplicaciones abiertas:

```
gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita'
gsettings set org.gnome.desktop.interface gtk-theme 'TurtleGlasses-GTK'
```

O simplemente se reinicia la aplicación. Aplicaciones GTK3 recién abiertas
cargan el tema desde `gtk-3.0/gtk.css` automáticamente.

## Instalación

```
cp -r TurtleGlasses-GTK ~/.local/share/themes/
gsettings set org.gnome.desktop.interface gtk-theme 'TurtleGlasses-GTK'
```

Reinicia las aplicaciones GTK3 abiertas para ver el cambio. Bajo Niri no se
necesita xfwm4: las aplicaciones GTK3 dibujan su propia barra de título, por
eso los selectores CSD son críticos.