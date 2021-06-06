.PHONY: docs test clean env clean

PYTHON:=$(shell test -e env/bin/activate && echo "env/bin/python" || echo "python3")

env:
	echo "Using $(shell exec $(PYTHON) --version): $(PYTHON)"
	$(PYTHON) -m ensurepip

test:
	$(PYTHON) -m pip install pytest pycodestyle
	PYTHONPATH="./src/" $(PYTHON) -m pytest ./tests -vvv
	$(PYTHON) -m pycodestyle --max-line-length=120 src tests

docs:
	$(PYTHON) -m pip install -r docs/requirements.txt
	cd docs/ && make clean html

clean:
	cd docs/ && make clean
