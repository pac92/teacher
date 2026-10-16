# Referencias

| Archivo | Origen | Notas |
|---|---|---|
| `original/diddo-full-bold.svg` | https://diddo.es/img/logo/diddo-full-bold.svg | Subido al repo en el commit `00f4afa` (2026-10-16). Sin modificar. |
| `original/pad-bold-dark.svg` | https://pad.diddo.es/icons/pad-bold-dark.svg | Subido al repo en el commit `00f4afa` (2026-10-16). Sin modificar. Exportado desde Inkscape 1.1. |

Los archivos de `original/` **no se editan nunca**. Las versiones normalizadas
(escala en unidades de fuente, línea base en y = 0) están en `normalized/` y las genera
`make analyze` (`scripts/analyze_reference.py`). No se editan a mano:

| Archivo | Contenido |
|---|---|
| `normalized/diddo.svg`, `normalized/pad.svg` | Cada letra en UPM con dos capas: `relleno` (sin trazo) y `final` (relleno ∪ trazo, el aspecto del logo) |
| `normalized/medidas.md`, `normalized/medidas.json` | Escala, trazo, métricas verticales, astas, comparación con Montserrat y relaciones de construcción |

Fuente base (ver `../docs/analisis-logos.md`): **Montserrat**, OFL 1.1,
https://github.com/JulietaUla/Montserrat, commit fijado `555facfb2a18c72c3c0380f0d9c0f060453a9058`.
