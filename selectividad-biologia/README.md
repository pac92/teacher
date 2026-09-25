# Selectividad · Biología (PAU/PEvAU Andalucía 2008–2025)

Banco de preguntas de Biología de la prueba de acceso a la universidad de Andalucía, con un visor web para usar en clase.

**Producto final:** `selectividad-biologia-visor.zip`. Descomprímelo y abre `selectividad-biologia/index.html` en el navegador (funciona sin conexión y sin servidor).

## Qué contiene

- **1356 preguntas** de 107 exámenes (2008–2025): titulares, suplentes, reservas y los «modelos» de los años en que el zip no indica la convocatoria.
- Cada pregunta es un **recorte del PDF original con sus figuras**. Si una pregunta (o su criterio) continúa en la página siguiente, los trozos se unen en una sola imagen. En 2017–2019 las preguntas 6 y 7 comparten imagen, así que se muestran juntas («Pregunta 6‑7»).
- Los **criterios de corrección** oficiales de cada pregunta, también recortados.
- **Clasificación por bloques** con dos esquemas que se pueden alternar:
  - **LOMLOE** (currículo actual, RD 243/2022): A Biomoléculas · B Genética molecular · C Biología celular · D Metabolismo · E Biotecnología · F Inmunología. La genética mendeliana ya no forma parte de Biología de 2º, así que esas preguntas aparecen como «X · Fuera del currículo LOMLOE».
  - **LOMCE** (5 bloques, el currículo de los exámenes hasta 2024): 1 Base molecular · 2 Célula · 3 Genética y evolución · 4 Microorganismos y biotecnología · 5 Inmunología.
  Cada pregunta tiene además 1–2 temas finos (glúcidos, meiosis, catabolismo…). La clasificación es automática por palabras clave y se ha revisado a mano (`tools/overrides.json`).
- Se marcan las **preguntas repetidas** entre años («También apareció en…»).

## Visor

- Filtros por bloque/tema, tipo de examen, año (rango), convocatoria, «con figura» y «repetidas».
- Buscador indexado por palabras del enunciado, bloque, tipo y año: prefijos, `"frases exactas"`, exclusiones `-palabra`, rangos `2015-2019`. Opcionalmente busca también en los criterios.
- Barra inferior: anterior / siguiente / **aleatoria** / ir al número / lista de resultados.
- Lightbox: zoom con rueda, pellizco o botones, arrastrar para mover, descargar (WebP; PNG si el visor se sirve desde una web).
- Atajos: `←` `→`, `R` aleatoria, `C` criterios, `T` texto, `Z` ampliar, `/` buscar, `L` lista.
- Enlace directo a cada pregunta (`index.html#2019-titular-juni-a6-7`).

## Estructura

```
zips/                 zips originales (sel_AAAA_biologia.zip)
tools/unpack.py       descomprime y normaliza nombres  -> build/raw
tools/catalog.py      metadatos de cada examen (año, tipo, convocatoria, criterios)
tools/extract.py      detecta preguntas, recorta imágenes, OCR de 2009 -> build/out
tools/classify.py     temas y bloques (+ tools/overrides.json con las correcciones)
tools/build_viewer.py base de datos del visor, repetidas y zip final
tools/sheet.py        hojas de revisión visual por examen
visor-src/            código del visor (index.html, app.js, style.css)
```

Para regenerarlo todo (Python 3 con `pymupdf pillow numpy scipy pytesseract` y `tesseract-ocr` con idioma `spa`):

```
python3 tools/unpack.py && python3 tools/extract.py && python3 tools/classify.py && python3 tools/build_viewer.py
```

## Limitaciones conocidas

- 2009 son PDF escaneados: la imagen es la original, pero el texto (para el buscador) sale de OCR y puede tener errores.
- 2018 Reserva B: el PDF de criterios solo trae la opción B.
- En 2008, 2009, 2011, 2012 (salvo septiembre), 2014 (modelos 2, 3, 5 y 6), 2015 y 2020 los ficheros no dicen qué modelo fue titular, suplente o reserva: aparecen como «Modelo n».
- En 2023–2025 los exámenes vienen marcados como A y B; lo más probable es que A sea la convocatoria ordinaria y B la extraordinaria, pero los ficheros no lo confirman.
