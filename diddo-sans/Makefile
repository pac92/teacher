# Diddo Sans: flujo completo. `make all` = sources + build + test + proof.
PY      ?= .venv/bin/python
MONTSERRAT_COMMIT = 555facfb2a18c72c3c0380f0d9c0f060453a9058
MONTSERRAT_URL    = https://raw.githubusercontent.com/JulietaUla/Montserrat/$(MONTSERRAT_COMMIT)/sources/Montserrat.glyphs
UPSTREAM  = sources/upstream/Montserrat.glyphs
INSTANCE  = build/instance_ufo/Montserrat-Regular.ufo
UFO       = sources/DiddoSans-Bold.ufo

.PHONY: all setup sources build test proof analyze clean

all: sources build test proof

setup:
	python3 -m venv .venv
	$(PY) -m pip install -r requirements.txt

$(UPSTREAM):
	mkdir -p sources/upstream
	curl -fsSL -o $@ $(MONTSERRAT_URL)
	sha256sum -c sources/upstream.sha256

$(INSTANCE): $(UPSTREAM)
	$(PY) -m fontmake -g $(UPSTREAM) -o ufo -i "Montserrat Regular" \
	  --master-dir build/master_ufo --instance-dir build/instance_ufo

analyze:
	$(PY) scripts/analyze_reference.py > /dev/null

sources: $(INSTANCE)
	$(PY) scripts/diddoize.py --out $(UFO)

build:
	$(PY) scripts/build.py

test:
	$(PY) scripts/overlay_test.py $(UFO) --min 0.975
	mkdir -p qa
	-$(PY) -m fontbakery check-universal fonts/ttf/DiddoSans-Bold.ttf \
	  --skip-network --no-progress -l WARN --json qa/fontbakery-ttf.json > /dev/null 2>&1
	-$(PY) -m fontbakery check-universal fonts/otf/DiddoSans-Bold.otf \
	  --skip-network --no-progress -l WARN --json qa/fontbakery-otf.json > /dev/null 2>&1
	$(PY) scripts/qa_summary.py

proof:
	$(PY) scripts/specimen.py

clean:
	rm -rf build
