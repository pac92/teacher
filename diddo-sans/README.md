# Diddo Sans

Tipografía para logotipos de subproductos de Diddo y material promocional. Deriva de
Montserrat aplicando la misma transformación que se usó en los logos de diddo y pad.

**Licencia:** [SIL Open Font License 1.1](OFL.txt), la misma que Montserrat y obligatoria
para una versión modificada. Los logos que se hagan con la fuente no quedan bajo la OFL.
Detalles en [`docs/licencia.md`](docs/licencia.md) y créditos en [`FONTLOG.txt`](FONTLOG.txt). El plan completo está en [`PLAN.md`](PLAN.md).

**Estado:** el [brief de diseño](docs/design-brief.md) está decidido; la fase 4 (construir
la fuente) está por empezar. Todavía no hay ninguna fuente compilada.

## Uso

Requiere Python ≥ 3.11 y `make`. Todo se ejecuta desde esta carpeta:

```sh
make setup     # crea .venv e instala requirements.txt
make analyze   # descarga Montserrat fijada y mide los logos → reference/normalized/
make proof     # pruebas visuales del brief → proofs/brief/
make clean     # borra las salidas generadas
```

## Documentos

- [`docs/analisis-logos.md`](docs/analisis-logos.md): de dónde salen los logos y cómo se construyeron.
- [`reference/normalized/medidas.md`](reference/normalized/medidas.md): medidas generadas por script.
- [`docs/design-brief.md`](docs/design-brief.md): decisiones de diseño, con pruebas visuales.
- [`docs/licencia.md`](docs/licencia.md): verificación de la licencia y obligaciones pendientes.
