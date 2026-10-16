# Brief de diseño de Diddo Sans Bold (fase 2)

Estado: **propuesta, pendiente de tu revisión**. El prototipo v0.100 (`fonts/`) ya
aplica las opciones marcadas como *propuesta*. Cambiar cualquiera de ellas es
cambiar un parámetro de `scripts/diddoize.py` (`DEFAULTS`) y ejecutar `make all`.

Las imágenes de comparación están en `proofs/brief/` y se regeneran con `make proof`.

## 0. Lo que el análisis automático ha corregido respecto al análisis inicial

`scripts/analyze_reference.py` mide los logos de forma reproducible
(`reference/normalized/measurements.json`). Cambian cuatro cosas de `analisis-logos.md`:

| Tema | Antes | Ahora (medido) |
|---|---|---|
| Ascendente de la d | No se mencionaba (se suponía la de Montserrat, 742) | **≈ 857 UPM**: la d del logo es un 15 % más alta que la de Montserrat |
| Descendente de la p | — | **≈ −326 UPM** (es la d girada); Montserrat llega a −194 |
| Apertura del asta | ≈ 4,5° | **≈ 3°** (pendiente 0,05). En la base, la d además se desplaza ≈ 20 UPM hacia fuera (el "pie") |
| Origen de la a | Derivada a mano de la d | Montserrat ya la trae: **`a.ss01`**, con la misma construcción (cuenco de la d y asta cortada a la altura x) |

Además, la Montserrat de 2024 tiene contraformas ≈ 4 % más altas que la de los logos (2021).
Se corrige en o, d, b, a y g (parámetro `counters`).

**Fidelidad conseguida** (`make test`; IoU = intersección/unión píxel a píxel):

| Letra | diddo (trazo 95) | pad, mismo peso |
|---|---|---|
| i | 0,979 | — |
| d | 0,980 | 0,981 |
| o | 0,991 | — |
| p | — | 0,978 |
| a | — | 0,979 |

El objetivo del plan era 0,98. Tres letras se quedan a 0,1–0,2 puntos: son diferencias de
1–3 UPM en los bordes, invisibles en las superposiciones de `proofs/overlay/`
(negro = coinciden, rojo = solo logo, azul = solo fuente). La prueba automática exige 0,975.

## 1. Peso de referencia → **propuesta: trazo de 95 UPM (diddo)**

`proofs/brief/peso.png`. pad usa 105 (≈ 10 % más grueso). Con 95, «diddo» y «pad»
compuestos con la fuente casan con el logo de diddo, y pad queda algo más ligero que su logo.
Si se prefiere que pad sea el canónico: `stroke = 105`.

## 2. Asta ahusada → **propuesta: extenderla a todas las astas de minúscula**

La regla que sale de los logos:

- El borde interior (el del cuenco, o el izquierdo si no hay cuenco) es vertical.
- El exterior se abre ≈ 3° hacia la base.
- Los dos extremos son semicírculos. En la base mide ≈ 103–117 UPM de relleno (≈ 200 con el trazo).
- En las letras con cuenco (d, b, a y, derivadas, p y q), la base se desplaza hacia fuera
  (el pie) y deja una muesca donde se une con el cuenco.

Ahora se aplica a **b d i l k a p q**, que en Montserrat tienen el asta como contorno
independiente. En **h m n r u j f t** el asta está fundida con el arco y solo se ha engrosado.
En `proofs/brief/ahusado.png` (fila «bdhiklmnpqu») se ve el problema: la d y la l
ahusadas, al lado de la h, la m y la n rectas.

Opciones:
- **a)** Extenderla a h m n r u (j f t con la misma lógica). Hay que reconstruir esas letras
  como asta + arco. Es trabajo de la fase 5, pero es la opción coherente. *(Recomendada)*
- **b)** Dejarla solo en las letras del logo (d i p a, más b q por simetría).
- **c)** Quitarla y usar el asta de Montserrat engrosada. Se pierde el rasgo más reconocible.

## 3. Pie de la d → **propuesta: en todas las letras de cuenco con asta (d b a p q)**

En pad aparece en la d, en la a y, girado, en la p. Extenderlo a la u (cuya asta derecha
es análoga) depende de la decisión 2a.

## 4. Ascendentes y descendentes → **propuesta: las del logo (857 / −331)**

`proofs/brief/ascendentes.png`. Las astas altas de la d son parte de la identidad de diddo.
Precio: el interlineado por defecto sube a ≈ 1,24 em (ver § 6). La i y la j mantienen
el punto del logo (Ø 125 UPM, borde inferior a 669), que queda por debajo de las ascendentes,
como en el logo.

## 5. Mayúsculas → **propuesta: Montserrat engrosada, sin ahusar (v1)**

Los logos no muestran ninguna. Ahusar I L D P… es posible con la misma maquinaria
(`tapered` admite mayúsculas con asta independiente), pero propongo dejarlo para
cuando haya un uso real de versales en una marca.

## 6. Métricas finales (ya aplicadas)

Se reescala para que la altura de mayúsculas visible sea 700 (escala 0,8805). Una vez engrosado:

| Métrica | Valor |
|---|---|
| UPM | 1000 |
| Altura de mayúsculas | 700 |
| Altura x | 546 |
| Ascendente (b d h k l) | 838 |
| Descendente (g j p q y) | −292 |
| typo = hhea = win | 943 / −296, `lineGap` 0, `USE_TYPO_METRICS` |

943 es la cima de los agudos de mayúscula (Á É Í Ó Ú) y −296 el fondo de g j y. El interlineado por defecto es, por tanto, 1,239 em.

## 7. El símbolo "D" de diddo → fuera de la v1

Sin cambios respecto al plan. Opcional en la v2, como `ss01`.

## 8. Correcciones automáticas (`scripts/fixes.py`)

Se resuelven por programa, con parámetros, los glifos que el engrosado rompía (fase 5,
primer pase). Conviene revisarlos a ojo en `proofs/alfabeto.png`:

| Glifo | Problema | Corrección |
|---|---|---|
| ü Ü ¨ | Los puntos se funden | Se separan hasta dejar ≥ 50 UPM de hueco visible |
| á é í ó ú ñ… | El acento se funde con la letra | Los diacríticos superiores suben 95 UPM (el doble del desplazamiento) |
| % | Los círculos se pegan a la barra | Se apartan (164 UPM en total) y el glifo se ensancha |
| @ | Hueco de un pelo entre el cuenco y la espiral | Cuenco interior al 86 % |
| © ® | La letra toca el anillo | Anillo con trazo de 40 y la C/R Diddo al 55 % |
| ª º | La ª de Montserrat es de dos pisos | Se construyen con la a y la o de Diddo al 58 %, **sin subrayado** como en Montserrat (`ordinal_underline` lo activa) |

## 9. Lo que queda abierto para fases siguientes

- **Espaciado y kerning (fase 6):** ahora se heredan de Montserrat, reescalados y con los
  márgenes engrosados. Algunos pares quedan justos (p. ej. «» €).
- **Funciones OpenType (fase 7):** el prototipo tiene `kern`, `mark` y `mkmk` generados.
  Faltan `case`, `tnum`/`pnum` y `ordn`.
- **Juego de caracteres:** v1 = 132 caracteres (ASCII + español + puntuación tipográfica).
  ¿Hace falta ç Ç (catalán), à è ò ï (catalán/francés) o ª/º con subrayado?

## Decisiones que necesito de ti

1. Peso: ¿95 (diddo) o 105 (pad)?
2. Asta ahusada: ¿a, b o c?
3. Pie de la d: ¿en d b a p q, o solo en la d?
4. Ascendentes: ¿las del logo (857) o las de Montserrat (742)?
5. Mayúsculas: ¿sin ahusar en la v1?
6. ª y º: ¿sin subrayado (como ahora) o con él?
7. ¿Algún carácter más para la v1?
