.PHONY: docs test clean env clean setuptools pypi

PYTHON:=$(shell test -e env/bin/activate && echo "env/bin/python" || echo "python3")

env:
	echo "Using $(shell exec $(PYTHON) --version): $(PYTHON)"
	$(PYTHON) -m ensurepip
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pip install -r requirements.test.txt
	PYTHONPATH="./src/" $(PYTHON) -m pytest ./tests --cov=./src --cov-report html:htmlcov -vvv
	$(PYTHON) -m pycodestyle --max-line-length=120 src tests

docs:
	$(PYTHON) -m pip install -r docs/requirements.txt
	cd docs/ && make clean html

clean:
	cd docs/ && make clean

setuptools: env
	$(PYTHON) -m pip install --upgrade setuptools wheel

pypi: env setuptools test
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m pip install --user --upgrade twine
	$(PYTHON) -m twine upload dist/*

testcoverage: env
	PYTHONPATH="./src/" $(PYTHON) -m pytest --cov=./src tests/

