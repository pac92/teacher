# Análisis de los logos de referencia

Fecha: 2026-10-16. Medidas tomadas sobre los SVG de `reference/original/` con
fontTools y skia-pathops. Las unidades "lienzo" son las del `viewBox` del SVG,
y las "UPM" son unidades de fuente sobre 1000/em.

## 1. Origen tipográfico: Montserrat, no Lato

- Los trazados de `pad-bold-dark.svg` conservan en su `style` el atributo
  `font-family:Montserrat`. Es un resto de haber convertido texto a trazado en Inkscape.
- Comparación geométrica de la **o** del logo (normalizada por altura)
  frente a la **o** de cada fuente. El valor es la desviación máxima entre contornos:

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

## 4. El asta característica (d, a, p, i)

- Arriba es estrecha: relleno de ≈ 11,2 en el lienzo (≈ 62 UPM) frente a ≈ 15 (≈ 82 UPM) del asta de Montserrat 400.
- Abajo es más ancha: relleno de ≈ 20 en el lienzo (≈ 110 UPM).
- El borde izquierdo es vertical y el derecho se abre hacia fuera ≈ 4,5°.
- El extremo superior es redondo.
- En la base, la d tiene un **pie/lóbulo** que baja ligeramente por debajo de la línea base,
  con una **muesca** donde el cuenco se une al asta.
- Una vez sumado el trazo de 95 UPM, el asta visible va de ≈ 157 UPM arriba a ≈ 205 UPM abajo.

La regla general para extenderla a otras letras (b, h, k, l, n, m, q, r, u, j…) **no está
determinada por los logos**. La i se ensancha hacia abajo, y la p (d girada) se ensancha
hacia arriba. Se decidirá con pruebas visuales en la fase 2.

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
