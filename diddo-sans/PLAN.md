# Diddo Sans: plan de trabajo

Tipografía para logotipos de subproductos de Diddo y material promocional.
Estado: **fase 2, brief pendiente de revisión** (todavía no se ha generado ninguna fuente).
Fases 0, 1 y 3 terminadas.

## Decisiones tomadas

| Tema | Decisión |
|---|---|
| Pesos | Solo **Bold** |
| Juego de caracteres v1 | A–Z, a–z, 0–9, puntuación básica y español (á é í ó ú ü ñ ¿ ¡ « » € @ #); unos 120 glifos |
| Licencia | **SIL Open Font License 1.1**. Además es obligatoria, porque la fuente deriva de Montserrat (OFL) |
| Fuente base | **Montserrat Regular (400)**, confirmado por medición (ver `docs/analisis-logos.md`). No es Lato. |
| Ubicación | Carpeta `diddo-sans/` dentro de este repositorio |

## Enfoque

El análisis cambia el enfoque inicial. Los logos **no se dibujaron desde cero**: son
Montserrat Regular **engrosada con un trazo redondo de ≈ 95 UPM** y con unas
pocas formas retocadas a mano: asta ahusada con extremos redondos (la misma en la i y la d),
a de un piso, ascendentes y descendentes alargadas y un punto de la i mayor.

Por eso, en lugar de extrapolar 90 letras a partir de 5, haremos lo siguiente:

1. Partimos de las **fuentes originales de Montserrat** (`Montserrat.glyphs`, OFL, commit fijado).
2. Aplicamos por programa la **"transformación Diddo"**, la misma que se aplicó en el logo:
   - **a)** Modificaciones de esqueleto en las letras con rasgos propios (asta ahusada, a de un piso, pie de la d…).
   - **b)** Engrosado: relleno ∪ trazo redondo, con skia-pathops.
3. Corregimos a mano solo lo que el automatismo rompe (diacríticos, %, @, ª…).
4. Validamos superponiendo "diddo" y "pad", compuestos con la fuente, sobre los logos originales.

El engrosado se hace **en las fuentes de diseño**. La fuente final tiene contornos rellenos
normales: una fuente no puede "aplicar un trazo" al renderizar.

## Fases

### Fase 0 · Referencias ✅
- SVG originales en `reference/original/`, con su procedencia anotada.

### Fase 1 · Análisis ✅
- Origen tipográfico, peso del trazo, construcción de d/i/o/p/a, defectos y viabilidad
  (en `docs/analisis-logos.md`).
- `scripts/analyze_reference.py` (`make analyze`) reproduce las medidas y genera
  `reference/normalized/`: letras en UPM (`diddo.svg`, `pad.svg`) y `medidas.md`/`.json`.
  Al hacerlo se corrigieron el ancho del asta de Montserrat (71, no 82 UPM) y el ángulo
  del ahusado (≈ 4°). También salieron rasgos nuevos: extensiones más largas que
  Montserrat, el asta de la d igual a la de la i y un punto de la i mayor.

### Fase 2 · Brief de diseño (`docs/design-brief.md`), con revisión contigo ⏳
Borrador hecho, con pruebas visuales en `proofs/brief/` (`make proof`, `scripts/proof_brief.py`).
Falta cerrar las decisiones 1–6 del resumen del brief. Estos eran los temas de partida:
1. **Peso de referencia:** diddo (95 UPM, recomendado) o pad (105 UPM).
2. **Regla del asta ahusada** y a qué letras se aplica (b d h i j k l m n p q r u…). Se decide con pruebas visuales.
3. **Pie de la d:** si se extiende a a/q/u o queda exclusivo de la d.
4. **Mayúsculas:** los logos no muestran ninguna. Propuesta: Montserrat engrosada sin ahusar,
   y probar el ahusado en I, L, D, P…
5. **Métricas finales:** el engrosado añade ≈ 95 UPM a todas las alturas. Propuesta: reescalar
   para que la altura de mayúsculas visible sea ≈ 700 UPM, y fijar la altura x, ascendentes,
   descendentes y métricas verticales (esquema typo/hhea/win de Google Fonts, `USE_TYPO_METRICS`).
6. **El símbolo "D" de diddo:** fuera de la v1. Opcionalmente en v2, como alternativa `ss01`.

### Fase 3 · Entorno y herramientas ✅
- `requirements.txt` con versiones fijadas (fontmake, fontTools, glyphsLib, ufo2ft, ufoLib2,
  skia-pathops, freetype-py, Pillow, fontbakery), instalado en `.venv` con `make setup`.
- `Makefile` con `setup`, `upstream`, `analyze`, `proof` y `clean`. Los objetivos
  `sources`, `build` y `test` se añadirán en las fases 4–8.
- `scripts/fetch_upstream.py` (`make upstream`) descarga Montserrat en el commit `555facf`
  (`Montserrat.glyphs`, `Montserrat[wght].ttf` y `OFL.txt`) y verifica su SHA-256.
- `scripts/diddolib.py` reúne las utilidades comunes: lectura de SVG, engrosado, medidas
  y renderizado.

### Fase 4 · Fuente de diseño Diddo Sans
1. `Montserrat.glyphs` → UFO con glyphsLib; instancia Regular 400; subconjunto con el juego de caracteres v1.
2. `scripts/diddoize.py` (la transformación):
   - Rasgos de esqueleto: "asta Diddo" (ahusada y con extremos redondos; sustituye al asta
     rectangular de Montserrat), a de un piso (derivada de la d), extensiones y punto de
     la i según el brief. La p se construye como la d girada, igual que en el logo.
     El prototipo de `scripts/proof_brief.py` sirve de punto de partida.
   - Engrosado: relleno ∪ trazo redondo; luego quitar solapamientos, corregir la dirección de los contornos y redondear a enteros.
   - Reescalado a las métricas finales y +r en los márgenes laterales de cada glifo.
   - Diacríticos rehechos como **componentes con anclajes**, separados para que no se fundan.
3. Salida: `sources/DiddoSans-Bold.ufo` (UFO 3) y `sources/features/*.fea`.
4. **Prueba de fidelidad:** `scripts/overlay_test.py` compone "diddo" y "pad" y los compara
   píxel a píxel con los logos. Objetivo: IoU ≥ 0,98 en d/i/o/p/a.

### Fase 5 · Correcciones manuales, por familias y con revisión contigo en cada bloque
Minúsculas → mayúsculas → números → puntuación → diacríticos. Los casos ya detectados:
`% @ ª` y todas las acentuadas.

### Fase 6 · Espaciado y kerning
- Espaciado con el método de Tracy (letras de control n o H O).
- Kerning: se heredan los grupos de Montserrat (`public.kern1`/`kern2`), se reescalan y se revisan
  con pares de prueba en español.

### Fase 7 · Funciones OpenType (`.fea`)
`kern`, `mark`/`mkmk`, `ccmp`, `case` (¿¡ y paréntesis para mayúsculas), `tnum`/`pnum` y `ordn`
(º ª). Sin `liga` en la v1.

### Fase 8 · Compilación, control de calidad y publicación
- `fontmake` con `--overlaps-backend pathops`. Salidas:
  - `fonts/otf/DiddoSans-Bold.otf` (CFF, para Illustrator, Figma y Affinity)
  - `fonts/ttf/DiddoSans-Bold.ttf` (con `ttfautohint`)
  - `fonts/webfonts/DiddoSans-Bold.woff2`
- Nombres: familia "Diddo Sans", estilo "Bold", `usWeightClass` 700, bits Bold en `fsSelection` y `macStyle`.
- Versión 1.000 en `head.fontRevision` y en `name` ID 5. `CHANGELOG.md` y tag de git `diddo-sans-v1.0.0`.
- `fontbakery check-universal` sin FAIL. Informe en `qa/`.
- `proofs/specimen.html`: alfabeto, pares de kerning, textos en español y nombres de subproductos.

## Licencia y créditos (OFL 1.1) ✅ verificada
Verificación completa en `docs/licencia.md`. En resumen: derivar de Montserrat está
permitido, y la OFL **obliga** a que Diddo Sans también sea OFL 1.1, que es una licencia libre.
- `OFL.txt` (ya creado) con los tres avisos de copyright, porque Montserrat usa dos distintos:
  - `Copyright 2011 The Montserrat Project Authors (https://github.com/JulietaUla/Montserrat)` (fuente y .glyphs)
  - `Copyright 2024 The Montserrat.Git Project Authors (https://github.com/JulietaUla/Montserrat.git)` (OFL.txt)
  - `Copyright 2026 The Diddo Sans Project Authors`
- Montserrat no declara *Reserved Font Name*, así que "Diddo Sans" es un nombre válido.
- Recomendación: **no** declarar "Diddo" como Reserved Font Name. La marca se protege por la
  vía del registro de marca, no con la licencia de la fuente.
- `FONTLOG.txt` (ya creado) documenta la derivación y los cambios.

## Estructura de carpetas
```
diddo-sans/
├── PLAN.md  README.md  CHANGELOG.md  FONTLOG.txt  OFL.txt
├── requirements.txt  Makefile
├── reference/   original/ (intocable) · normalized/
├── docs/        analisis-logos.md · design-brief.md · licencia.md
├── sources/     DiddoSans-Bold.ufo · features/ · upstream/ (Montserrat fijada, ignorada en git)
├── scripts/     diddolib.py · fetch_upstream.py · analyze_reference.py · proof_brief.py
│                (pendientes: diddoize.py · overlay_test.py · build.py)
├── fonts/       otf/ · ttf/ · webfonts/
├── proofs/      brief/*.png · specimen.html · overlay/*.png
└── qa/          informes de fontbakery
```

## Riesgos
| Riesgo | Mitigación |
|---|---|
| Sin referencia para mayúsculas ni números | Montserrat ya los tiene: solo hay que decidir si llevan ahusado (fase 2) |
| Contraformas que se cierran con el engrosado | Detección automática (cambio en el número de contornos) y corrección manual |
| Diferencias entre la Montserrat de 2021 y la de 2024 | Prueba de superposición; ajustar la o/d si la desviación supera el 1 % |
| Los logos no tienen el mismo peso (diddo y pad) | Elegir una referencia en la fase 2 |
| Extensiones largas → interlineado grande | Métricas verticales propias (brief §5) y prueba en varias líneas |
| El ahusado automático falla en j, u, f, t y m | Corrección manual en la fase 5 (ya identificadas) |
