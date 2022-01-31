install_dev:
	python3 -m venv venv
	. venv/bin/activate
	pip3 install -r requirements.txt -r requirements-dev.txt

run:
	. venv/bin/activate
	python3 -m oneonone --help;

tests:
	. venv/bin/activate
	python3 -m unittest test/*test*

build_test:
	. venv/bin/activate
	python3 setup.py sdist
	pip3 install twine
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

build:
	. venv/bin/activate
	python3 setup.py sdist
	pip3 install twine
	twine upload dist/*

clean:
	rm -rf venv/ dist/ asana_random_one_on_one.egg-info/
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

