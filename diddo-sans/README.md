# Diddo Sans

Tipografía para los logotipos de los subproductos de Diddo y su material promocional.
Solo tiene un estilo, **Bold**. Deriva de [Montserrat](https://github.com/JulietaUla/Montserrat)
(SIL OFL 1.1) mediante la *transformación Diddo*, la misma que dio forma a los logos de diddo y pad:

1. **Rasgos de esqueleto:** asta ahusada con pie, ascendentes largas, a de un piso,
   p = d girada y punto de la i del logo.
2. **Engrosado:** relleno ∪ trazo redondo de 95 UPM.
3. **Reescalado:** la altura de mayúsculas visible se lleva a 700 UPM.

Estado: **prototipo v0.101** (con los extremos redondos del brief). Las decisiones de diseño pendientes están en
[`docs/design-brief.md`](docs/design-brief.md) y el plan completo, en [`PLAN.md`](PLAN.md).

## Archivos de fuente

| Formato | Archivo | Uso |
|---|---|---|
| OTF (CFF) | `fonts/otf/DiddoSans-Bold.otf` | Illustrator, Figma, Affinity, InDesign |
| TTF (ttfautohint) | `fonts/ttf/DiddoSans-Bold.ttf` | Office, sistemas operativos |
| WOFF2 | `fonts/webfonts/DiddoSans-Bold.woff2` | Web (`@font-face`, `font-weight: 700`) |

Espécimen: abre `proofs/specimen.html` en el navegador.

## Compilar

Hace falta Python ≥ 3.10, `make` y `curl`.

```sh
make setup   # entorno virtual .venv con las versiones fijadas en requirements.txt
make all     # descarga Montserrat (commit fijado, con suma de verificación), genera el UFO,
             # compila, pasa las pruebas y regenera las pruebas visuales
```

Objetivos sueltos:

- `make sources`: genera `sources/DiddoSans-Bold.ufo`.
- `make build`: compila `fonts/`.
- `make test`: prueba de fidelidad con los logos y fontbakery (resumen en `qa/README.md`).
- `make proof`: genera `proofs/`.
- `make analyze`: genera `reference/normalized/`.

`sources/DiddoSans-Bold.ufo` **se genera**: no lo edites a mano, porque `make sources` lo
sobrescribe. Los cambios de diseño se hacen en los parámetros de `scripts/diddoize.py`
(`DEFAULTS`) y en `scripts/fixes.py`. Para probar un valor sin tocar el código:

```sh
.venv/bin/python scripts/diddoize.py --set stroke=105 --out build/prueba.ufo
```

## Estructura

```
reference/  logos originales (intocables) y sus versiones normalizadas en UPM
docs/       análisis de los logos y brief de diseño
sources/    UFO generado; upstream/ (Montserrat, descargada, fuera de git)
scripts/    transformación, correcciones, compilación, pruebas
fonts/      binarios compilados
proofs/     espécimen, alfabeto, comparaciones del brief y superposiciones
qa/         informes de fontbakery
```

## Licencia

SIL Open Font License 1.1: ver [`OFL.txt`](OFL.txt). Diddo Sans es una versión
modificada de Montserrat. No se declara ningún *Reserved Font Name*.
Historial de la derivación en [`FONTLOG.txt`](FONTLOG.txt).
Verificación de la licencia y obligaciones en [`docs/licencia.md`](docs/licencia.md).
