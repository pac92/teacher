# Análisis de los logos de referencia

Fecha: 2026-10-16. Medidas tomadas sobre los SVG de `reference/original/` con
fontTools y skia-pathops. Desde la fase 1, las medidas son reproducibles con
`make analyze` (`scripts/analyze_reference.py`), que genera `reference/normalized/medidas.md`.
Las correcciones que salieron al hacerlo están marcadas con **[corregido]** o **[nuevo]**.

Las unidades "lienzo" son las del `viewBox` del SVG, y las "UPM" son unidades de fuente
sobre 1000/em.

## 1. Origen tipográfico: Montserrat, no Lato

- Los trazados de `pad-bold-dark.svg` conservan en su `style` el atributo
  `font-family:Montserrat`. Es un resto de haber convertido texto a trazado en Inkscape.
- Comparación geométrica de la **o** del logo (normalizada por altura)
  frente a la **o** de cada fuente. El valor es la desviación máxima entre contornos.
  El script reproduce los de Montserrat con un método algo distinto (Hausdorff):
  300: 4,93 %, 350: 3,29 %, **400: 1,66 %**, 450: 1,75 %, 500: 3,52 %.
  La conclusión no cambia, aunque 450 queda más cerca de lo que decía esta tabla:

| Fuente | Desviación máx. |
|---|---|
| Montserrat 300 | 5,07 % |
| Montserrat 350 | 3,33 % |
| **Montserrat 400 (Regular)** | **1,64 %** |
| Montserrat 450 | 2,21 % |
| Montserrat 500 | 4,45 % |
| Lato Regular | 11,56 % |
| Lato Bold | 14,64 % |
| Lato Black | 15,82 % |

- Proporciones de la o: el logo tiene una relación ancho/alto de **1,000** (círculo). Montserrat 400 da 1,000 y Lato Regular 0,926.
  La relación contraforma/exterior en horizontal es 0,731 en el logo y 0,732 en Montserrat 400.
- El 1,6 % residual probablemente se explica por la versión: el logo es de 2021 y la
  Montserrat actual es la variable de 2024. Su contraforma es algo más alta que la del logo
  (0,766 frente a 0,735 de relación vertical).

**Conclusión:** el esqueleto es **Montserrat Regular (400)**. Su licencia es OFL 1.1, sin *Reserved Font Name*.

## 2. Cómo se consigue el aspecto "bold"

No se usó Montserrat Bold. Cada letra es un **contorno Regular relleno al que se suma
un trazo (`stroke`) grueso con uniones y extremos redondeados**
(`stroke-linejoin:round`, `stroke-linecap:round`, `paint-order: markers fill stroke`).
De ahí salen las tres señas de identidad:

1. Peso muy alto, visualmente cercano a un Black.
2. **Todas las esquinas redondeadas**, con un radio igual a la mitad del trazo.
3. Contraformas pequeñas y aperturas cerradas: el trazo crece hacia dentro.

| Logo | Trazo (lienzo) | Equivalente en UPM | Desplazamiento por lado |
|---|---|---|---|
| diddo | 17,2 (17,97 × 0,957 en la i; 17,86 × 0,9629 en la o) | **≈ 95** | ≈ 47,5 |
| pad | 19,0 | ≈ 105 | ≈ 52,5 |

La escala se fija así: la o mide 96,8 en el lienzo y 535 UPM en Montserrat, de modo que
1 unidad de lienzo equivale a 5,53 UPM.

⚠️ Los dos logos **no tienen el mismo peso**: pad es ≈ 10 % más grueso.
La propuesta es tomar **diddo (95 UPM)** como referencia canónica.

## 3. Letras presentes y cómo se construyeron

| Letra | Logo | Construcción observada |
|---|---|---|
| d | diddo ×2, pad | Cuenco de Montserrat y **asta modificada a mano** (ver §4). Las dos d de diddo son idénticas (misma geometría, desplazada). |
| i | diddo | Punto circular más asta **ahusada** (17,1 → 22,1 de ancho de relleno en el lienzo, más estrecha arriba). |
| o | diddo | Montserrat 400 casi sin cambios. |
| p | pad | **Es la d girada 180°** (mismas coordenadas con signo invertido). |
| a | pad | **De un piso, derivada de la d**: mismo cuenco, asta acortada a la altura x. Montserrat usa una a de dos pisos, así que esta es un rasgo propio de Diddo. |
| D (inicial de diddo) | diddo | **No es una letra tipográfica**: es un símbolo (trazo abierto de 50 de grosor, sin relleno) con forma de "D/play/bocadillo". Queda fuera del juego base. |

Todo el sistema minúsculo del logo sale, pues, de **dos piezas: el cuenco de la o/d y el asta ahusada**.

## 4. El asta característica (d, a, p, i) [corregido]

- **Es la misma pieza en la i y en la d**: un trazo ahusado con los **dos extremos
  redondos**. El borde interior es vertical y el exterior se inclina ≈ **4°**
  (4,1° en la d y 3,7° en la i).
- **El ancho del relleno depende solo de la altura**: ≈ 86 UPM en la altura x, 67 UPM a 800
  de altura y ≈ 124 UPM extrapolado a la base, igual en la i que en la d. El asta de
  Montserrat 400 mide **71 UPM** (la primera estimación decía 82; era errónea).
- El "pie" de la d es el **extremo redondo inferior de esa asta**, que baja apenas 0,7 UPM
  por debajo de la base y queda separado del cuenco por una **muesca en V**. No es un remate
  añadido.
- Una vez sumado el trazo de 95 UPM, el asta visible va de ≈ 162 UPM (a 800) a ≈ 181 UPM
  (en la altura x), y sigue ensanchándose hacia la base.
- La p, que es la d girada, se ensancha hacia la altura x y se estrecha hacia abajo.

La regla para extenderla a otras letras no está determinada por los logos. Las opciones,
con pruebas visuales, están en `design-brief.md` §2.

### Ascendentes, descendentes y punto de la i [nuevo]

Los logos **no** conservan las proporciones verticales de Montserrat:

| | Logo (relleno) | Montserrat 400 |
|---|---|---|
| Ascendente (d) | 857 | 742 |
| Descendente (p) | −326 | −194 |
| Punto de la i | ⌀ 125, centro a 730 | ⌀ 104, centro a 692 |
| Altura x | 532 | 525,5 (el `sxHeight` de la tabla OS/2, 517, está desfasado) |

## 5. Defectos de los SVG que no se deben copiar

- La d tiene nodos con retrocesos y bucles diminutos (`… 2.803-42.15-2.019-4.054-3.594-6.384-2.149-3.179 1.15-2.213 …`),
  ocultos bajo el trazo. Son restos de la edición manual.
  **Las formas se redibujarán limpias**, no se importarán tal cual.
- En el logo, el espaciado entre letras está ajustado a ojo para este logotipo y no sirve como espaciado de la fuente.

## 6. Prueba de viabilidad del engrosado automático

Se aplicó el mismo procedimiento del logo (relleno ∪ trazo redondo de 95 UPM) a 116
caracteres de Montserrat 400: A–Z, a–z, 0–9, español y puntuación. Resultado:

- **Sin problemas:** todas las letras base, incluidas las que corren más riesgo
  (e, a, B, 8, g, R, &, $, €).
- **Cambian de número de contornos (14):**
  - Acentuadas y con diéresis (á é í ó ú ü ñ Á É Í Ó Ú Ü Ñ): **el acento se funde con la letra**.
    Hay que separar los diacríticos (anclajes con hueco extra).
  - `%`: los ceros se unen a la barra.
  - `@` y `ª`: aparece o desaparece una contraforma.

  Todos tienen solución con ajustes locales.
