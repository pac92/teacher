# Diddo Sans

Tipografía para logotipos de subproductos de Diddo y material promocional. Deriva de
Montserrat (SIL OFL 1.1) aplicando la misma transformación que se usó en los logos de
diddo y pad. El plan completo está en [`PLAN.md`](PLAN.md).

**Estado:** fase 2. El [brief de diseño](docs/design-brief.md) está pendiente de revisión
y todavía no hay ninguna fuente compilada.

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
