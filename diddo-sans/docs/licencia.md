# Licencia de Diddo Sans: verificación

Fecha: 2026-10-16. Comprobado sobre los archivos de Montserrat fijados en el commit
`555facf` (`make upstream`).

## Conclusión

- **Sí se puede** crear Diddo Sans a partir de Montserrat y usarla en logotipos y
  material promocional, también con fines comerciales.
- **Diddo Sans tiene que publicarse bajo la SIL Open Font License 1.1.** No es una
  elección: la OFL obliga a que las versiones modificadas sigan bajo la misma licencia.
  No se puede usar otra licencia (MIT, CC BY, propietaria…).
- La OFL es una **licencia libre**. La reconocen como tal la Free Software Foundation y
  distribuciones como Debian y Fedora. Aunque se dibujara desde cero, también sería la
  licencia recomendada para una tipografía libre.

## Qué se ha comprobado en Montserrat

| Comprobación | Resultado |
|---|---|
| Licencia | SIL OFL 1.1, en `OFL.txt` y en la tabla `name` (IDs 13 y 14) |
| *Reserved Font Name* | **No hay ninguno.** Ninguna línea de copyright dice "with Reserved Font Name". Se puede derivar sin cambiar nada por ese motivo, y "Diddo Sans" no choca con ningún nombre reservado |
| Permiso de incrustación (`OS/2.fsType`) | 0: incrustación sin restricciones (PDF, web, apps) |
| Avisos de copyright | Hay **dos versiones**: `Copyright 2011 The Montserrat Project Authors` (en la fuente y en `Montserrat.glyphs`) y `Copyright 2024 The Montserrat.Git Project Authors` (en `OFL.txt`). Se conservan **las dos** |
| Otras fuentes | No se usa ninguna. Lato solo se midió para descartarla, sin copiar nada de ella |

## Qué permite y qué exige la OFL (aplicado a Diddo Sans)

Permite:
- Usarla para cualquier cosa, incluidos logotipos, publicidad y productos comerciales.
- Modificarla y redistribuirla.
- Incrustarla en documentos, webs y aplicaciones.
- Venderla **junto con** software.

Exige:
1. **No venderla sola**, como archivo de fuente suelto.
2. **Conservar los avisos de copyright de Montserrat** y la licencia en toda copia, tanto
   de las fuentes compiladas como de las fuentes de diseño.
3. Distribuir Diddo Sans **solo bajo la OFL 1.1**.
4. **No usar el nombre de los autores de Montserrat** para promocionar Diddo Sans sin su
   permiso. Sí se puede, y se debe, darles crédito en `FONTLOG.txt` y en `OFL.txt`.
5. No usar un *Reserved Font Name* ajeno. Montserrat no tiene, así que no aplica.

**Los logos y documentos hechos con la fuente no quedan bajo la OFL.** La licencia cubre
el software de la fuente, no lo que se compone con ella. El logotipo de un subproducto
puede registrarse como marca aunque esté hecho con Diddo Sans. Por la misma razón, la
recomendación es **no** declarar "Diddo" como *Reserved Font Name*: la marca se protege
con el registro de marca, no con la licencia de la fuente.

**Consecuencia práctica:** cualquiera podrá descargar, usar y modificar Diddo Sans. Si se
quisiera una tipografía exclusiva, no podría salir de Montserrat ni de ninguna otra fuente
OFL. Habría que dibujarla desde cero, sin partir de ninguna fuente.

## Herramientas

Las herramientas no afectan a la licencia de la fuente que generan:

| Herramienta | Licencia |
|---|---|
| fontmake, glyphsLib, ufo2ft, fontbakery | Apache 2.0 |
| fontTools, Pillow | MIT, o equivalente |
| skia-pathops, freetype-py | BSD |
| ttfautohint (fase 8) | Su licencia excluye expresamente el resultado generado |

## Archivos que no son la fuente

Los logos de `reference/original/` **no forman parte de Diddo Sans** y no se distribuyen
bajo la OFL. Sus derechos son de sus titulares. Lo mismo vale para las versiones derivadas
de `reference/normalized/`.

## Obligaciones pendientes por fase

- [x] `OFL.txt` con los tres avisos de copyright (2011 y 2024 de Montserrat, 2026 de Diddo Sans)
      y el texto íntegro de la licencia, sin cambios.
- [x] `FONTLOG.txt` con el origen y los cambios.
- [ ] Fase 4: copiar el copyright, la licencia y la URL de la licencia (`openfontlicense.org`)
      en la información de la fuente (UFO).
- [ ] Fase 8: comprobar en la tabla `name` los IDs 0 (copyright con las tres líneas),
      13 (descripción de la licencia) y 14 (URL), sin "Montserrat" en los IDs 1, 4 y 6
      (nombres); `fsType` 0. fontbakery revisa casi todo esto.
- [ ] Fase 8: incluir `OFL.txt` y `FONTLOG.txt` junto a las fuentes compiladas en cada
      distribución.
