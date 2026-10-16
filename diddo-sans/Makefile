# Diddo Sans · tareas habituales. Ejecutar desde diddo-sans/.
#
#   make setup     crea .venv e instala requirements.txt
#   make upstream  descarga Montserrat fijada (con verificación SHA-256)
#   make analyze   fase 1: medidas y letras normalizadas en reference/normalized/
#   make proof     fase 2: pruebas del brief en proofs/brief/
#   make clean     borra las salidas generadas (no toca reference/original/)
#
# Pendientes (fases 4–8): sources, build, test.

VENV   := .venv
PY     := $(VENV)/bin/python
export PYTHONPATH := scripts

.PHONY: all setup upstream analyze proof clean

all: analyze proof

$(VENV)/.ok: requirements.txt
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	touch $@

setup: $(VENV)/.ok

upstream: setup
	$(PY) scripts/fetch_upstream.py

analyze: upstream
	$(PY) scripts/analyze_reference.py

proof: analyze
	$(PY) scripts/proof_brief.py

clean:
	rm -rf reference/normalized proofs/brief
