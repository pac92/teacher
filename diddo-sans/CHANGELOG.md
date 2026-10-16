# Cambios

## 0.101 · 2026-10-16 · extremos redondos

- Todos los extremos libres de trazo acaban en semicírculo, como las astas de la d y la p
  (brief, decisión 3): astas sin ahusar (h m n r u…), terminales (c e s f t g j y),
  brazos de k v w x y z, barras de f t z, números, signos, acentos y mayúsculas.
  222 extremos en 93 glifos. En las diagonales cortadas en la base o la altura x
  (v x k A…), el disco no pasa de esas líneas; la letra no crece en ningún caso.
- Fidelidad con los logos y fontbakery, sin cambios.
- Pruebas regeneradas (`alfabeto.png`, `specimen.html`, `brief/*.png`). `make proof`
  falla si falta algún carácter del juego v1.

## 0.100 · 2026-10-16 · prototipo

- Primera compilación (OTF, TTF y WOFF2) a partir de Montserrat Regular, en el commit `555facf`.
- Transformación Diddo: asta ahusada en b d i l k a p q, pie en las letras de cuenco,
  ascendentes y descendentes del logo, a de un piso, punto de la i del logo,
  contraformas como en 2021 y trazo redondo de 95 UPM.
- Correcciones automáticas en ¨ % @ © ® ª º y en los diacríticos superiores.
- Fidelidad con los logos: IoU de 0,978 a 0,991 en d i o p a.
- fontbakery `check-universal`: sin FAIL.
