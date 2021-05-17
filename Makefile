install_dev:
	( \
		python3 -m venv v-env; \
		source v-env/bin/activate; \
		pip3 install -r requirements.txt -r requirements-dev.txt; \
    	)

run:
	( \
		source v-env/bin/activate; \
		python3 -m oneonone --help; \
	)

tests:
	( \
		source v-env/bin/activate; \
		python3 -m unittest test/*test*; \
	)

build_test:
	( \
		source v-env/bin/activate; \
		python3 setup.py sdist; \
		pip3 install twine; \
		twine upload --repository-url https://test.pypi.org/legacy/ dist/*; \
	)

build:
	( \
               source v-env/bin/activate; \
               python3 setup.py sdist; \
               pip3 install twine; \
               twine upload dist/*; \
       )

clean:
	rm -rf v-env/ dist/ asana_random_one_on_one.egg-info/
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

