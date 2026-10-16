# Diddo Sans: plan de trabajo

Tipografía para logotipos de subproductos de Diddo y material promocional.
Estado: **prototipo v0.100 compilado** (`fonts/`) y **brief decidido**. Siguiente paso:
aplicar las decisiones del brief (`docs/design-brief.md`) en `scripts/diddoize.py`; después,
las fases 5–8.

## Decisiones tomadas

| Tema | Decisión |
|---|---|
| Pesos | Solo **Bold**, con el trazo de pad (105 UPM) |
| Juego de caracteres v1 | **Solo minúsculas**: a–z, 0–9, puntuación básica y español (á é í ó ú ü ñ ¿ ¡ « » € @ #). Sin mayúsculas (¿unicase?, ver brief) |
| Diseño | Ver `docs/design-brief.md`: asta ahusada en todas (n y m solo la 1.ª), todos los extremos redondos, ascendentes del logo y punto de diddo |
| Licencia | **SIL Open Font License 1.1**, obligatoria porque la fuente deriva de Montserrat (OFL). Verificada en `docs/licencia.md` |
| Fuente base | **Montserrat Regular (400)**, confirmado por medición (ver `docs/analisis-logos.md`). No es Lato. |
| Ubicación | Carpeta `diddo-sans/` dentro de este repositorio |

## Enfoque

El análisis cambia el enfoque inicial. Los logos **no se dibujaron desde cero**: son
Montserrat Regular **engrosada con un trazo redondo de ≈ 95 UPM** y con unas
pocas formas retocadas a mano (asta ahusada, a de un piso, pie de la d).

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
- Hecho: origen tipográfico, peso del trazo, construcción de d/i/o/p/a, defectos y viabilidad
  (en `docs/analisis-logos.md`).
- Hecho: `scripts/analyze_reference.py` reproduce las medidas y genera `reference/normalized/`.
  Corrige el análisis inicial: ascendente de 857, apertura del asta de ≈ 3° y existencia de `a.ss01`.

### Fase 2 · Brief de diseño (`docs/design-brief.md`), con revisión contigo 🟡 propuesta escrita, faltan tus decisiones
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
- `requirements.txt` con versiones fijadas, en un entorno virtual (venv) de Python:
  - `fontmake`, que incluye glyphsLib, ufo2ft y fontTools
  - `skia-pathops`
  - `ufoLib2`
  - `fontbakery`
  - `Pillow`, para las comparaciones de imagen
- `Makefile` con objetivos `setup`, `sources`, `build`, `test`, `proof` y `clean`.
- Descarga reproducible de Montserrat en el commit `555facf`, con suma de verificación.

### Fase 4 · Fuente de diseño Diddo Sans ✅ (prototipo con las opciones propuestas)
1. `Montserrat.glyphs` → UFO con glyphsLib; instancia Regular 400; subconjunto con el juego de caracteres v1.
2. `scripts/diddoize.py` (la transformación):
   - Rasgos de esqueleto: asta ahusada, a de un piso (derivada de la d) y pie de la d.
     La p se construye como la d girada, igual que en el logo.
   - Engrosado: relleno ∪ trazo redondo; luego quitar solapamientos, corregir la dirección de los contornos y redondear a enteros.
   - Reescalado a las métricas finales y +r en los márgenes laterales de cada glifo.
   - Diacríticos rehechos como **componentes con anclajes**, separados para que no se fundan.
3. Salida: `sources/DiddoSans-Bold.ufo` (UFO 3) y `sources/features/*.fea`.
4. **Prueba de fidelidad:** `scripts/overlay_test.py` compara d/i/o/p/a píxel a píxel
   con los logos. Objetivo: IoU ≥ 0,98. Conseguido: 0,978–0,991 (la prueba exige 0,975;
   ver el brief, § 0).

### Fase 5 · Correcciones manuales, por familias y con revisión contigo en cada bloque 🟡 primer pase automático
Minúsculas → mayúsculas → números → puntuación → diacríticos. Primer pase hecho por programa
(`scripts/fixes.py`): ¨ % @ © ® ª º y diacríticos separados. Pendiente: reconstruir
h m n r u j f t con el asta Diddo (si se elige la opción 2a del brief).

### Fase 6 · Espaciado y kerning
- Espaciado con el método de Tracy (letras de control n o H O).
- Kerning: se heredan los grupos de Montserrat (`public.kern1`/`kern2`), se reescalan y se revisan
  con pares de prueba en español.

### Fase 7 · Funciones OpenType (`.fea`)
`kern`, `mark`/`mkmk`, `ccmp`, `case` (¿¡ y paréntesis para mayúsculas), `tnum`/`pnum` y `ordn`
(º ª). Sin `liga` en la v1.

### Fase 8 · Compilación, control de calidad y publicación 🟡 compilación y QA funcionando; falta publicar la v1.0
- `fontmake` (los contornos ya llegan sin solapamientos, así que se compila con `--keep-overlaps`
  para conservar los componentes). Salidas:
  - `fonts/otf/DiddoSans-Bold.otf` (CFF, para Illustrator, Figma y Affinity)
  - `fonts/ttf/DiddoSans-Bold.ttf` (con `ttfautohint`)
  - `fonts/webfonts/DiddoSans-Bold.woff2`
- Nombres: familia "Diddo Sans", estilo "Bold", `usWeightClass` 700, bits Bold en `fsSelection` y `macStyle`.
- Versión 1.000 en `head.fontRevision` y en `name` ID 5. `CHANGELOG.md` y tag de git `diddo-sans-v1.0.0`.
- `fontbakery check-universal` sin FAIL. Informe en `qa/`. Estado de la v0.100: OTF sin avisos;
  TTF con 1 WARN esperable (`contour_count`: las letras engrosadas tienen menos contornos).
- `proofs/specimen.html`: alfabeto, pares de kerning, textos en español y nombres de subproductos.

## Licencia y créditos (OFL 1.1)
Verificación y obligaciones pendientes en `docs/licencia.md`.
- `OFL.txt` y la tabla `name` (ID 0) con los tres avisos de copyright, porque Montserrat usa dos distintos:
  - `Copyright 2011 The Montserrat Project Authors (https://github.com/JulietaUla/Montserrat)` (en la fuente y en el .glyphs)
  - `Copyright 2024 The Montserrat.Git Project Authors (https://github.com/JulietaUla/Montserrat.git)` (en su OFL.txt)
  - `Copyright 2026 The Diddo Sans Project Authors`
- Montserrat no declara *Reserved Font Name*, así que "Diddo Sans" es un nombre válido.
- Recomendación: **no** declarar "Diddo" como Reserved Font Name. La marca se protege por la
  vía del registro de marca, no con la licencia de la fuente.
- `FONTLOG.txt` documenta la derivación y los cambios.

## Estructura de carpetas
```
diddo-sans/
├── PLAN.md  README.md  CHANGELOG.md  FONTLOG.txt  OFL.txt
├── requirements.txt  Makefile
├── reference/   original/ (intocable) · normalized/
├── docs/        analisis-logos.md · design-brief.md · licencia.md
├── sources/     DiddoSans-Bold.ufo · features/ · upstream/ (Montserrat fijada, ignorada en git)
├── scripts/     diddolib.py · analyze_reference.py · diddoize.py · fixes.py · build.py
│                overlay_test.py · proof.py · specimen.py · qa_summary.py
├── fonts/       otf/ · ttf/ · webfonts/
├── proofs/      specimen.html · alfabeto.png · brief/*.png · overlay/*.png
└── qa/          informes de fontbakery
```

## Riesgos
| Riesgo | Mitigación |
|---|---|
| Sin referencia para mayúsculas ni números | Montserrat ya los tiene: solo hay que decidir si llevan ahusado (fase 2) |
| Contraformas que se cierran con el engrosado | Detección automática (cambio en el número de contornos) y corrección manual |
| Diferencias entre la Montserrat de 2021 y la de 2024 | Prueba de superposición; ajustar la o/d si la desviación supera el 1 % |
| Los logos no tienen el mismo peso (diddo y pad) | Elegir una referencia en la fase 2 |
