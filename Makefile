PYTHON=python3
PID=app.pid

run:
	$(PYTHON) app.py

start:
	$(PYTHON) app.py > /dev/null 2>&1 & echo $$! > $(PID)

test:
	pytest

package:
	python3 setup.py sdist bdist_wheel

upload-test-pypi:
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload-pypi:
	python3 -m twine upload dist/*

example:
	python3 example_component.py

kill:
	kill $$(cat $(PID))
