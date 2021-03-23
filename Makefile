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

clean:
	rm -rf v-env/
	find . -type d -name __pycache__ -delete

